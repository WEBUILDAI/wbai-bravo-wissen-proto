# Annahmen: wbai-bravo-wissen-proto

Getroffen ohne Rückfrage (unbeaufsichtigter Lauf, Stand 2026-11-24). Status: **angenommen** =
umgesetzt, bitte bei Review bestätigen; **offen** = braucht einen Menschen bzw. Admin-Rechte.

## S5 Wissens-Repo

| # | Annahme | Status |
|---|---|---|
| A-W1 | PRs gehen direkt gegen `main` (kein `develop`), wie in HANDOFF als Abweichung festgelegt. | angenommen |
| A-W2 | Fünf synthetische Einträge, je einer pro `typ`. Abgelaufen: `learning/pydantic-v1-kompatibilitaet` (`gueltig_bis: 2026-06-30`). | angenommen |
| A-W3 | `projekt: bravo-proto` für alle Einträge; `quelle` zeigt auf `docs/HANDOFF.md` in diesem Repo (öffentlich, `https://`). | angenommen |
| A-W4 | `gueltig_bis` wird im YAML gequotet. Der Validator lädt Datumswerte trotzdem als String (YAML-Timestamps deaktiviert), damit ungequotete Daten nicht am Schema-Typ `string` scheitern. | angenommen |
| A-W5 | Zusatzregeln im Validator über das Schema hinaus: `typ` = Ordnername, Slug kebab-case, `kunde == wbai`, Inhalt nicht leer, nur `.md` direkt unter `eintraege/<typ>/`. Das Schema selbst ist unverändert. | angenommen |
| A-W6 | Abgelaufene Einträge sind **kein** Validierungsfehler (sonst wäre der Testeintrag ein Dauerrot). Sie erscheinen als Warnung und über `make abgelaufen`. | angenommen |
| A-W7 | Format `uri` wird nicht über ein Zusatzpaket geprüft; das Schema-Pattern `^https://` reicht im Prototyp. Format `date` wird geprüft. | angenommen |
| A-W8 | WBAI-Python-Standard schlank umgesetzt: eine `requirements.in` für Laufzeit und Dev (Repo hat nur ein Skript), Python 3.11, Zeilenlänge 100. `.env.example` ist leer, weil keine Laufzeit-Variablen nötig sind. | angenommen |
| A-W9 | CI-Workflow heißt `schema`, Job-ID und Job-Name `verify`; läuft auf jedem `pull_request` und auf Push nach `main`. | angenommen |
| A-W10 | Branch-Schutz auf `main` (Check `verify` Pflicht, PR Pflicht, kein Force-Push) ist ein Admin-Schritt und hier nicht gesetzt. | **offen** (Admin) |
| A-W11 | Repo-Beschreibung `[PROTOTYP, nonprod] …` ist gesetzt; Topics `prototype`, `nonprod` konnten aus der Session nicht geprüft/gesetzt werden. | **offen** (Admin) |

## S10 Automatische Wissenspflege

| # | Annahme | Status |
|---|---|---|
| A-W12 | Branch `feature/s10-wissen-pflege` baut auf `feature/s5-wissens-repo` auf (braucht `scripts/validate.py --abgelaufen`, `make verify` und den CI-Check). Der PR gegen `main` zeigt daher bis zum Merge von S5 auch dessen Commits; S5 zuerst mergen. | angenommen |
| A-W13 | Zeitplan montags 05:17 UTC plus `workflow_dispatch`. Ein deterministischer Vorjob ermittelt abgelaufene Einträge; Claude läuft nur, wenn es welche gibt. | angenommen |
| A-W14 | Auth zur Claude API nur per WIF: `anthropic_federation_rule_id` und `anthropic_organization_id` aus Repo-Variablen `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID`; `id-token: write` nur im Pflege-Job. Kein API-Key. Inputs gegen die aktuelle `action.yml` von `anthropics/claude-code-action@v1` geprüft (actionlint kennt sie noch nicht und meldet sie fälschlich). | angenommen |
| A-W15 | Claude bekommt keine Shell außer `Bash(make verify)` und `Bash(make abgelaufen)`, dazu Read/Glob/Grep/Edit/Write; `--max-turns 15`, Job-`timeout-minutes: 20`. Kein git für Claude: Branch `claude/wissen-pflege-<run_id>`, Commit und PR legt `peter-evans/create-pull-request@v7` an (nur `eintraege/**`). | angenommen |
| A-W16 | Claude verlängert `gueltig_bis` höchstens um 12 Monate, wenn der Inhalt weiter zutrifft; veraltete Einträge werden nur im Bericht zur Entfernung vorgeschlagen, nicht gelöscht. Ändert Claude nichts, entsteht kein PR (Bericht bleibt dann nur im Job-Log). | angenommen |
| A-W17 | Der absichtliche Testeintrag `learning/pydantic-v1-kompatibilitaet` bleibt unverändert; solange er der einzige abgelaufene Eintrag ist, läuft Claude wöchentlich ohne PR (kleiner, durch `--max-turns` begrenzter Durchlauf als Rauchtest). | angenommen |
| A-W18 | Repo-Variablen `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID` und die WIF-Regel (A14) auf Anthropic-Seite für `repo:WEBUILDAI/wbai-bravo-wissen-proto` anlegen. | **offen** (Admin) |
| A-W19 | Repo-Einstellung "Allow GitHub Actions to create and approve pull requests" aktivieren, sonst scheitert der PR-Schritt mit `GITHUB_TOKEN`. | **offen** (Admin) |
| A-W20 | Mit `GITHUB_TOKEN` erzeugte PRs lösen keine weiteren Workflows aus; der Check `verify` läuft dort nicht automatisch (der Pflege-Job führt `make verify` selbst als Gate aus). Später GitHub-App-Token (A12) verwenden, damit Branch-Schutz greift. | **offen** (Admin) |
