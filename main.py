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

# Lunch Picker
@bot.tree.command(name="lunch", description="消除困難！根據行政區與預算挑選午餐")
@app_commands.describe(district="選擇你現在想去的行政區", max_price="你能接受的最高預算級別")
@app_commands.choices(
    district=[
        app_commands.Choice(name="中西區 (府城校區周邊)", value="中西區"),
        app_commands.Choice(name="東區 (榮譽校區/育樂街)", value="東區"),
        app_commands.Choice(name="南區 (大成路/新興路周邊)", value="南區"),
        app_commands.Choice(name="北區", value="北區"),
        app_commands.Choice(name="安平區", value="安平區")
    ],
    max_price=[
        app_commands.Choice(name="百元小確幸 (100~130元以內)", value=1),
        app_commands.Choice(name="正常的一餐 (130~300元之間)", value=2),
        app_commands.Choice(name="犒賞自己/大餐 (300元以上)", value=3)
    ]
)
async def lunch(interaction: discord.Interaction, district: app_commands.Choice[str], max_price: app_commands.Choice[int]):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "restaurants.json")
    
    if not os.path.exists(json_path):
        await interaction.response.send_message("❌ 找不到餐廳資料庫檔案 `restaurants.json`！")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        restaurant_data = json.load(f)

    selected_district = district.value
    user_budget = max_price.value
    
    all_restaurants_in_district = restaurant_data.get(selected_district, [])

    valid_restaurants = []
    for res in all_restaurants_in_district:
        if res.get("price_level", 1) <= user_budget:
            valid_restaurants.append(res)

    if not valid_restaurants:
        await interaction.response.send_message(f"⚠️ 糟糕，在 **{selected_district}** 找不到符合您預算限制的餐廳（太便宜或沒開拓到）。")
        return

    chosen_res = random.choice(valid_restaurants)

    price_tags = {1: "百元小確幸(100~130元以內)", 2: "正常的一餐(130~300元之間)", 3: "大餐(300元以上)"}
    res_price_level = chosen_res.get("price_level", 1)

    embed = discord.Embed(
        title="台南大學生的午餐救星",
        description=f"今天在 **{selected_district}** 幫你找符合預算的店：",
        color=discord.Color.magenta()
    )
    embed.add_field(name="餐廳名稱", value=f"**{chosen_res['name']}**", inline=False)
    embed.add_field(name="價位落點", value=f"{price_tags.get(res_price_level, '未知')}", inline=True)
    embed.set_footer(text="別想了，就吃這家吧！")

    await interaction.response.send_message(embed=embed)

# Lunch List
@bot.tree.command(name="lunch_list", description="查看餐廳清單（可選擇是否篩選預算）")
@app_commands.describe(district="選擇你想查看的行政區", max_price="你能接受的最高預算級別（不選則顯示全部）")
@app_commands.choices(
    district=[
        app_commands.Choice(name="中西區 (府城校區周邊)", value="中西區"),
        app_commands.Choice(name="東區 (榮譽校區/育樂街)", value="東區"),
        app_commands.Choice(name="南區 (大成路/新興路周邊)", value="南區"),
        app_commands.Choice(name="北區", value="北區"),
        app_commands.Choice(name="安平區", value="安平區")
    ],
    max_price=[
        app_commands.Choice(name="百元小確幸 (100~130元以內)", value=1),
        app_commands.Choice(name="正常的一餐 (130~300元之間)", value=2),
        app_commands.Choice(name="犒賞自己/大餐 (300元以上)", value=3)
    ]
)

async def lunch_list(interaction: discord.Interaction, district: app_commands.Choice[str], max_price: app_commands.Choice[int] = None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "restaurants.json")
    
    if not os.path.exists(json_path):
        await interaction.response.send_message("❌ 找不到餐廳資料庫檔案 `restaurants.json`！")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        restaurant_data = json.load(f)

    selected_district = district.value
    all_restaurants = restaurant_data.get(selected_district, [])

    if max_price is None:
        valid_restaurants = all_restaurants
        budget_title = "全部預算"
    else:
        user_budget = max_price.value
        valid_restaurants = [res for res in all_restaurants if res.get("price_level", 1) <= user_budget]
        price_tags = {1: "百元小確幸(100~130元以內)", 2: "正常的一餐 (130~300元之間)", 3: "犒賞自己/大餐 (300元以上)"}
        budget_title = f"{price_tags.get(user_budget)} 以內"

    if not valid_restaurants:
        await interaction.response.send_message(f"⚠️ 糟糕，在 **{selected_district}** 找不到符合您預算的餐廳。")
        return

    list_text = ""
    price_icons = {1: "💰", 2: "💰💰", 3: "💰💰💰"}
    
    for index, res in enumerate(valid_restaurants, start=1):
        name = res.get("name")
        level = res.get("price_level", 1)
        icon = price_icons.get(level, "❓")
        list_text += f"{index}. {name} [{icon}]\n"

    embed = discord.Embed(
        title=f" {selected_district} 的美食地圖 ({budget_title})",
        description=f"以下是幫您找到的餐廳清單：\n\n{list_text}",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"總共幫你找到了 {len(valid_restaurants)} 家店")

    await interaction.response.send_message(embed=embed)

# Drink Picker
@bot.tree.command(name="drink", description="喝飲料時間！隨機挑選一杯台南大學生的飲料")
async def drink(interaction: discord.Interaction):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "drink.json")
    
    if not os.path.exists(json_path):
        await interaction.response.send_message("❌ 找不到飲料資料庫檔案 `drink.json`！")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        drinks_list = json.load(f)

    if not drinks_list:
        await interaction.response.send_message("⚠️ 飲料資料庫空空如也，快去 drink.json 檔案裡加點飲料吧！")
        return

    chosen_drink = random.choice(drinks_list)

    embed = discord.Embed(
        title="台南大學生的飲料選擇",
        description="今天下午推薦你喝這家：",
        color=discord.Color.teal()
    )
    embed.add_field(name="飲料店名稱", value=f"**{chosen_drink}**", inline=False)
    embed.set_footer(text="甜度冰塊請自行選擇！")

    await interaction.response.send_message(embed=embed)

# Token
TOKEN = os.getenv("BOT_TOKEN")
bot.run(TOKEN)