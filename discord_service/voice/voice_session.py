import asyncio
import wave
from typing import Optional

from discord.ext.voice_recv import VoiceRecvClient

from discord_service.voice.audio_buffer import AudioBuffer
from discord_service.voice.audio_listener import AudioListener


class VoiceSession:
    def __init__(self, guild_id: int, voice_client: VoiceRecvClient):
        self.guild_id = guild_id
        self.voice_client = voice_client
        self.buffer = AudioBuffer()
        self.listener = AudioListener(self.buffer)
        self.is_recording = False

    async def listen(self, duration: int) -> Optional[bytes]:
        if self.is_recording:
            return None
        self.buffer.clear()
        self.listener.reset_packets()
        self.is_recording = True
        self.listener.is_recording = True
        print("[VoiceSession]: Start listening...")
        try:
            self.voice_client.listen(self.listener)
            await asyncio.sleep(duration)
            self.voice_client.stop()

            wav_data = self.buffer.build()


            try:

                with wave.open("E:\\test.wav", 'wb') as wf:
                    wf.setnchannels(2)
                    wf.setsampwidth(2)
                    wf.setframerate(48000)
                    wf.writeframes(wav_data)
                    print("file saved")
            except Exception as e:
                print(f"Error: {str(e)}")

            return wav_data
        finally:
            self.is_recording = False
            self.listener.is_recording = False
            print("[VoiceSession]: Listening stopped.")