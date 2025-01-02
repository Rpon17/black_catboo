import discord
from discord.ext import commands
from discord import app_commands
from yt_dlp import YoutubeDL
from settings import ydl_opts, ffmpeg_opts  # 설정 파일에서 가져옴
import asyncio
from music_utils import MusicPlayer

class Skip(commands.Cog):
    def __init__(self, bot, song_queue, current_song):
        self.bot = bot
        self.song_queue = song_queue
        self.current_song = current_song
        self.music_player = MusicPlayer(bot, song_queue, current_song)

    @app_commands.command(name="스킵", description="현재 곡을 스킵하고 다음 곡을 재생합니다.")
    async def skip(self, interaction: discord.Interaction):
        await interaction.response.defer()
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if voice_client and voice_client.is_playing():
            voice_client.stop()

            if self.song_queue:
                next_song = self.song_queue.pop(0)
                title = await self.music_player.play_song(interaction, next_song)
                await self.music_player.send_message(interaction, f"다음 곡 재생 중: {title} 🎶")
            elif self.current_song:
                video_id = self.music_player.extract_video_id(self.current_song)
                if video_id:
                    recommended_song = f"https://www.youtube.com/watch?v={video_id}&list=RD"
                    title = await self.music_player.play_song(interaction, recommended_song)
                    await self.music_player.send_message(interaction, f"추천 곡 재생 중: {title} 🎶")
                else:
                    await self.music_player.send_message(interaction, "캣부가 추천을 받습니다")
            else:
                await self.music_player.send_message(interaction, "캣부가 다음 무대를 준비중입니다")
        else:
            await self.music_player.send_message(interaction, "캣부가 디렉을 대기중입니다")
