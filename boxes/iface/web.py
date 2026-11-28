"""FastAPI + Jinja2：体积表与报价对比。"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..adapters.store import SqliteStore
from ..app.run import plan, sheet
from ..config import Settings
from ..domain.engine import by_category
from ..domain.rules.address import missing

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))


def create_app(settings: Settings, store: SqliteStore | None = None) -> FastAPI:
    app = FastAPI(title="Boxes", version="1.0.0")
    app.mount(
        "/static",
        StaticFiles(directory=str(Path(__file__).resolve().parents[2] / "static")),
        name="static",
    )
    store = store or SqliteStore(settings.db_path)

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request, floors: int = 1) -> HTMLResponse:
        p = plan(store, floors)
        return TEMPLATES.TemplateResponse(
            request, "index.html",
            {"p": p, "cats": by_category(store.list_items()), "items": store.list_items(),
             "left": missing(store.list_addresses()), "addr": sheet(store, floors)["addr"], "floors": floors},
        )

    @app.post("/notify/{org}")
    def notify_org(org: str) -> dict[str, object]:
        return {"ok": store.notify(org)}

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "items": len(store.list_items())}

    return app


def app_factory(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        from ..config import settings as default_settings

        settings = default_settings
    return create_app(settings)

