"""/lunch_list：列出某行政區的餐廳（可依預算篩選）。"""
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.constants import (
    COOLDOWN_PER_SECONDS,
    COOLDOWN_RATE,
    DISTRICT_CHOICES,
    PRICE_CHOICES,
    PRICE_ICONS,
    PRICE_TAGS,
)
from bot.data_loader import load_restaurants
from bot.utils import build_numbered_list, escape


class LunchList(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="lunch_list", description="查看餐廳清單（可選擇是否篩選預算）")
    @app_commands.describe(district="選擇你想查看的行政區", max_price="你能接受的最高預算級別（不選則顯示全部）")
    @app_commands.choices(district=DISTRICT_CHOICES, max_price=PRICE_CHOICES)
    @app_commands.checks.cooldown(COOLDOWN_RATE, COOLDOWN_PER_SECONDS, key=lambda i: i.user.id)
    async def lunch_list(
        self,
        interaction: discord.Interaction,
        district: app_commands.Choice[str],
        max_price: Optional[app_commands.Choice[int]] = None,
    ) -> None:
        restaurants = load_restaurants().get(district.value, [])

        if max_price is None:
            candidates = restaurants
            budget_title = "全部預算"
        else:
            candidates = [r for r in restaurants if r["price_level"] <= max_price.value]
            budget_title = f"{PRICE_TAGS[max_price.value]} 以內"

        if not candidates:
            await interaction.response.send_message(
                f"⚠️ 糟糕，在 **{district.value}** 找不到符合您預算的餐廳。", ephemeral=True
            )
            return

        lines = [f"{escape(r['name'])} [{PRICE_ICONS.get(r['price_level'], '❓')}]" for r in candidates]

        embed = discord.Embed(
            title=f"{district.value} 的美食地圖 ({budget_title})",
            description=build_numbered_list(lines, header="以下是幫您找到的餐廳清單：\n\n"),
            color=discord.Color.blue(),
        )
        embed.set_footer(text=f"總共幫你找到了 {len(candidates)} 家店")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LunchList(bot))
