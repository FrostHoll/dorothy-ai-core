class AudioDataRecord:

    def __init__(self, user_id: int, user_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.pcm_frames = []

    def add_frame(self, frame: bytes):
        self.pcm_frames.append(frame)

    def build_pcm(self) -> bytes:
        return b''.join(self.pcm_frames)