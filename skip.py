import discord
from discord.ext import commands
from discord import app_commands
from yt_dlp import YoutubeDL
from settings import ydl_opts, ffmpeg_opts  # 설정 파일에서 가져옴
import asyncio
from music_utils import MusicPlayer

class Skip(commands.Cog):
    def __init__(self, bot, song_queues):
        self.bot = bot
        self.song_queues = song_queues
        self.music_player = MusicPlayer(bot, song_queues)

    @app_commands.command(name="스킵", description="현재 곡을 스킵하고 다음 곡을 재생합니다.")
    async def skip(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if guild_id not in self.song_queues:
            self.song_queues[guild_id] = []

        await interaction.response.defer()
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if voice_client and voice_client.is_playing():
            try:
                # 현재 곡 중지 (이후 자동으로 다음 곡을 재생해야 함)
                voice_client.stop()
                await self.music_player.send_message(interaction, "현재 곡을 스킵했습니다. ⏭️")
            except Exception as e:
                await self.music_player.send_message(interaction, f"스킵 중 오류 발생: {str(e)}")
        else:
            await self.music_player.send_message(interaction, "현재 재생 중인 곡이 없습니다.")
