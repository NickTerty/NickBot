"""NickBot 啟動入口：python main.py"""
import logging

import discord

from bot.client import NickBot
from bot.config import get_token


def main() -> None:
    discord.utils.setup_logging(level=logging.INFO)
    token = get_token()
    bot = NickBot()
    # log_handler=None：沿用上面設定的 logging，不重複輸出
    bot.run(token, log_handler=None)


if __name__ == "__main__":
    main()
