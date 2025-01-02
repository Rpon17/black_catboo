import discord
from discord.ext import commands
from discord import app_commands
import random
from music_utils import MusicPlayer
import asyncio

class Catmakase(commands.Cog):
    def __init__(self, bot, song_queue, current_song):
        self.bot = bot
        self.song_queue = song_queue
        self.current_song = current_song
        self.music_player = MusicPlayer(bot, song_queue, current_song)
        # 캣마카세 플레이리스트
        self.catmakase_playlist = [
            "https://www.youtube.com/watch?v=BQif6mSCl8Y",
            "https://www.youtube.com/watch?v=6-ZNmVWM_UQ"
        ]

    @app_commands.command(name="캣마카세", description="캣부가 랜덤으로 노래를 선곡합니다.")
    async def catmakase(self, interaction: discord.Interaction):
        await interaction.response.defer()
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        # 랜덤으로 곡 선택
        selected_song = random.choice(self.catmakase_playlist)

        if voice_client and voice_client.is_playing():
            self.song_queue.append(selected_song)
            await self.music_player.send_message(interaction, "캣부가 대기열에 곡을 추가했습니다 🎵")
        else:
            def after_callback(e):
                asyncio.run_coroutine_threadsafe(
                    self.music_player.check_queue(interaction), 
                    self.bot.loop
                )
            
            try:
                title = await self.music_player.play_song(interaction, selected_song, after_callback)
                await self.music_player.send_message(interaction, f"캣부의 선곡: {title} 🎶")
            except Exception as e:
                await self.music_player.send_message(interaction, f"캣부가 목이 아프답니다: {str(e)}") 