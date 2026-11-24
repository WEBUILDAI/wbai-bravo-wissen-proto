> **PROTOTYP, nonprod.** Tracer Bullet für Bravo. Nur synthetische Einträge (`kunde: wbai`).
> Ablaufdatum: 2027-02-24. Verantwortlich: lukas.sekoulidis@we-build-ai.de

# wbai-bravo-wissen-proto

Wissens-Repo für Bravo. Ein Eintrag = eine Markdown-Datei unter `eintraege/<typ>/<slug>.md` mit
YAML-Frontmatter nach `schema/eintrag.schema.json`. Gelesen wird es vom Wissens-MCP
(`wbai-bravo-kontext-proto`), neue Einträge kommen als PR.

## Neuer Eintrag

1. Datei `eintraege/<typ>/<slug>.md` anlegen (`typ`: entscheidung, learning, muster, gotcha, standard).
2. Frontmatter mit allen Pflichtfeldern aus dem Schema, `kunde: wbai`, `gueltig_bis` als Datum.
3. `make install` (einmalig), dann `make verify`.
4. PR gegen `main`, Beschreibung beginnt mit `[PROTOTYP]`, Checkliste im Template abhaken.

Beispiel-Frontmatter:

```yaml
---
typ: gotcha
titel: Kurzer, sprechender Titel
beschreibung: Ein Satz, wann der Eintrag relevant ist.
tech: [python, fastapi]
tags: [beispiel]
kunde: wbai
projekt: bravo-proto
quelle: https://github.com/WEBUILDAI/wbai-bravo-wissen-proto
gueltig_bis: "2027-06-30"
---
```

## Befehle

| Befehl | Zweck |
|---|---|
| `make verify` | Lint + Tests + Schema-Validierung (CI-Check `verify`) |
| `make abgelaufen` | Einträge mit `gueltig_bis` in der Vergangenheit |
| `make compile` | Abhängigkeiten neu pinnen |

## Wissenspflege (automatisch)

`.github/workflows/bravo-wissen-pflege.yml` läuft montags (und manuell per *Run workflow*):
findet Einträge mit `gueltig_bis` in der Vergangenheit, lässt Claude (WIF, ohne API-Key, ohne freie
Shell) Aktualisierungen vorschlagen und öffnet einen PR auf `claude/wissen-pflege-<run_id>`.
Voraussetzungen: Repo-Variablen `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID`
(siehe `docs/ASSUMPTIONS.md`, A-W18 bis A-W20).

Stand und Auftrag: `docs/HANDOFF.md`. Annahmen: `docs/ASSUMPTIONS.md`.
