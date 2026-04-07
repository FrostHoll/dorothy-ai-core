from collections import deque

class AudioDataRecord:

    def __init__(self, user_id: int, user_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.frames = []
        self.state: str = "SILENCE"
        self.pre_roll_buffer: deque = deque(maxlen=15)
        self.silence_start: float = 0.0
        self.speech_duration: float = 0.0
        self.vad_buffer = b''

    def add_frame(self, frame: bytes):
        self.frames.append(frame)

    def build_pcm(self) -> bytes:
        return b''.join(self.frames)