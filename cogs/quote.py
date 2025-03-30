import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import requests
import textwrap

class Quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="名言")
    async def make_quote(self, ctx, mode: str = "黑白"):
        """製作帶有頭像的名言圖片，支援黑白/彩色模式"""
        async with ctx.typing():
            if not ctx.message.reference:
                await ctx.send("請回覆一則訊息來製作名言！")
                return

            # 獲取被回覆的訊息
            replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            author = replied_message.author
            author_name = author.display_name
            content = replied_message.content

            # 獲取頭像
            avatar_url = author.display_avatar.url
            avatar = self.download_avatar(avatar_url, mode)

            # 生成名言圖片
            img = self.create_quote_image(content, author_name, avatar)

            # 將圖片轉換為 BytesIO 並上傳
            with io.BytesIO() as image_binary:
                img.save(image_binary, "PNG")
                image_binary.seek(0)
                await ctx.send(file=discord.File(fp=image_binary, filename="quote.png"))

    def download_avatar(self, url, mode):
        """下載 Discord 頭像，並轉換為黑白或彩色"""
        response = requests.get(url, stream=True)
        avatar = Image.open(io.BytesIO(response.content)).convert("RGBA")

        # 縮放並裁切為圓形
        avatar = avatar.resize((300, 300), Image.LANCZOS)
        # mask = Image.new("L", (100, 100), 0)
        # draw = ImageDraw.Draw(mask)
        # draw.ellipse((0, 0, 100, 100), fill=255)
        # avatar.putalpha(mask)

        # 黑白模式
        avatar = ImageOps.grayscale(avatar).convert("RGBA") if mode != "彩色" else avatar

        return avatar

    def create_quote_image(self, text, author, avatar):
        """生成帶有頭像的名言圖片"""
        # 設定圖片大小
        width, height = 600, 300
        left_width = width // 2

        # 字體設定
        try:
            font_text = ImageFont.truetype(r"assets\font\TW-Kai-98_1.ttf", 28)
            font_author = ImageFont.truetype(r"assets\font\TW-Kai-98_1.ttf", 22)
        except IOError:
            font_text = ImageFont.load_default()
            font_author = ImageFont.load_default()

        # 創建圖片
        img = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # 調整並置中頭像
        avatar_size = 300
        avatar = avatar.resize((avatar_size, avatar_size), Image.LANCZOS)
        avatar_x = (left_width - avatar_size) // 2 - 25
        avatar_y = (height - avatar_size) // 2
        img.paste(avatar, (avatar_x, avatar_y), avatar)

        parallelogram = [(225, -50), (275, 350), (650, 350), (650, -50)]
        draw.polygon(parallelogram, fill="black")

        # 計算文字區域並繪製文字 (換行處理)
        text_width = width - left_width - 40  # 右側留出邊距
        wrapped_text = textwrap.fill(text, width=20)  # 減少每行字數以適應新寬度
        
        # 獲取文字大小以便垂直置中
        text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font_text)
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = left_width + 20  # 右側文字起始位置
        text_y = (height - text_height - 40) // 2  # 垂直置中（保留作者名稱的空間）
        
        # 繪製文字（白色）
        draw.text((text_x, text_y), wrapped_text, font=font_text, fill=(255, 255, 255))

        # 繪製發送者名稱（白色，靠右對齊）
        author_text = f"- {author}"
        author_bbox = draw.textbbox((0, 0), author_text, font=font_author)
        author_width = author_bbox[2] - author_bbox[0]
        author_x = width - author_width - 20
        author_y = height - 50
        draw.text((author_x, author_y), author_text, font=font_author, fill=(255, 255, 255))

        return img

async def setup(bot):
    await bot.add_cog(Quote(bot))
