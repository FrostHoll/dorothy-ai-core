import discord


class DorothyBot(discord.Client):
    user: discord.ClientUser

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"Logged in as {self.user} ID: {self.user.id}")