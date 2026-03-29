class VoiceSegment:
    def __init__(self, user_id: int, user_name: str, pcm: bytes):
        self.user_id = user_id
        self.user_name = user_name
        self.pcm_48k = pcm