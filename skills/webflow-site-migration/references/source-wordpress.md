# Źródło: WordPress / Elementor

`audit.py` rozpoznaje WordPress/Elementor automatycznie (`platform` w `content/<slug>.json`) i próbuje REST API (`urls.json`: `wp_pages`, `wp_posts`).

## Treść
- Strony: `/wp-json/wp/v2/pages?per_page=100` — w WP z kampaniami bywa dużo landingów (`*_ty`, `*advertorial*`, `out_*`, `meta_*`, `tab_*`). Migruj tylko strony z zakresu (nawigacja, stopka, linki CTA) — resztę wypisz w intake jako „poza zakresem” do decyzji człowieka.
- Wpisy (poradnik/blog) → kolekcja CMS: `/wp-json/wp/v2/posts?per_page=100&_embed` (treść `content.rendered`, `date`, `categories`, `featured_media`). Kategorie: `/wp-json/wp/v2/categories`. Obrazki z treści podmień na assety Webflow.
- Brakujące/zepsute pliki: `/wp-json/wp/v2/media?search=<fragment nazwy>` pokazuje oryginały i alternatywy (np. logo w .webp gdy .svg zwraca 404 — sprawdź, czy brakuje go też na źródle).

## Tokeny (Elementor)
- `tokens.json > elementor_kit`: reguła `.elementor-kit-<id>` z `--e-global-color-primary/secondary/text/accent/...` i `--e-global-typography-*-font-family/size/weight`. To są kolory i typografia marki → Variables.
- Hover przycisków: reguła `.elementor-kit-<id> .elementor-button:hover` (w kit CSS).
- Font: link Google Fonts z `fonts` (zwykle ładuje wszystkie wagi — w Webflow dodaj tylko używane).

## Widżety (`sections[].items[].type`)
| Elementor | Webflow |
|---|---|
| `heading.default`, `text-editor.default` | Heading / Paragraph (zachowaj poziom nagłówka i rozmiar ze `style`) |
| `image.default` | Image + asset |
| `call-to-action.default` | karta: obraz (tło 200 px) + treść + przycisk |
| `icon-list.default` | lista z ✓ (lub ikoną SVG) |
| `button.default` | link z klasą `button` |
| `html.default` | HtmlEmbed z pełnym kodem (`html`) — formularze leadowe, skrypty śledzące per strona |
| `nav-menu.default` | linki w stopce/nawigacji |
| `pp-posts`, `posts` | lista wpisów → Collection List (CMS) albo statyczne karty |
| `pp-magazine-slider`, `slides`, `image-carousel` | uproszczenie: statyczna siatka (opisz w QA) |
| `pp-faq`, `accordion`, `toggle` | FAQ z odpowiedziami widocznymi (opisz w QA) |
| `eael-dual-color-header` | Heading + Paragraph |

## Pułapki
- `lang` w WP bywa błędny (`en-US` przy treści DE) — ustaw właściwy i odnotuj.
- Tagline/teksty w nagłówku często mają `<br>` — zachowaj podziały linii.
- `[shortcode]` widoczny dosłownie w HTML (np. `[cmc_vid]`) — zostaw 1:1, to część osadzenia.
- Cookiebot/consent blokuje skrypty do zgody — audyt tylko ukrywa baner (DOM), nigdy nie klika zgody.
