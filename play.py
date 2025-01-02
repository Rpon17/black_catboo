import discord
from discord.ext import commands
from discord import app_commands
from yt_dlp import YoutubeDL
import asyncio
from settings import ydl_opts, ffmpeg_opts  # 설정 파일에서 가져옴
from music_utils import MusicPlayer

class Play(commands.Cog):
    def __init__(self, bot, song_queue, current_song):
        self.bot = bot
        self.song_queue = song_queue
        self.current_song = current_song
        self.music_player = MusicPlayer(bot, song_queue, current_song)

    @app_commands.command(name="재생", description="캣부가 노래합니다.")
    async def play(self, interaction: discord.Interaction, 제목: str):
        """Slash 명령어로 노래를 재생하거나 대기열에 추가합니다."""
        await interaction.response.defer()  # 대기 응답
        song_url = f"ytsearch:{제목}"
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if voice_client and voice_client.is_playing():
            self.song_queue.append(song_url)
            await self.music_player.send_message(interaction, f"대기열에 추가됨: {제목}")
        else:
            def after_callback(e):
                asyncio.run_coroutine_threadsafe(
                    self.music_player.check_queue(interaction), 
                    self.bot.loop
                )
            
            try:
                title = await self.music_player.play_song(interaction, song_url, after_callback)
                await self.music_player.send_message(interaction, f"캣부의 현재곡: {title} 🎶")
            except Exception as e:
                await self.music_player.send_message(interaction, f"캣부가 목이 아프답니다: {str(e)}")

    async def check_queue(self, interaction):
        """대기열 확인 및 추천 곡 재생."""
        await self.music_player.check_queue(interaction)

    async def play_recommended_song(self, interaction, song_url):
        """유튜브 추천 곡을 재생합니다."""
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song_url, download=False)

                if 'entries' in info and len(info['entries']) > 0:
                    info = info['entries'][0]

                    audio_url = None
                    for fmt in info.get('formats', []):
                        if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                            audio_url = fmt['url']
                            break

                    if not audio_url:
                        raise ValueError("추천 곡의 유효한 오디오 URL을 찾을 수 없습니다.")

                    voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
                    if voice_client is None:
                        voice_channel = interaction.user.voice.channel
                        voice_client = await voice_channel.connect()

                    self.current_song = info.get('webpage_url', None)

                    voice_client.play(
                        discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts),
                        after=None
                    )
                    await interaction.followup.send(f"추천 곡 재생 중: {info.get('title', '알 수 없는 제목')} 🎶")
                else:
                    await interaction.followup.send("추천 곡 목록이 비어 있습니다. 다른 곡을 추가해주세요.")

        except Exception as e:
            await interaction.followup.send(f"추천 곡을 재생할 수 없습니다: {str(e)}")