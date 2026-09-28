# Webflow migration kit

Powtarzalna migracja żywej strony (WordPress/Elementor, statyczna, Next.js, Wix…) do Webflow — w sesji **Claude Code w chmurze** albo lokalnie jako **plugin**.

Co robi:
1. **Audyt bez repozytorium** — headless Chromium (Playwright) czyta stronę: treść, sekcje, style, tokeny, obrazy, formularze, skrypty śledzące, zrzuty 1440/375 px.
2. **Projekt Webflow z puli** — zajmuje pierwszy wolny pusty projekt `Blank-migration-NN` (API Webflow nie tworzy projektów poza Enterprise).
3. **Budowa bez Designera** — Webflow MCP (`data_*`): strony, zmienne, sekcje, osadzenia, CMS; obrazy przez Data API (`scripts/assets.py`, z konwersją webp).
4. **QA i staging** — publikacja tylko na `*.webflow.io`, raport QA z metrykami i zrzutami.
5. **Bezpieczniki** — hook blokuje publikację na domenę klienta i zapisy do innych projektów, pyta przed akcjami destrukcyjnymi i przed dodaniem skryptów śledzących.

```
.claude-plugin/        plugin.json + marketplace.json (instalacja jako plugin)
.claude/settings.json  uprawnienia + hook (sesje w chmurze czytają to z repo)
.claude/skills  ->     symlink do skills/ (sesje w chmurze)
.mcp.json              serwer Playwright MCP
hooks/hooks.json       hook dla trybu plugin
skills/                webflow-site-migration (+ references/), migration-preflight
scripts/               audit.py, assets.py, qa.py, preflight.py, guard.py, _browser.py
setup/cloud-setup.sh   setup script środowiska chmurowego
migrations/            wyniki migracji (po jednej gałęzi na domenę)
```

## Jednorazowa konfiguracja

### 1. Repozytorium
1. Utwórz prywatne repo (np. `fouroceanlimited/webflow-migration-kit`) i wypchnij zawartość tego katalogu.
2. Zainstaluj **Claude GitHub App** na tym repo (claude.ai/code → onboarding albo github.com/apps/claude).

### 2. Pula projektów Webflow
1. Webflow Dashboard (workspace docelowy) → New site → **Blank site**: `Blank-migration-01` … `Blank-migration-05`.
2. claude.ai → Ustawienia → Connectors → **Webflow** → rozłącz/połącz; na ekranie autoryzacji zaznacz nowe projekty (najlepiej cały workspace).
3. Gdy pula się wyczerpie, agent poda dokładne nazwy kolejnych projektów do założenia.

### 3. Środowisko w chmurze (claude.ai/code → Environments → Add cloud environment)
- **Name**: `webflow-migration`
- **Network access**: **Full** (najprościej — strony klientów są różne) albo **Custom** z zaznaczonym „Also include default list” i domenami:
  ```
  webflow-prod-assets.s3.amazonaws.com
  cdn.prod.website-files.com
  *.webflow.io
  fonts.googleapis.com
  fonts.gstatic.com
  cdn.playwright.dev
  playwright.download.prss.microsoft.com
  <domena-źródłowa>
  *.<domena-źródłowa>
  ```
  (+ CDN-y obrazów źródła, jeśli inne, np. `*.wp.com`). Webflow MCP idzie przez connector i nie wymaga wpisu.
- **Setup script**: zawartość `setup/cloud-setup.sh`.
- **Environment variables**: opcjonalnie `MIGRATION_TRACKING_APPROVED=1` tylko dla środowisk, w których klient z góry zgodził się na przeniesienie skryptów śledzących. Nie wpisuj sekretów (zmienne są widoczne dla użytkowników środowiska).

W organizacji Team/Enterprise właściciel może utworzyć to środowisko jako **współdzielone** (Admin settings → Cloud environments).

## Uruchomienie migracji

**W chmurze (claude.ai/code lub aplikacja):** wybierz repo `webflow-migration-kit`, środowisko `webflow-migration`, włącz connector **Webflow**, tryb uprawnień „Auto” lub „Accept edits” i napisz np.:

```
Przenieś https://mission-gruener-wohnen.ch do Webflow. Zakres: strona główna, Solaranlage, Wärmepumpe,
artykuły Ratgeber do CMS. Formularze osadzone 1:1, bez skryptów śledzących.
```

**Z terminala:** `claude --cloud "Przenieś https://… do Webflow …"` (z katalogu repo).

**Cyklicznie / z kolejki:** Routine (claude.ai/code → Routines) z tym samym promptem i listą adresów.

Pierwszy raz w nowym środowisku: `Uruchom migration-preflight dla https://…`.

Wynik: staging `https://<shortName>.webflow.io`, `migrations/<domena>/qa-report.md`, zrzuty, gałąź `migration/<domena>`.

## Lokalnie jako plugin (Claude Code)
```
/plugin marketplace add fouroceanlimited/webflow-migration-kit
/plugin install webflow-migration-kit@fouroceanlimited-tools
claude mcp add --transport http webflow https://mcp.webflow.com/mcp     # logowanie OAuth do Webflow
pip install -r requirements.txt && python3 -m playwright install chromium
```

## Uprawnienia (`.claude/settings.json`)
- **Dozwolone bez pytania**: skrypty kitu, instalacja zależności, zapis w `migrations/`, Playwright MCP, Webflow MCP.
- **Hook `guard.py` (Webflow)**: *blokuje* publikację na domeny własne i zapisy do projektu innego niż `migrations/.active-site`; *pyta* przed delete/remove/clear i przed dodaniem skryptów śledzących.
- **Zabronione**: `rm -rf`, `git push --force`, odczyt `.env`.

## Ograniczenia
- Nowe projekty Webflow zakłada człowiek (pula) — chyba że workspace jest Enterprise.
- Strony z ochroną przed botami / geo-blokadą: migracja zatrzymuje się i prosi o dostęp albo eksport.
- Slidery, akordeony, złożone animacje — upraszczane i opisane w QA.
- Domena, DNS, 301 na produkcji — zawsze człowiek.
