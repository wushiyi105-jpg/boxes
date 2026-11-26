"""改址清单：22 家机构逐个勾，没勾的报出来。"""

from __future__ import annotations

from ..models import Address, Finding

PENALTY = 4


def missing(rows: list[Address]) -> list[str]:
    return [a.org for a in rows if not a.notified]


def check(rows: list[Address]) -> list[Finding]:
    out: list[Finding] = []
    for org in missing(rows):
        out.append(Finding("addr.missing", f"{org} 还没改地址", PENALTY, org))
    return out


def progress(rows: list[Address]) -> float:
    return sum(1 for a in rows if a.notified) / len(rows) if rows else 1.0
