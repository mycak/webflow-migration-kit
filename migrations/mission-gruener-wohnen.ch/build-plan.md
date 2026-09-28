# Plan budowy — mission-gruener-wohnen.ch → Blank-migration-01

## Strony (slug = stary slug)
| Źródło | Webflow | Budowa |
|---|---|---|
| `/` | Home | Site Header (komponent) · intro H1 · 2 karty CTA · siatka 6 artykułów (zamiast slidera) · Ratgeber (Collection List, 4 najnowsze) · FAQ · Site Footer (komponent) |
| `/agb/`, `/datenschutz/`, `/impressum/` | `/agb`, `/datenschutz`, `/impressum` | Simple Header (logo, linia) · treść 1:1 z WP REST · Simple Footer |
| `/solaranlage_m_e1/`, `/waermepumpe_m_e1/` | te same slugi | zielony pasek · H1/H2 · HtmlEmbed useleadbot 1:1 · odznaka · lista zalet · Lead Footer (komponent) |
| wpisy WP `/<slug>/` | CMS „Ratgeber” → `/ratgeber/<slug>` | szablon: Simple Header · H1 · data \| autor · obraz · excerpt · Rich Text · CTA · „Weitere Artikel” (Collection List) · Site Footer · © |

## Tokeny (Variables „MGW Tokens”)
Primary `#184B44`, Secondary `#80CC28`, Text `#383838`, Accent `#FF3131`, White, Border `#D9D9D9`, Surface `#F7F9F8`, Font Primary `Roboto`, Container Max `1140px`.

## CMS „Ratgeber” (`ratgeber`)
Pola: Name, Slug, Kategorie (Option: Solar / Wärmepumpe), Datum, Autor, Beitragsbild, Auszug, Inhalt (Rich Text), SEO Beschreibung. 6 itemów, opublikowane.

## Osadzenia
useleadbot (`get-pixel-script.js` + `window.form_token` + `#leadforms-embd-form`) — 1:1. ClickMagick (`cdn.clkmc.com/cmc.js`, odczyt `_fbp`) pominięty jako skrypt śledzący.

## Uproszczenia
- `pp-magazine-slider` → statyczna siatka 2×(1 duży + 2 małe), wszystkie 6 artykułów.
- `pp-faq` (akordeon) → odpowiedzi widoczne.
- Nawigacja „Vorheriger / Nächster Artikel” w artykułach — pominięta (brak natywnej funkcji w Webflow CMS).
