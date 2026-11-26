from __future__ import annotations

from boxes.domain.models import Item
from boxes.domain.rules.volume import check, total, trips, weight


def _items() -> list[Item]:
    return [Item(1, "书", "书", 100, 0.0025, 0.7), Item(2, "锅", "厨房", 10, 0.02, 1.0)]


def test_total_volume():
    assert total(_items()) == 0.45


def test_total_weight():
    assert weight(_items()) == 80.0


def test_single_trip_needs_no_flag():
    assert check(3.0) == []


def test_two_trips_flagged():
    findings = check(8.4)
    assert findings[0].rule_id == "volume.trip"
    assert "2 趟" in findings[0].message


def test_trips_rounds_up():
    assert trips(4.3) == 2
    assert trips(4.2) == 1


def test_zero_items_still_one_trip():
    assert trips(0.0) == 1


def test_item_volume_property():
    assert Item(1, "a", "b", 3, 0.5).volume == 1.5
