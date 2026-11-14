"""/drink_list：列出所有飲料店。"""
import discord
from discord import app_commands
from discord.ext import commands

from bot.constants import COOLDOWN_PER_SECONDS, COOLDOWN_RATE
from bot.data_loader import load_drinks
from bot.utils import build_numbered_list, escape


class DrinkList(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="drink_list", description="列出所有會隨機選擇的飲料店")
    @app_commands.checks.cooldown(COOLDOWN_RATE, COOLDOWN_PER_SECONDS, key=lambda i: i.user.id)
    async def drink_list(self, interaction: discord.Interaction) -> None:
        drinks = load_drinks()
        if not drinks:
            await interaction.response.send_message("⚠️ 飲料資料庫空空如也！", ephemeral=True)
            return

        embed = discord.Embed(
            title="手搖飲全系列地圖",
            description=build_numbered_list(
                [escape(d) for d in drinks], header="以下是目前資料庫內所有的飲料店：\n\n"
            ),
            color=discord.Color.teal(),
        )
        embed.set_footer(text=f"總共幫你找到了 {len(drinks)} 家飲料店")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DrinkList(bot))
