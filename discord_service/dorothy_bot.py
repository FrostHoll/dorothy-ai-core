import discord

from discord_service.handlers.mention_handler import MentionHandler


class DorothyBot(discord.Client):
    user: discord.ClientUser

    def __init__(self, *, intents: discord.Intents, mention_handler: MentionHandler):
        super().__init__(intents=intents)
        self.mention_handler = mention_handler
        self.tag = ""

    async def on_ready(self):
        print(f"Logged in as {self.user} ID: {self.user.id}")

    async def on_message(self, message: discord.Message):
        if message.author.id == self.user.id:
            return
        if self.tag == "":
            self.tag = f"<@{self.user.id}>"
        if self.tag in message.content:
            await self.mention_handler.handle(message,
                                              message.content.replace(self.tag, "").strip())