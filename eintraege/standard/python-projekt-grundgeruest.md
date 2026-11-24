---
typ: standard
titel: Python-Grundgerüst für WBAI-Repos
beschreibung: Relevant beim Anlegen oder Prüfen eines Python-Repos nach WBAI-Standard (Tooling, Abhängigkeiten, Logging, Docstrings).
tech: [python, ruff, black, pre-commit]
tags: [standard, tooling, python]
kunde: wbai
projekt: bravo-proto
quelle: https://github.com/WEBUILDAI/wbai-bravo-wissen-proto/blob/main/docs/HANDOFF.md
gueltig_bis: "2027-12-31"
---

## Standard

- Formatierung mit Black, Lint mit Ruff, beides über pre-commit.
- Abhängigkeiten in `requirements.in`, gepinnt per `make compile` nach `requirements.txt`.
- `.env.example` statt echter `.env` im Repo.
- `logging` statt `print`, Docstrings im Google-Stil.
- devcontainer und `make verify` als Einstieg.
