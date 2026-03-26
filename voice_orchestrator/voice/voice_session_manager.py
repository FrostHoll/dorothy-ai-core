import asyncio
import time
import threading

from voice_orchestrator.voice.voice_segment import VoiceSegment
from voice_orchestrator.voice.voice_session import VoiceSession
from voice_orchestrator.voice.voice_session_state import VoiceSessionState


class VoiceSessionManager:
    def __init__(self):
        self.sessions: dict[str, VoiceSession] = {}
        self.silence_timeout = 3.0

    def get_or_create(self, session_id: str, external_id: str) -> VoiceSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = VoiceSession(session_id, external_id)
        return self.sessions[session_id]

    async def add_segment(self, session_id: str, external_id: str, segment: VoiceSegment) -> None:
        session = self.get_or_create(session_id, external_id)

        if session.state != VoiceSessionState.COLLECTING:
            return

        session.segments.append(segment)
        session.pending_stt += 1
        session.last_activity = time.time()

        await self.enqueue_stt(session, segment)

    async def enqueue_stt(self, session: VoiceSession, segment: VoiceSegment) -> None:
        ## --- TEST ---
        print("sending to stt...")
        asyncio.create_task(self.mock_stt_response(session.session_id, f"[Transcribed text for {segment.user_name}]"))

    async def mock_stt_response(self, session_id: str, text: str):
        print("got audio")
        await asyncio.sleep(4.0)
        print("sending mock transcribe")
        await self.on_stt_result(session_id, text)

    async def on_stt_result(self, session_id: str, text: str):
        session = self.sessions[session_id]

        print(f"Got STT result: {text}")
        session.pending_stt -= 1
        session.messages.append(text)

        await self.maybe_finalize(session)

    async def maybe_finalize(self, session: VoiceSession):
        if session.state != VoiceSessionState.COLLECTING:
            return

        is_silence = time.time() - session.last_activity > self.silence_timeout

        if is_silence and session.pending_stt == 0:
            session.state = VoiceSessionState.GENERATING
            print("Generating response")

            response = await self.generate_response(session)

            print(f"Sending response: {response}")
            session.result = response
            session.state = VoiceSessionState.DONE

    async def generate_response(self, session: VoiceSession):
        await asyncio.sleep(2.0)
        return f"[Generated response for {session.messages}]"