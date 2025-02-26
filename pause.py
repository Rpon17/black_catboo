import discord
from discord.ext import commands
from discord import app_commands
from music_utils import MusicPlayer

class Pause(commands.Cog):
    def __init__(self, bot, song_queues):
        self.bot = bot
        self.song_queues = song_queues
        self.music_player = MusicPlayer(bot, song_queues)

    @app_commands.command(name="정지", description="현재 재생 중인 곡을 일시정지/재개합니다.")
    async def pause(self, interaction: discord.Interaction):
        await interaction.response.defer()
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if voice_client:
            if voice_client.is_playing():
                voice_client.pause()
                await self.music_player.send_message(interaction, "노래를 일시정지했습니다. ⏸️")
            elif voice_client.is_paused():
                voice_client.resume()
                await self.music_player.send_message(interaction, "노래를 다시 재생합니다. ▶️")
            else:
                await self.music_player.send_message(interaction, "현재 재생 중인 곡이 없습니다.")
        else:
            await self.music_player.send_message(interaction, "봇이 음성 채널에 없습니다.")