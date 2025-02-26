import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from play import Play  # Play 클래스 가져오기
from skip import Skip  # Skip 클래스 가져오기
from pause import Pause  # 추가

os.system("ffmpeg -version")

# .env 파일에서 토큰 로드
load_dotenv()
bot_token = os.getenv("DISCORD_BOT_TOKEN")

# 봇 초기 설정
intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True  # 메시지 내용 권한
intents.guilds = True          # 서버 권한
bot = commands.Bot(command_prefix="/", intents=intents)

# 공유 데이터
song_queues = {}  # 서버별 대기열 관리를 위한 딕셔너리

async def main():
    await bot.add_cog(Play(bot, song_queues))  # song_queues 전달
    await bot.add_cog(Skip(bot, song_queues))
    await bot.add_cog(Pause(bot, song_queues))  # 추가
    await bot.start(bot_token)

@bot.event
async def on_ready():
    print(f"{bot.user}로 로그인되었습니다.")
    try:
        synced = await bot.tree.sync()
        print(f"Slash 명령어 {len(synced)}개 동기화 완료")
    except Exception as e:
        print(f"명령어 동기화 중 오류 발생: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    # 봇 자신의 상태 변경은 무시
    if member == bot.user:
        return
        
    # 봇이 음성 채널에서 나가거나 연결이 끊어졌을 때 처리
    if before.channel is not None:
        voice_client = discord.utils.get(bot.voice_clients, channel=before.channel)
        if voice_client:
            guild_id = before.channel.guild.id
            if guild_id not in song_queues:
                song_queues[guild_id] = []
                
            # 봇이 혼자 남았거나 채널에 아무도 없을 때만 연결 해제 및 대기열 초기화
            if len(before.channel.members) <= 1:
                try:
                    if voice_client.is_playing():
                        voice_client.stop()
                    await voice_client.disconnect()
                except:
                    pass
                song_queues[guild_id] = []
            # 봇의 연결이 끊어졌지만 사용자가 있는 경우 재연결 시도 (대기열 유지)
            elif not voice_client.is_connected():
                try:
                    # 기존 연결 정리
                    if voice_client.is_playing():
                        voice_client.stop()
                    await voice_client.disconnect()
                    # 새로운 연결 시도 (타임아웃 증가)
                    await asyncio.sleep(1)  # 잠시 대기 후 재연결 시도
                    await before.channel.connect(timeout=30.0)
                except Exception as e:
                    print(f"재연결 실패: {e}")
    
    # 봇이 새로운 채널로 이동했을 때 처리
    if after and after.channel:
        voice_client = discord.utils.get(bot.voice_clients, guild=after.channel.guild)
        if voice_client and not voice_client.is_connected():
            try:
                # 기존 연결 정리
                await voice_client.disconnect()
                # 새로운 연결 시도
                await after.channel.connect(timeout=20.0)
            except Exception as e:
                print(f"채널 이동 중 연결 실패: {e}")
                # 해당 서버의 대기열만 초기화
                guild_id = after.channel.guild.id
                if guild_id in song_queues:
                    song_queues[guild_id] = []

asyncio.run(main())
