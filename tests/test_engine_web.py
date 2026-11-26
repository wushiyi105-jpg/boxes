from __future__ import annotations

from fastapi.testclient import TestClient

from boxes.adapters.store import SqliteStore
from boxes.domain.engine import address_progress, build, by_category, cheapest
from boxes.domain.models import Address, Item, Quote
from boxes.iface.web import create_app


def _rows() -> tuple[list[Item], list[Quote], list[Address]]:
    items = [Item(1, "书", "书", 100, 0.0025, 0.7), Item(2, "锅", "厨房", 10, 0.02, 1.0)]
    quotes = [Quote(1, "甲", "按体积", 260, 800), Quote(2, "乙", "按重量", 1.6, 500)]
    addrs = [Address(1, "移动", True), Address(2, "税务", False)]
    return items, quotes, addrs


def test_build_totals():
    items, quotes, addrs = _rows()
    p = build(items, quotes, addrs)
    assert p.volume == 0.45
    assert p.pieces == 110
    assert p.trips == 1


def test_build_cheapest():
    items, quotes, addrs = _rows()
    p = build(items, quotes, addrs)
    assert cheapest(p) in {"甲", "乙"}


def test_by_category_sums():
    items, _, _ = _rows()
    assert by_category(items)["书"] == 0.25


def test_address_progress_via_build():
    items, quotes, addrs = _rows()
    assert address_progress(addrs) == 0.5


def _seed(store: SqliteStore):
    store.add_item("书", "书", 100, 0.0025, 0.7)
    store.add_quote("甲", "按体积", 260, 800)
    store.add_quote("乙", "按重量", 1.6, 500)
    store.add_address("税务", False)


def test_index(store, settings):
    _seed(store)
    client = TestClient(create_app(settings, store))
    body = client.get("/").text
    assert client.get("/").status_code == 200
    assert "报价归一" in body
