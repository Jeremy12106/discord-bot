import os
import json
import requests
import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from cogs.llm import LLMService

weather_api_key = os.getenv('WEATHER_API_KEY', None)

class WeatherView(discord.ui.View):
    def __init__(self, bot: commands.Bot, data, location, interaction: discord.Interaction, llm: LLMService):
        super().__init__(timeout=60)
        self.bot = bot
        self.data = data
        self.location = location
        self.current_index = 0
        self.interaction = interaction
        self.llm = llm

    def format_weather_message(self, index):
        weather_elements = self.data["records"]["location"][0]["weatherElement"]
        time_data = weather_elements[0]["time"][index]
        start_time = time_data["startTime"]
        end_time = time_data["endTime"]
        weather_state = time_data["parameter"]["parameterName"]
        rain_prob = weather_elements[1]["time"][index]["parameter"]["parameterName"]
        min_tem = weather_elements[2]["time"][index]["parameter"]["parameterName"]
        comfort = weather_elements[3]["time"][index]["parameter"]["parameterName"]
        max_tem = weather_elements[4]["time"][index]["parameter"]["parameterName"]

        weather_message = (
            f"🌍 | **地點**：{self.location}\n"
            f"⏰ | **時間**：{start_time} ~ {end_time}\n"
            f"🌤 | **天氣狀態**：{weather_state}\n"
            f"🌧 | **降雨機率**：{rain_prob}%\n"
            f"🌡 | **氣溫**：{min_tem}°C ~ {max_tem}°C\n"
            f"😌 | **舒適度**：{comfort}\n"
        )
        recommend = self.llm.get_weather_recommendation(weather_message)
        weather_message += f"💡 **出門建議**：{recommend}"
        return weather_message

    async def update_message(self):
        weather_message = self.format_weather_message(self.current_index)
        embed = discord.Embed(title="今日天氣預報", description=weather_message, color=discord.Color.blue())
        await self.interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label="⬅ 上一個時段", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index == 0:
            await interaction.response.send_message("無上一個時段的資訊", ephemeral=True)
        elif self.current_index > 0:
            self.current_index -= 1
            await self.update_message()
            await interaction.response.defer()

    @discord.ui.button(label="下一個時段 ➡", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index == 2:
            await interaction.response.send_message("無下一個時段的資訊", ephemeral=True)
        if self.current_index < 2:  # 最多切換到 ["time"][2]
            self.current_index += 1
            await self.update_message()
            await interaction.response.defer()

class Weather(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.llm = bot.get_cog('LLMService')
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    @app_commands.command(name="weather", description="查詢指定地區的天氣預報")
    @app_commands.choices(region=[
    app_commands.Choice(name=city, value=city) 
    for city in [
        "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
        "基隆市", "新竹市", "新竹縣", "苗栗縣", "彰化縣", "南投縣",
        "雲林縣", "嘉義市", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣",
        "臺東縣", "澎湖縣", "金門縣", "連江縣"
    ]
    ])
    async def get_weather(self, interaction: discord.Interaction, region: app_commands.Choice[str]):
        await interaction.response.defer()
        # API 設定
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
        params = {
            "Authorization": weather_api_key,
            "locationName": region.value,
        }

        # 呼叫 API 並處理回應
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = json.loads(response.text)
            try:
                location = data["records"]["location"][0]["locationName"]  # 地點
                view = WeatherView(self.bot, data, location, interaction, self.llm)
                await view.update_message()
            except (KeyError, IndexError):
                error_message = "⚠ 無法取得指定城市的天氣資訊，請確認名稱是否正確。"
                logger.error(f"[Weather] 伺服器 ID: {interaction.guild_id}, 使用者名稱: {interaction.user.name}, bot 輸出: {error_message}")
                await interaction.followup.send(error_message)
        else:
            error_message = "⚠ 天氣服務目前不可用，請稍後再試！"
            logger.error(f"[Weather] 伺服器 ID: {interaction.guild_id}, 使用者名稱: {interaction.user.name}, bot 輸出: {error_message}")
            await interaction.followup.send(error_message)

async def setup(bot: commands.Bot):
    if not weather_api_key:
        logger.info("Weather API key 未設定，不啟用 `/weather` 功能")
        return
    await bot.add_cog(Weather(bot))
