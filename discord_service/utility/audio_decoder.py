import os
import ctypes

from opuslib import Decoder, OpusError

import numpy as np
import resampy

class AudioDecoder:
    @staticmethod
    def decode_opus_frames_to_pcm(decoder: Decoder, opus_frames: list[bytes]) -> bytes:
        result = []
        for frame in opus_frames:
            try:
                result.append(decoder.decode(frame, frame_size=960))
            except OpusError:
                pass
        return b''.join(result)

    @staticmethod
    def decode_opus_to_pcm_16k_frame(decoder: Decoder, frame: bytes) -> bytes | None:
        try:
            pcm_48k = decoder.decode(frame, frame_size=960)

            audio = np.frombuffer(pcm_48k, dtype=np.int16).reshape(-1, 2)
            mono = audio.mean(axis=1).astype(np.int16)

            audio_16k = resampy.resample(mono.astype(np.float32), 48000, 16000)

            return audio_16k.astype(np.int16).tobytes()
        except OpusError:
            return None