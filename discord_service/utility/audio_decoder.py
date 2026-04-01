import os
import ctypes

opus_path = os.getcwd()
ctypes.CDLL(os.path.join(opus_path, 'opus.dll'))
os.add_dll_directory(opus_path)

import opuslib

opus_decoder = opuslib.Decoder(48000, 2)

class AudioDecoder:
    @staticmethod
    def decode_opus_frames_to_pcm(opus_frames: list[bytes]) -> bytes:
        result = []
        for frame in opus_frames:
            try:
                result.append(opus_decoder.decode(frame, frame_size=960))
            except opuslib.OpusError:
                pass
        return b''.join(result)