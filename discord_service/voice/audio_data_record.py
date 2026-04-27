from collections import deque
import os
import ctypes

opus_path = os.getcwd()
ctypes.CDLL(os.path.join(opus_path, 'opus.dll'))
os.add_dll_directory(opus_path)

import opuslib
from opuslib import Decoder

class AudioDataRecord:

    def __init__(self, user_id: int, user_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.frames = []
        self.state: str = "SILENCE"
        self.pre_roll_buffer: deque = deque(maxlen=15)
        self.silence_start: float = 0.0
        self.speech_duration: float = 0.0
        self.vad_buffer = b''
        self.decoder: Decoder = opuslib.Decoder(48000, 2)

    def add_frame(self, frame: bytes):
        self.frames.append(frame)

    def build_pcm(self) -> bytes:
        return b''.join(self.frames)