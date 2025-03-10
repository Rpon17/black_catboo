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
    'source_address': '0.0.0.0',

    # 🔹 YouTube 인증을 위한 쿠키 추가
    'cookies': 'cookies.txt',

    # 🔹 ffmpeg 자동 병합 활성화
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

ffmpeg_opts = {
    'executable': 'ffmpeg',
    'options': '-vn -b:a 192k'
}
