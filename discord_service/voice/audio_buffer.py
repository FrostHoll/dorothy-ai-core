from discord_service.voice.audio_data_record import AudioDataRecord


class AudioBuffer:
    def __init__(self):
        self.users_frames: dict[int, AudioDataRecord] = {}

    def get_or_create_record(self, user_id: int, user_name: str) -> AudioDataRecord:
        if not user_id in self.users_frames:
            self.users_frames[user_id] = AudioDataRecord(
                user_id = user_id,
                user_name = user_name
            )
        return self.users_frames[user_id]

    def add_user_frame(self, user_id: int, user_name: str, frame: bytes) -> None:
        if not user_id in self.users_frames:
            self.users_frames[user_id] = AudioDataRecord(
                user_id = user_id,
                user_name = user_name
            )
        self.users_frames[user_id].add_frame(frame)

    def get_records(self) -> list[AudioDataRecord]:
        return [f for _, f in self.users_frames.items()]

    def clear(self) -> None:
        self.users_frames.clear()