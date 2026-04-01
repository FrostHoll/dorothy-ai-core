from discord_service.utility.audio_decoder import AudioDecoder


class AudioDataRecord:

    def __init__(self, user_id: int, user_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.opus_frames = []

    def add_frame(self, frame: bytes):
        self.opus_frames.append(frame)

    def build_pcm(self) -> bytes:
        return AudioDecoder.decode_opus_frames_to_pcm(self.opus_frames)