import discord
from discord import app_commands

from discord_service.handlers.mention_handler import MentionHandler
from discord_service.voice.voice_manager import VoiceManager


class DorothyBot(discord.Client):
    user: discord.ClientUser

    def __init__(self, *, intents: discord.Intents, mention_handler: MentionHandler, voice_manager: VoiceManager):
        super().__init__(intents=intents)
        self.mention_handler = mention_handler
        self.voice_manager = voice_manager
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} ID: {self.user.id}")

    async def setup_hook(self) -> None:
        from commands.voice_commands import setup as voice_commands_setup

        voice_commands_setup(self.tree, self.voice_manager)

        #GUILD_ID = 1455226648948637709 # Developer's Lair
        GUILD_ID = 621369145862389760 # Red Ufa Gang

        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("Commands in tree:")
        for cmd in self.tree.get_commands():
            print(f"/{cmd.name}")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.id == self.user.id:
            return
        if self.user.mention in message.content:
            await self.mention_handler.handle(message,
                                              message.content.replace(self.user.mention, "").strip())