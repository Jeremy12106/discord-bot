import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import json
import os
from loguru import logger
from pathlib import Path
from typing import Dict, List, Optional


# 指令群組：/debt add, /debt list, ...
class DebtGroup(app_commands.Group):
    def __init__(self, cog):
        super().__init__(name="debt", description="債務管理相關指令")
        self.cog = cog

    @app_commands.command(name="add", description="新增債務")
    async def add(self, interaction: discord.Interaction, debtor: discord.Member, amount: float, description: str):
        data = self.cog._load_data(interaction.guild_id)
        debtor_id = str(debtor.id)

        if debtor_id not in data:
            data[debtor_id] = []

        debt_entry = {
            "debtor_id": debtor_id,
            "creditor_id": interaction.user.id,
            "amount": amount,
            "description": description,
            "timestamp": interaction.created_at.timestamp()
        }

        data[debtor_id].append(debt_entry)
        self.cog._save_data(interaction.guild_id, data)

        try:
            await debtor.send(
                f"你被 {interaction.user.name} 記了一筆債務：{amount} 元，原因：{description}"
            )
        except discord.Forbidden:
            logger.warning(f"無法私訊 {debtor.name}")

        await interaction.response.send_message(
            f"✅ 已記錄: {debtor.name} 欠 {interaction.user.name} {amount} 元\n📌 原因: {description}"
        )

    @app_commands.command(name="list", description="列出債務")
    @app_commands.describe(member="要查看的成員，不填則顯示所有人")
    async def list(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        data = self.cog._load_data(interaction.guild_id)

        if not data:
            await interaction.response.send_message("目前沒有任何債務記錄")
            return

        if member:
            member_id = str(member.id)
            if member_id not in data or not data[member_id]:
                await interaction.response.send_message(f"{member.name} 目前沒有任何債務")
                return

            embed = discord.Embed(title=f"{member.name} 的債務清單", color=discord.Color.blue())
            for entry in data[member_id]:
                creditor = interaction.guild.get_member(entry["creditor_id"])
                creditor_name = creditor.name if creditor else "未知用戶"
                timestamp = datetime.fromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
                embed.add_field(
                    name=f"欠 {creditor_name} {entry['amount']} 元",
                    value=f"原因: {entry['description']}（{timestamp}）",
                    inline=False
                )
        else:
            embed = discord.Embed(title="所有債務清單", color=discord.Color.blue())
            for debtor_id, debts in data.items():
                if not debts:
                    continue
                debtor = interaction.guild.get_member(int(debtor_id))
                if not debtor:
                    continue
                total = sum(d["amount"] for d in debts)
                debt_text = f"總共欠款: {total} 元\n"
                debt_text += "\n".join(
                    f"- 欠 {interaction.guild.get_member(d['creditor_id']).name if interaction.guild.get_member(d['creditor_id']) else '未知用戶'} {d['amount']} 元（{d['description']}）"
                    for d in debts
                )
                embed.add_field(name=f"{debtor.name} 的債務", value=debt_text, inline=False)

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="top", description="負債排行榜")
    async def top(self, interaction: discord.Interaction):
        data = self.cog._load_data(interaction.guild_id)
        if not data:
            await interaction.response.send_message("目前沒有任何債務記錄")
            return

        debtor_totals = {}

        # 計算每位欠債人的總欠款
        for debtor_id, debts in data.items():
            total_debt = sum(entry["amount"] for entry in debts)
            debtor_totals[debtor_id] = total_debt

        if not debtor_totals:
            await interaction.response.send_message("目前沒有任何債務記錄")
            return

        # 根據欠款金額進行排序
        sorted_debtors = sorted(debtor_totals.items(), key=lambda x: x[1], reverse=True)

        embed = discord.Embed(title="💰 欠債排行榜", color=discord.Color.blue())
        
        medals = ["🥇", "🥈", "🥉"]
        for i, (user_id, total) in enumerate(sorted_debtors[:10], start=1):
            user = interaction.guild.get_member(int(user_id))
            name = user.name if user else f"未知用戶 ({user_id})"
            medal = medals[i - 1] if i <= len(medals) else f"#{i}"
            embed.add_field(name=f"{medal} {name}", value=f"總共欠了 {total} 元", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="repay", description="還清一筆債務")
    @app_commands.describe(debt_description="選擇要還清的債務")
    async def repay(self, interaction: discord.Interaction, debt_description: str):
        data = self.cog._load_data(interaction.guild_id)
        debtor_id = str(interaction.user.id)
        if debtor_id not in data:
            await interaction.response.send_message("你沒有任何債務可以還清。", ephemeral=True)
            return

        debt_index = next((i for i, d in enumerate(data[debtor_id]) if self._format_repay_debt(d, interaction) == debt_description), None)
        if debt_index is None:
            await interaction.response.send_message("找不到指定的債務。", ephemeral=True)
            return

        debt_entry = data[debtor_id][debt_index]
        creditor = interaction.guild.get_member(debt_entry["creditor_id"])

        del data[debtor_id][debt_index]
        if not data[debtor_id]:
            del data[debtor_id]

        self.cog._save_data(interaction.guild_id, data)

        if creditor:
            try:
                await creditor.send(
                    f"{interaction.user.name} 剛還清了一筆債務：{debt_entry['amount']} 元\n📌 原因：{debt_entry['description']}"
                )
            except discord.Forbidden:
                logger.warning(f"無法私訊債主 {creditor.name}")

        await interaction.response.send_message(f"✅ 已還清債務：{debt_entry['amount']} 元 - {debt_entry['description']}")
    
    @repay.autocomplete("debt_description")
    async def repay_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        data = self.cog._load_data(interaction.guild_id)
        debtor_id = str(interaction.user.id)
        if debtor_id not in data:
            return []

        choices = []
        for entry in data[debtor_id]:
            text = self._format_repay_debt(entry, interaction)
            if current.lower() in text.lower():
                choices.append(app_commands.Choice(name=text[:100], value=text[:100]))

        return choices[:25]

    def _format_repay_debt(self, entry: dict, interaction: discord.Interaction) -> str:
        creditor = interaction.guild.get_member(entry["creditor_id"])
        creditor_name = creditor.name if creditor else "未知用戶"
        return f"欠 {creditor_name} {entry['amount']} 元（{entry['description']}）"

    @app_commands.command(name="remove_by_creditor", description="債主刪除一筆債務")
    @app_commands.describe(debt_description="選擇要刪除的債務")
    async def remove_by_creditor(self, interaction: discord.Interaction, debt_description: str):
        data = self.cog._load_data(interaction.guild_id)
        creditor_id = interaction.user.id

        found = None
        for debtor_id, debts in data.items():
            for i, entry in enumerate(debts):
                if entry["creditor_id"] == creditor_id and self._format_remove_debt(entry, interaction) == debt_description:
                    found = (debtor_id, i, entry)
                    break
            if found:
                break

        if not found:
            await interaction.response.send_message("找不到指定的債務。", ephemeral=True)
            return

        debtor_id, index, entry = found
        debtor = interaction.guild.get_member(int(debtor_id))

        del data[debtor_id][index]
        if not data[debtor_id]:
            del data[debtor_id]

        self.cog._save_data(interaction.guild_id, data)

        if debtor:
            try:
                await debtor.send(
                    f"{interaction.user.name} 已刪除你的一筆債務：{entry['amount']} 元\n📌 原因：{entry['description']}"
                )
            except discord.Forbidden:
                logger.warning(f"無法私訊債務人 {debtor.name}")

        await interaction.response.send_message(f"✅ 已刪除債務：{entry['amount']} 元 - {entry['description']}")

    @remove_by_creditor.autocomplete("debt_description")
    async def remove_by_creditor_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        data = self.cog._load_data(interaction.guild_id)
        creditor_id = interaction.user.id
        choices = []

        for debtor_id, debts in data.items():
            for entry in debts:
                if entry["creditor_id"] == creditor_id:
                    text = self._format_remove_debt(entry, interaction)
                    if current.lower() in text.lower():
                        choices.append(app_commands.Choice(name=text[:100], value=text[:100]))

        return choices[:25]
    
    def _format_remove_debt(self, entry: dict, interaction: discord.Interaction) -> str:
        creditor = interaction.guild.get_member(entry["creditor_id"])
        debtor = interaction.guild.get_member(int(entry["debtor_id"]))
        debtor_name = debtor.name if debtor else "未知債務人"
        return f"{debtor_name} 欠 {entry['amount']} 元（{entry['description']}）"
    

# 債務功能主 Cog
class DebtCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = Path("assets/data/debt_log")
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.bot.tree.add_command(DebtGroup(self))
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    def _get_server_file(self, server_id: int) -> Path:
        return self.data_path / f"{server_id}.json"

    def _load_data(self, server_id: int) -> Dict:
        file_path = self._get_server_file(server_id)
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"{file_path} JSON 載入失敗")
                return {}
        return {}

    def _save_data(self, server_id: int, data: Dict):
        file_path = self._get_server_file(server_id)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


async def setup(bot: commands.Bot):
    await bot.add_cog(DebtCog(bot))
