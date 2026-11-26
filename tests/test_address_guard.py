from __future__ import annotations

from boxes.domain.guard import check
from boxes.domain.models import Address
from boxes.domain.rules.address import check as a_check
from boxes.domain.rules.address import missing, progress


def test_missing_lists_unnotified():
    rows = [Address(1, "移动", True), Address(2, "税务", False)]
    assert missing(rows) == ["税务"]


def test_each_missing_flagged():
    findings = a_check([Address(1, "a", False), Address(2, "b", False)])
    assert len(findings) == 2
    assert findings[0].penalty == 4


def test_all_notified_clean():
    assert a_check([Address(1, "a", True)]) == []


def test_progress_ratio():
    assert progress([Address(1, "a", True), Address(2, "b", False)]) == 0.5


def test_progress_empty_is_one():
    assert progress([]) == 1.0


def test_guard_number_from_facts():
    assert check("一共 5.5 立方", ["体积 5.5"]) == []


def test_guard_flags_invented():
    findings = check("一共 7 立方", ["体积 5.5"])
    assert findings[0].rule_id == "guard.number"
