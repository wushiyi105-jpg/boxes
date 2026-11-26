"""本地核算：体积 → 趟数 → 三档报价 → 中位比较 → 改址缺口。"""

from __future__ import annotations

from .models import Address, Finding, Item, Plan, Quote
from .rules.address import check as addr_check
from .rules.address import progress
from .rules.pricing import check as price_check
from .rules.pricing import compute
from .rules.volume import check as trip_check
from .rules.volume import total, trips, weight


def build(items: list[Item], quotes: list[Quote], addresses: list[Address], floors: int = 1) -> Plan:
    p = Plan()
    p.volume = total(items)
    p.weight = weight(items)
    p.pieces = sum(i.qty for i in items)
    p.trips = trips(p.volume)
    findings: list[Finding] = []
    findings += trip_check(p.volume)
    p.lines = [compute(q, p.volume, p.weight, p.pieces, floors) for q in quotes]
    findings += price_check(p.lines)
    findings += addr_check(addresses)
    p.findings = findings
    return p


def by_category(items: list[Item]) -> dict[str, float]:
    out: dict[str, float] = {}
    for i in items:
        out[i.category] = round(out.get(i.category, 0.0) + i.volume, 2)
    return out


def address_progress(rows: list[Address]) -> float:
    return progress(rows)


def cheapest(plan: Plan) -> str:
    return plan.cheapest.company if plan.cheapest else ""
