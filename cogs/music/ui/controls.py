import os
import json
import discord
import asyncio
from loguru import logger

from ..queue import guild_queues

PROJECT_ROOT = os.getcwd()
SETTING_PATH=f"{PROJECT_ROOT}/config"

class MusicControlView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, cog):
        super().__init__(timeout=None)
        self.guild = interaction.guild
        self.cog = cog
        self.current_position = 0
        self.message = None
        self.update_task = None
        self.current_embed = None

        music_config_path = os.path.join(SETTING_PATH, "music_config.json")
        with open(music_config_path, "r", encoding="utf-8") as file:
            self.music_setting = json.load(file)

    def create_progress_bar(self, current, total, length=20):
        filled = int(length * current / total)
        bar = "▰" * filled + "▱" * (length - filled)
        minutes_current, seconds_current = divmod(current, 60)
        minutes_total, seconds_total = divmod(total, 60)
        return f"> {minutes_current:02d}:{seconds_current:02d} {bar} {minutes_total:02d}:{seconds_total:02d}"

    async def update_progress(self, duration):
        try:
            while True:
                if not self.guild.voice_client or not self.guild.voice_client.is_playing():
                    break
                
                self.current_position += 1
                if self.current_position > duration:
                    break
                    
                if self.current_embed and self.message:
                    progress_bar = self.create_progress_bar(self.current_position, duration)
                    self.current_embed.set_field_at(3, name="播放進度", value=progress_bar, inline=False)
                    await self.message.edit(embed=self.current_embed)
                # 更新頻率 (加上延遲約1秒)
                await asyncio.sleep(0.6)
        except Exception as e:
            logger.error(f"Progress update error: {e}")

    async def update_embed(self, interaction: discord.Interaction, title: str, color: discord.Color = discord.Color.blue()):
        if self.current_embed and self.message:
            self.current_embed.title = title
            self.current_embed.color = color
            await self.message.edit(embed=self.current_embed)

    @discord.ui.button(emoji='<:pause:1315853280852574239>', label=" 暫停", style=discord.ButtonStyle.gray)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = self.guild.voice_client
        if voice_client:
            if voice_client.is_playing():
                voice_client.pause()
                await self.update_embed(interaction, f"⏸️ | {interaction.user.name} 暫停了音樂")
                if self.update_task:
                    self.update_task.cancel()
            elif voice_client.is_paused():
                await interaction.response.send_message("❌ 已暫停音樂！", ephemeral=True)
            await interaction.response.defer()
        else:
            await interaction.response.send_message("❌ 沒有正在播放的音樂！", ephemeral=True)
    
    @discord.ui.button(emoji='<:play:1315853281519468644>', label=" 播放", style=discord.ButtonStyle.gray)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = self.guild.voice_client
        if voice_client:
            if voice_client.is_playing():
                await interaction.response.send_message("❌ 正在播放音樂！", ephemeral=True)
            elif voice_client.is_paused():
                voice_client.resume()
                await self.update_embed(interaction, f"▶️ | {interaction.user.name} 繼續了音樂")
                # 重新啟動進度更新
                if self.music_setting['display_progress_bar']:
                    if hasattr(self.cog, 'current_song'):
                        self.update_task = self.cog.bot.loop.create_task(
                            self.update_progress(self.cog.current_song["duration"])
                        )
            await interaction.response.defer()
        else:
            await interaction.response.send_message("❌ 沒有正在播放的音樂！", ephemeral=True)

    @discord.ui.button(emoji='<:skip:1315853298770776134>', label=" 下一首歌", style=discord.ButtonStyle.gray)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = self.guild.voice_client
        if voice_client:
            voice_client.stop()
            await self.update_embed(interaction, f"⏭️ | {interaction.user.name} 跳過了音樂")
            await interaction.response.defer()
        else:
            await interaction.response.send_message("❌ 沒有正在播放的音樂！", ephemeral=True)

    @discord.ui.button(emoji='<:stop:1321510975123488800>', label=" 停止", style=discord.ButtonStyle.gray)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = self.guild.voice_client
        if voice_client:
            # 清空播放隊列
            queue = guild_queues.get(self.guild.id)
            if queue:
                while not queue.empty():
                    await queue.get()
            # 停止播放
            voice_client.stop()
            await voice_client.disconnect()
            await self.update_embed(interaction, f"⏹️ | {interaction.user.name} 停止了播放", discord.Color.red())
            await interaction.response.defer()
        else:
            await interaction.response.send_message("❌ 沒有正在播放的音樂！", ephemeral=True)

    @discord.ui.button(emoji='<:playlist:1321510957956206613>', label=" 更新播放清單", style=discord.ButtonStyle.gray)
    async def show_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        queue = guild_queues.get(self.guild.id)
        if not queue or queue.empty():
            await interaction.response.send_message("目前沒有歌曲在播放清單中", ephemeral=True)
            return

        # 直接獲取隊列內容的副本而不修改原隊列
        queue_copy = list(queue._queue)

        # 更新播放清單到當前 embed
        if self.current_embed and self.message:
            queue_text = ""
            for i, item in enumerate(queue_copy, 1):
                minutes, seconds = divmod(item["duration"], 60)
                queue_text += f"{i}. {item['title']} | {minutes:02d}:{seconds:02d}\n"
            
            if self.music_setting['display_progress_bar']:
                self.current_embed.set_field_at(4, name="📜 播放清單", value=queue_text if queue_text else "> 清單為空", inline=False)
            else:
                self.current_embed.set_field_at(3, name="📜 播放清單", value=queue_text if queue_text else "> 清單為空", inline=False)

            await self.message.edit(embed=self.current_embed)
            await interaction.response.defer()
        else:
            await interaction.response.send_message("無法更新播放清單", ephemeral=True)

class RadioControlView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, cog):
        super().__init__(timeout=None)
        self.guild = interaction.guild
        self.cog = cog
        self.current_position = 0
        self.message = None
        self.update_task = None
        self.current_embed = None

        music_config_path = os.path.join(SETTING_PATH, "music_config.json")
        with open(music_config_path, "r", encoding="utf-8") as file:
            self.music_setting = json.load(file)

    async def update_embed(self, interaction: discord.Interaction, title: str, color: discord.Color = discord.Color.blue()):
        if self.current_embed and self.message:
            self.current_embed.title = title
            self.current_embed.color = color
            await self.message.edit(embed=self.current_embed)

    @discord.ui.button(emoji='<:pause:1315853280852574239>', label=" 暫停", style=discord.ButtonStyle.gray)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = self.guild.voice_client
        if voice_client:
            if voice_client.is_playing():
                voice_client.pause()
                await self.update_embed(interaction, f"⏸️ | {interaction.user.name} 暫停了音樂")
                if self.update_task:
                    self.update_task.cancel()
            elif voice_client.is_paused():
                await interaction.response.send_message("❌ 已暫停音樂！", ephemeral=True)
            await interaction.response.defer()
        else:
            await interaction.response.send_message("❌ 沒有正在播放的音樂！", ephemeral=True)
    
    @discord.ui.button(emoji='<:play:1315853281519468644>', label=" 播放", style=discord.ButtonStyle.gray)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = self.guild.voice_client
        if voice_client:
            if voice_client.is_playing():
                await interaction.response.send_message("❌ 正在播放音樂！", ephemeral=True)
            elif voice_client.is_paused():
                voice_client.resume()
                await self.update_embed(interaction, f"▶️ | {interaction.user.name} 繼續了音樂")
            await interaction.response.defer()
        else:
            await interaction.response.send_message("❌ 沒有正在播放的音樂！", ephemeral=True)

    @discord.ui.button(emoji='<:stop:1321510975123488800>', label=" 停止", style=discord.ButtonStyle.gray)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = self.guild.voice_client
        if voice_client:
            # 清空播放隊列
            queue = guild_queues.get(self.guild.id)
            if queue:
                while not queue.empty():
                    await queue.get()
            # 停止播放
            voice_client.stop()
            await voice_client.disconnect()
            await self.update_embed(interaction, f"⏹️ | {interaction.user.name} 停止了播放", discord.Color.red())
            await interaction.response.defer()
        else:
            await interaction.response.send_message("❌ 沒有正在播放的音樂！", ephemeral=True)
