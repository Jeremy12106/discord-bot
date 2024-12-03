
FROM python:3.11-slim

# 安裝 FFmpeg
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg

# 設定工作目錄
WORKDIR /app

# 複製程式碼到容器內
COPY . /app

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 執行主程式
CMD ["python", "discord_bot.py"]