import os
import ctypes

opus_path = os.getcwd()
ctypes.CDLL(os.path.join(opus_path, 'opus.dll'))
os.add_dll_directory(opus_path)

import opuslib

from discord_service.voice.audio_buffer import AudioBuffer
from discord.ext.voice_recv import AudioSink, VoiceData


class AudioListener(AudioSink):
    def __init__(self, buffer: AudioBuffer, /):
        super().__init__()
        self.buffer = buffer
        self.is_recording = False
        self.packets = 0
        self.decoder = opuslib.Decoder(48000, 2)


    def reset_packets(self):
        self.packets = 0

    def wants_opus(self) -> bool:
        return True

    def write(self, user, data: VoiceData) -> None:

        if not self.is_recording:
            return
        if self.packets < 50:
            self.packets += 1
            return
        if data.packet:
            try:
                opus_frame = data.packet.decrypted_data
                pcm_frame = self.decoder.decode(opus_frame, frame_size=960)
                self.buffer.add_user_frame(user.id, user.name, pcm_frame)
            except opuslib.OpusError:
                pass

    def cleanup(self) -> None:
        pass