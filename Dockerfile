FROM python:3.12

# 🛠️ 필수 패키지 설치
RUN apt update && apt upgrade -y && \
    apt install -y libopus0 ffmpeg && \
    apt clean && rm -rf /var/lib/apt/lists/*

# 📁 작업 디렉토리 설정
WORKDIR /app

# 📂 필요한 파일 복사
COPY . .

# 📦 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 🎵 봇 실행
CMD ["python", "main.py"]
