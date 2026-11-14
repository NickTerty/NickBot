"""/lunch：根據行政區與預算隨機挑一家餐廳。"""
import secrets

import discord
from discord import app_commands
from discord.ext import commands

from bot.constants import COOLDOWN_PER_SECONDS, COOLDOWN_RATE, DISTRICT_CHOICES, PRICE_CHOICES, PRICE_TAGS
from bot.data_loader import load_restaurants
from bot.utils import escape


class Lunch(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="lunch", description="消除困難！根據行政區與預算挑選午餐")
    @app_commands.describe(district="選擇你現在想去的行政區", max_price="你能接受的最高預算級別")
    @app_commands.choices(district=DISTRICT_CHOICES, max_price=PRICE_CHOICES)
    @app_commands.checks.cooldown(COOLDOWN_RATE, COOLDOWN_PER_SECONDS, key=lambda i: i.user.id)
    async def lunch(
        self,
        interaction: discord.Interaction,
        district: app_commands.Choice[str],
        max_price: app_commands.Choice[int],
    ) -> None:
        restaurants = load_restaurants().get(district.value, [])
        candidates = [r for r in restaurants if r["price_level"] <= max_price.value]

        if not candidates:
            await interaction.response.send_message(
                f"⚠️ 糟糕，在 **{district.value}** 找不到符合您預算限制的餐廳（太便宜或沒開拓到）。",
                ephemeral=True,
            )
            return

        chosen = secrets.choice(candidates)

        embed = discord.Embed(
            title="台南大學生的午餐救星",
            description=f"今天在 **{district.value}** 幫你找符合預算的店：",
            color=discord.Color.magenta(),
        )
        embed.add_field(name="餐廳名稱", value=f"**{escape(chosen['name'])}**", inline=False)
        embed.add_field(name="價位落點", value=PRICE_TAGS.get(chosen["price_level"], "未知"), inline=True)
        embed.set_footer(text="別想了，就吃這家吧！")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Lunch(bot))
