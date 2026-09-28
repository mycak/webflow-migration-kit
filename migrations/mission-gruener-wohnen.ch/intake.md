# Intake — mission-gruener-wohnen.ch

- **Źródło**: https://mission-gruener-wohnen.ch (WordPress + Elementor), tryb B (tylko żywa strona)
- **Data**: 2026-09-28, sesja `cse_01Ybh9sdy8j5x7ruFCN4FXBz`
- **Projekt Webflow**: `Blank-migration-01` — site_id `6aba24f6e0f264400c443d76`, shortName `blank-migration-01`, staging https://blank-migration-01.webflow.io
- **Znacznik zajęcia**: strona-draft `migration-claim` (id `6aba35a4cd900e0a614fc569`)

## Zakres (polecenie użytkownika: „cała strona: strony z nawigacji i stopki, artykuły Ratgeber do CMS”)
| Strona | Slug | Skąd |
|---|---|---|
| Home | `/` | — |
| AGB | `/agb` | stopka |
| Datenschutzerklärung | `/datenschutz` | stopka |
| Impressum | `/impressum` | stopka |
| Solar (lead form) | `/solaranlage_m_e1` | CTA „Jetzt beraten lassen” (Solaranlage) na Home |
| Wärmepumpe (lead form) | `/waermepumpe_m_e1` | CTA „Jetzt beraten lassen” (Wärmepumpe) na Home |

Źródło nie ma menu w nagłówku — nawigacja to logo + przycisk CTA; stopka: AGB, Datenschutz, Impressum.

**CMS „Ratgeber”**: 6 wpisów WP (`/wp-json/wp/v2/posts`), kategorie Solar / Wärmepumpe. Slugi zachowane, strona szablonu kolekcji.
Uwaga: w WordPress wpisy są pod `/<slug>/`; w Webflow będą pod `/ratgeber/<slug>` → przekierowania 301 przy przełączeniu domeny (człowiek).

## Formularze
useleadbot (`#leadforms-embd-form`, `window.form_token`) na obu stronach lead form — **HtmlEmbed 1:1**.

## Skrypty śledzące — NIE przenoszone (polecenie użytkownika)
Tylko raport w `qa-report.md`: Outbrain, Meta Pixel, Cookiebot, Google Site Kit, ClickMagick (`cdn.clkmc.com/cmc.js` + skrypt czytający `_fbp` — osadzony w widżecie HTML stron lead form; pominięty jako skrypt śledzący), useleadbot pixel jest częścią osadzenia formularza (zostaje).

## Poza zakresem (decyzja człowieka)
43 strony kampanijne WP (`*_ty`, `*advertorial*`, `out_*`, `meta_*`, `tab_*`, `yt_*`, `webpage_*`, `treppenlift_y_e1`, `solaranlage_y_e1`, `solaranlage_m_b`, `solaranlage_m_adv1`, `was-kostet-eine-solaranlage-wirklich` …) — niepodlinkowane z nawigacji/stopki/Home.
