"""Tests für scripts/validate.py."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("validate", ROOT / "scripts" / "validate.py")
validate = importlib.util.module_from_spec(_spec)
sys.modules["validate"] = validate
_spec.loader.exec_module(validate)

GUELTIG = """---
typ: gotcha
titel: Ein gültiger Testeintrag
beschreibung: Relevant für Tests des Validators.
tech: [python]
tags: [test]
kunde: wbai
projekt: bravo-proto
quelle: https://example.com/quelle
gueltig_bis: {datum}
---

Inhalt.
"""


def _schreibe(wurzel: Path, rel: str, text: str) -> Path:
    pfad = wurzel / rel
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(text, encoding="utf-8")
    return pfad


def _fehler(wurzel: Path) -> list[str]:
    return [m for e in validate.validiere(wurzel) for m in e.fehler]


def test_repo_eintraege_sind_gueltig() -> None:
    ergebnisse = validate.validiere()
    assert 3 <= len(ergebnisse) <= 5
    assert all(not e.fehler for e in ergebnisse), [(e.id, e.fehler) for e in ergebnisse]


def test_repo_hat_genau_einen_abgelaufenen_eintrag() -> None:
    abgelaufen = [e for e in validate.validiere() if e.ist_abgelaufen(dt.date(2026, 11, 24))]
    assert [e.id for e in abgelaufen] == ["learning/pydantic-v1-kompatibilitaet"]


@pytest.mark.parametrize("datum", ["2027-01-01", '"2027-01-01"'])
def test_gueltiger_eintrag(tmp_path: Path, datum: str) -> None:
    _schreibe(tmp_path, "gotcha/gueltig.md", GUELTIG.format(datum=datum))
    assert _fehler(tmp_path) == []


@pytest.mark.parametrize(
    ("ersetzen", "erwartet"),
    [
        (("kunde: wbai", "kunde: acme"), "kunde muss"),
        (("typ: gotcha", "typ: muster"), "passt nicht zum Ordner"),
        (("tech: [python]", "tech: []"), "Schema: tech"),
        (("quelle: https://", "quelle: http://"), "Schema: quelle"),
        (("projekt: bravo-proto\n", ""), "'projekt' is a required property"),
        (("tags: [test]", "tags: [test]\nextra: x"), "Additional properties"),
    ],
)
def test_ungueltige_eintraege(tmp_path: Path, ersetzen: tuple[str, str], erwartet: str) -> None:
    text = GUELTIG.format(datum="2027-01-01").replace(*ersetzen)
    _schreibe(tmp_path, "gotcha/kaputt.md", text)
    assert any(erwartet in m for m in _fehler(tmp_path)), _fehler(tmp_path)


def test_ungueltiges_datum(tmp_path: Path) -> None:
    _schreibe(tmp_path, "gotcha/datum.md", GUELTIG.format(datum='"2027-13-01"'))
    assert any("gueltig_bis" in m for m in _fehler(tmp_path))


def test_fehlablage_und_slug(tmp_path: Path) -> None:
    _schreibe(tmp_path, "gotcha/Gross_Schreibung.md", GUELTIG.format(datum="2027-01-01"))
    _schreibe(tmp_path, "lose.md", GUELTIG.format(datum="2027-01-01"))
    fehler = _fehler(tmp_path)
    assert any("kebab-case" in m for m in fehler)
    assert any("eintraege/<typ>/<slug>.md" in m for m in fehler)


def test_ohne_frontmatter_und_leerer_inhalt(tmp_path: Path) -> None:
    _schreibe(tmp_path, "gotcha/ohne.md", "nur text\n")
    _schreibe(tmp_path, "gotcha/leer.md", GUELTIG.format(datum="2027-01-01").replace("Inhalt.", ""))
    fehler = _fehler(tmp_path)
    assert any("kein YAML-Frontmatter" in m for m in fehler)
    assert any("Inhalt" in m for m in fehler)


def test_cli_abgelaufen_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _schreibe(tmp_path, "gotcha/alt.md", GUELTIG.format(datum="2020-01-01"))
    _schreibe(tmp_path, "gotcha/neu.md", GUELTIG.format(datum="2099-01-01"))
    code = validate.main(
        ["--wurzel", str(tmp_path), "--abgelaufen", "--json", "--heute", "2026-11-24"]
    )
    assert code == 0
    daten = json.loads(capsys.readouterr().out)
    assert [d["id"] for d in daten] == ["gotcha/alt"]


def test_cli_exit_code(tmp_path: Path) -> None:
    _schreibe(tmp_path, "gotcha/ok.md", GUELTIG.format(datum="2027-01-01"))
    assert validate.main(["--wurzel", str(tmp_path)]) == 0
    _schreibe(tmp_path, "gotcha/kaputt.md", "kaputt\n")
    assert validate.main(["--wurzel", str(tmp_path)]) == 1
