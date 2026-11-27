"""车型容量与 10 条加价套路。"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parents[2] / "data"


@lru_cache(maxsize=1)
def _data() -> dict[str, Any]:
    return json.loads((DATA / "seed.json").read_text(encoding="utf-8"))


def trucks() -> list[dict[str, Any]]:
    return sorted(_data()["trucks"], key=lambda x: x["m3"])


def surcharges() -> list[dict[str, str]]:
    return list(_data()["surcharges"])


def vehicle_for(volume: float) -> dict[str, Any]:
    for t in trucks():
        if t["m3"] >= volume:
            return t
    return trucks()[-1]
