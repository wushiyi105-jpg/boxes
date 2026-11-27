"""真实内存 Store 跑 plan：不建 SQLite，mypy 校验 StorePort。"""

from __future__ import annotations

from boxes.app.run import plan
from boxes.domain.models import Address, Item, Quote
from boxes.ports import StorePort


class InMemoryStore:
    def list_items(self) -> list[Item]:
        return []

    def list_quotes(self) -> list[Quote]:
        return []

    def list_addresses(self) -> list[Address]:
        return []


def test_plan_with_memory_store() -> None:
    store: StorePort = InMemoryStore()
    out = plan(store, 1)
    assert out.volume == 0.0
