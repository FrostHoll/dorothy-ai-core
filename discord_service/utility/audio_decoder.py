import subprocess


class AudioDecoder:
    @staticmethod
    async def opus_to_wav(opus_data: bytes) -> bytes:
        command = [
            'ffmpeg',
            '-i', 'pipe:0',
            '-ar', '16000',
            '-ac', '1',
            '-f', 'wav'
            'pipe:1'
        ]

        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate(input=opus_data)

        if process.returncode != 0:
            print(f"FFmpeg error: {stderr.decode()}")
            return b''

        return stdout