# Pula pustych projektów Webflow

Na planach innych niż Enterprise API Webflow nie tworzy projektów (site). Dlatego człowiek zakłada zapas pustych projektów, a migracja zajmuje pierwszy wolny.

## Konwencja nazw
- `Blank-migration-01`, `Blank-migration-02`, … (dwucyfrowy numer, rośnie).
- Zakładane ręcznie: Dashboard → New site → **Blank site**, w workspace docelowym.
- Po założeniu nowych projektów connector Webflow musi mieć do nich dostęp: claude.ai → Ustawienia → Connectors → Webflow → rozłącz/połącz i zaznacz nowe projekty albo cały workspace. Projekty niewidoczne w `list_sites` = brak autoryzacji.

## Zajęcie projektu (lock)
1. `data_sites_tool > list_sites` → kandydaci: `displayName` pasuje do `^Blank-migration-\d{2}$`, brak `lastPublished`.
2. Dla każdego kandydata (rosnąco po numerze): `data_pages_tool > list_pages`.
   - **Wolny**, jeśli jedyną stroną jest Home i nie ma strony o slugu `migration-claim`.
   - Dodatkowo `data_element_tool > get_all_elements` (depth 1) na Home: Body bez dzieci.
3. Najpierw nadpisz `migrations/.active-site` id wybranego kandydata (hook `guard.py` blokuje zapisy do innych projektów, a plik może zawierać id z poprzedniej migracji).
4. Zajmij kandydata: `data_pages_tool > create_page` z `slug: "migration-claim"`, `draft: true`, `title: "Claimed: <domena> <YYYY-MM-DD>"`, `seo.description: "<URL źródła> – session <CLAUDE_CODE_REMOTE_SESSION_ID lub opis>"`. Strona-draft jest znacznikiem i zostaje w projekcie (nie publikuje się).
5. Zapisz `site_id`, `shortName`, nazwę do `migrations/<domena>/intake.md`.
6. Jeśli po zajęciu `list_pages` pokazuje więcej niż jeden `migration-claim` (wyścig dwóch sesji) — wybierz inny projekt i zapisz to w raporcie.

## Brak wolnych projektów
Zatrzymaj się i napisz użytkownikowi dokładnie, jakie nazwy założyć — kolejne numery po najwyższym istniejącym, np.:

> Pula pustych projektów się wyczerpała. Załóż w Webflow (workspace <nazwa>) projekty **Blank-migration-06**, **Blank-migration-07**, **Blank-migration-08** (New site → Blank site), a potem w claude.ai → Ustawienia → Connectors → Webflow połącz connector ponownie i zaznacz nowe projekty. Daj znać, gdy będą gotowe.

## Enterprise
Jeśli workspace ma plan Enterprise (np. `data_enterprise_tool > list_301_redirects` nie zwraca błędu planu), nowy projekt można utworzyć przez Webflow Data API `POST /v2/workspaces/{workspace_id}/sites` (scope `workspace:write`) — wymaga tokena workspace; poza zakresem kitu v0.1.
