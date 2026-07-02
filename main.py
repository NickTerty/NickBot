import json
import os
import discord
from discord import app_commands
import random

intents = discord.Intents.default()
intents.message_content = True

class NickBotClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("全域斜線指令已成功同步至 Discord 總部！")

bot = NickBotClient(intents=intents)

@bot.event
async def on_ready():
    print(f"我們已經成功登入為 {bot.user}")

@bot.tree.command(name="lunch", description="消除困難！隨機挑選台南大學周邊午餐")
@app_commands.describe(district="選擇你現在想去的行政區")
@app_commands.choices(district=[
    app_commands.Choice(name="中西區 (府城校區周邊)", value="中西區"),
    app_commands.Choice(name="東區 (榮譽校區/育樂街)", value="東區"),
    app_commands.Choice(name="南區 (大成路/新興路周邊)", value="南區")
])
async def lunch(interaction: discord.Interaction, district: app_commands.Choice[str]):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "restaurants.json")
    
    if not os.path.exists(json_path):
        await interaction.response.send_message("❌ 找不到餐廳資料庫檔案 `restaurants.json`！")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        restaurant_data = json.load(f)

    selected_district = district.value
    restaurants_list = restaurant_data.get(selected_district, [])

    if not restaurants_list:
        await interaction.response.send_message(f"⚠️ 糟糕，{selected_district} 目前沒有安排任何餐廳資料。")
        return

    chosen_restaurant = random.choice(restaurants_list)

    embed = discord.Embed(
        title="台南大學生的午餐救星",
        description=f"今天在 **{selected_district}**，推薦你吃：",
        color=discord.Color.magenta()
    )
    embed.add_field(name="餐廳名稱", value=f"**{chosen_restaurant}**", inline=False)
    embed.set_footer(text="別想了，就吃這家吧！")

    await interaction.response.send_message(embed=embed)

TOKEN = os.getenv("BOT_TOKEN")
bot.run(TOKEN)