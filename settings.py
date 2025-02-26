# settings.py
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch',
    'quiet': True
}

ffmpeg_opts = {
    'executable': 'ffmpeg',
    'options': '-vn -b:a 192k'
}
