import asyncio
import uuid
from asyncio import Task
from typing import Optional

from discord.ext.voice_recv import VoiceRecvClient

from discord_service.voice.audio_buffer import AudioBuffer
from discord_service.voice.audio_data_record import AudioDataRecord
from discord_service.voice.audio_listener import AudioListener
from discord_service.voice.vad_manager import VADManager


class VoiceSession:
    def __init__(self, guild_id: int, callback_channel, voice_client: VoiceRecvClient, vad_manager: VADManager):
        self.session_id = str(uuid.uuid4())
        self.guild_id = guild_id
        self.voice_client = voice_client
        self.callback_channel = callback_channel
        self.poll_result_task: Task | None = None

        self.buffer = AudioBuffer()
        self.listener = AudioListener(self.buffer, vad_manager)
        self.is_recording = False
        self.is_vad = False

    async def listen(self, duration: int) -> Optional[list[AudioDataRecord]]:
        if self.is_recording:
            return None
        self.buffer.clear()
        self.listener.vad_callback = None
        self.is_recording = True
        self.listener.is_recording = True
        print("[VoiceSession]: Start listening...")
        try:
            self.listener.set_start_timestamp()
            self.voice_client.listen(self.listener)
            await asyncio.sleep(duration)
            wav_data = self.buffer.get_records()
            self.voice_client.stop_listening()

            return wav_data
        finally:
            self.is_recording = False
            self.listener.is_recording = False
            print("[VoiceSession]: Listening stopped.")


    def start_listening(self, callback) -> None:
        if self.is_recording:
            return
        self.buffer.clear()
        self.listener.vad_callback = callback
        self.is_recording = True
        self.listener.is_recording = True
        print("[VoiceSession]: Start listening with VAD...")
        try:
            self.listener.set_start_timestamp()
            self.voice_client.listen(self.listener)
        except Exception as e:
            print(f"[VoiceSession]: Error: {str(e)}")

    def stop_listening(self) -> None:
        self.voice_client.stop_listening()
        self.is_recording = False
        self.listener.is_recording = False
        self.poll_result_task.cancel()
        print("[VoiceSession]: Listening stopped.")