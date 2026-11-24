# CLAUDE.md: wbai-bravo-wissen-proto

**PROTOTYP, nonprod.** Wissens-Repo für den Bravo Tracer Bullet. Auftrag und Regeln: `docs/HANDOFF.md`.

## Aufbau
- `eintraege/<typ>/<slug>.md`: ein Eintrag pro Datei, YAML-Frontmatter + Markdown-Inhalt.
  `typ` ∈ entscheidung, learning, muster, gotcha, standard (= Ordnername). ID = `<typ>/<slug>`.
- `schema/eintrag.schema.json`: **eingefroren, nie ändern.**
- `scripts/validate.py`: prüft Schema, Ordner/typ, Slug, `kunde: wbai`, nicht-leeren Inhalt.
- `.github/workflows/schema.yml`: CI-Job `verify` = `make verify`.
- `.github/workflows/bravo-wissen-pflege.yml`: wöchentliche Pflege abgelaufener Einträge (S10).

## Befehle
- `make install`: gepinnte Abhängigkeiten aus `requirements.txt`.
- `make compile`: `requirements.in` → `requirements.txt` neu pinnen.
- `make verify`: Lint (Ruff, Black) + Tests + Schema-Validierung. Muss vor jedem PR grün sein.
- `make abgelaufen`: Einträge mit `gueltig_bis` < heute auflisten.

## Regeln
- Nur synthetische Inhalte, `kunde: wbai`. Keine Secrets, keine echten Kundendaten.
- `kunde` und `projekt` sind Metadaten; der Wissens-MCP gibt sie nie aus.
- Abgelaufene Einträge sind gültig, werden aber nie ausgeliefert. Der Eintrag
  `learning/pydantic-v1-kompatibilitaet` ist absichtlich abgelaufen (Testfall), nicht "reparieren".
- Branches `feature/…` (Menschen), `claude/…` (automatische Läufe); PRs gegen `main`,
  Beschreibung beginnt mit `[PROTOTYP]`. Nie mergen, nie force-pushen.
- Python: `logging` statt `print`, Google-Docstrings, Black + Ruff.
- Jede Annahme in `docs/ASSUMPTIONS.md`.
