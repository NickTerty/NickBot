"""集中管理設定：路徑、環境變數。Token 只從環境變數 / .env 讀取，絕不寫進程式碼。"""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
COGS_DIR = Path(__file__).resolve().parent / "cogs"

RESTAURANTS_FILE = DATA_DIR / "restaurants.json"
DRINKS_FILE = DATA_DIR / "drink.json"

# 記錄上次同步的指令雜湊，指令沒變就不重新同步（避免撞到 Discord 的同步次數限制）
SYNC_HASH_FILE = ROOT_DIR / ".command_sync_hash"


def _load_dotenv() -> None:
    """若有安裝 python-dotenv 就讀取 .env；沒有的話直接使用系統環境變數。"""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(ROOT_DIR / ".env")


_load_dotenv()

# Discord bot token 格式大致為三段 base64 以 "." 分隔
_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{4,}\.[A-Za-z0-9_\-]{20,}$")


def get_token() -> str:
    token = (os.getenv("BOT_TOKEN") or "").strip()
    if not token:
        raise SystemExit("❌ 找不到環境變數 BOT_TOKEN，請設定環境變數或在 .env 中填入（參考 .env.example）。")
    if not _TOKEN_PATTERN.match(token):
        # 不印出 token 內容，避免洩漏到 log
        raise SystemExit("❌ BOT_TOKEN 格式看起來不正確，請確認是否複製完整（不要包含引號或 'Bot ' 前綴）。")
    return token


def get_dev_guild_id() -> int | None:
    """開發用：設定 DEV_GUILD_ID 時，指令只同步到該伺服器（立即生效，方便測試）。"""
    raw = (os.getenv("DEV_GUILD_ID") or "").strip()
    if not raw:
        return None
    if not raw.isdigit():
        raise SystemExit("❌ DEV_GUILD_ID 必須是純數字的伺服器 ID。")
    return int(raw)
