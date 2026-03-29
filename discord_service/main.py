import discord

from discord_service.clients.core_client import CoreClient
from discord_service.clients.voice_orc_client import VoiceOrchestratorClient
from discord_service.config import settings
from discord_service.dorothy_bot import DorothyBot
from discord_service.handlers.mention_handler import MentionHandler
from discord_service.voice.voice_manager import VoiceManager

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

core_client = CoreClient()
voice_orc_client = VoiceOrchestratorClient()
mention_handler = MentionHandler(core_client)
voice_manager = VoiceManager(voice_orc_client)
client = DorothyBot(intents=intents, mention_handler=mention_handler, voice_manager=voice_manager)

client.run(
    token=settings.discord_token
)
