import os
import asyncio
import discord
from discord import FFmpegPCMAudio
from discord.ui import Button, View
from discord.ext import commands
from pytubefix import YouTube
from pytubefix.cli import on_progress
from loguru import logger

# 定義每個伺服器的播放清單
guild_queues = {}

# 確保伺服器有獨立的資料夾和播放清單
def get_guild_queue_and_folder(guild_id):
    if guild_id not in guild_queues:
        guild_queues[guild_id] = asyncio.Queue()

    # 為每個伺服器設定獨立的下載資料夾
    guild_folder = f"./assets/music_temp/{guild_id}"
    if not os.path.exists(guild_folder):
        os.makedirs(guild_folder)
    return guild_queues[guild_id], guild_folder

class MusicControlView(View):
    def __init__(self, ctx, cog):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.cog = cog

    @discord.ui.button(emoji='<:play:1315853281519468644>', style=discord.ButtonStyle.gray)
    async def resume(self, interaction: discord.Interaction, button: Button):
        voice_client = self.ctx.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message(f"▶️ | {self.ctx.author} 繼續了音樂！")
        else:
            embed = discord.Embed(title="❌ | 沒有正在播放的音樂！", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(emoji='<:pause:1315853280852574239>', style=discord.ButtonStyle.gray)
    async def pause(self, interaction: discord.Interaction, button: Button):
        voice_client = self.ctx.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message(f"⏸️ | {self.ctx.author} 暫停了音樂！")
        else:
            embed = discord.Embed(title="❌ | 沒有正在播放的音樂！", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(emoji='<:skip:1315853298770776134>', style=discord.ButtonStyle.gray)
    async def skip(self, interaction: discord.Interaction, button: Button):
        voice_client = self.ctx.voice_client
        if voice_client:
            voice_client.stop()
            await interaction.response.send_message(f"⏸️ | {self.ctx.author} 跳過了音樂！")
        else:
            embed = discord.Embed(title="❌ | 沒有正在播放的音樂！", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

class YTMusic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, url: str = ""):
        
        # 檢查使用者是否已在語音頻道
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:  # 檢查機器人是否已在語音頻道
                await channel.connect()
        else:
            embed = discord.Embed(title="❌ | 請先加入語音頻道！", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        # 如果有提供 URL，將音樂加入播放清單
        if url:
            logger.info(f"[音樂] 伺服器 ID： {ctx.guild.id}, 使用者名稱： {ctx.author.name}, 使用者輸入： {url}")
            await self.add_to_queue(ctx, url)
        
        # 播放音樂
        voice_client = ctx.voice_client
        if not voice_client.is_playing():
            await self.play_next(ctx)

    async def add_to_queue(self, ctx, url):
        guild_id = ctx.guild.id
        queue, folder = get_guild_queue_and_folder(guild_id)

        try:
            # 使用 pytubefix 並指定 get_audio_only 方法
            yt = YouTube(url)
            audio_stream = yt.streams.get_audio_only()
            file_path = os.path.join(folder, f"{yt.video_id}.mp3")

            if not os.path.exists(file_path):  # 避免重複下載
                audio_stream.download(output_path=folder, filename=f"{yt.video_id}.mp3")
            
            # 將檔案路徑與標題作為字典加入佇列
            await queue.put({"file_path": file_path, "title": yt.title, "url": url, "duration": yt.length, "video_id": yt.video_id,
                             "author": yt.author, "views": yt.views, "requester": ctx.author, "user_avatar": ctx.author.avatar.url})

            logger.debug(f"[音樂] 伺服器 ID： {ctx.guild.id}, 使用者名稱： {ctx.author.name}, 成功將 {yt.title} 添加到播放清單")
            embed = discord.Embed(title=f"✅ | 已添加到播放清單： {yt.title}", color=discord.Color.blue())
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"[音樂] 伺服器 ID： {ctx.guild.id}, 使用者名稱： {ctx.author.name}, 下載失敗： {e}")
            embed = discord.Embed(title="❌ | 下載失敗", color=discord.Color.red())
            await ctx.send(embed=embed)

    async def play_next(self, ctx):
        guild_id = ctx.guild.id
        queue, _ = get_guild_queue_and_folder(guild_id)

        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return
        if not queue.empty():
            item = await queue.get()
            file_path = item["file_path"]
            try:
                voice_client.play(
                    FFmpegPCMAudio(file_path),
                    after=lambda e: self.bot.loop.create_task(self.handle_after_play(ctx, file_path))
                )
                # 音樂資訊
                title = item["title"]
                url = item["url"]
                author = item["author"]
                duration = item["duration"]
                video_id = item["video_id"]
                thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                views = item["views"]
                minutes, seconds = divmod(duration, 60)
                requester = item["requester"]
                user_avatar = item["user_avatar"]
                embed = discord.Embed(title=f"📀 | 正在播放音樂：", description=f"**[{title}]({url})**", color=discord.Color.blue())
                embed.add_field(name="上傳頻道：", value=f"> {author}", inline=True)
                embed.add_field(name="播放時長：", value=f"> {minutes:02}:{seconds:02}", inline=True)
                embed.add_field(name="觀看次數：", value=f"> {int(views):,}", inline=False)
                embed.set_thumbnail(url=thumbnail)
                embed.set_footer(text=requester, icon_url=user_avatar)  
                # 功能按鈕
                view = MusicControlView(ctx, self)
                await ctx.send(embed=embed, view=view)
            except Exception as e:
                logger.error(f"[音樂] 伺服器 ID： {ctx.guild.id}, 播放音樂時出錯： {e}")
                embed = discord.Embed(title=f"❌ | 播放音樂時出錯", color=discord.Color.red())
                await ctx.send(embed=embed)
                await self.play_next(ctx)  # 嘗試播放下一首
        else:
            embed = discord.Embed(title="🌟 | 播放清單已播放完畢！", color=discord.Color.blue())
            await ctx.send(embed=embed)

    async def handle_after_play(self, ctx, file_path):
        try:
            if os.path.exists(file_path):
                await asyncio.sleep(1)
                os.remove(file_path)
                logger.debug(f"[音樂] 伺服器 ID： {ctx.guild.id}, 刪除檔案成功！")
        except Exception as e:
            logger.warning(f"[音樂] 伺服器 ID： {ctx.guild.id}, 刪除檔案失敗： {e}")
        await self.play_next(ctx)

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


async def setup(bot):
    await bot.add_cog(YTMusic(bot))
    logger.info("YTMusic 功能載入成功！")
