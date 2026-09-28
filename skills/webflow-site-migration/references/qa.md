# QA migracji

`scripts/qa.py` daje twarde metryki; agent dopisuje ocenę wizualną i listę różnic.

## Kryteria „gotowe do akceptacji”
- każda strona z zakresu odpowiada HTTP 200 na `https://<shortName>.webflow.io/<slug>`,
- pokrycie tekstu (`text_coverage`) ≥ 98% — brakujące linie z `missing_text` albo uzupełnij, albo uzasadnij (np. tekst z wyłączonego slidera),
- 0 zepsutych obrazów, alt texty obecne,
- brak poziomego scrolla na 375 px (`mobile_overflow: false`),
- title/description/OG na każdej stronie; liczba H1 jak w źródle (lub 1),
- font marki załadowany (`font`),
- zrzuty `qa-screenshots/<slug>-1440.png` i `-375.png` obejrzane i porównane ze `screenshots/` źródła.

## Zewnętrzne formularze i skrypty
Jeśli osadzony formularz (useleadbot, HubSpot, Typeform…) nie renderuje się na stagingu, sprawdź to samo na oryginale tą samą przeglądarką (Playwright MCP: `browser_navigate` + `browser_network_requests`). Ten sam błąd na oryginale = zgodność, nie błąd migracji; zapisz, że dostawca może wymagać dodania domeny stagingu do listy dozwolonych.

## Raport (`qa-report.md`)
Uzupełnij sekcję „Świadome różnice / do ręcznego dopracowania”:
1. uproszczenia (slider → siatka, akordeon → widoczne odpowiedzi),
2. pliki brakujące także na źródle i użyte zamienniki,
3. teksty złożone przez agenta (np. meta description, gdy źródło jej nie ma),
4. linki nadal prowadzące do starej domeny (celowo: artykuły/prawne poza zakresem),
5. skrypty śledzące: dodane / czekające na zgodę; domeny do dodania w Cookiebot/formularzach,
6. `lang` ustawiony skryptem,
7. zawartość `designer-todo.md`.
