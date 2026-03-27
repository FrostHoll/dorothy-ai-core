import asyncio
import time

from voice_orchestrator.http_clients.stt_client import STTClient
from voice_orchestrator.voice.voice_segment import VoiceSegment
from voice_orchestrator.voice.voice_session import VoiceSession
from voice_orchestrator.voice.voice_session_state import VoiceSessionState


class VoiceSessionManager:
    def __init__(self, stt_client: STTClient):
        self.sessions: dict[str, VoiceSession] = {}
        self.silence_timeout = 3.0
        self.stt_client = stt_client

    def get_or_create(self, session_id: str, external_id: str) -> VoiceSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = VoiceSession(session_id, external_id)
        return self.sessions[session_id]

    async def add_segment(self, session_id: str, external_id: str, segment: VoiceSegment) -> None:
        session = self.get_or_create(session_id, external_id)

        if session.state == VoiceSessionState.DONE:
            session.reset()

        if session.state != VoiceSessionState.COLLECTING:
            return

        session.segments.append(segment)
        session.pending_stt += 1
        session.last_activity = time.time()

        await self.enqueue_stt(session, segment)

    async def enqueue_stt(self, session: VoiceSession, segment: VoiceSegment) -> None:
        print("sending to stt...")
        job_id = await self.stt_client.enqueue_segment(segment.pcm_48k, segment.user_name)
        asyncio.create_task(self.poll_result(session, job_id))

    async def poll_result(self, session: VoiceSession, job_id: str) -> None:
        while True:
            await asyncio.sleep(3.0)
            result = await self.stt_client.poll_result(job_id)
            if result:
                await self.on_stt_result(session.session_id, result)
                return

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