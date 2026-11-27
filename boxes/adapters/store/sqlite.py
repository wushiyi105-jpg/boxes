"""SQLite：items / quotes / addresses / jobs。"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Boolean, Float, Integer, String, inspect, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker
from sqlalchemy.orm import Session as OrmSession

from ...domain.models import Address, Item, Quote
from .base import Base, make_engine, make_session


class ItemRow(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    category: Mapped[str] = mapped_column(String(20))
    qty: Mapped[int] = mapped_column(Integer, default=1)
    volume_each: Mapped[float] = mapped_column(Float, default=0.0)
    weight_each: Mapped[float] = mapped_column(Float, default=0.0)


class QuoteRow(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company: Mapped[str] = mapped_column(String(40))
    mode: Mapped[str] = mapped_column(String(10))
    rate: Mapped[float] = mapped_column(Float)
    minimum: Mapped[float] = mapped_column(Float, default=0.0)
    floor_fee: Mapped[float] = mapped_column(Float, default=0.0)


class AddrRow(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org: Mapped[str] = mapped_column(String(60))
    notified: Mapped[bool] = mapped_column(Boolean, default=False)


class JobRow(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    idem_key: Mapped[str] = mapped_column(String(80), unique=True)


def _upgrade_schema(engine) -> None:
    root = next(p for p in Path(__file__).resolve().parents if (p / "alembic.ini").exists())
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("script_location", str(root / "migrations"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{engine.url.database}")
    command.upgrade(cfg, "head")


class SqliteStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.engine = make_engine(self.path)
        self.session: sessionmaker[OrmSession] = make_session(self.engine)
        self.init_schema()

    def init_schema(self) -> None:
        _upgrade_schema(self.engine)

    def schema_ok(self) -> bool:
        return {"items", "quotes", "addresses", "jobs"} <= set(inspect(self.engine).get_table_names())

    def summary(self) -> str:
        return f"{len(self.list_items())} 类物品、{len(self.list_quotes())} 份报价、{len(self.list_addresses())} 家机构"

    def add_item(self, name: str, category: str, qty: int, volume_each: float, weight_each: float = 0.0) -> int:
        if qty <= 0 or volume_each <= 0:
            raise ValueError("数量与单件体积都要大于 0")
        with self.session() as s:
            row = ItemRow(name=name, category=category, qty=qty, volume_each=volume_each, weight_each=weight_each)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_items(self) -> list[Item]:
        with self.session() as s:
            rows = s.scalars(select(ItemRow)).all()
        return [Item(r.id, r.name, r.category, r.qty, float(r.volume_each), float(r.weight_each)) for r in rows]

    def add_quote(self, company: str, mode: str, rate: float, minimum: float = 0.0, floor_fee: float = 0.0) -> int:
        if mode not in ("按体积", "按重量", "按件"):
            raise ValueError(f"没有这种计价：{mode}")
        if rate <= 0:
            raise ValueError("单价要大于 0")
        with self.session() as s:
            row = QuoteRow(company=company, mode=mode, rate=rate, minimum=minimum, floor_fee=floor_fee)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_quotes(self) -> list[Quote]:
        with self.session() as s:
            rows = s.scalars(select(QuoteRow)).all()
        return [Quote(r.id, r.company, r.mode, float(r.rate), float(r.minimum), float(r.floor_fee)) for r in rows]

    def add_address(self, org: str, notified: bool = False) -> int:
        with self.session() as s:
            row = AddrRow(org=org, notified=notified)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_addresses(self) -> list[Address]:
        with self.session() as s:
            rows = s.scalars(select(AddrRow)).all()
        return [Address(r.id, r.org, r.notified) for r in rows]

    def notify(self, org: str) -> bool:
        with self.session() as s:
            row = s.scalars(select(AddrRow).where(AddrRow.org == org)).first()
            if row is None:
                return False
            row.notified = True
            s.commit()
            return True
