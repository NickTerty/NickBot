"""共用小工具。"""
from __future__ import annotations

import discord

# Discord embed description 上限 4096 字，保留一點空間
EMBED_DESCRIPTION_LIMIT = 4000


def escape(text: str) -> str:
    """跳脫 Markdown 與 @mention，避免資料內容破壞排版或 tag 到人。"""
    return discord.utils.escape_mentions(discord.utils.escape_markdown(text))


def build_numbered_list(items: list[str], header: str = "", limit: int = EMBED_DESCRIPTION_LIMIT) -> str:
    """產生編號清單，超過 embed 長度上限時截斷並註明剩餘數量，避免送出失敗。"""
    text = header
    for index, item in enumerate(items, start=1):
        line = f"{index}. {item}\n"
        if len(text) + len(line) > limit - 30:
            text += f"…還有 {len(items) - index + 1} 筆未顯示"
            break
        text += line
    return text
