import io
import wave


class AudioEncoder:

    @staticmethod
    def pcm_to_wav(pcm_bytes: bytes) -> bytes:
        buffer = io.BytesIO()

        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(pcm_bytes)

        return buffer.getvalue()
