import io
import numpy as np
import torch
from tts_service.config import TTSConfig as Config

class SileroEngine:
    def __init__(self):
        print("[TTS Service]: Loading Silero model...")
        model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language=Config.language,
            speaker=Config.model_id
        )
        model.to(Config.device)
        self.model = model
        print("[TTS Service]: Silero model loaded.")

    def synthesize(self, text: str) -> io.BytesIO | None:
        print(f"[TTS Service]: Got text: '{text}'")
        try:
            with torch.inference_mode():
                audio_tensor = self.model.apply_tts(
                    text=text,
                    speaker=Config.speaker,
                    sample_rate=Config.sample_rate,
                    put_accent=True,
                    put_yo=True
                )
        except Exception as e:
            print(f"[TTS Service]: Generation failed: {str(e)}")
            return None

        audio_np = (audio_tensor.cpu().numpy() * 32767).astype("int16")
        buf = io.BytesIO()
        self._write_wav(buf, audio_np, Config.sample_rate)
        buf.seek(0)
        return buf


    def _write_wav(self, buf: io.BytesIO, pcm: "np.ndarray", sample_rate: int) -> None:
        import struct
        num_samples = len(pcm)
        num_channels = 1
        bits_per_sample = 16
        byte_rate = sample_rate * num_channels * bits_per_sample // 8
        block_align = num_channels * bits_per_sample // 8
        data_size = num_samples * block_align

        buf.write(b"RIFF")
        buf.write(struct.pack("<I", 36 + data_size))
        buf.write(b"WAVE")
        buf.write(b"fmt ")
        buf.write(struct.pack("<IHHIIHH", 16, 1, num_channels, sample_rate,
                              byte_rate, block_align, bits_per_sample))
        buf.write(b"data")
        buf.write(struct.pack("<I", data_size))
        buf.write(pcm.tobytes())