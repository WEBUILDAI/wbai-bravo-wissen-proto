---
typ: learning
titel: pydantic.v1-Kompatibilitätsschicht nur übergangsweise nutzen
beschreibung: Relevant bei der Migration von Pydantic 1 auf 2, wenn alter Code über pydantic.v1 weiterlaufen soll.
tech: [python, pydantic]
tags: [migration, abgelaufen-test]
kunde: wbai
projekt: bravo-proto
quelle: https://github.com/WEBUILDAI/wbai-bravo-wissen-proto/blob/main/docs/HANDOFF.md
gueltig_bis: "2026-06-30"
---

## Learning

Der Import `from pydantic import v1` hält alten Code lauffähig, mischt aber zwei Modellwelten.
Modelle aus v1 und v2 lassen sich nicht ineinander verschachteln.

## Hinweis

Dieser Eintrag ist absichtlich abgelaufen (`gueltig_bis` in der Vergangenheit). Er dient als
Testfall: Der Wissens-MCP darf ihn nie ausliefern, die Wissenspflege soll ihn aufgreifen.
