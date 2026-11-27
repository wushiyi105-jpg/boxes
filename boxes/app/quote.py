"""搬家成文：车型、三家报价归一、加价套路、可勾选改址清单。"""

from __future__ import annotations

from ..domain.catalog import surcharges, vehicle_for
from ..domain.models import Address, Plan
from ..domain.rules.pricing import median


def build_quote(plan: Plan, addresses: list[Address], floors: int = 1) -> str:
    vehicle = vehicle_for(plan.volume)
    trips_on_vehicle = max(1, int(-(-plan.volume // vehicle["m3"])))
    med = median([x.total for x in plan.lines])
    lines = [
        "# 搬家报价对比",
        "",
        f"> 体积 {plan.volume:g} 立方、{plan.weight:g} 公斤、{plan.pieces} 件；楼层 {floors} 层。"
        "所有金额为本地报价归一，不含未写进合同的附加费。",
        "",
        "## 一、车型建议",
        "",
        f"- 推荐 **{vehicle['name']}**（{vehicle['m3']:g} 立方，{vehicle['note']}），按体积算 {trips_on_vehicle} 趟。",
        f"- 若用最小面包车（4.2 立方），要 {plan.trips} 趟；每多一趟就多一次装卸和楼层费。",
        "- 判断口径：体积只算物品，不含拆装和通道占用；大件家具先量再定。",
        "",
        "## 二、三家报价归一",
        "",
        "| 公司 | 计价方式 | 归一总价 | 每立方 | 相对中位 | 备注 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for line in plan.lines:
        diff = f"{(line.total - med) / med:+.0%}" if med else "—"
        lines.append(
            f"| {line.company} | {line.mode} | {line.total:,.0f} | {line.per_m3:,.0f} | {diff} | {line.note or '—'} |"
        )
    if med:
        lines += ["", f"三家中位 **{med:,.0f} 元**。低于中位 30% 的先问清缺了什么项，不要直接定。"]
    high = [f for f in plan.findings if f.rule_id == "quote.outlier"]
    if high:
        lines += ["", "### 明显高于中位"]
        lines += [f"- {f.message}" for f in high]

    lines += [
        "",
        "## 三、10 条加价套路（签合同前逐条问）",
        "",
        "| # | 加价项 | 要问清的那句话 |",
        "| --- | --- | --- |",
    ]
    for i, s in enumerate(surcharges(), 1):
        lines.append(f"| {i} | {s['name']} | {s['ask']} |")

    lines += ["", "## 四、改地址清单（可勾选）", ""]
    left = 0
    for a in addresses:
        box = "x" if a.notified else " "
        if not a.notified:
            left += 1
        lines.append(f"- [{box}] {a.org}")
    lines += [
        "",
        f"还有 **{left}** 家没改，共 {len(addresses)} 家。改完一家跑 `boxes notify --org 机构名`。",
        "",
        "---",
        "",
        f"本地核算：{len(plan.lines)} 份报价、{len(addresses)} 家机构、扣分 {plan.penalty_total}。"
        "费用只作比价，最终以合同写明的总价为准。",
        "",
    ]
    return "\n".join(lines)
