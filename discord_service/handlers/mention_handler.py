import discord

from discord_service.clients.core_client import CoreClient
from discord_service.utility.external_id_compiler import ExternalIDCompiler


class MentionHandler:
    def __init__(self, core_client: CoreClient):
        self.client = core_client

    async def handle(self, message: discord.Message, stripped_msg: str):
        print(f"Got message: '{stripped_msg}'")
        if not await self.client.health_check():
            await message.reply("Сервер Core недоступен.")
            return
        if not stripped_msg:
            await message.reply(content=f"Введите сообщение, чтобы я ответила.")
            return
        for user in message.mentions:
            stripped_msg = stripped_msg.replace(user.mention, user.name)
        clean_msg = " ".join(stripped_msg.split())
        external_id = ExternalIDCompiler.compile(
            message.author.id,
            message.channel.id,
            message.guild.id
        )
        msg_with_name = f"{message.author.name}: {clean_msg}"
        async with message.channel.typing():
            reply = await self.client.generate_response(msg_with_name, external_id)
            if not reply:
                await message.reply("**Что-то пошло не так!**")
                return
            await message.reply(reply)