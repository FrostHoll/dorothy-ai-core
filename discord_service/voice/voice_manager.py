import asyncio
import io
from functools import partial

import discord.channel
from discord import Guild
from discord.ext.voice_recv import VoiceRecvClient

from discord_service.clients.voice_orc_client import VoiceOrchestratorClient
from discord_service.utility.external_id_compiler import ExternalIDCompiler
from discord_service.voice.audio_data_record import AudioDataRecord
from discord_service.voice.vad_manager import VADManager
from discord_service.voice.voice_session import VoiceSession

class VoiceManager:
    def __init__(self, voice_orc_client: VoiceOrchestratorClient, vad: VADManager):
        self.sessions = {}
        self.voice_orc_client = voice_orc_client
        self.vad = vad

    async def join_channel(self, guild: Guild, callback_channel, target_vc: discord.channel.VoiceChannel) -> VoiceSession:

        if guild.id in self.sessions:
            return self.sessions[guild.id]

        if guild.voice_client:
            voice_client = await guild.voice_client.move_to(target_vc)
        else:
            voice_client = await target_vc.connect(cls=VoiceRecvClient)

        session = VoiceSession(guild.id, callback_channel, voice_client, self.vad)

        self.sessions[guild.id] = session

        return session

    async def leave_channel(self, guild: Guild) -> None:
        session: VoiceSession = self.sessions[guild.id]

        await session.voice_client.disconnect(force=False)

        if session.poll_result_task:
            session.poll_result_task.cancel()
        self.sessions.pop(guild.id)

    async def listen(self, user_id: int, channel_id: int, guild_id: int, duration: int) -> str | None:
        if guild_id not in self.sessions:
            return "ERROR: Voice session was not found."

        if not await self.voice_orc_client.health_check():
            return "ERROR: Voice orchestrator module is offline."

        session: VoiceSession = self.sessions[guild_id]

        if session.is_recording:
            return "ERROR: Already recording."

        session.is_vad = False
        records = await session.listen(duration)
        session.poll_result_task = asyncio.create_task(self.poll_result(session))

        if records:
            for rec in records:
                if rec.frames:
                    response = await self.voice_orc_client.request_process(
                        voice_session_id=session.session_id,
                        external_id=ExternalIDCompiler.compile(user_id, channel_id, guild_id),
                        audio_record=rec
                    )
                    if not response:
                        return "ERROR: Process request failed."
            return "OK"
        return "ERROR: Audio was not found."

    async def start_listening(self, user_id: int, channel_id: int, guild_id: int) -> str | None:
        if guild_id not in self.sessions:
            return "ERROR: Voice session was not found."

        if not await self.voice_orc_client.health_check():
            return "ERROR: Voice orchestrator module is offline."

        session: VoiceSession = self.sessions[guild_id]

        loop = asyncio.get_running_loop()

        if session.is_recording:
            return "ERROR: Already recording."

        callback = lambda record: asyncio.run_coroutine_threadsafe(
            self.on_vad_send_request(record, session.session_id, external_id=ExternalIDCompiler.compile(user_id, channel_id, guild_id)),
            loop
        ).result()

        session.is_vad = True
        session.start_listening(callback)
        task = asyncio.create_task(self.poll_result(session))
        session.poll_result_task = task

        return "OK"

    async def stop_listening(self, guild_id: int):
        if guild_id not in self.sessions:
            return "ERROR: Voice session was not found."

        session: VoiceSession = self.sessions[guild_id]

        session.stop_listening()

    async def on_vad_send_request(self, record: AudioDataRecord, session_id: str, external_id: str):
        try:
            response = await self.voice_orc_client.request_process(
                voice_session_id=session_id,
                external_id=external_id,
                audio_record=record
            )
            if not response:
                raise "ERROR: Process request failed."
        except Exception as e:
            print(f"[VoiceOrchestrator]: {str(e)}")

    async def on_orchestrator_result(self, session: VoiceSession, result: bytes, transcript: str, response_text: str):

        print(f"Got Voice Orchestrator result")
        buf = io.BytesIO(result)

        if not session.is_vad:
            session.poll_result_task.cancel()

        audio_source = discord.FFmpegPCMAudio(
            buf,
            pipe=True,
            options="-vn"
        )

        vc = session.voice_client
        if vc.is_playing():
            vc.stop_playing()
        vc.play(audio_source)

        embed = discord.Embed(color=0x5865F2)

        messages = transcript.split("\n")
        for msg in messages:
            user, text = msg.split(": ")
            embed.add_field(name=user, value=text, inline=False)
        embed.add_field(name="Ответ", value=response_text, inline=False)

        await session.callback_channel.send(embed=embed)

    async def poll_result(self, session: VoiceSession):
        while True:
            try:
                await asyncio.sleep(2.0)
                result = await self.voice_orc_client.poll_result(session.session_id)
                if result:
                    await self.on_orchestrator_result(session, result[0], result[1], result[2])
            except asyncio.CancelledError:
                print("Poll result task finished.")
                return