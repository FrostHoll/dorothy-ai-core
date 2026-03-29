import discord
from discord import app_commands

from discord_service.voice.voice_manager import VoiceManager


def setup(tree: app_commands.CommandTree, voice_manager: VoiceManager):
    voice = app_commands.Group(name="voice", description="Голосовые команды")

    @voice.command(name="join", description="Присоединиться к голосовому каналу")
    async def join(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        if not interaction.user.voice:
            await interaction.followup.send(
                "Вы не находитесь в голосовом канале. 😔",
                ephemeral=True
            )
            return

        channel = interaction.user.voice.channel
        guild = interaction.guild

        await voice_manager.join_channel(guild, channel)

        await interaction.followup.send(
            f"Я присоединилась к {channel.name}! 👋",
            ephemeral=True)

    @voice.command(name="leave", description="Отключиться от голосового канала")
    async def leave(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.followup.send(
                "Я сейчас не нахожусь в голосовом канале. 😔",
                ephemeral=True)
            return

        await voice_manager.leave_channel(interaction.guild)

        await interaction.followup.send(
            "Пока-пока! 👋",
            ephemeral=True)

    @voice.command(name="listen", description="Послушать голосовой канал")
    @app_commands.describe(seconds="Сколько секунд слушать")
    async def listen(interaction: discord.Interaction, seconds: int):
        await interaction.response.defer(thinking=True)

        vc = interaction.guild.voice_client
        if not vc:
            await interaction.followup.send("Я не нахожусь в голосовом канале. 😔", ephemeral=True)
            return
        try:
            response = await voice_manager.listen(interaction.user.id, interaction.channel.id, interaction.guild.id, seconds)
            await interaction.followup.send(response if response else "ERROR")
        except Exception as e:
            await interaction.followup.send(f"Ошибка: {str(e)}")

    tree.add_command(voice)