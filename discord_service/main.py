import discord
import json

from discord_service.dorothy_bot import DorothyBot

intents = discord.Intents.default()
intents.message_content = True

with open("discord_service\\config.json", 'r', encoding='utf-8') as file:
    data = json.load(file)
    token = data['discord-token']

client = DorothyBot(intents=intents)

client.run(
    token=token
)
