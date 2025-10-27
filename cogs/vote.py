import asyncio
import aiohttp
import discord
import datetime
from discord import app_commands
from discord.ext import commands
from typing import Optional
from loguru import logger

class Vote(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.processed_polls = set()
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    @app_commands.command(name="vote", description="建立投票")
    @app_commands.describe(question="投票主題", options="投票選項，請以 ｢陣列｣ 形式提供", multiple="允許複選，預設為否", duration="投票時長（小時），預設為24")
    async def slash_vote(self, interaction: discord.Interaction, question: str, 
                         options: str, multiple: Optional[bool]=False, duration: Optional[float] = 24.0):
        poll = discord.Poll(
            question=question,
            duration=datetime.timedelta(hours=duration),
            multiple=multiple,
        )
        options_list = [x.strip().strip('"').strip("'") for x in options.strip("[]").split(",") if x.strip()]
        for option in options_list:
            poll.add_answer(text=option)

        await interaction.response.send_message(poll=poll)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        # 確認訊息是否為機器人發送
        if before.author != self.bot.user:
            return

        # 如果這個投票已經處理過，直接跳過
        if after.id in self.processed_polls:
            return

        # 標記為已處理，避免重複
        self.processed_polls.add(after.id)

        # 確認訊息內是否含有投票且已結束
        if after.poll and after.poll.is_finalized:
            poll = after.poll
            embed = discord.Embed(
                title="投票結果",
                description=f"**主題：{poll.question}**",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text="投票已結束")

            # 用 set 追蹤不重複投票者
            unique_voters = set()

            for answer in poll.answers:
                voters = await get_poll_voters(self.bot, after.channel.id, after.id, [answer.id])
                voter_ids = voters.get(answer.id, [])
                unique_voters.update(voter_ids)  # 將這個選項的投票者加入集合（自動去重）

                voter_count = len(voter_ids)
                embed.add_field(
                    name=f"{answer.text} - {voter_count} 票",
                    value="> " + (", ".join(f"<@{voter_id}>" for voter_id in voter_ids) or "無人投票"),
                    inline=False
                )

            # 在最後加上總投票人數
            embed.add_field(
                name="🧮 參與人數",
                value=f"> 共 {len(unique_voters)} 人參與投票",
                inline=False
            )

            await after.channel.send(embed=embed)


async def get_poll_voters(bot, channel_id, message_id, answer_ids):
    token = bot.http.token
    headers = {"Authorization": f"Bot {token}"}
    voters = {}

    async with aiohttp.ClientSession(headers=headers) as session:
        for ans_id in answer_ids:
            url = f"https://discord.com/api/v10/channels/{channel_id}/polls/{message_id}/answers/{ans_id}"
            async with session.get(url) as resp:
                data = await resp.json()
                voters[ans_id] = [u["id"] for u in data.get("users", [])]

    return voters

async def setup(bot: commands.Bot):
    await bot.add_cog(Vote(bot))
