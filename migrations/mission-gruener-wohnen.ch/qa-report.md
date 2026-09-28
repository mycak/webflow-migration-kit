# QA – mission-gruener-wohnen.ch → https://blank-migration-01.webflow.io

| Strona | HTTP | Tekst | Obrazy (zepsute) | H1 (źródło) | Mobile overflow | Linki do starej domeny |
|---|---|---|---|---|---|---|
| [home](https://blank-migration-01.webflow.io/) | 200 | 100% | 13 (0) | 1 (0) | OK | 0 |
| [agb](https://blank-migration-01.webflow.io/agb/) | 200 | 100% | 1 (0) | 0 (0) | OK | 1 |
| [datenschutz](https://blank-migration-01.webflow.io/datenschutz/) | 200 | 100% | 1 (0) | 0 (0) | OK | 0 |
| [impressum](https://blank-migration-01.webflow.io/impressum/) | 200 | 100% | 1 (0) | 0 (0) | OK | 1 |
| [solaranlage_m_e1](https://blank-migration-01.webflow.io/solaranlage_m_e1/) | 200 | 100% | 1 (0) | 1 (0) | OK | 0 |
| [waermepumpe_m_e1](https://blank-migration-01.webflow.io/waermepumpe_m_e1/) | 200 | 100% | 1 (0) | 1 (0) | OK | 0 |
| [alles-was-hausbesitzer-uber-solaranlagen-wissen-mussen-faq](https://blank-migration-01.webflow.io/ratgeber/alles-was-hausbesitzer-uber-solaranlagen-wissen-mussen-faq) | 200 | 91% | 2 (0) | 1 (1) | OK | 1 |
| [wie-arbeitet-eine-warmepumpe-ein-leitfaden-fur-umweltfreundliche-energie](https://blank-migration-01.webflow.io/ratgeber/wie-arbeitet-eine-warmepumpe-ein-leitfaden-fur-umweltfreundliche-energie) | 200 | 91% | 2 (0) | 1 (1) | OK | 1 |
| [vorteile-von-warmepumpen-energieeffizienz-und-kosteneinsparungen](https://blank-migration-01.webflow.io/ratgeber/vorteile-von-warmepumpen-energieeffizienz-und-kosteneinsparungen) | 200 | 94% | 2 (0) | 1 (1) | OK | 1 |
| [solaranlagen-auf-steildachern-nachhaltige-energie-fur-die-schweiz](https://blank-migration-01.webflow.io/ratgeber/solaranlagen-auf-steildachern-nachhaltige-energie-fur-die-schweiz) | 200 | 95% | 2 (0) | 1 (1) | OK | 1 |
| [technologie-fuer-private-solaranlagen](https://blank-migration-01.webflow.io/ratgeber/technologie-fuer-private-solaranlagen) | 200 | 96% | 2 (0) | 1 (1) | OK | 0 |
| [solaranlagen_einfuhrung](https://blank-migration-01.webflow.io/ratgeber/solaranlagen_einfuhrung) | 200 | 98% | 2 (0) | 1 (1) | OK | 0 |

## Brakujące teksty (max 30 na stronę)

**alles-was-hausbesitzer-uber-solaranlagen-wissen-mussen-faq**: vorheriger artikel · vorteile von wärmepumpen: energieeffizienz und kosteneinsparungen · entdecken sie die vorteile von wärmepumpen in der schweiz: hohe energieeffizienz, kosteneinsparungen und umweltfreundlichkeit. erfahren sie, wie wärmepumpen ihre heizkosten senken und von staatlichen förderprogrammen profitieren können.
**wie-arbeitet-eine-warmepumpe-ein-leitfaden-fur-umweltfreundliche-energie**: vorheriger artikel · nächster artikel · vorteile von wärmepumpen: energieeffizienz und kosteneinsparungen · entdecken sie die vorteile von wärmepumpen in der schweiz: hohe energieeffizienz, kosteneinsparungen und umweltfreundlichkeit. erfahren sie, wie wärmepumpen ihre heizkosten senken und von staatlichen förderprogrammen profitieren können.
**vorteile-von-warmepumpen-energieeffizienz-und-kosteneinsparungen**: vorheriger artikel · nächster artikel
**solaranlagen-auf-steildachern-nachhaltige-energie-fur-die-schweiz**: vorheriger artikel · nächster artikel
**technologie-fuer-private-solaranlagen**: vorheriger artikel · nächster artikel
**solaranlagen_einfuhrung**: nächster artikel

## Świadome różnice / do ręcznego dopracowania

**Wynik**: wszystkie 12 adresów → HTTP 200; 6 stron statycznych 100% tekstu; 6 artykułów 91–98% (braki opisane niżej); 0 zepsutych obrazów (zweryfikowane także po HTTP); brak poziomego scrolla na 375 px; font Roboto; title + description na każdej stronie (szablon CMS: dynamiczne `{Name} - MISSION GRÜNER WOHNEN` + `SEO Beschreibung`).

1. **Uproszczenia**
   - Slider „pp-magazine-slider” na Home → statyczna siatka 2 × (1 duży + 2 małe), wszystkie 6 artykułów.
   - FAQ (akordeon) → odpowiedzi widoczne od razu.
   - Artykuły: brak nawigacji „Vorheriger / Nächster Artikel” (WordPress) — główna przyczyna pokrycia < 98% w artykułach; „Weitere Artikel” pokazuje 2 najnowsze (na źródle: 2 najnowsze bez bieżącego) → `designer-todo.md` pkt 3–4.
   - Źródło nie ma H1 na Home i stronach lead — w Webflow dodano po 1 H1 (Home: „GRÜNE ENERGIE FÜR IHR HAUS”, lead: główny nagłówek); strony prawne bez H1 jak w źródle (H2).
   - Format daty w CMS: `January 8, 2025` zamiast `08/01/2025` → `designer-todo.md` pkt 2.
   - Social ikony (Facebook/LinkedIn) ze stopki artykułów pominięte — brak adresów docelowych na źródle.
2. **Pliki brakujące na źródle**: logo `mission-gruener-wohnen.de/.../mgw-logo-110px-60px.svg` (404) w pasku stron lead — pasek zostawiony pusty jak na źródle. Obrazek „Steildächer” na liście Ratgeber źródła nie ładuje się (miniatura) — w Webflow użyto oryginału.
3. **Teksty złożone przez agenta**: meta description stron Home, AGB, Datenschutz, Impressum, Solar, Wärmepumpe (źródło ich nie ma — zbudowane z tekstu strony); alt texty obrazów (źródło: puste).
4. **Linki do starej domeny (celowo 1:1)**: `http://www.mission-gruener-wohnen.ch` w treści AGB/Impressum; linki `?p=…&preview=true` w 4 artykułach (niedziałające linki podglądu WP także na źródle).
5. **Skrypty śledzące — nie dodane (polecenie użytkownika)**: Google Tag Manager + gtag (consent mode), Meta Pixel (`connect.facebook.net`), Outbrain (`amplify/tr/wave.outbrain.com`), Cookiebot (`consent.cookiebot.com`), Google Site Kit, ClickMagick (`cdn.clkmc.com/cmc.js` + odczyt cookie `_fbp` w widżecie stron lead). CTA na Home zachowują parametr `?pubid_affpubid=686_home` jak na źródle.
6. **Formularze (useleadbot, osadzone 1:1)**: na stagingu formularz się nie renderuje — API `api.useleadbot.com/lead-bots/generate` zwraca `400 no lead bot with such form token` dla obu tokenów (`GLFT-53M5…`, `GLFT-4AJS…`). **Ten sam błąd występuje dla adresu oryginalnego** (sprawdzone 2026-09-28) — tokeny są nieaktywne u dostawcy, to nie błąd migracji. Po aktywacji / nowych tokenach może być potrzebne dodanie `blank-migration-01.webflow.io` i docelowej domeny w useleadbot.
7. **`lang`**: `de-CH` ustawiany skryptem w head (źródło: błędnie `en-US`).
8. **Komponenty**: Site Header, Site Footer, Simple Header, Simple Footer, Lead Footer. Zmienne: kolekcja „MGW Tokens”.
9. **Adresy artykułów**: `/<slug>/` → `/ratgeber/<slug>` — przy przełączeniu domeny potrzebne przekierowania 301 (człowiek). Strony kampanijne WP (43) poza zakresem — lista w `intake.md`.
10. **`designer-todo.md`**: OG image szablonu, format daty, filtr „exclude current item”, opcjonalnie prev/next, favicon i język w Site Settings.

_Uwaga techniczna_: przeglądarka w sesji chmurowej sporadycznie gubi żądania przez proxy (`ERR_TOO_MANY_RETRIES`) — pojedyncze obrazy na zrzutach w `qa-screenshots/` mogą być puste, mimo że zwracają HTTP 200.
