"""Validiert alle Wissenseinträge gegen schema/eintrag.schema.json.

Prüft je Datei unter ``eintraege/<typ>/<slug>.md``:

* YAML-Frontmatter vorhanden und gegen das JSON-Schema gültig,
* ``typ`` entspricht dem Ordnernamen,
* Slug ist kebab-case,
* ``kunde`` ist ``wbai`` (Prototyp-Regel, Repo ist öffentlich),
* Inhalt unter dem Frontmatter ist nicht leer.

Abgelaufene Einträge (``gueltig_bis`` < heute) sind kein Fehler; sie werden gemeldet und
lassen sich mit ``--abgelaufen`` als Liste ausgeben (für die Wissenspflege).

Beispiel:
    python scripts/validate.py
    python scripts/validate.py --abgelaufen --json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

LOG = logging.getLogger("validate")

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "eintrag.schema.json"
EINTRAEGE_DIR = REPO_ROOT / "eintraege"
ERLAUBTER_KUNDE = "wbai"
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)


class _StringDateLoader(yaml.SafeLoader):
    """SafeLoader, der Datumswerte als String belässt (das Schema erwartet Strings)."""


_StringDateLoader.yaml_implicit_resolvers = {
    key: [(tag, regex) for tag, regex in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


@dataclass
class Eintrag:
    """Ein geparster Wissenseintrag.

    Attributes:
        pfad: Pfad zur Markdown-Datei.
        frontmatter: Geparstes Frontmatter (leer, wenn nicht lesbar).
        inhalt: Markdown-Inhalt unter dem Frontmatter.
        fehler: Gefundene Validierungsfehler.
    """

    pfad: Path
    frontmatter: dict = field(default_factory=dict)
    inhalt: str = ""
    fehler: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        """Eintrags-ID ``<typ>/<slug>``, aus dem Pfad abgeleitet."""
        return f"{self.pfad.parent.name}/{self.pfad.stem}"

    def ist_abgelaufen(self, heute: dt.date) -> bool:
        """Gibt zurück, ob ``gueltig_bis`` vor ``heute`` liegt.

        Args:
            heute: Stichtag.

        Returns:
            True, wenn der Eintrag abgelaufen ist; False auch bei ungültigem Datum.
        """
        try:
            return dt.date.fromisoformat(str(self.frontmatter.get("gueltig_bis"))) < heute
        except ValueError:
            return False


def lade_schema(pfad: Path = SCHEMA_PATH) -> Draft202012Validator:
    """Lädt das eingefrorene Schema als Validator.

    Args:
        pfad: Pfad zur Schema-Datei.

    Returns:
        Validator mit Format-Prüfung (u. a. ``date``).
    """
    schema = json.loads(pfad.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def parse_eintrag(pfad: Path) -> Eintrag:
    """Liest Frontmatter und Inhalt einer Eintragsdatei.

    Args:
        pfad: Pfad zur Markdown-Datei.

    Returns:
        Eintrag; Parse-Fehler stehen in ``fehler``.
    """
    eintrag = Eintrag(pfad=pfad)
    text = pfad.read_text(encoding="utf-8")
    treffer = FRONTMATTER_RE.match(text)
    if not treffer:
        eintrag.fehler.append("kein YAML-Frontmatter zwischen '---'-Zeilen am Dateianfang")
        return eintrag
    try:
        daten = yaml.load(treffer.group(1), Loader=_StringDateLoader)  # noqa: S506
    except yaml.YAMLError as exc:
        eintrag.fehler.append(f"Frontmatter ist kein gültiges YAML: {exc}")
        return eintrag
    if not isinstance(daten, dict):
        eintrag.fehler.append("Frontmatter muss ein YAML-Objekt sein")
        return eintrag
    eintrag.frontmatter = daten
    eintrag.inhalt = treffer.group(2)
    return eintrag


def pruefe_eintrag(eintrag: Eintrag, validator: Draft202012Validator) -> None:
    """Prüft einen geparsten Eintrag und ergänzt ``eintrag.fehler``.

    Args:
        eintrag: Geparster Eintrag.
        validator: Schema-Validator.
    """
    if eintrag.fehler:
        return
    fm = eintrag.frontmatter
    for err in sorted(validator.iter_errors(fm), key=lambda e: list(e.absolute_path)):
        ort = "/".join(str(p) for p in err.absolute_path) or "<root>"
        eintrag.fehler.append(f"Schema: {ort}: {err.message}")
    if fm.get("typ") != eintrag.pfad.parent.name:
        eintrag.fehler.append(
            f"typ '{fm.get('typ')}' passt nicht zum Ordner '{eintrag.pfad.parent.name}'"
        )
    if not SLUG_RE.match(eintrag.pfad.stem):
        eintrag.fehler.append(f"Slug '{eintrag.pfad.stem}' ist nicht kebab-case")
    if fm.get("kunde") != ERLAUBTER_KUNDE:
        eintrag.fehler.append(
            f"kunde muss im Prototyp '{ERLAUBTER_KUNDE}' sein (öffentliches Repo), "
            f"gefunden: '{fm.get('kunde')}'"
        )
    if not eintrag.inhalt.strip():
        eintrag.fehler.append("Inhalt unter dem Frontmatter ist leer")


def finde_dateien(wurzel: Path) -> tuple[list[Path], list[str]]:
    """Sammelt Eintragsdateien und meldet falsch abgelegte Dateien.

    Args:
        wurzel: Verzeichnis ``eintraege/``.

    Returns:
        Tupel aus gültigen Eintragspfaden und Fehlermeldungen für Fehlablagen.
    """
    dateien: list[Path] = []
    fehler: list[str] = []
    if not wurzel.is_dir():
        return dateien, [f"Verzeichnis fehlt: {wurzel}"]
    for pfad in sorted(wurzel.rglob("*")):
        if pfad.is_dir() or pfad.name == ".gitkeep":
            continue
        rel = pfad.relative_to(wurzel)
        if pfad.suffix != ".md" or len(rel.parts) != 2:
            fehler.append(f"{rel}: Einträge liegen als eintraege/<typ>/<slug>.md")
            continue
        dateien.append(pfad)
    return dateien, fehler


def validiere(wurzel: Path = EINTRAEGE_DIR, schema_pfad: Path = SCHEMA_PATH) -> list[Eintrag]:
    """Parst und prüft alle Einträge unterhalb von ``wurzel``.

    Args:
        wurzel: Verzeichnis ``eintraege/``.
        schema_pfad: Pfad zum Schema.

    Returns:
        Liste aller Einträge inkl. Fehlern. Fehlablagen erscheinen als Eintrag mit Fehler.
    """
    validator = lade_schema(schema_pfad)
    dateien, ablagefehler = finde_dateien(wurzel)
    ergebnisse: list[Eintrag] = []
    for meldung in ablagefehler:
        ergebnisse.append(Eintrag(pfad=wurzel / meldung.split(":")[0], fehler=[meldung]))
    for pfad in dateien:
        eintrag = parse_eintrag(pfad)
        pruefe_eintrag(eintrag, validator)
        ergebnisse.append(eintrag)
    return ergebnisse


def main(argv: list[str] | None = None) -> int:
    """CLI-Einstieg.

    Args:
        argv: Argumente (Standard: ``sys.argv[1:]``).

    Returns:
        Exit-Code: 0 bei gültigen Einträgen, 1 bei Fehlern.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--wurzel", type=Path, default=EINTRAEGE_DIR)
    parser.add_argument("--heute", type=dt.date.fromisoformat, default=dt.date.today())
    parser.add_argument(
        "--abgelaufen", action="store_true", help="nur abgelaufene Einträge ausgeben"
    )
    parser.add_argument("--json", action="store_true", help="Ausgabe als JSON auf stdout")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s", stream=sys.stderr)

    ergebnisse = validiere(args.wurzel)
    abgelaufen = [e for e in ergebnisse if not e.fehler and e.ist_abgelaufen(args.heute)]

    if args.abgelaufen:
        daten = [
            {
                "id": e.id,
                "pfad": os.path.relpath(e.pfad),
                "gueltig_bis": e.frontmatter["gueltig_bis"],
            }
            for e in abgelaufen
        ]
        if args.json:
            sys.stdout.write(json.dumps(daten, ensure_ascii=False) + "\n")
        else:
            for d in daten:
                LOG.info("abgelaufen: %s (gueltig_bis %s)", d["id"], d["gueltig_bis"])
        return 0

    fehlerhaft = [e for e in ergebnisse if e.fehler]
    for e in fehlerhaft:
        for meldung in e.fehler:
            LOG.error("%s: %s", e.id, meldung)
    for e in abgelaufen:
        LOG.warning("%s: abgelaufen seit %s (kein Fehler)", e.id, e.frontmatter["gueltig_bis"])
    LOG.info("%d Einträge geprüft, %d fehlerhaft", len(ergebnisse), len(fehlerhaft))
    return 1 if fehlerhaft else 0


if __name__ == "__main__":
    sys.exit(main())
