"""三种计价归一：按体积、按重量、按件，统一折成总额与每立方价。"""

from __future__ import annotations

from ..models import Finding, Line, Quote

PENALTY = 5


def compute(q: Quote, volume: float, weight: float, pieces: int, floors: int = 1) -> Line:
    if q.mode == "按体积":
        raw = q.rate * volume
    elif q.mode == "按重量":
        raw = q.rate * weight
    elif q.mode == "按件":
        raw = q.rate * pieces + q.floor_fee * max(0, floors)
    else:
        raise ValueError(f"没有这种计价：{q.mode}")
    total = round(max(raw, q.minimum), 2)
    note = "低于起步价，按起步价算" if raw < q.minimum else ""
    per_m3 = round(total / volume, 2) if volume else 0.0
    return Line(q.company, q.mode, total, per_m3, note)


def median(values: list[float]) -> float:
    s = sorted(values)
    n = len(s)
    if n == 0:
        return 0.0
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def check(lines: list[Line]) -> list[Finding]:
    if len(lines) < 2:
        return []
    med = median([x.total for x in lines])
    out: list[Finding] = []
    for line in lines:
        if med and (line.total - med) / med > 0.30:
            out.append(
                Finding(
                    "quote.outlier",
                    f"{line.company} 报 {line.total:,.0f}，比中位 {med:,.0f} 高 {(line.total - med) / med:.0%}",
                    PENALTY,
                    line.company,
                )
            )
    return out
