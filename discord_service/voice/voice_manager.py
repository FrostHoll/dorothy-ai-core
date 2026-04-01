import asyncio
import io

import discord.channel
from discord import Guild
from discord.ext.voice_recv import VoiceRecvClient

from discord_service.clients.voice_orc_client import VoiceOrchestratorClient
from discord_service.utility.external_id_compiler import ExternalIDCompiler
from discord_service.voice.voice_session import VoiceSession


class VoiceManager:
    def __init__(self, voice_orc_client: VoiceOrchestratorClient):
        self.sessions = {}
        self.voice_orc_client = voice_orc_client

    async def join_channel(self, guild: Guild, callback_channel, target_vc: discord.channel.VoiceChannel) -> VoiceSession:

        if guild.id in self.sessions:
            return self.sessions[guild.id]

        if guild.voice_client:
            voice_client = await guild.voice_client.move_to(target_vc)
        else:
            voice_client = await target_vc.connect(cls=VoiceRecvClient)

        session = VoiceSession(guild.id, callback_channel, voice_client)

        self.sessions[guild.id] = session

        return session

    async def leave_channel(self, guild: Guild) -> None:
        session: VoiceSession = self.sessions[guild.id]

        await session.voice_client.disconnect(force=False)

        self.sessions.pop(guild.id)

    async def listen(self, user_id: int, channel_id: int, guild_id: int, duration: int) -> str | None:
        if guild_id not in self.sessions:
            raise ValueError

        if not await self.voice_orc_client.health_check():
            return None

        session: VoiceSession = self.sessions[guild_id]

        records = await session.listen(duration)
        asyncio.create_task(self.poll_result(session))

        if records:
            for rec in records:
                if rec.opus_frames:
                    response = await self.voice_orc_client.request_process(
                        voice_session_id=session.session_id,
                        external_id=ExternalIDCompiler.compile(user_id, channel_id, guild_id),
                        audio_record=rec
                    )
                    if not response:
                        return None
            return "OK"
        return None

    async def on_orchestrator_result(self, session: VoiceSession, result: bytes, transcript: str, response_text: str):

        print(f"Got Voice Orchestrator result")
        buf = io.BytesIO(result)

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
        while session.is_pending_result:
            await asyncio.sleep(2.0)
            result = await self.voice_orc_client.poll_result(session.session_id)
            if result:
                session.is_pending_result = False
                await self.on_orchestrator_result(session, result[0], result[1], result[2])