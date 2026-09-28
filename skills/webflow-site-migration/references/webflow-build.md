# Budowa w Webflow przez MCP (bez Designera)

Sprawdzone na Webflow MCP 2.1. Wszystkie narzędzia poniżej działają bez otwartego Designera (podaj `siteId` + `pageId`).

## Sesja MCP
- `webflow_guide_tool` raz na sesję z `session_id: "start"`; wynik jest bardzo duży — przeszukuj zapisany plik (`jq -r '.[].text' | grep`), nie czytaj całości.
- Każde kolejne wywołanie: ten sam `ses_…` i stały `agent_id` (np. `opus|cc-cloud|mig01`).
- Nazwy narzędzi zależą od sposobu podłączenia (`mcp__Webflow__…`, `mcp__claude_ai_Webflow__…`, `mcp__webflow__…`) — szukaj po końcówce (`data_pages_tool` itd.).

## Kolejność
1. **Strony** — `data_pages_tool > create_page` (title, slug = stary slug, `seo`, `openGraph`); Home istnieje: `update_page_settings`.
2. **Obrazy** — `scripts/assets.py` (niżej). Nie używaj `asset_tool > upload_image_by_url` (wymaga Designera; odrzuca pliki bez Content-Type).
3. **Head strony** — `data_scripts_tool > set_site_freeform_code` (location `head`): link Google Fonts + `<script>document.documentElement.lang='xx-XX'</script>` (API nie ustawia `lang`; odnotuj w QA). Zapis zastępuje cały blok — przy późniejszym dodawaniu skryptów śledzących wstaw całość ponownie.
4. **Variables** — `data_variable_tool > create_variable_collection` („<Marka> Tokens”), potem `create_color_variable` / `create_font_family_variable` / `create_size_variable`. Zapisz id zmiennych w `migrations/<domena>/webflow-ids.json`.
5. **Sekcje** — `data_whtml_builder` do elementu Body (id z `data_element_tool > get_all_elements` depth 0). Owijka: `div.page-wrapper` (font + kolor bazowy), potem `section > padding-global > container-large > …`.
6. **Poprawki po każdym wstawieniu** (obowiązkowe):
   - `<img src>` NIE podpina assetu → `data_element_tool > query_elements` (`element_filter.type: "Image"`, limit 100) i `set_image_asset` dla każdego obrazu w kolejności dokumentu, wg `assets/asset-map.json`.
   - `var(--…)` w CSS NIE wiąże się ze zmiennymi (ostrzeżenie `unknown_variable`) → w CSS pisz hex/px, potem `data_style_tool > update_style` z `variable_as_value` (kolory, `font-family`, `max-width`; hover przez `pseudo: "hover"`).
7. **Osadzenia** (formularze zewnętrzne, skrypty per strona) — w HTML zostaw pusty kontener (np. `div.lp_form`), potem `data_element_builder` (`type: "HtmlEmbed"`, parent = kontener) i `data_element_settings_tool > set_settings` z `key: "code"`, `static_text.value` = pełny kod z `content/<slug>.json` (pole `html` widżetu).
8. **CMS** — `data_cms_tool`: `create_collection`, `create_collection_static_field` / `create_collection_reference_field`, `create_collection_items` (draft). Szablon i Collection List: `data_element_builder` `type: "CMSCollection"` + wiązania przez `data_element_settings_tool > get_bindable_sources` / `set_settings`.

## Ograniczenia `data_whtml_builder`
- max 5 akcji na wywołanie; `html` = jeden element główny; CSS bez `<style>` i `@keyframes`;
- tylko media queries Webflow: `@media screen and (max-width: 991px)`, `767px`, `479px`;
- klasy z CSS stają się globalnymi stylami — reużywaj ich na kolejnych stronach (wtedy wystarczy sam HTML);
- `<details>`, `<summary>`, sliders — nie polegaj na nich; akordeon/slider upraszczaj i opisz w QA (albo `designer-todo.md`).

## Obrazy — ścieżka headless
```
python3 KIT/scripts/assets.py prepare migrations/<domena>
# dla każdego wpisu z assets/manifest.json (pole file, md5):
#   data_assets_tool > create_asset { site_id, file_name: <file>, file_hash: <md5> }
#   zapisz CAŁY obiekt result do migrations/<domena>/assets/uploads/<file>.json (Write, dokładnie jak zwrócony)
python3 KIT/scripts/assets.py upload migrations/<domena>
```
- `prepare` pobiera oryginał bez sufiksu `-300x200` (WordPress), konwertuje webp/nieznane do PNG/JPEG, liczy MD5.
- `upload` wysyła do S3 (presigned POST), sprawdza CDN (200) i tworzy `asset-map.json`. Presigned URL wygasa po ~1 h — przy błędzie 403 ponów `create_asset`.
- Alt texty: `data_assets_tool > update_asset` (alt z audytu; brak → opisowy, odnotuj w QA).
- Foldery assetów (`create_asset_folder`) są nieusuwalne — tylko po potwierdzeniu.

## Publikacja
`data_sites_tool > publish_site { site_id, publishToWebflowSubdomain: true, customDomains: [] }` → `https://<shortName>.webflow.io`. Nigdy custom domain (hook blokuje).

## Skrypty śledzące (po zgodzie)
Ze `scripts.json`: consent (Cookiebot/Usercentrics…) jako pierwszy w head, consent-mode default, GTM (raz, nawet jeśli źródło ładowało go 2×), `noscript` GTM w `footer`. Pixel ładowany przez GTM (skrypt bez `src` z `fbq("init")` wstrzyknięty dynamicznie) NIE dodawaj osobno. Zachowaj atrybuty (np. `data-culture`). Cookiebot pokaże baner na `*.webflow.io` dopiero po dodaniu tej domeny w Cookiebot Managerze — zapisz w QA.

## Błędy
401/403 — nie ponawiaj; 429 — odczekaj; 5xx przy zapisie — najpierw sprawdź stan (`get_all_elements`, `query_styles`), potem ponów.
