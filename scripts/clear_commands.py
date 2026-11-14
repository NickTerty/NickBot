"""清除 Discord 上殘留的 ghost command。

以前若用「測試伺服器 (guild) 同步」註冊過指令，即使之後改成全域同步，
那些 guild 指令仍會留在該伺服器，導致指令出現兩次或舊指令刪不掉。

用法（在專案根目錄執行）：
    python -m scripts.clear_commands --guild 123456789012345678   # 清除某伺服器的 guild 指令
    python -m scripts.clear_commands --global                     # 清除所有全域指令（下次啟動 bot 會重新註冊）
"""
from __future__ import annotations

import argparse
import logging

import discord

from bot.config import SYNC_HASH_FILE, get_token


def main() -> None:
    parser = argparse.ArgumentParser(description="清除 Discord 上殘留的斜線指令")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--guild", type=int, action="append", help="要清除指令的伺服器 ID（可重複指定）")
    group.add_argument("--global", dest="global_", action="store_true", help="清除全域指令")
    args = parser.parse_args()

    discord.utils.setup_logging(level=logging.INFO)
    log = logging.getLogger("clear_commands")

    class Cleaner(discord.Client):
        def __init__(self) -> None:
            super().__init__(intents=discord.Intents.none())
            self.tree = discord.app_commands.CommandTree(self)

        async def setup_hook(self) -> None:
            if args.global_:
                self.tree.clear_commands(guild=None)
                await self.tree.sync()
                log.info("已清除所有全域指令。")
            else:
                for gid in args.guild:
                    guild = discord.Object(id=gid)
                    self.tree.clear_commands(guild=guild)
                    await self.tree.sync(guild=guild)
                    log.info("已清除伺服器 %s 的 guild 指令。", gid)
            # 讓 bot 下次啟動時一定重新同步
            SYNC_HASH_FILE.unlink(missing_ok=True)
            await self.close()

    Cleaner().run(get_token(), log_handler=None)


if __name__ == "__main__":
    main()
