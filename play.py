import discord
from discord.ext import commands
from discord import app_commands
from yt_dlp import YoutubeDL
import asyncio
import traceback
import re
from settings import ydl_opts, ffmpeg_opts
from music_utils import MusicPlayer

class Play(commands.Cog):
    def __init__(self, bot, song_queues):
        self.bot = bot
        self.song_queues = song_queues
        self.music_player = MusicPlayer(bot, song_queues)
        print("[✅ Play Cog 로드 완료]")

    @app_commands.command(name="재생", description="캣부가 노래합니다.")
    async def play(self, interaction: discord.Interaction, 입력값: str):
        """Slash 명령어로 노래를 재생하거나 대기열에 추가합니다."""
        print(f"[🎵 명령 실행] /재생 {입력값} (서버: {interaction.guild.name})")
        await interaction.response.defer()
        await self.process_play_request(interaction, 입력값)

    @commands.Cog.listener()
    async def on_message(self, message):
        """유튜브 링크 감지 후 자동 재생"""
        if message.author.bot:
            return
        
        youtube_url_pattern = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be|music\.youtube\.com)/")
        if youtube_url_pattern.match(message.content):
            await message.channel.send(f"🎵 감지된 유튜브 링크! `{message.content}` 를 재생할게요!")

            # 가짜 interaction 생성 (음성 채널 정보 포함)
            class FakeInteraction:
                def __init__(self, user, guild, channel):
                    self.user = user
                    self.guild = guild
                    self.channel = channel
                    self.guild_id = guild.id
                    self.response = self  # response.defer()가 가능하도록 추가
                async def defer(self):
                    pass  # 응답 필요 없음

            fake_interaction = FakeInteraction(message.author, message.guild, message.channel)
            await self.process_play_request(fake_interaction, message.content)

    async def process_play_request(self, interaction, 입력값):
        """공통 재생 처리 함수"""
        if not interaction.user.voice:
            await self.music_player.send_message(interaction, "음성 채널에 먼저 입장해주세요!")
            return

        guild_id = interaction.guild_id
        if guild_id not in self.song_queues:
            self.song_queues[guild_id] = []

        # 🔹 유튜브 & 유튜브 뮤직 URL 확인
        youtube_url_pattern = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be|music\.youtube\.com)/")
        song_url = 입력값 if youtube_url_pattern.match(입력값) else f"ytsearch:{입력값}"

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
                await self.music_player.send_message(interaction, f"대기열에 추가됨: {입력값}")
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

async def setup(bot):
    await bot.add_cog(Play(bot, {}))
