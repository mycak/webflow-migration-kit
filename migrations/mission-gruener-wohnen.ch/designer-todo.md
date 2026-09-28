# Designer — do ręcznego dopracowania (nie da się przez Data API)

1. **Szablon Ratgeber — OG image**: Title i Meta Description są już dynamiczne (ustawione przez API); w Page Settings podepnij jeszcze Open Graph Image = `Beitragsbild`.
2. **Format daty** (Home: lista Ratgeber, szablon artykułu): ustaw format `DD/MM/YYYY` jak na źródle (API wiąże pole, ale nie ustawia formatu).
3. **„Weitere Artikel”** na szablonie: w ustawieniach Collection List włącz filtr „Exclude current Ratgeber item” (dziś pokazuje 2 najnowsze).
4. **Opcjonalnie**: nawigacja „Vorheriger / Nächster Artikel” (źródło ma ją z WordPressa) — wymaga np. Finsweet CMS Prev/Next albo ręcznych pól referencyjnych.
5. **Favicon / Webclip**: Site Settings → Favicon (`3.png` jest w Assets; na razie ustawiony przez `<link rel="icon">` w head).
6. **Język strony**: Site Settings → Localization → `de-CH` (na razie `lang` ustawiany skryptem w head).
