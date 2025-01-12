
FROM python:3.11-slim

# 更新並升級系統
RUN apt-get update && apt-get -y upgrade

# 安裝 FFmpeg
RUN apt-get install -y --no-install-recommends ffmpeg

# 安裝 wget 和 gnupg
RUN apt-get install -y wget gnupg

# 設定 Google Chrome 倉庫並安裝 Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# 設定工作目錄
WORKDIR /app

# 複製程式碼到容器內
COPY . /app

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 執行主程式
CMD ["python", "discord_bot.py"]