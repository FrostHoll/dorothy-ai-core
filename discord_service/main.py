import discord

from discord_service.clients.core_client import CoreClient
from discord_service.config import settings
from discord_service.dorothy_bot import DorothyBot
from discord_service.handlers.mention_handler import MentionHandler

intents = discord.Intents.default()
intents.message_content = True

core_client = CoreClient()
mention_handler = MentionHandler(core_client)
client = DorothyBot(intents=intents, mention_handler=mention_handler)

client.run(
    token=settings.discord_token
)
