"""端口：app 实际调用的方法集合，实现见 adapters。"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..domain.models import Address, Item, Quote


@runtime_checkable
class StorePort(Protocol):
    def list_items(self) -> list[Item]: ...

    def list_quotes(self) -> list[Quote]: ...

    def list_addresses(self) -> list[Address]: ...


@runtime_checkable
class LLMPort(Protocol):
    def write(self, system: str, facts: str) -> str: ...
