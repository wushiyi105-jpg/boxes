"""命令行：seed / plan / notify / note / doctor / serve。"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from ..adapters.store import SqliteStore
from ..app.run import plan, sheet, summary
from ..config import Settings
from ..config import settings as default_settings
from ..doctor import main as doctor_main
from ..domain.rules.address import missing

app = typer.Typer(help="搬家清单：多少立方、几家没改址", no_args_is_help=True)
console = Console()


def _settings(db: Path | None, port: int | None = None) -> Settings:
    s = default_settings.model_copy(deep=True)
    if db:
        s.db_path = db
    if port:
        s.port = port
    return s


def _store(settings: Settings) -> SqliteStore:
    return SqliteStore(settings.db_path)


@app.command()
def seed(db: Path = typer.Option(None)) -> None:
    """写入物品、报价、机构清单。"""
    s = _settings(db)
    store = _store(s)
    data = json.loads(
        (Path(__file__).resolve().parents[2] / "data" / "seed.json").read_text(encoding="utf-8")
    )
    for it in data["items"]:
        store.add_item(it["name"], it["category"], it["qty"], it["volume"], it.get("weight", 0.0))
    for q in data["quotes"]:
        store.add_quote(q["company"], q["mode"], q["rate"], q.get("minimum", 0.0), q.get("floor_fee", 0.0))
    for a in data["addresses"]:
        store.add_address(a["org"], a.get("notified", False))
    console.print(f"已写入 {len(data['items'])} 类物品、{len(data['quotes'])} 份报价、{len(data['addresses'])} 家机构")


@app.command("plan")
def plan_cmd(floors: int = typer.Option(1), db: Path = typer.Option(None)) -> None:
    """体积、趟数、三档报价、扣分。"""
    store = _store(_settings(db))
    p = plan(store, floors)
    console.print(f"体积 {p.volume:g} 立方 · 重量 {p.weight:g} 公斤 · {p.pieces} 件 · {p.trips} 趟")
    for line in p.lines:
        console.print(f"  {line.company}（{line.mode}）：{line.total:,.0f} 元，折 {line.per_m3:,.0f} 元/立方 {line.note}")
    for f in p.findings:
        console.print(f"  [yellow]{f.rule_id}[/] -{f.penalty} {f.message}")
    console.print(f"合计扣 {p.penalty_total} 分")




@app.command()
def notify(org: str = typer.Option(..., help="机构名"), db: Path = typer.Option(None)) -> None:
    """勾掉一家已改址。"""
    store = _store(_settings(db))
    console.print("已勾" if store.notify(org) else "没有这家")


@app.command()
def note(floors: int = typer.Option(1), db: Path = typer.Option(None)) -> None:
    """模型写清单说明（无 key 时不编）。"""
    s = _settings(db)
    text, notes = summary(_store(s), s, floors)
    if text:
        console.print(text)
    for n in notes:
        console.print(f"  [yellow]{n}[/]")
    if not text:
        console.print(sheet(_store(s), floors))


@app.command()
def todo(db: Path = typer.Option(None)) -> None:
    """还没改址的机构。"""
    store = _store(_settings(db))
    rows = missing(store.list_addresses())
    console.print(f"还有 {len(rows)} 家：" + "、".join(rows[:8]))


@app.command()
def doctor(db: Path = typer.Option(None)) -> None:
    """四项体检。"""
    raise typer.Exit(code=doctor_main(_settings(db)))


@app.command()
def serve(port: int = typer.Option(None), db: Path = typer.Option(None)) -> None:
    """Web 界面。"""
    import uvicorn

    from .web import create_app

    s = _settings(db, port)
    uvicorn.run(create_app(s), host="127.0.0.1", port=s.port)


if __name__ == "__main__":
    app()
