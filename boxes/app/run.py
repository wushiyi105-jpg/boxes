"""用例：体积与报价 → 中位挑档 → 改址进度 → 模型写清单说明。"""

from __future__ import annotations

import json
from pathlib import Path

from ..config import Settings
from ..domain.engine import address_progress, build, by_category
from ..domain.guard import check
from ..domain.models import Plan
from ..ports import LLMPort, StorePort

PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "summary.md").read_text(encoding="utf-8")


def plan(store: StorePort, floors: int = 1) -> Plan:
    return build(store.list_items(), store.list_quotes(), store.list_addresses(), floors)


def summary(
    store: StorePort, settings: Settings, floors: int = 1, llm: LLMPort | None = None
) -> tuple[str, list[str]]:
    p = plan(store, floors)
    if llm is None:
        return "", []
    facts = [f"体积 {p.volume}", f"重量 {p.weight}", f"件数 {p.pieces}", f"趟数 {p.trips}"]
    facts += [f"{line.company} {line.total}" for line in p.lines]
    try:
        data = json.loads(llm.write(PROMPT, "\n".join(facts)))
    except Exception:  # noqa: BLE001
        return "", []
    text = str(data.get("text", ""))
    return text, [f.message for f in check(text, facts)]


def sheet(store: StorePort, floors: int = 1) -> dict[str, object]:
    p = plan(store, floors)
    return {"volume": p.volume, "weight": p.weight, "pieces": p.pieces, "trips": p.trips,
            "lines": p.lines, "categories": by_category(store.list_items()),
            "addr": address_progress(store.list_addresses()), "penalty": p.penalty_total}
