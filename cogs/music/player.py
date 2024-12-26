import os
import asyncio
import discord
import json
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord import app_commands
from loguru import logger

from .queue import get_guild_queue_and_folder, guild_queues
from .youtube import YouTubeManager
from .ui.controls import MusicControlView
from .ui.song_select import SongSelectView

PROJECT_ROOT = os.getcwd()
SETTING_PATH=f"{PROJECT_ROOT}/config"

class YTMusic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_song = None
        self.current_message = None
        self.music_setting = None
        self.youtube = YouTubeManager()

        music_config_path = os.path.join(SETTING_PATH, "music_config.json")
        with open(music_config_path, "r", encoding="utf-8") as file:
            self.music_setting = json.load(file)

    @app_commands.command(name="play", description="播放音樂")
    @app_commands.describe(song = "輸入網址或關鍵字")
    async def play(self, interaction: discord.Interaction, song: str = ""):
        # 檢查使用者是否已在語音頻道
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            if interaction.guild.voice_client is None:
                await channel.connect()
        else:
            embed = discord.Embed(title="❌ | 請先加入語音頻道！", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return

        # 如果有提供查詢，將音樂加入播放清單
        if song:
            logger.info(f"[音樂] 伺服器 ID： {interaction.guild.id}, 使用者名稱： {interaction.user.name}, 使用者輸入： {song}")
            
            await interaction.response.defer()
            
            # 檢查是否為URL
            if "youtube.com" in song or "youtu.be" in song:
                is_valid = await self.add_to_queue(interaction, song, is_deferred=True)
            else:
                # 使用關鍵字搜尋
                results = await self.youtube.search_videos(song)
                if not results:
                    embed = discord.Embed(title="❌ | 未找到相關影片", color=discord.Color.red())
                    await interaction.followup.send(embed=embed)
                    return
                
                # 創建選擇菜單
                view = SongSelectView(self, results, interaction)
                
                # 創建包含搜尋結果的embed
                embed = discord.Embed(title="🔍 | YouTube搜尋結果", description="請選擇要播放的歌曲：", color=discord.Color.blue())
                for i, result in enumerate(results, 1):
                    duration = result.get('duration', 'N/A')
                    embed.add_field(
                        name=f"{i}. {result['title']}", 
                        value=f"頻道: {result['channel']}\n時長: {duration}", 
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed, view=view)
                return
                
            if is_valid == False:
                return
        
        # 播放音樂
        voice_client = interaction.guild.voice_client
        if not voice_client.is_playing():
            await self.play_next(interaction)

    async def add_to_queue(self, interaction, url, is_deferred=False):
        guild_id = interaction.guild.id
        queue, folder = get_guild_queue_and_folder(guild_id)

        # 下載並獲取影片資訊
        video_info, error = await self.youtube.download_audio(url, folder, interaction)
        
        if error:
            embed = discord.Embed(title=f"❌ | {error}", color=discord.Color.red())
            if is_deferred:
                await interaction.followup.send(embed=embed)
            else:
                await interaction.response.send_message(embed=embed)
            return False

        # 將檔案資訊加入佇列
        await queue.put(video_info)

        logger.debug(f"[音樂] 伺服器 ID： {interaction.guild.id}, 使用者名稱： {interaction.user.name}, 成功將 {video_info['title']} 添加到播放清單")
        embed = discord.Embed(title=f"✅ | 已添加到播放清單： {video_info['title']}", color=discord.Color.blue())
        if is_deferred:
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)
        return True

    async def play_next(self, interaction):
        guild_id = interaction.guild.id
        queue, _ = get_guild_queue_and_folder(guild_id)

        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            return
            
        if not queue.empty():
            item = await queue.get()
            file_path = item["file_path"]
            try:
                # 保存當前播放的歌曲信息
                self.current_song = item
                
                # 開始播放
                voice_client.play(
                    FFmpegPCMAudio(file_path, pipe=False),
                    after=lambda e: self.bot.loop.create_task(self.handle_after_play(interaction, file_path))
                )
                
                # 創建或更新 embed
                embed = discord.Embed(
                    title="🎵 | 正在播放音樂",
                    description=f"**[{item['title']}]({item['url']})**",
                    color=discord.Color.blue()
                )
                
                minutes, seconds = divmod(item['duration'], 60)
                embed.add_field(name="上傳頻道", value=f"> {item['author']}", inline=True)
                embed.add_field(name="播放時長", value=f"> {minutes:02d}:{seconds:02d}", inline=True)
                embed.add_field(name="觀看次數", value=f"> {int(item['views']):,}", inline=True)
                if self.music_setting['display_progress_bar']:
                    embed.add_field(name="播放進度", value=f"> 00:00 ▱▱▱▱▱▱▱▱▱▱ {minutes:02d}:{seconds:02d}", inline=False)
                embed.add_field(name="播放清單", value="> 清單為空", inline=False)
                
                thumbnail = self.youtube.get_thumbnail_url(item['video_id'])
                embed.set_thumbnail(url=thumbnail)
                embed.set_footer(text=item['requester'], icon_url=item['user_avatar'])
                
                # 創建新的控制視圖並添加進度條選擇器
                view = MusicControlView(interaction, self)
                # view.add_progress_select()
                
                # 發送新訊息
                message = await interaction.followup.send(embed=embed, view=view)
                self.current_message = message
                
                # 設置視圖的訊息和 embed
                view.message = message
                view.current_embed = embed
                view.current_position = 0
                
                # 開始更新進度
                if self.music_setting['display_progress_bar']:
                    if view.update_task:
                        view.update_task.cancel()
                    view.update_task = self.bot.loop.create_task(view.update_progress(item['duration']))
                
            except Exception as e:
                logger.error(f"[音樂] 伺服器 ID： {interaction.guild.id}, 播放音樂時出錯： {e}")
                embed = discord.Embed(title=f"❌ | 播放音樂時出錯", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                await self.play_next(interaction)  # 嘗試播放下一首
        else:
            embed = discord.Embed(title="🌟 | 播放清單已播放完畢！", color=discord.Color.blue())
            await interaction.followup.send(embed=embed)
            self.current_message = None

    async def handle_after_play(self, interaction, file_path):
        try:
            if os.path.exists(file_path):
                await asyncio.sleep(1)
                os.remove(file_path)
                logger.debug(f"[音樂] 伺服器 ID： {interaction.guild.id}, 刪除檔案成功！")
        except Exception as e:
            logger.warning(f"[音樂] 伺服器 ID： {interaction.guild.id}, 刪除檔案失敗： {e}")
        await self.play_next(interaction)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # 偵測機器人離開語音頻道時，清理伺服器相關資料
        if member.bot and before.channel is not None and after.channel is None:
            guild_id = member.guild.id
            _, folder = get_guild_queue_and_folder(guild_id)
            logger.info(f"[音樂] 伺服器 ID： {member.guild.id}, 離開語音頻道")
            await asyncio.sleep(2)
            # 刪除所有音檔
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                try:
                    os.remove(file_path)
                    logger.debug(f"[音樂] 伺服器 ID： {member.guild.id}, 刪除檔案成功！")
                except Exception as e:
                    logger.warning(f"[音樂] 伺服器 ID： {member.guild.id}, 刪除檔案失敗： {e}")
            
            # 清空播放隊列
            if guild_id in guild_queues:
                guild_queues[guild_id] = asyncio.Queue()
            
            # 清除當前訊息引用
            self.current_message = None