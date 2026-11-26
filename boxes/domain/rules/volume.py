"""体积：按类目单件体积估，超一车要跑几趟。"""

from __future__ import annotations

from math import ceil

from ..models import VAN_M3, Finding, Item

PENALTY = 3


def total(items: list[Item]) -> float:
    return round(sum(i.volume for i in items), 2)


def weight(items: list[Item]) -> float:
    return round(sum(i.weight for i in items), 2)


def trips(volume: float) -> int:
    return max(1, ceil(volume / VAN_M3))


def check(volume: float) -> list[Finding]:
    n = trips(volume)
    if n <= 1:
        return []
    return [
        Finding(
            "volume.trip",
            f"合计 {volume:g} 立方，超过一车 {VAN_M3:g} 立方，要跑 {n} 趟",
            PENALTY,
            "trips",
        )
    ]
