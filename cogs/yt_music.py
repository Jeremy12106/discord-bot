import os
import asyncio
import discord
from pytubefix import YouTube
from pytubefix.cli import on_progress
from discord.ext import commands
from discord import FFmpegPCMAudio
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
            await ctx.send("請先加入語音頻道！")
            return

        # 如果有提供 URL，將音樂加入播放清單
        if url:
            await self.add_to_queue(ctx, url)
        
        logger.info(f"[音樂] 伺服器 ID: {ctx.guild.id}, 使用者名稱: {ctx.author.name}, 使用者輸入: {url:None}")
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
            await queue.put({"file_path": file_path, "title": yt.title})
            await ctx.send(f"已添加到播放清單: {yt.title}")
        except Exception as e:
            await ctx.send(f"下載失敗: {e}")

    async def play_next(self, ctx):
        guild_id = ctx.guild.id
        queue, _ = get_guild_queue_and_folder(guild_id)

        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return

        if not queue.empty():
            item = await queue.get()  # 從佇列取出字典
            file_path = item["file_path"]
            title = item["title"]
            try:
                voice_client.play(
                    discord.FFmpegPCMAudio(file_path),
                    after=lambda e: self.bot.loop.create_task(self.handle_after_play(ctx, file_path))
                )
                await ctx.send(f"正在播放音樂: {title}")  # 顯示音樂標題
            except Exception as e:
                await ctx.send(f"播放音樂時出錯: {e}")
                await self.play_next(ctx)  # 嘗試播放下一首
        else:
            await ctx.send("播放清單已播放完畢！")

    async def handle_after_play(self, ctx, file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            await print(f"刪除檔案失敗: {e}")
        await self.play_next(ctx)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # 偵測機器人離開語音頻道時，清理伺服器相關資料
        if member.bot and before.channel is not None and after.channel is None:
            guild_id = member.guild.id
            _, folder = get_guild_queue_and_folder(guild_id)
            await asyncio.sleep(2)
            # 刪除所有音檔
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            
            # 清空播放隊列
            if guild_id in guild_queues:
                guild_queues[guild_id] = asyncio.Queue()

    
    # @commands.command()
    # async def next(self, ctx):
    #     """播放下一首音樂。"""
    #     guild_id = ctx.guild.id
    #     queue, folder = get_guild_queue_and_folder(guild_id)

    #     voice_client = ctx.voice_client
    #     if voice_client is None:
    #         await ctx.send("我不在任何語音頻道中！")
    #         return

    #     if not voice_client.is_playing():
    #         await ctx.send("目前沒有正在播放的音樂！")
    #         return

    #     # 停止當前播放音樂
    #     voice_client.stop()

    #     # 取得當前播放音樂的檔案路徑
    #     current_source = voice_client.source
    #     if isinstance(current_source, FFmpegPCMAudio):
    #         current_file_path = current_source.filename  # 獲取當前檔案的路徑
    #         try:
    #             if os.path.exists(current_file_path):
    #                 os.remove(current_file_path)
    #         except Exception as e:
    #             print(f"刪除檔案失敗: {current_file_path} - {e}")

    #     # 播放下一首音樂
    #     await self.play_next(ctx)


# 加入 cog 到機器人中
async def setup(bot):
    await bot.add_cog(YTMusic(bot))
    print("YTMusic 功能載入成功！")
