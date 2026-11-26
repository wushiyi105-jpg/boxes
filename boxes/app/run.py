"""用例：体积与报价 → 中位挑档 → 改址进度 → 模型写清单说明。"""

from __future__ import annotations

import json

from ..adapters.llm import build_llm
from ..adapters.store import SqliteStore
from ..config import Settings
from ..domain.engine import address_progress, build, by_category
from ..domain.guard import check
from ..domain.models import Plan

PROMPT = """把给出的搬家清单写成四句以内，只能用输入里的数字。
不要估没算过的体积或价格。输出 JSON：{"text": "…"}"""


def plan(store: SqliteStore, floors: int = 1) -> Plan:
    return build(store.list_items(), store.list_quotes(), store.list_addresses(), floors)


def summary(store: SqliteStore, settings: Settings, floors: int = 1) -> tuple[str, list[str]]:
    p = plan(store, floors)
    if not settings.llm_enabled:
        return "", []
    facts = [f"体积 {p.volume}", f"重量 {p.weight}", f"件数 {p.pieces}", f"趟数 {p.trips}"]
    facts += [f"{line.company} {line.total}" for line in p.lines]
    llm = build_llm(settings.llm_base_url, settings.llm_api_key, settings.llm_model, PROMPT)
    try:
        data = json.loads(llm.write(PROMPT, "\n".join(facts)))
    except Exception:  # noqa: BLE001
        return "", []
    text = str(data.get("text", ""))
    return text, [f.message for f in check(text, facts)]


def sheet(store: SqliteStore, floors: int = 1) -> dict[str, object]:
    p = plan(store, floors)
    return {"volume": p.volume, "weight": p.weight, "pieces": p.pieces, "trips": p.trips,
            "lines": p.lines, "categories": by_category(store.list_items()),
            "addr": address_progress(store.list_addresses()), "penalty": p.penalty_total}
