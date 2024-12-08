# Discord Bot

一個功能強大、簡單易用的 Discord 機器人，提供多種功能來增強你的伺服器體驗！


## 🚀 功能

- 🎵 音樂播放：支援 YouTube MP3 下載，無縫播放音樂。
- 📷 圖片分享：從 pic 資料夾中獲取圖片並與伺服器成員分享。
- 🌌 API 整合：與 Gemini API 整合，帶來豐富的功能。
- 🛠️ 模組化設計：使用 cogs 分離功能，易於維護和擴展。
- 🐳 Docker 支援：簡單的部署流程，內建 FFmpeg 支援。


## 🛠️ 安裝與執行

### 使用 Docker

1. 確保已安裝 [Docker](https://www.docker.com)。
2. 複製專案：
    ```
    git clone https://github.com/yourusername/your-discord-bot.git
    cd your-discord-bot
    ```
3. 建立並啟動容器：
    ```
    docker build -t discord-bot .
    docker run -d --name discord-bot discord-bot
    ```

### 手動執行

1. 安裝 Python 依賴：
    ```
    pip install -r requirements.txt
    ```
2. 啟動機器人：
    ```
    python main.py
    ```


## 🔧 設定

1. 在 assets/settings.json 中設定你的 bot token 和其他必要參數：
    ```
    {
    "token": "你的機器人TOKEN",
    "prefix": "!"
    }
    ```
2. 確保 assets/themes.json 和 pic 資料夾已正確配置。


## 🖼️ 範例截圖

### 音樂播放

> 使用 !play 指令開始播放音樂！

### 圖片分享

> 使用 !pic 指令分享隨機圖片。


## 🤝 貢獻

歡迎提交問題與貢獻代碼！

1. Fork 本專案。
2. 創建分支 (`git checkout -b feature/你的功能名稱`)。
3. 提交更改 (`git commit -m '新增功能'`)。
4. Push 到分支 (`git push origin feature/你的功能名稱`)。
5. 提交 Pull Request。


## 📄 授權

此專案使用 [MIT License](https://opensource.org/license/mit)。歡迎自由使用和修改！