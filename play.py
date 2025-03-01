import discord
from discord.ext import commands
from discord import app_commands
from yt_dlp import YoutubeDL
import asyncio
import traceback
from settings import ydl_opts, ffmpeg_opts  # 설정 파일에서 가져옴
from music_utils import MusicPlayer

class Play(commands.Cog):
    def __init__(self, bot, song_queues):
        self.bot = bot
        self.song_queues = song_queues
        self.music_player = MusicPlayer(bot, song_queues)
        print("[✅ Play Cog 로드 완료]")  # Cog가 정상적으로 로드되었는지 확인

    @app_commands.command(name="재생", description="캣부가 노래합니다.")
    async def play(self, interaction: discord.Interaction, 제목: str):
        """Slash 명령어로 노래를 재생하거나 대기열에 추가합니다."""
        print(f"[🎵 명령 실행] /재생 {제목} (서버: {interaction.guild.name})")
        await interaction.response.defer()

        if not interaction.user.voice:
            await self.music_player.send_message(interaction, "음성 채널에 먼저 입장해주세요!")
            return

        guild_id = interaction.guild_id
        if guild_id not in self.song_queues:
            self.song_queues[guild_id] = []

        song_url = f"ytsearch:{제목}"
        print(f"[🔍 검색] {song_url}")

        try:
            voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
            if not voice_client or not voice_client.is_connected():
                try:
                    if voice_client:
                        print("[🔄 기존 음성 연결 해제]")
                        await voice_client.disconnect()
                    print("[🔗 음성 채널 연결 중...]")
                    voice_client = await interaction.user.voice.channel.connect()
                    print("[✅ 음성 채널 연결 성공]")
                except Exception as e:
                    error_msg = f"음성 채널 연결 실패: {repr(e)}\n{traceback.format_exc()}"
                    print(f"[❌ 오류 발생] {error_msg}")
                    await self.music_player.send_message(interaction, error_msg)
                    return

            if voice_client.is_playing():
                self.song_queues[guild_id].append(song_url)
                await self.music_player.send_message(interaction, f"대기열에 추가됨: {제목}")
            else:
                try:
                    title = await self.music_player.play_song(interaction, song_url)
                    await self.music_player.send_message(interaction, f"캣부의 현재곡: {title} 🎶")
                except Exception as e:
                    error_msg = f"캣부가 목이 아프답니다: {repr(e)}\n{traceback.format_exc()}"
                    print(f"[❌ 오류 발생] {error_msg}")
                    await self.music_player.send_message(interaction, error_msg)
        except Exception as e:
            error_msg = f"오류가 발생했습니다: {repr(e)}\n{traceback.format_exc()}"
            print(f"[❌ 오류 발생] {error_msg}")
            await self.music_player.send_message(interaction, error_msg)

    async def check_queue(self, interaction):
        """대기열 확인 및 추천 곡 재생."""
        print("[🔄 대기열 확인]")
        await self.music_player.check_queue(interaction)

    async def play_recommended_song(self, interaction, song_url):
        """유튜브 추천 곡을 재생합니다."""
        print(f"[🎵 추천 곡 재생 요청] {song_url}")
        try:
            voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
            if not voice_client or not voice_client.is_connected():
                if not interaction.user.voice:
                    raise Exception("음성 채널에 먼저 입장해주세요!")
                print("[🔗 음성 채널 연결 중...]")
                voice_client = await interaction.user.voice.channel.connect()

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song_url, download=False)
                print(f"🎵 유튜브 다운로드 정보: {info}")

                if 'entries' in info and len(info['entries']) > 0:
                    info = info['entries'][0]
                    audio_url = next((fmt['url'] for fmt in info.get('formats', []) if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none'), None)
                    if not audio_url:
                        raise ValueError("추천 곡의 유효한 오디오 URL을 찾을 수 없습니다.")

                    print(f"🔗 재생할 오디오 URL: {audio_url}")

                    def after_playback(error):
                        if error:
                            print(f"[❌ 재생 중 오류] {repr(error)}\n{traceback.format_exc()}")
                        print("[🎵 노래가 끝났습니다] 다음 곡 확인 중...")

                    voice_client.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts), after=after_playback)
                    await interaction.followup.send(f"추천 곡 재생 중: {info.get('title', '알 수 없는 제목')} 🎶")
                else:
                    await interaction.followup.send("추천 곡 목록이 비어 있습니다. 다른 곡을 추가해주세요.")

        except Exception as e:
            error_msg = f"추천 곡을 재생할 수 없습니다: {repr(e)}\n{traceback.format_exc()}"
            print(f"[❌ 오류 발생] {error_msg}")
            await interaction.followup.send(error_msg)
