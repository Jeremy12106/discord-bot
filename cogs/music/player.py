import os
import asyncio
import json
import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio
from typing import Optional, Dict, Any, TYPE_CHECKING
from loguru import logger

from .queue import get_guild_queue_and_folder, guild_queues
from .youtube import YouTubeManager
from .ui.controls import MusicControlView
from utils.models import VideoInfo
from discord_bot import config

if TYPE_CHECKING:
    from .radio import Radio

class YTMusic(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.current_song = None
        self.current_message = None
        self.music_setting = config.music
        self.is_playing = False
        
        self.youtube = YouTubeManager(time_limit=self.music_setting.time_limit)
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    @app_commands.command(name="play", description="播放音樂")
    @app_commands.describe(song="輸入網址或關鍵字", stream="啟動即時串流 (預設為否)")
    async def play(self, interaction: discord.Interaction, song: str="", stream: Optional[bool]=False):
        # 檢查使用者是否已在語音頻道
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            
            # 如果在播放收音機，先停止
            voice_client: discord.VoiceClient = interaction.guild.voice_client
            if voice_client and voice_client.is_playing():
                # 檢查是否有Radio cog在播放
                radio_cog: Radio = self.bot.get_cog('Radio')
                if radio_cog and radio_cog.current_song:
                    voice_client.stop()
                    radio_cog.current_song = None
                    if radio_cog.current_message:
                        await radio_cog.current_message.delete()
                        radio_cog.current_message = None
                    
            # 連接語音頻道
            try:
                if interaction.guild.voice_client is None:
                    await channel.connect()
                    logger.info(f"[音樂] 伺服器 ID： {interaction.guild.id}, 成功連接語音頻道")
            except Exception as e:
                logger.error(f"[音樂] 伺服器 ID： {interaction.guild.id}, 連接語音頻道失敗：{e}")
        
        else:
            embed = discord.Embed(title="❌ | 請先加入語音頻道！", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # 檢查是否為 URL 或使用關鍵字播放
        if "youtube.com" in song or "youtu.be" in song:
            await interaction.response.defer()
            is_valid = await self.add_to_queue(interaction, song, is_deferred=True, stream=stream)
            if not is_valid:
                return
        else:
            embed = discord.Embed(title="❌ | 請輸入有效的Youtube影片連結！", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # 播放音樂
        voice_client = interaction.guild.voice_client
        if not voice_client.is_playing() and not self.is_playing:
            await self.play_next(interaction)

    @play.autocomplete("song")
    async def song_autocomplete(self, interaction: discord.Interaction, current: str):
        # 搜尋前十項
        max_results = self.music_setting.search_count
        results = await self.youtube.search_videos(current, max_results=max_results)
        if results:
            try:
                return [
                    app_commands.Choice(
                        name = f"{str(result['title'])[:50]} ⌂ {str(result['channel'])[:30]} - {str(result['duration'])[:10]}",
                        value=f"https://www.youtube.com{result['url_suffix']}"
                    )
                    for result in results[:max_results]
                ]
            except Exception as e:
                logger.error(f"[音樂] 伺服器 ID： {interaction.guild.id}, Autocomplete 發生錯誤: {e}")
        return []

    async def add_to_queue(self, interaction: discord.Interaction, url, is_deferred=False, stream=False):
        guild_id = interaction.guild.id
        queue, folder = get_guild_queue_and_folder(guild_id)
        
        if stream:
            # 獲取影片資訊
            video_info, error = await self.youtube.extract_audio(url, interaction)
        else:
            # 下載並獲取影片資訊
            video_info, error = await self.youtube.download_audio(url, folder, interaction)
        
        if error:
            embed = discord.Embed(title=f"❌ | {error}", color=discord.Color.red())
            if is_deferred:
                await interaction.followup.send(embed=embed)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return False

        # 將檔案資訊加入佇列
        await queue.put(video_info)

        logger.info(f"[音樂] 伺服器 ID： {interaction.guild.id}, 使用者名稱： {interaction.user.name}, 成功將 {video_info.title} 添加到播放清單")
        embed = discord.Embed(title=f"✅ | 已添加到播放清單： {video_info.title}", color=discord.Color.blue())
        if is_deferred:
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)
        return True

    async def play_next(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        queue, _ = get_guild_queue_and_folder(guild_id)

        voice_client: discord.VoiceClient = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            return

        if self.is_playing:
            return
        self.is_playing = True
        
        # 取消現有的計時器(如果存在)
        if hasattr(self, 'disconnect_task'):
            self.disconnect_task.cancel()
            delattr(self, 'disconnect_task')

        if queue and not queue.empty():
            song: VideoInfo = await queue.get()
            file_path = song.file_path
            try:
                # 保存當前播放的歌曲信息
                self.current_song = song
                
                # 開始播放
                FFMPEG_OPTIONS = {'before_options': self.music_setting.before_options,
                                   'options': self.music_setting.options}
                voice_client.play(
                    FFmpegPCMAudio(file_path, **FFMPEG_OPTIONS),
                    after=lambda e: self.bot.loop.create_task(self.handle_after_play(interaction, file_path))
                )
                
                # 創建或更新 embed
                embed = discord.Embed(
                    title="🎵 | 正在播放音樂",
                    description=f"**[{song.title}]({song.url})**",
                    color=discord.Color.blue()
                )
                if song.duration:
                    minutes, seconds = divmod(song.duration, 60)
                    duration = f"{minutes:02d}:{seconds:02d}"
                else:
                    duration = "直播"
                
                if song.views:
                    views = f"{int(song.views):,}"
                else:
                    views = "直播"
                embed.add_field(name="上傳頻道", value=f"> {song.author}", inline=True)
                embed.add_field(name="播放時長", value=f"> {duration}", inline=True)
                embed.add_field(name="觀看次數", value=f"> {views}", inline=True)
                if self.music_setting.display_progress_bar and song.duration:
                    embed.add_field(name="播放進度", value=f"> 00:00 ▱▱▱▱▱▱▱▱▱▱ {minutes:02d}:{seconds:02d}", inline=False)
                embed.add_field(name="播放清單", value="> 清單為空", inline=False)
                
                thumbnail = self.youtube.get_thumbnail_url(song.video_id)
                embed.set_thumbnail(url=thumbnail)
                embed.set_footer(text=song.requester, icon_url=song.user_avatar)
                
                # 創建新的控制視圖並添加進度條選擇器
                view = MusicControlView(interaction, self)
                # view.add_progress_select()
                
                # 發送新訊息
                message = await interaction.channel.send(embed=embed, view=view)
                self.current_message = message
                
                # 設置視圖的訊息和 embed
                view.message = message
                view.current_embed = embed
                view.current_position = 0
                
                # 開始更新進度
                if self.music_setting.display_progress_bar and song.duration:
                    if view.update_task:
                        view.update_task.cancel()
                    view.update_task = self.bot.loop.create_task(view.update_progress(song.duration))
                
            except Exception as e:
                logger.error(f"[音樂] 伺服器 ID： {interaction.guild.id}, 播放音樂時出錯： {e}")
                embed = discord.Embed(title=f"❌ | 播放音樂時出錯", color=discord.Color.red())
                await interaction.channel.send(embed=embed)
                await self.play_next(interaction)  # 嘗試播放下一首
        else:
            embed = discord.Embed(title="🌟 | 播放清單已播放完畢！", color=discord.Color.blue())
            await interaction.channel.send(embed=embed)
            self.current_message = None

            # 設置 5 分鐘計時器
            async def disconnect_after_timeout():
                await asyncio.sleep(300)  # 5 minutes
                if voice_client and voice_client.is_connected():
                    await voice_client.disconnect()
                    embed = discord.Embed(title=f"⏰ | 沒有人點音樂，我先去睡了！", color=discord.Color.orange())
                    await interaction.channel.send(embed=embed)
                    logger.info(f"[音樂] 伺服器 ID： {interaction.guild.id}, 閒置超時，已自動離開語音頻道")
            
            self.disconnect_task = asyncio.create_task(disconnect_after_timeout())

    async def handle_after_play(self, interaction: discord.Interaction, file_path):
        self.is_playing = False
        try:
            if os.path.exists(file_path):
                await asyncio.sleep(1)
                os.remove(file_path)
                logger.debug(f"[音樂] 伺服器 ID： {interaction.guild.id}, 刪除檔案成功！")
        except Exception as e:
            logger.warning(f"[音樂] 伺服器 ID： {interaction.guild.id}, 刪除檔案失敗： {e}")
                
        if not self.is_playing:
            await self.play_next(interaction)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
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
