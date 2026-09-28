# Audyt sesji — migracja mission-gruener-wohnen.ch

Źródło danych: zapis sesji Claude Code (pola `usage` każdego wywołania modelu, znaczniki czasu). Model: Claude Opus 5.5.
Cennik API (za 1 mln tokenów): wejście $4, wyjście $20, zapis cache (TTL 1 h) $8, odczyt cache $0,20.

## Czas

| Etap | Od–do (UTC) | Czas |
|---|---|---|
| Setup repo + preflight | 09:07 → 09:19 | ~12 min |
| Migracja (audyt → budowa → staging → QA → raport → commit) | 09:19 → 11:09 | ~1 h 50 min |
| **Razem do oddania migracji** | 09:07 → 11:09 | **~2 h 03 min** |

W migracji ok. 40 min to przebiegi QA w przeglądarce, spowolnione przez sporadyczne zrywanie połączeń przez proxy chmury. Zostało to już poprawione w kicie.

## Tokeny i koszt (ekwiwalent cen API)

| Etap | Wywołania modelu | Wyjście | Zapis cache | Odczyt cache | Koszt |
|---|---|---|---|---|---|
| Setup + preflight | 18 | 7 061 | 52 963 | 1 269 909 | $0,82 |
| Migracja | 193 | 151 048 | 471 840 | 73 314 059 | $21,45 |
| **Razem** | **211** | **158 109** | **524 803** | **74 583 968** | **$22,27** |

Tokeny wejścia bez cache: 422 (pomijalne). Łącznie przetworzono ok. 75,3 mln tokenów, z czego 99% to tańsze odczyty cache.

Struktura kosztu migracji:
- odczyty cache: 68% ($14,66),
- zapis cache: 18% ($3,77),
- wyjście: 14% ($3,02).

Koszt rośnie głównie z długością kontekstu: każde wywołanie ponownie czyta całą dotychczasową rozmowę (z cache).

**Uwaga:** jeśli sesja działała w ramach planu Claude (Team, Max lub Enterprise), nie ma osobnej faktury — zużycie liczy się do limitu planu. Kwota powyżej to równowartość przy rozliczeniu przez API.

## Gdzie można taniej przy kolejnych migracjach
1. **QA bez przeglądarki MCP**: tylko `qa.py` w tle, bez ręcznych zrzutów w kontekście.
2. **Treści CMS wgrywane skryptem przez Data API** zamiast wklejania HTML w wywołania MCP. Około 50 KB tekstu artykułów przechodziło przez kontekst dwukrotnie.
3. **Krótsze odpowiedzi narzędzi**: `return_element_info: false`, mniejsze zapytania `query_elements`.
4. **Podział na subagentów**, np. osobny agent do CMS. Główny kontekst rośnie wolniej.

Szacunkowo pozwoli to zejść do ok. $10–15 za podobną stronę; wymaga pomiaru na kolejnej migracji.
