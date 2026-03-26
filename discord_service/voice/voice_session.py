import asyncio
import uuid
from typing import Optional

from discord.ext.voice_recv import VoiceRecvClient

from discord_service.voice.audio_buffer import AudioBuffer
from discord_service.voice.audio_data_record import AudioDataRecord
from discord_service.voice.audio_listener import AudioListener


class VoiceSession:
    def __init__(self, guild_id: int, voice_client: VoiceRecvClient):
        self.session_id = str(uuid.uuid4())
        self.guild_id = guild_id
        self.voice_client = voice_client
        self.buffer = AudioBuffer()
        self.listener = AudioListener(self.buffer)
        self.is_recording = False
        self.is_pending_result = False

    async def listen(self, duration: int) -> Optional[list[AudioDataRecord]]:
        if self.is_recording:
            return None
        self.buffer.clear()
        self.listener.reset_packets()
        self.is_recording = True
        self.listener.is_recording = True
        self.is_pending_result = True
        print("[VoiceSession]: Start listening...")
        try:
            self.voice_client.listen(self.listener)
            await asyncio.sleep(duration)
            self.voice_client.stop()

            wav_data = self.buffer.get_records()

            return wav_data
        finally:
            self.is_recording = False
            self.listener.is_recording = False
            print("[VoiceSession]: Listening stopped.")