# Webflow migration kit

To repozytorium służy do powtarzalnej migracji żywych stron do Webflow w sesjach Claude Code (chmura lub lokalnie).

- Każdą migrację prowadź skillem `webflow-site-migration` (`skills/webflow-site-migration/SKILL.md`); przed pierwszą migracją w nowym środowisku uruchom `migration-preflight`.
- Skrypty: `scripts/audit.py` (odczyt źródła), `scripts/assets.py` (obrazy → Webflow bez Designera), `scripts/qa.py` (QA stagingu), `scripts/preflight.py`, `scripts/guard.py` (hook bezpieczeństwa).
- Wyniki każdej migracji: `migrations/<domena>/` — commituj je na gałąź `migration/<domena>` razem z raportem QA.
- Nigdy nie publikuj na domenę klienta, nie używaj Designera, nie dodawaj skryptów śledzących bez zgody, nie obchodź zabezpieczeń źródła.
- Rozmawiaj z użytkownikiem po polsku, chyba że pisze w innym języku.
