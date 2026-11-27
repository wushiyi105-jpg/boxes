"""搬家报价：车型、10 条加价套路、改址勾选。"""

from __future__ import annotations

from pathlib import Path

from boxes.adapters.store import SqliteStore
from boxes.app.quote import build_quote
from boxes.app.run import plan


def _store(tmp_path: Path) -> SqliteStore:
    store = SqliteStore(tmp_path / "b.db")
    store.add_item("书", "书", 60, 0.0025, 0.7)
    store.add_item("床垫", "家具", 1, 0.45, 28)
    store.add_quote("A", "按体积", 260, 800, 0)
    store.add_quote("B", "按重量", 1.6, 500, 0)
    store.add_quote("C", "按件", 12, 400, 70)
    store.add_address("税务局", False)
    store.add_address("物业", True)
    return store


def test_quote_has_vehicle_and_surcharges(tmp_path) -> None:
    store = _store(tmp_path)
    p = plan(store, 2)
    text = build_quote(p, store.list_addresses(), 2)
    assert "车型建议" in text
    assert "10 条加价套路" in text
    assert text.count("| ") >= 10
    assert "改地址清单" in text
    assert "- [ ] 税务局" in text
    assert "- [x] 物业" in text


def test_quote_median_and_outlier(tmp_path) -> None:
    store = _store(tmp_path)
    p = plan(store, 1)
    text = build_quote(p, store.list_addresses(), 1)
    assert "三家中位" in text
    assert "相对中位" in text
