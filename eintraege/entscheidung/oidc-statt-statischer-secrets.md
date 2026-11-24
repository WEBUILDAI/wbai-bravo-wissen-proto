---
typ: entscheidung
titel: OIDC-Federation statt statischer Secrets in GitHub Actions
beschreibung: Relevant, wenn ein Workflow sich bei Azure oder der Claude API anmelden muss und ein Secret hinterlegt werden soll.
tech: [github-actions, azure, oidc]
tags: [sicherheit, ci, secrets]
kunde: wbai
projekt: bravo-proto
quelle: https://github.com/WEBUILDAI/wbai-bravo-wissen-proto/blob/main/docs/HANDOFF.md
gueltig_bis: "2027-06-30"
---

## Entscheidung

Workflows authentifizieren sich per OIDC (Workload Identity Federation): `azure/login` mit
Federated Credential für Azure, `anthropic_federation_rule_id` + `anthropic_organization_id`
für die Claude API. Im Repo liegen nur IDs als Repo-Variablen, keine Schlüssel.

## Begründung

- Kein Secret, das rotiert oder geleakt werden kann.
- Federated Credential ist an Repo und Ref gebunden (z. B. `ref:refs/heads/main`).

## Konsequenz

Workflows brauchen `permissions: id-token: write`. Einrichtung der Federation ist ein Admin-Schritt.
