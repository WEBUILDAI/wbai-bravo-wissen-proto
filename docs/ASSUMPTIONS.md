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
