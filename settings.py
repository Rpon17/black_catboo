# settings.py
ydl_opts = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'noplaylist': True,
    'geo_bypass': True,  # 🔹 YouTube Music 지역 제한 우회
    'nocheckcertificate': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0'
}


ffmpeg_opts = {
    'executable': 'ffmpeg',
    'options': '-vn -b:a 192k'
}
