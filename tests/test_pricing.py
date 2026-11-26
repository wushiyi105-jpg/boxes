from __future__ import annotations

import pytest

from boxes.domain.models import Quote
from boxes.domain.rules.pricing import check, compute, median


def test_volume_mode():
    line = compute(Quote(1, "甲", "按体积", 260), 5.0, 100.0, 50)
    assert line.total == 1300.0
    assert line.per_m3 == 260.0


def test_weight_mode():
    line = compute(Quote(1, "乙", "按重量", 1.6), 5.0, 300.0, 50)
    assert line.total == 480.0


def test_piece_mode_with_floor_fee():
    line = compute(Quote(1, "丙", "按件", 38, 0, 70), 5.0, 300.0, 10, floors=3)
    assert line.total == 38 * 10 + 70 * 3


def test_minimum_applies_and_notes():
    line = compute(Quote(1, "甲", "按体积", 100, 800), 2.0, 10.0, 5)
    assert line.total == 800.0
    assert "起步价" in line.note


def test_unknown_mode_raises():
    with pytest.raises(ValueError):
        compute(Quote(1, "x", "按时间", 10), 1.0, 1.0, 1)


def test_median_even():
    assert median([100, 200, 300, 400]) == 250.0


def test_outlier_above_thirty_percent():
    lines = [compute(Quote(1, "甲", "按体积", 100), 1.0, 1.0, 1),
             compute(Quote(2, "乙", "按体积", 120), 1.0, 1.0, 1),
             compute(Quote(3, "丙", "按体积", 200), 1.0, 1.0, 1)]
    findings = check(lines)
    assert findings[0].target == "丙"
