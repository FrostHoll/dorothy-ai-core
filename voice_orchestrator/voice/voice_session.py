import time

from voice_orchestrator.voice.voice_session_state import VoiceSessionState


class VoiceSession:
    def __init__(self, session_id: str, external_id: str):
        self.session_id = session_id
        self.external_id = external_id

        self.state = VoiceSessionState.COLLECTING

        self.segments = []
        self.messages = []
        self.response = None

        self.pending_stt = 0

        self.last_activity = time.time()
        self.created_at = time.time()

        self.result = None

    def reset(self):
        self.state = VoiceSessionState.COLLECTING
        self.segments.clear()
        self.messages.clear()
        self.response = None
        self.result = None