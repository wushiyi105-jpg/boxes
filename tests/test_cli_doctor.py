from __future__ import annotations

from typer.testing import CliRunner

from boxes.doctor import run_doctor
from boxes.iface.cli import app


def test_cli_plan_empty(tmp_path):
    runner = CliRunner()
    assert runner.invoke(app, ["plan", "--db", str(tmp_path / "c.db")]).exit_code == 0


def test_cli_notify_unknown(tmp_path):
    runner = CliRunner()
    res = runner.invoke(app, ["notify", "--org", "税务局", "--db", str(tmp_path / "d.db")])
    assert res.exit_code == 0
    assert "没有这家" in res.stdout


def test_cli_todo_empty(tmp_path):
    runner = CliRunner()
    res = runner.invoke(app, ["todo", "--db", str(tmp_path / "e.db")])
    assert res.exit_code == 0


def test_doctor_green(settings):
    checks, ok = run_doctor(settings)
    assert ok is True
