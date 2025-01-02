import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from play import Play  # Play 클래스 가져오기
from skip import Skip  # Skip 클래스 가져오기
from catmakase import Catmakase  # 추가

# .env 파일에서 토큰 로드
load_dotenv()
bot_token = os.getenv("DISCORD_BOT_TOKEN")

# 봇 초기 설정
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# 공유 데이터
song_queue = []
current_song = None

async def main():
    await bot.add_cog(Play(bot, song_queue, current_song))  # Play Cog 추가
    await bot.add_cog(Skip(bot, song_queue, current_song))  # Skip Cog 추가
    await bot.add_cog(Catmakase(bot, song_queue, current_song))  # 추가
    await bot.start(bot_token)

@bot.event
async def on_ready():
    print(f"{bot.user}로 로그인되었습니다.")
    try:
        synced = await bot.tree.sync()
        print(f"Slash 명령어 {len(synced)}개 동기화 완료")
    except Exception as e:
        print(f"명령어 동기화 중 오류 발생: {e}")

asyncio.run(main())
