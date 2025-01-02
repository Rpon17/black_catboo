import discord
from yt_dlp import YoutubeDL
from settings import ydl_opts, ffmpeg_opts
import asyncio

class MusicPlayer:
    def __init__(self, bot, song_queue, current_song):
        self.bot = bot
        self.song_queue = song_queue
        self.current_song = current_song
        self.song_queues = {}
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
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song_url, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                
                webpage_url = info.get('webpage_url', None)
                self.current_song = webpage_url
                self.current_songs[guild_id] = webpage_url

                audio_url = None
                for fmt in info.get('formats', []):
                    if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                        audio_url = fmt['url']
                        break

                if not audio_url:
                    raise ValueError("유효한 오디오 URL을 찾을 수 없습니다")

                voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
                if voice_client is None:
                    voice_channel = interaction.user.voice.channel
                    voice_client = await voice_channel.connect()

                # 이전 재생이 있다면 중지
                if voice_client.is_playing():
                    voice_client.stop()

                # 노래 재생
                voice_client.play(
                    discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts),
                    after=after_callback  # 콜백 함수 설정
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
        
        def after_callback(e):
            asyncio.run_coroutine_threadsafe(
                self.check_queue(interaction), 
                self.bot.loop
            )

        # 이전 메시지들 삭제
        await self.delete_last_messages(interaction)

        if self.song_queue:
            next_song = self.song_queue.pop(0)
            await self.play_song(interaction, next_song, after_callback)
        else:
            current = self.current_song
            if current:
                video_id = self.extract_video_id(current)
                if video_id:
                    try:
                        # YouTube Mix 플레이리스트 URL
                        mix_url = f"https://www.youtube.com/watch?v={video_id}&list=RD{video_id}"
                        with YoutubeDL({'format': 'bestaudio/best', 
                                      'quiet': True,
                                      'noplaylist': False,
                                      'extract_flat': False,
                                      'playlist_items': '1-4'  # 처음 4개 항목만 가져오기
                                     }) as ydl:
                            info = ydl.extract_info(mix_url, download=False)
                            
                            # entries가 있고 길이가 충분한지 확인
                            if 'entries' in info and len(info['entries']) >= 4:
                                # 세 번째 곡 선택 (0번이 현재곡, 3번이 세 번째 추천곡)
                                recommended_song = info['entries'][3]['webpage_url']
                                await self.play_song(interaction, recommended_song, after_callback)
                                return
                                
                            await self.send_message(interaction, "캣부가 다음곡을 준비중입니다 🎵")
                    except Exception as e:
                        print(f"추천 곡 오류: {str(e)}")
                        await self.send_message(interaction, "캣부가 다음곡을 준비중입니다 🎵")
                else:
                    await self.send_message(interaction, "캣부가 다음곡을 준비중입니다 🎵")
            else:
                await self.send_message(interaction, "캣부가 다음곡을 준비중입니다 🎵") 