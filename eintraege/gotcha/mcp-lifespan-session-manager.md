---
typ: gotcha
titel: FastMCP Streamable HTTP braucht session_manager.run() im Host-Lifespan
beschreibung: Relevant, wenn ein FastMCP-Server per Streamable HTTP in eine eigene Starlette- oder FastAPI-App eingehängt wird.
tech: [python, mcp, starlette, fastapi]
tags: [mcp, lifespan, streamable-http]
kunde: wbai
projekt: bravo-proto
quelle: https://github.com/WEBUILDAI/wbai-bravo-wissen-proto/blob/main/docs/HANDOFF.md
gueltig_bis: "2027-05-31"
---

## Symptom

Requests an `/mcp` scheitern mit "Task group is not initialized", sobald die MCP-App als
Sub-App gemountet ist.

## Ursache

Der Lifespan der gemounteten App läuft nicht automatisch. Der Session-Manager wird nie gestartet.

## Lösung

Im Lifespan der Host-App `async with mcp.session_manager.run(): yield` ausführen. Zusätzlich
`TransportSecuritySettings` mit expliziten `allowed_hosts` setzen.
