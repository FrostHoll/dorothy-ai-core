from discord_service.voice.audio_buffer import AudioBuffer
from discord.ext.voice_recv import AudioSink, VoiceData

import time

class AudioListener(AudioSink):
    def __init__(self, buffer: AudioBuffer, /):
        super().__init__()
        self.buffer = buffer
        self.is_recording = False
        self.start_timestamp = 0.0

    def set_start_timestamp(self):
        self.start_timestamp = time.time() + 0.3

    def wants_opus(self) -> bool:
        return True

    def write(self, user, data: VoiceData) -> None:
        if not self.is_recording:
            return
        if time.time() < self.start_timestamp:
            return
        if data.packet.decrypted_data:
            opus_frame = data.packet.decrypted_data
            self.buffer.add_user_frame(user.id, user.name, opus_frame)

    def cleanup(self) -> None:
        self.buffer.clear()
        print("AudioSink cleanup is called.")