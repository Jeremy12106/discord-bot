# Discord Bot

豆白，一個功能強大、簡單易用的 Discord 機器人，提供多種功能來增加你的伺服器體驗！


## 🚀 功能

🎵 音樂播放：支援 YouTube MP3 下載，讓音樂播放更加無縫順暢。  
🤖 語言模型：整合語言模型，讓機器人對話更靈活生動。  
🌤️ 氣象預報：即時提供天氣資訊，給予出門建議。  
🍜 拉麵推薦：精選台北捷運沿線的美味拉麵推薦。  
🖼️ 梗圖搜尋：建立並管理專屬的梗圖庫，隨時分享圖片。  
🎮 特色小遊戲：內建終極密碼與海龜湯等小遊戲，增添互動樂趣。  


## 🛠️ 安裝與執行

### 使用 Docker

1. 確保已安裝 [Docker](https://www.docker.com)。
2. 複製專案：
    ```
    git clone https://github.com/Jeremy12106/discord-bot.git
    cd discord-bot
    ```
3. 建立並啟動容器：
    ```
    docker build -t discord_bot .
    docker compose up
    ```

### 手動執行

1. 安裝 Python 依賴：
    ```
    pip install -r requirements.txt
    ```
2. 啟動機器人：
    ```
    python discord_bot.py
    ```


## 🔧 設定

1. 在根目錄中創建 `.env` 設定你的 bot token 和其他必要參數：
    ```
    // discord bot token
    DISCORD_TOKEN = 

    // google gemini api key
    GOOGLE_API_KEY = 

    // 中央氣象署-資料開放平台 key
    WEATHER_API_KEY = 

    // 日誌紀錄等級
    LOG_LEVEL = INFO
    ```
2. 在 `assets\data\gemini_api_setting` 檔案路經中新增 `personality.json` 來設定機器人個性
    ```
    {
    "personality": "None"
    }   
    ```


## 🖼️ 範例截圖 (施工中)

### 音樂播放

- 使用 `豆白 play` 指令開始播放音樂！  
![yt__music](assets\pic\readme\yt_music.jpg)


## 🤝 貢獻

歡迎提交問題與貢獻代碼！

1. Fork 本專案。
2. 創建分支 (`git checkout -b feature/您的功能名稱`)。
3. 提交更改 (`git commit -m '新增功能'`)。
4. Push 到分支 (`git push origin feature/您的功能名稱`)。
5. 提交 Pull Request。


## 📄 授權

此專案使用 [MIT License](https://opensource.org/license/mit)。歡迎自由使用和修改！