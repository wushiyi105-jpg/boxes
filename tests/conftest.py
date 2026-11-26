from __future__ import annotations

import pytest

from boxes.adapters.store import SqliteStore
from boxes.config import Settings


@pytest.fixture()
def store(tmp_path) -> SqliteStore:
    return SqliteStore(tmp_path / "t.db")


@pytest.fixture()
def settings(tmp_path) -> Settings:
    return Settings(db_path=tmp_path / "t.db", llm_api_key="", port=8010)
