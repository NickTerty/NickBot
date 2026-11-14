"""Bot 本體：自動載入 cogs、智慧同步斜線指令、全域錯誤處理。"""
from __future__ import annotations

import hashlib
import json
import logging

import discord
from discord import app_commands
from discord.ext import commands

from .config import COGS_DIR, SYNC_HASH_FILE, get_dev_guild_id
from .data_loader import DataError

log = logging.getLogger(__name__)


class NickBot(commands.Bot):
    def __init__(self) -> None:
        # 只用斜線指令，不需要 message_content 這種特權 intent（最小權限原則）
        intents = discord.Intents.default()
        super().__init__(
            command_prefix=commands.when_mentioned,  # 不使用文字指令，給一個不會誤觸的前綴
            intents=intents,
            help_command=None,
            # 全域禁止 bot 訊息 tag 任何人 / @everyone / 身分組
            allowed_mentions=discord.AllowedMentions.none(),
        )
        self.tree.on_error = self.on_app_command_error

    async def setup_hook(self) -> None:
        await self._load_cogs()
        await self._sync_commands()

    async def _load_cogs(self) -> None:
        """自動載入 bot/cogs/ 裡的每個 .py：一個檔案 = 一個指令，新增指令只要丟一個檔案進去。"""
        for path in sorted(COGS_DIR.glob("*.py")):
            if path.name.startswith("_"):
                continue
            ext = f"bot.cogs.{path.stem}"
            await self.load_extension(ext)
            log.info("已載入指令模組 %s", ext)

    def _command_fingerprint(self, guild: discord.abc.Snowflake | None) -> str:
        payload = sorted(
            (cmd.to_dict(self.tree) for cmd in self.tree.get_commands(guild=guild)),
            key=lambda c: c["name"],
        )
        scope = f"guild:{guild.id}" if guild else "global"
        raw = json.dumps([scope, payload], sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def _sync_commands(self) -> None:
        """只有指令內容有變動才同步，避免每次重開都打 API（Discord 對同步有每日次數限制）。

        Discord 端的指令清單會被「整份取代」，所以刪掉 / 改名的指令會在同步時一併移除，
        不會留下 ghost command。
        """
        guild_id = get_dev_guild_id()
        guild = discord.Object(id=guild_id) if guild_id else None
        if guild:
            # 開發模式：複製全域指令到測試伺服器，立即生效
            self.tree.copy_global_to(guild=guild)

        fingerprint = self._command_fingerprint(guild)
        try:
            previous = SYNC_HASH_FILE.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            previous = ""

        if previous == fingerprint:
            log.info("斜線指令沒有變動，略過同步。")
            return

        synced = await self.tree.sync(guild=guild)
        SYNC_HASH_FILE.write_text(fingerprint, encoding="utf-8")
        where = f"測試伺服器 {guild_id}" if guild else "全域"
        log.info("已同步 %d 個斜線指令到%s：%s", len(synced), where, ", ".join(c.name for c in synced))

    async def on_ready(self) -> None:
        log.info("已登入為 %s (ID: %s)", self.user, self.user.id if self.user else "?")

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """統一處理錯誤：使用者只看到友善訊息，詳細錯誤只寫在後台 log，不外洩內部資訊。"""
        original = getattr(error, "original", error)

        if isinstance(error, app_commands.CommandOnCooldown):
            msg = f"⏳ 你用得太快了，請 {error.retry_after:.1f} 秒後再試。"
        elif isinstance(original, DataError):
            log.error("資料錯誤（/%s）：%s", interaction.command and interaction.command.name, original)
            msg = f"❌ {original}，請通知管理員。"
        elif isinstance(error, app_commands.CheckFailure):
            msg = "🚫 你沒有權限使用這個指令。"
        else:
            log.exception(
                "指令 /%s 發生未預期錯誤",
                interaction.command and interaction.command.name,
                exc_info=original,
            )
            msg = "⚠️ 發生未預期的錯誤，請稍後再試。"

        try:
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except discord.HTTPException:
            pass
