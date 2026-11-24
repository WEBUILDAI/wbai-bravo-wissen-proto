[PROTOTYP] <!-- Kurzbeschreibung: was und warum -->

## Änderung

- 

## Checkliste Wissenseintrag

- [ ] Datei liegt unter `eintraege/<typ>/<slug>.md`, Slug in kebab-case
- [ ] `typ` im Frontmatter entspricht dem Ordner
- [ ] `kunde: wbai` (keine echten Kundennamen, Repo ist öffentlich)
- [ ] Keine Secrets, internen Hostnamen oder personenbezogenen Daten
- [ ] `beschreibung` sagt in einem Satz, wann der Eintrag relevant ist
- [ ] `quelle` ist eine `https://`-URL, `gueltig_bis` ist gesetzt und realistisch
- [ ] Schema `schema/eintrag.schema.json` nicht geändert
- [ ] `make verify` lokal grün (CI-Check `verify`)
- [ ] Neue Annahmen in `docs/ASSUMPTIONS.md` geloggt
