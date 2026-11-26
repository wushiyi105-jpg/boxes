"""领域对象：物品、报价、改址清单。"""

from __future__ import annotations

from dataclasses import dataclass, field

VAN_M3 = 4.2


@dataclass(frozen=True)
class Item:
    id: int
    name: str
    category: str
    qty: int
    volume_each: float
    weight_each: float = 0.0

    @property
    def volume(self) -> float:
        return round(self.qty * self.volume_each, 3)

    @property
    def weight(self) -> float:
        return round(self.qty * self.weight_each, 2)


@dataclass(frozen=True)
class Quote:
    id: int
    company: str
    mode: str
    rate: float
    minimum: float = 0.0
    floor_fee: float = 0.0


@dataclass(frozen=True)
class Address:
    id: int
    org: str
    notified: bool = False


@dataclass
class Finding:
    rule_id: str
    message: str
    penalty: int
    target: str = ""


@dataclass
class Line:
    company: str
    mode: str
    total: float
    per_m3: float
    note: str = ""


@dataclass
class Plan:
    volume: float = 0.0
    weight: float = 0.0
    pieces: int = 0
    trips: int = 1
    lines: list[Line] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    @property
    def penalty_total(self) -> int:
        return sum(f.penalty for f in self.findings)

    @property
    def cheapest(self) -> Line | None:
        return min(self.lines, key=lambda x: x.total) if self.lines else None
