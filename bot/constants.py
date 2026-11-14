"""多個指令共用的選項與文字，改一個地方就全部同步。"""
from discord import app_commands

DISTRICT_CHOICES = [
    app_commands.Choice(name="中西區 (府城校區周邊)", value="中西區"),
    app_commands.Choice(name="東區 (榮譽校區/育樂街)", value="東區"),
    app_commands.Choice(name="南區 (大成路/新興路周邊)", value="南區"),
    app_commands.Choice(name="北區", value="北區"),
    app_commands.Choice(name="安平區", value="安平區"),
]

PRICE_CHOICES = [
    app_commands.Choice(name="百元小確幸 (100~130元以內)", value=1),
    app_commands.Choice(name="正常的一餐 (130~300元之間)", value=2),
    app_commands.Choice(name="犒賞自己/大餐 (300元以上)", value=3),
]

PRICE_TAGS = {
    1: "百元小確幸 (100~130元以內)",
    2: "正常的一餐 (130~300元之間)",
    3: "犒賞自己/大餐 (300元以上)",
}

PRICE_ICONS = {1: "💰", 2: "💰💰", 3: "💰💰💰"}

# 每位使用者每 N 秒最多使用幾次指令（防洗版 / 濫用）
COOLDOWN_RATE = 3
COOLDOWN_PER_SECONDS = 10.0
