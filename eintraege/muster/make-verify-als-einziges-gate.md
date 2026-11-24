---
typ: muster
titel: make verify als einziges lokales und CI-Gate
beschreibung: Relevant beim Aufsetzen eines Repos, wenn lokale Checks, Agent-Hooks und CI dieselben Prüfungen ausführen sollen.
tech: [make, github-actions, python]
tags: [ci, qualitaet, agent-ready]
kunde: wbai
projekt: bravo-proto
quelle: https://github.com/WEBUILDAI/wbai-bravo-wissen-proto/blob/main/docs/HANDOFF.md
gueltig_bis: "2027-11-30"
---

## Muster

Ein Target `make verify` bündelt Lint, Tests und fachliche Prüfungen. Die CI ruft genau dieses
Target in einem Job mit dem Namen `verify` auf; Branch-Schutz verlangt diesen Check. Agents
(Stop-Hook, automatische Läufe) dürfen nur `Bash(make verify)` statt freier Shell.

## Warum

- Eine Wahrheit für Mensch, Agent und CI.
- Erlaubnislisten für Agents bleiben klein und prüfbar.
