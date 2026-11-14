"""讀取並驗證 JSON 資料。

- 依檔案修改時間快取：改 JSON 不用重開 bot，但也不會每次指令都重讀檔案。
- 嚴格驗證格式：避免壞掉 / 被竄改的資料讓 bot 崩潰或送出異常內容。
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Callable, TypeVar

from .config import DRINKS_FILE, RESTAURANTS_FILE

log = logging.getLogger(__name__)

MAX_FILE_BYTES = 1 * 1024 * 1024  # 資料檔超過 1MB 視為異常
MAX_NAME_LENGTH = 100
VALID_PRICE_LEVELS = {1, 2, 3}

T = TypeVar("T")


class DataError(Exception):
    """資料檔不存在或格式錯誤。訊息會顯示給使用者，所以不要放敏感資訊。"""


# path -> (mtime, 已驗證的資料)
_cache: dict[Path, tuple[float, Any]] = {}


def _load(path: Path, validate: Callable[[Any], T]) -> T:
    try:
        stat = path.stat()
    except FileNotFoundError:
        raise DataError(f"找不到資料檔 `{path.name}`") from None

    cached = _cache.get(path)
    if cached and cached[0] == stat.st_mtime:
        return cached[1]

    if stat.st_size > MAX_FILE_BYTES:
        raise DataError(f"資料檔 `{path.name}` 過大")

    try:
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        log.error("解析 %s 失敗：%s", path, e)
        raise DataError(f"資料檔 `{path.name}` 格式錯誤") from None

    data = validate(raw)
    _cache[path] = (stat.st_mtime, data)
    return data


def _clean_name(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    name = value.strip()
    if not name or len(name) > MAX_NAME_LENGTH:
        return None
    return name


def _validate_restaurants(raw: Any) -> dict[str, list[dict[str, Any]]]:
    if not isinstance(raw, dict):
        raise DataError("`restaurants.json` 最外層必須是物件")

    cleaned: dict[str, list[dict[str, Any]]] = {}
    for district, items in raw.items():
        if not isinstance(items, list):
            log.warning("restaurants.json：%s 不是陣列，已略過", district)
            continue
        valid = []
        for item in items:
            name = _clean_name(item.get("name")) if isinstance(item, dict) else None
            level = item.get("price_level", 1) if isinstance(item, dict) else None
            if name is None or level not in VALID_PRICE_LEVELS:
                log.warning("restaurants.json：略過格式錯誤的項目 %r", item)
                continue
            valid.append({"name": name, "price_level": level})
        cleaned[district] = valid
    return cleaned


def _validate_drinks(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        raise DataError("`drink.json` 最外層必須是陣列")

    cleaned = []
    for item in raw:
        name = _clean_name(item)
        if name is None:
            log.warning("drink.json：略過格式錯誤的項目 %r", item)
            continue
        cleaned.append(name)
    return cleaned


def load_restaurants() -> dict[str, list[dict[str, Any]]]:
    return _load(RESTAURANTS_FILE, _validate_restaurants)


def load_drinks() -> list[str]:
    return _load(DRINKS_FILE, _validate_drinks)
