---
name: webflow-site-migration
description: Migrates a live website (WordPress/Elementor, static, Next.js, Wix…) to Webflow reproducibly and without the Webflow Designer - headless Playwright audit, build through the Webflow MCP data tools, image upload through the Data API, QA and staging publish. Use when asked to "przenieś stronę do Webflow", "migrate <url> to Webflow", "skopiuj stronę na Webflow", "/webflow-site-migration <url>".
---

# Migracja strony do Webflow (migration kit)

Cel: wierna kopia istniejącej strony jako czysty, edytowalny projekt Webflow (Variables + klasy Client-First, CMS dla treści powtarzalnych), opublikowana **tylko** na `*.webflow.io`. Nie kopiuj markupu 1:1 — przebudowuj natywnie, zachowując treść i wygląd. Komunikuj się z użytkownikiem w jego języku.

Katalog kitu (`KIT`): katalog, w którym leży `scripts/audit.py` — w sesji chmurowej to root repozytorium, w pluginie `${CLAUDE_PLUGIN_ROOT}`. Wyniki zawsze w `migrations/<domena>/` w bieżącym katalogu projektu.

## Zasady nadrzędne

- **Bez Designera.** Nie wywołuj `designer_tool` ani `asset_tool` (wymagają otwartego Designera). Buduj wyłącznie narzędziami `data_*`; obrazy przez `scripts/assets.py`. Kroki, które naprawdę wymagają Designera, wpisz do `migrations/<domena>/designer-todo.md`.
- **Tylko staging.** `publish_site` zawsze z `publishToWebflowSubdomain: true` i `customDomains: []` (hook `guard.py` blokuje inne).
- **Jedna strona docelowa.** Po zajęciu projektu z puli zapisz jego id do `migrations/.active-site`; hook blokuje zapisy do innych projektów.
- **Nie wymyślaj treści.** Teksty kopiuj dosłownie ze snapshotu audytu; braki opisuj w QA.
- **Skrypty śledzące** (GTM, pixel, Cookiebot…) dodawaj dopiero po zgodzie użytkownika (hook pyta), chyba że sesja ma `MIGRATION_TRACKING_APPROVED=1`.
- **Blokady źródła** (ochrona przed botami, geo-blokada, brak sieci): zatrzymaj się i zgłoś, czego potrzeba (dostęp od klienta, eksport WordPress, domena na liście dozwolonych). Nie obchodź zabezpieczeń.
- Destrukcyjne akcje (delete/remove/clear) tylko po potwierdzeniu. Stron nie da się usunąć przez API.

## Przebieg

### 0. Preflight
1. `python3 KIT/scripts/preflight.py <URL>` — musi zwrócić `ok: true`. Przy błędach sieci podaj użytkownikowi poprawkę z pola `fix` (ustawienia sieci środowiska — README, sekcja „Środowisko w chmurze”) i zatrzymaj się.
2. Webflow MCP: `webflow_guide_tool` raz na sesję (`session_id: "start"`, stały `agent_id`), potem ten sam `ses_…` w każdym wywołaniu. Brak narzędzi Webflow → poproś o włączenie connectora Webflow w sesji i zatrzymaj się.

### 1. Intake
Ustal (z polecenia albo AskUserQuestion; w trybie bez nadzoru przyjmij domyślne i zapisz założenia):
- URL źródła i zakres (domyślnie: strona główna + strony z nawigacji/stopki), dostęp do repozytorium (tryb A) czy tylko żywa strona (tryb B, domyślny),
- co idzie do CMS (domyślnie: wpisy bloga/poradnika, jeśli są w zakresie),
- formularze: embed 1:1 (domyślnie) / Webflow Forms,
- czy przenosić skrypty śledzące (domyślnie: nie, tylko raport).
Zapisz w `migrations/<domena>/intake.md`.

### 2. Projekt docelowy z puli
Zajmij pusty projekt wg `references/site-pool.md`. Nigdy nie buduj w projekcie spoza puli bez wyraźnej zgody.

### 3. Audyt (headless)
`python3 KIT/scripts/audit.py <URL> [--pages / /a /b] [--max-pages N]` → `inventory.json`, `content/<slug>.json`, `tokens.json`, `scripts.json`, `urls.json`, zrzuty 1440/375.
- Exit 3 = źródło zablokowane → zasada „Blokady źródła”.
- Przeczytaj `content/*.json` (sekcje, teksty, style) i obejrzyj zrzuty ekranu przed budową.
- Tryb A (repo): treść i tokeny bierz ze źródeł repo, audyt robi tylko zrzuty i listę skryptów.
- WordPress/Elementor: `references/source-wordpress.md`.

### 4. Plan budowy
Na podstawie audytu zapisz `migrations/<domena>/build-plan.md`: strony (slug = stary slug), sekcje → komponenty/klasy, kolekcje CMS, obrazy, osadzenia, uproszczenia (slidery, akordeony) — każde uproszczenie trafi potem do QA.

### 5. Budowa w Webflow (bez Designera)
Postępuj wg `references/webflow-build.md`:
1. Strony: `data_pages_tool > create_page` (slug zgodny ze źródłem, SEO/OG), Home przez `update_page_settings`.
2. Obrazy: `python3 KIT/scripts/assets.py prepare migrations/<domena>` → dla każdego wpisu `data_assets_tool > create_asset` → zapisz wynik do `assets/uploads/<file>.json` → `python3 KIT/scripts/assets.py upload migrations/<domena>` → `asset-map.json` (źródło → asset id).
3. Font(y) Google i `lang` w site head (`data_scripts_tool > set_site_freeform_code`) — bez skryptów śledzących.
4. Variables (`data_variable_tool`) z `tokens.json`.
5. Sekcje: `data_whtml_builder` (+ obowiązkowe poprawki: `set_image_asset`, podpięcie zmiennych przez `update_style`), osadzenia przez `HtmlEmbed` + klucz `code`.
6. CMS (jeśli w zakresie): kolekcje, pola, itemy jako draft; listy przez Collection List.

### 6. Staging i QA
1. `data_sites_tool > publish_site` (`publishToWebflowSubdomain: true`, `customDomains: []`).
2. `python3 KIT/scripts/qa.py migrations/<domena> https://<shortName>.webflow.io` → `qa.json`, `qa-report.md`, zrzuty w `qa-screenshots/`.
3. Porównaj zrzuty źródła i stagingu (obejrzyj je). Popraw różnice, publikuj ponownie, powtórz QA aż: pokrycie tekstu ≥ 98% na każdej stronie, 0 zepsutych obrazów, brak poziomego scrolla na 375 px.
4. Uzupełnij `qa-report.md`: świadome różnice, linki do starej domeny, rzeczy do ręcznego dopracowania, lista skryptów ze `scripts.json` (dodane / czekają na zgodę), wynik zewnętrznych formularzy porównany z oryginałem (`references/qa.md`).

### 7. Raport końcowy
Wyślij użytkownikowi: link do stagingu, tabelę z `qa-report.md`, listę otwartych punktów i `designer-todo.md` (jeśli niepusty). Podpięcie domeny, DNS i przekierowania 301 na produkcji — wyłącznie człowiek, po akceptacji.

## Pliki referencyjne
- `references/site-pool.md` — pula pustych projektów i ich zajmowanie
- `references/webflow-build.md` — budowa przez MCP: pułapki, obrazy, zmienne, osadzenia, CMS
- `references/source-wordpress.md` — WordPress/Elementor: REST API, tokeny, widżety
- `references/qa.md` — kryteria QA i porównanie z oryginałem
