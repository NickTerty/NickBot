"""/drink：隨機挑一家飲料店。"""
import secrets

import discord
from discord import app_commands
from discord.ext import commands

from bot.constants import COOLDOWN_PER_SECONDS, COOLDOWN_RATE
from bot.data_loader import load_drinks
from bot.utils import escape


class Drink(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="drink", description="喝飲料時間！隨機挑選一杯台南大學生的飲料")
    @app_commands.checks.cooldown(COOLDOWN_RATE, COOLDOWN_PER_SECONDS, key=lambda i: i.user.id)
    async def drink(self, interaction: discord.Interaction) -> None:
        drinks = load_drinks()
        if not drinks:
            await interaction.response.send_message("⚠️ 飲料資料庫空空如也，請通知管理員補充！", ephemeral=True)
            return

        chosen = secrets.choice(drinks)

        embed = discord.Embed(
            title="台南大學生的飲料選擇",
            description="今天下午推薦你喝這家：",
            color=discord.Color.teal(),
        )
        embed.add_field(name="飲料店名稱", value=f"**{escape(chosen)}**", inline=False)
        embed.set_footer(text="甜度冰塊請自行選擇！")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Drink(bot))
