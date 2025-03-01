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
                voice_client.stop()  # 현재 곡 중지

                if self.song_queues[guild_id]:  # 서버별 대기열 확인
                    next_song = self.song_queues[guild_id].pop(0)  # 첫 번째 곡을 가져옴
                    try:
                        # 음성 채널 연결 확인
                        if not voice_client.is_connected():
                            if interaction.user.voice:
                                voice_client = await interaction.user.voice.channel.connect()
                            else:
                                await self.music_player.send_message(interaction, "음성 채널에 먼저 입장해주세요!")
                                return

                        title = await self.music_player.play_song(interaction, next_song)
                        await self.music_player.send_message(interaction, f"다음 곡 재생 중: {title} 🎶")
                    except Exception as e:
                        await self.music_player.send_message(interaction, f"재생 실패: {str(e)}")
                else:
                    await self.music_player.send_message(interaction, "대기열이 비어있습니다.")
            except Exception as e:
                await self.music_player.send_message(interaction, f"스킵 중 오류 발생: {str(e)}")
        else:
            await self.music_player.send_message(interaction, "현재 재생 중인 곡이 없습니다.")
