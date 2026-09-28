---
name: migration-preflight
description: Checks that a Claude Code session is ready to run a Webflow migration - Python deps, headless Chromium, network access to Webflow and the source site, Webflow connector and free projects in the Blank-migration pool. Use when asked "sprawdź środowisko migracji", "preflight", "czy mogę odpalić migrację", or before the first migration in a new environment.
---

# Preflight migracji

Wykonaj i zaraportuj w tabeli (✅/❌ + poprawka):

1. `python3 scripts/preflight.py <URL źródła, jeśli podany>` (w pluginie: `${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py`). Błędy `python:*` → `pip install -r requirements.txt`; `chromium` → `python3 -m playwright install chromium`; `net:*` → ustawienia sieci środowiska (README → „Środowisko w chmurze”).
2. Playwright MCP: wywołaj `browser_navigate` na `https://example.com` i `browser_close`. Brak narzędzi `mcp__playwright__*` → sesja nie wczytała `.mcp.json` (sesja musi startować w tym repozytorium) albo brak `npx`.
3. Webflow: `webflow_guide_tool` (`session_id: "start"`), potem `data_sites_tool > list_sites`. Brak narzędzi → włącz connector Webflow w sesji. Pusta/niepełna lista → ponowna autoryzacja connectora z zaznaczeniem projektów.
4. Pula: policz wolne projekty wg `skills/webflow-site-migration/references/site-pool.md` (bez zajmowania). Gdy 0 wolnych — podaj dokładne nazwy do założenia.
5. Hook: `echo '{"tool_name":"mcp__Webflow__data_sites_tool","tool_input":{"actions":[{"label":"t","publish_site":{"site_id":"x","customDomains":["a.com"]}}]}}' | python3 scripts/guard.py` musi zwrócić `"permissionDecision": "deny"`.

Nie zmieniaj niczego w Webflow podczas preflightu.
