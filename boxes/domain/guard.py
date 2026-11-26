"""数字守卫：模型写的数要能在清单里对上。"""

from __future__ import annotations

import re

from .models import Finding

PENALTY = 8
NUM = re.compile(r"(\d+(?:\.\d+)?)")


def _norm(s: str) -> str:
    return s.rstrip("0").rstrip(".") if "." in s else s


def check(text: str, facts: list[str]) -> list[Finding]:
    ok: set[str] = set()
    for f in facts:
        for m in NUM.findall(f):
            ok.add(m)
            ok.add(_norm(m))
    bad = [n for n in NUM.findall(text) if n not in ok and _norm(n) not in ok]
    if not bad:
        return []
    return [Finding("guard.number", f"清单里没有 {'、'.join(sorted(set(bad)))}，删掉这句", PENALTY, "summary")]
