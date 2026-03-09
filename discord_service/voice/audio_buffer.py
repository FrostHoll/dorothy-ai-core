class AudioBuffer:
    def __init__(self):
        self.frames = []

    def add_frame(self, frame: bytes) -> None:
        self.frames.append(frame)

    def build(self) -> bytes:
        return b''.join(self.frames)

    def clear(self) -> None:
        self.frames.clear()