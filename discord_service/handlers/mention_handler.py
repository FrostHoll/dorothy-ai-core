import discord

from discord_service.clients.core_client import CoreClient
from discord_service.utility.external_id_compiler import ExternalIDCompiler


class MentionHandler:
    def __init__(self, core_client: CoreClient):
        self.client = core_client

    async def handle(self, message: discord.Message, stripped_msg: str):
        print(f"Got message: '{stripped_msg}'")
        external_id = ExternalIDCompiler.compile(
            message.author.id,
            message.channel.id,
            message.guild.id
        )
        if not stripped_msg:
            await message.reply(content=f"Привет, {message.author.display_name}!")
            return
        stripped_msg = f"{message.author.name}: {stripped_msg}"
        async with message.channel.typing():
            reply = await self.client.generate_response(stripped_msg, external_id)
            if not reply:
                await message.reply("**Что-то пошло не так!**")
                return
            await message.reply(reply)