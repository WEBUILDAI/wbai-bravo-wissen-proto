# Bravo Tracer Bullet: Umsetzungsstand und Auftrag

Gleiche Datei in allen drei Repos. Stand: 2026-11-24.

## Ziel
Ein schmaler, durchgehender Prototyp (nonprod) des Bravo-Ablaufs auf Claude-Bausteinen:
Issue → Cloud session → PR → Review → Merge → Teams-Hinweis → Sync nach Azure DevOps,
plus ein Wissens-Repo mit Wissens-MCP, das Sessions Kontext liefert und Vorschläge annimmt.

## Repos (GitHub-Org WEBUILDAI, public, keine Secrets)
| Repo | Inhalt | Slices |
|---|---|---|
| `wbai-bravo-sample-proto` | FastAPI-Sample, Hooks, Skills, Workflows | S1, S2, S3, S4, S7, S8, S9-Workflow, S10 |
| `wbai-bravo-wissen-proto` | Wissenseinträge `eintraege/<typ>/<slug>.md`, Schema, Schema-CI | S5 (Inhalt) |
| `wbai-bravo-kontext-proto` | Wissens-MCP (`server/`), Pulumi-Stack (`infra/`) | S5 (Infra), S6, S9-Tools |

Eine Cloud session pro Repo. Jede Session arbeitet nur in ihrem Repo.

## Feste Regeln
- **Markierung:** Repo-Beschreibung `[PROTOTYP, nonprod] …`, Topics `prototype`, `nonprod`, README
  beginnt mit Hinweisblock. PR-Beschreibungen und Teams-Karten beginnen mit `[PROTOTYP]`.
- **Azure-Tags:** `environment=nonprod`, `stage=prototype`, `project=bravo`,
  `owner=lukas.sekoulidis@we-build-ai.de`, `expires=2027-02-24`.
- **Namen:** `<kürzel>-wbai-bravo[-<suffix>]-proto`, Repos `wbai-bravo-<service>-proto`.
- **Branches:** `feature/…`, `bugfix/…`, `hotfix/…`, `chore/…`; automatisierte Läufe `claude/…`.
  PRs direkt auf `main` (Abweichung, in ASSUMPTIONS geloggt).
- **Jede Annahme** in `docs/ASSUMPTIONS.md` des betroffenen Repos.
- **Nie:** Secrets committen, mergen, force-pushen, Azure-Ressourcen anlegen/löschen, `pulumi up`.
  Commits/PRs ohne Hinweis auf KI-Werkzeuge, ohne Co-Authored-By, ohne Session-Links.
- **WBAI-Standards (Python):** Black + Ruff + pre-commit, `requirements.in` → `make compile`,
  `.env.example`, `logging` statt `print`, Google-Docstrings, devcontainer, `make verify`.
- **Stoppen und fragen** (als PR-Kommentar / in ASSUMPTIONS als offen markieren) bei: Kosten über
  ~50 €/Monat, Löschen bestehender Ressourcen, Entra/ADO-Rechten über das Sample-Projekt hinaus.

## Slices
**S1 Agent-ready Repo (sample).** Erledigt bis auf: `docs/ASSUMPTIONS.md`, `docs/specs/`,
`docs/decisions/0001-prototyp-rahmen.md`. Branch-Schutz auf `main` (Check `verify`, PR Pflicht).

**S2 Async-Loop (sample).** `.github/ISSUE_TEMPLATE/` (board.yml, slice.yml, config.yml),
`docs/specs/0001-items-filter.md` (`GET /items?category=` filtert; leere Liste bei unbekannter
Kategorie; Tests), `docs/RUNBOOK.md` mit `claude --cloud "Board #<n> umsetzen"`. Board-Issue mit
2 Slice-Sub-Issues anlegen (macht der lokale Operator, nicht die Cloud session).

**S3 Teams-Hinweis (sample).** Fertig: `scripts/notify-teams.sh` (Adaptive Card, `[PROTOTYP]`,
No-op ohne `TEAMS_WEBHOOK_URL`/`BRAVO_KONTEXT_URL`), Stop-Hook `scripts/hooks/on-stop.sh`
(blockt bei rotem `make verify`, respektiert `stop_hook_active`). Offen: Test für den Card-Payload.

**S4 Sync nach ADO (sample).** `.github/workflows/sync-ado.yml`: auf push nach `main`, `azure/login`
per OIDC (Entra-App `wbai-bravo-sample-sync-proto`, Federated Credential
`repo:WEBUILDAI/wbai-bravo-sample-proto:ref:refs/heads/main`), pusht `sync/<short-sha>` ins
ADO-Repo, `az repos pr create`. Konfigurierbare Exclude-Liste (Prototyp leer; empfohlener
Kunden-Default `.claude/`, `CLAUDE.md`, `.mcp.json`). Vars: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`,
`AZURE_SUBSCRIPTION_ID`, `ADO_ORG_URL`, `ADO_PROJECT`, `ADO_REPO`. Doku `docs/output-sync.md`.

**S5 Wissens-Repo (wissen) + Infra (kontext/infra).**
- wissen: Schema `schema/eintrag.schema.json` ist eingefroren (nicht ändern). `eintraege/<typ>/<slug>.md`
  mit YAML-Frontmatter (typ, titel, beschreibung, tech, tags, kunde, projekt, quelle, gueltig_bis).
  `kunde: wbai` ausschließlich (synthetisch). 3–5 Einträge, einer davon mit `gueltig_bis` in der
  Vergangenheit (Test für Ausschluss). `scripts/validate.py` + `.github/workflows/schema.yml`
  (Job-Name `verify`), PR-Template mit Checkliste, README, CLAUDE.md, ASSUMPTIONS.
- kontext/infra: Pulumi Python, Stack `proto`, Backend
  `azblob://pulumi-state?storage_account=stwbaibravostateproto` (in `Pulumi.yaml` als `backend.url`),
  Region germanywestcentral, bestehende RG `rg-wbai-bravo-proto` (nur referenzieren, nicht anlegen).
  Ressourcen: `log-wbai-bravo-proto` (PerGB2018, 30 Tage), `cae-wbai-bravo-proto` (Consumption),
  `acrwbaibravoproto` (Basic), `kv-wbai-bravo-proto` (Standard, RBAC), `id-wbai-bravo-kontext-proto`
  (User-assigned MI mit AcrPull + Key Vault Secrets User), `ca-wbai-bravo-kontext-proto`
  (min 0 / max 1 Replica, 0.25 vCPU / 0.5 Gi, Ingress extern, Secret aus KV per MI),
  Budget-Alert 50 €/Monat auf der RG. Tags überall. Nur Code + `pulumi preview` lokal; `up` macht ein Mensch.

**S6 Wissens-MCP (kontext/server).** Python, offizielles MCP SDK (`mcp<2`, `FastMCP`,
Streamable HTTP, `TransportSecuritySettings` mit allowed_hosts; Host-Lifespan muss
`session_manager.run()` ausführen). Tools:
- `context_pack(aufgabe, tech?, max=10)`: Kandidaten per Keyword-Score, Ranking per Haiku
  (`claude-haiku-4-5-20251001`), Fallback reiner Keyword-Score ohne `ANTHROPIC_API_KEY`.
  Abgelaufene Einträge (`gueltig_bis` < heute) nie ausliefern.
- `search(query, typ?, tech?)`, `get(id)`, `related(id)`.
- `propose(typ, titel, …, inhalt)`: Branch `feature/wissen-<slug>` + PR im wissen-Repo.
- **Nie** `kunde` oder `projekt` ausgeben (Ausgabe-Filter + Test).
- Jede Auslieferung als strukturierte Log-Zeile (JSON) → Log Analytics über Container-Logs.
- Auth: Bearer-Token (aus Key Vault als Env `BRAVO_KONTEXT_TOKEN`), konstante Zeitvergleich.
- GitHub-Zugriff über GitHub App (A12): `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`,
  `GITHUB_APP_INSTALLATION_ID`; offline: lokaler Klon via `WISSEN_LOCAL_PATH`, `propose` gestubbt.
- `POST /notify`: Relay für Teams-Karten (siehe `scripts/notify-teams.sh` im sample-Repo),
  leitet an `TEAMS_WEBHOOK_URL` weiter, gleiche Bearer-Auth.
- Dockerfile, Makefile, Tests mit Fixture-Einträgen, README, CLAUDE.md, ASSUMPTIONS.

**S7 Kontext in Sessions (sample).** SessionStart-Hook `scripts/hooks/on-session-start.sh` ruft
`context_pack` per HTTP auf (nur wenn `BRAVO_KONTEXT_URL` gesetzt; sonst still), gibt Ergebnis als
`additionalContext` aus. `.mcp.json` mit dem Kontext-Server (URL aus Env). Skills
`.claude/skills/plan-to-issues/SKILL.md` und `.claude/skills/wissen/SKILL.md` (inkl. Destillier-Schritt:
am Ende einer Aufgabe Learnings per `propose`). `docs/specs/0002-items-by-id.md`.

**S8 Auto-Claude (sample).** `.claude/workflows/auto-claude.js`: Spielzeug-Baum
(Plan → 2 parallele Slices → Review), nur Gerüst, dokumentiert.

**S9 Vorschläge aus der Claude-App.**
- kontext/server: Tools `vorschlag_anlegen` (Issue mit Label `triage` im sample-Repo),
  `meine_rueckfragen`, `antworten`, `status`.
- sample: `.github/workflows/bravo-triage.yml` auf Label `triage` und auf `issue_comment`;
  Guard: author_association OWNER/MEMBER/COLLABORATOR oder `wbai-bravo-mcp-proto[bot]`;
  Kommentare von `claude[bot]` lösen nie aus. Skill `.claude/skills/aenderung-vorschlagen/SKILL.md`.

**S10 Automatische Läufe (sample).** `bravo-implement.yml` (Label `ready`, Branch-Präfix `claude/`),
in wissen: `bravo-wissen-pflege.yml` (wöchentlich, prüft `gueltig_bis` und schlägt Updates vor).
`anthropics/claude-code-action@v1` nur mit WIF (`anthropic_federation_rule_id`,
`anthropic_organization_id` aus Repo-Variablen), kein API-Key. `claude_args` mit `--allowedTools`
(kein freies `Bash`, nur z. B. `Bash(make verify)`, `Bash(git *)`), `--max-turns`, `timeout-minutes`.

## Abschluss
- Je Repo `docs/ASSUMPTIONS.md`.
- `docs/TRACER-BULLET-REPORT.md` im sample-Repo: Slice-Status (grün / blockiert durch Admin-Schritt),
  offene Admin-Schritte, nächste Befehle.

## Lokal zu erledigen (nicht in der Cloud session möglich)
- Rolle `Storage Blob Data Contributor` auf `stwbaibravostateproto` für den Operator, dann `pulumi preview`.
- Entra-App + Federated Credential für S4, ADO-Projekt/Repo, Repo-Variablen.
- GitHub App A12, WIF-Regel A14, Teams-Webhook, Network secrets der Cloud-Umgebung.
- Board-Issue + Sub-Issues anlegen, Test-PR für Branch-Schutz.
