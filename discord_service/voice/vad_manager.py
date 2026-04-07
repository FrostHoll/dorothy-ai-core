import time
import torch.hub

from discord_service.voice.audio_data_record import AudioDataRecord


class VADManager:
    def __init__(self):
        print("[VADManager]: Load VAD model...")
        self.model, _ = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad'
        )
        print("[VADManager]: VAD model loaded.")
        self.silence_threshold = 600
        self.chunk_ms = 20
        self.min_speech_ms = 250
        self.vad_buffer_size = 1024

    def is_speech(self, pcm_chunk: bytes) -> bool:
        tensor = torch.frombuffer(pcm_chunk, dtype=torch.int16).float() / 32768.0
        confidence = self.model(tensor, 16000).item()
        return confidence > 0.5

    def process_packet(self, user_record: AudioDataRecord, pcm_chunk: bytes, callback) -> None:
        user_record.vad_buffer += pcm_chunk

        if len(user_record.vad_buffer) < self.vad_buffer_size:
            return

        chunk = user_record.vad_buffer[:1024]
        user_record.vad_buffer = user_record.vad_buffer[1024:]

        self._process_chunk(user_record, chunk, callback)

    def _process_chunk(self, user_record: AudioDataRecord, pcm_chunk: bytes, callback) -> None:
        is_speech = self.is_speech(pcm_chunk)

        if user_record.state == "SILENCE":
            user_record.pre_roll_buffer.append(pcm_chunk)
            if is_speech:
                user_record.state = "SPEECH_START"
                user_record.frames = list(user_record.pre_roll_buffer)

        elif user_record.state in ("SPEECH_START", "SPEAKING"):
            user_record.frames.append(pcm_chunk)
            if is_speech:
                user_record.state = "SPEAKING"
            else:
                user_record.state = "END_WAIT"
                user_record.silence_start = time.time()

        elif user_record.state == "END_WAIT":
            user_record.frames.append(pcm_chunk)
            if is_speech:
                user_record.state = "SPEAKING"
            elif (time.time() - user_record.silence_start) * 1000 > self.silence_threshold:
                duration = len(user_record.frames) * self.chunk_ms
                if duration >= self.min_speech_ms:
                    print(f"Sending voice of {user_record.user_name}...")
                    callback(user_record)
                user_record.state = "SILENCE"
                user_record.frames.clear()