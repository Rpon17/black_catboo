import discord
from yt_dlp import YoutubeDL
from settings import ydl_opts, ffmpeg_opts
import asyncio

class MusicPlayer:
    def __init__(self, bot, song_queues):
        self.bot = bot
        self.song_queues = song_queues
        self.current_songs = {}
        self.last_messages = {}

    def extract_video_id(self, url):
        if not url:
            return None
        if "watch?v=" in url:
            return url.split("watch?v=")[1].split("&")[0]
        return None

    async def delete_last_messages(self, interaction):
        """이전 메시지들을 삭제합니다."""
        guild_id = interaction.guild_id
        if guild_id in self.last_messages:
            for message in self.last_messages[guild_id]:
                try:
                    await message.delete()
                except:
                    pass  # 이미 삭제된 메시지는 무시
            self.last_messages[guild_id] = []

    async def send_message(self, interaction, content):
        """메시지를 보내고 저장합니다."""
        guild_id = interaction.guild_id
        message = await interaction.followup.send(content)
        
        if guild_id not in self.last_messages:
            self.last_messages[guild_id] = []
        self.last_messages[guild_id].append(message)

    async def play_song(self, interaction, song_url, after_callback=None):
        try:
            # 이전 메시지들 삭제
            await self.delete_last_messages(interaction)
            
            guild_id = interaction.guild_id
            
            # 음성 채널 연결 확인 및 재연결
            voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
            if not voice_client or not voice_client.is_connected():
                if not interaction.user.voice:
                    raise Exception("음성 채널에 먼저 입장해주세요!")
                voice_channel = interaction.user.voice.channel
                voice_client = await voice_channel.connect()

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song_url, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                
                webpage_url = info.get('webpage_url', None)
                self.current_songs[guild_id] = webpage_url

                audio_url = None
                for fmt in info.get('formats', []):
                    if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                        audio_url = fmt['url']
                        break

                if not audio_url:
                    raise ValueError("유효한 오디오 URL을 찾을 수 없습니다")

                # 이전 재생이 있다면 중지
                if voice_client.is_playing():
                    voice_client.stop()

                # 노래 재생
                def after_fn(error):
                    if error:
                        print(f'재생 오류: {error}')
                    # 노래가 끝나면 다음 곡 재생
                    async def next_song():
                        try:
                            # 새로운 interaction 생성 또는 기존 interaction 재사용
                            if voice_client and voice_client.is_connected():
                                await self.check_queue(interaction)
                        except Exception as e:
                            print(f"다음 곡 재생 실패: {e}")

                    asyncio.run_coroutine_threadsafe(
                        next_song(),
                        self.bot.loop
                    )

                voice_client.play(
                    discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts),
                    after=after_fn  # 콜백 함수 설정
                )
                
                return info.get('title', '알 수 없는 제목')

        except Exception as e:
            if 'Video unavailable' in str(e):
                raise Exception("해당 동영상을 재생할 수 없습니다. (영상이 비공개이거나 삭제되었을 수 있습니다)")
            elif 'Sign in to confirm your age' in str(e):
                raise Exception("연령 제한이 있는 동영상입니다")
            else:
                raise Exception(f"재생 중 오류가 발생했습니다: {str(e)}")

    async def check_queue(self, interaction):
        guild_id = interaction.guild_id
        if guild_id not in self.song_queues:
            self.song_queues[guild_id] = []

        # 음성 채널 연결 확인 및 재연결
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if not voice_client or not voice_client.is_connected():
            try:
                if voice_client:
                    await voice_client.disconnect()
                if not interaction.user.voice:
                    print("음성 채널 연결 실패: 사용자가 음성 채널에 없음")
                    return
                voice_client = await interaction.user.voice.channel.connect()
            except Exception as e:
                print(f"음성 채널 연결 실패: {str(e)}")
                return

        try:
            if self.song_queues[guild_id]:  # 대기열에 곡이 있으면
                next_song = self.song_queues[guild_id].pop(0)
                title = await self.play_song(interaction, next_song)
                if title:
                    try:
                        await self.send_message(interaction, f"다음 곡 재생 중: {title} 🎶")
                    except:
                        print(f"재생 중인 곡: {title}")
            else:
                # 대기열이 비었을 때는 아무 것도 하지 않음
                pass
        except Exception as e:
            print(f"대기열 처리 중 오류: {str(e)}") 