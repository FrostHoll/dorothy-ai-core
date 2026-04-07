from discord_service.utility.audio_decoder import AudioDecoder
from discord_service.voice.audio_buffer import AudioBuffer
from discord.ext.voice_recv import AudioSink, VoiceData

import time

from discord_service.voice.vad_manager import VADManager


class AudioListener(AudioSink):
    def __init__(self, buffer: AudioBuffer, vad_manager: VADManager, /):
        super().__init__()
        self.buffer = buffer
        self.is_recording = False
        self.start_timestamp = 0.0
        self.vad_manager = vad_manager
        self.vad_callback = None

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
            pcm_frame = AudioDecoder.decode_opus_to_pcm_16k_frame(opus_frame)
            if pcm_frame:
                if self.vad_callback:
                    record = self.buffer.get_or_create_record(user.id, user.name)
                    self.vad_manager.process_packet(
                        record,
                        pcm_frame,
                        self.vad_callback
                    )
                else:
                    self.buffer.add_user_frame(user.id, user.name, pcm_frame)

    def cleanup(self) -> None:
        self.buffer.clear()
        print("AudioSink cleanup is called.")