import os
import asyncio
from pytube import YouTube
from discord.ext import commands
from discord import FFmpegPCMAudio

# 定義每個伺服器的播放隊列
guild_queues = {}

# 確保伺服器有獨立的資料夾和播放隊列
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

        # 確認機器人是否已加入語音頻道
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("請先加入語音頻道！")
            return

        # 如果提供了 URL，將音樂加入播放隊列
        if url:
            await ctx.send(f"添加到播放清單: {url}")
            await self.add_to_queue(ctx, url)
        
        # 播放音樂
        voice_client = ctx.voice_client
        if not voice_client.is_playing():
            await self.play_next(ctx)

    async def add_to_queue(self, ctx, url):
        guild_id = ctx.guild.id
        queue, folder = get_guild_queue_and_folder(guild_id)

        try:
            yt = YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            file_path = os.path.join(folder, f"{yt.video_id}.mp3")
            if not os.path.exists(file_path):  # 避免重複下載
                audio_stream.download(output_path=folder, filename=f"{yt.video_id}.mp3")
            await queue.put(file_path)
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
            file_path = await queue.get()
            try:
                voice_client.play(
                    FFmpegPCMAudio(file_path),
                    after=lambda e: self.bot.loop.create_task(self.handle_after_play(ctx, file_path))
                )
                await ctx.send(f"正在播放音樂: {os.path.basename(file_path)}")
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
            await ctx.send(f"刪除檔案失敗: {e}")
        await self.play_next(ctx)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # 偵測機器人離開語音頻道時，清理伺服器相關資料
        if member.bot and before.channel is not None and after.channel is None:
            guild_id = member.guild.id
            _, folder = get_guild_queue_and_folder(guild_id)
            
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

# 加入 cog 到機器人中
async def setup(bot):
    await bot.add_cog(YTMusic(bot))
    print("YTMusic 功能載入成功！")
