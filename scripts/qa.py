#!/usr/bin/env python3
"""QA of the migrated Webflow staging site against the audit snapshot.

For each audited page: open the staging URL at 1440 and 375 px and check
status, title/description, H1 count, broken images, horizontal overflow,
web font loading, links still pointing to the old domain, text coverage
(share of source text lines found on the new page), and screenshot both.

Usage:
  python3 scripts/qa.py migrations/<domain> https://<shortName>.webflow.io [--map /old-path=/new-path ...]
Writes migrations/<domain>/qa.json and qa-report.md (draft for the agent to complete).
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

from _browser import launch_browser, hide_consent_banners, goto

CHECK_JS = r"""
(oldHost) => ({
  title: document.title,
  description: document.querySelector('meta[name=description]')?.content || null,
  lang: document.documentElement.lang,
  h1: document.querySelectorAll('h1').length,
  broken_images: [...document.images].filter(i => !(i.complete && i.naturalWidth > 0)).map(i => i.currentSrc || i.src),
  images: document.images.length,
  overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
  font: getComputedStyle(document.querySelector('main p, main h1, main h2, p, h1, h2') || document.body).fontFamily,
  old_domain_links: [...new Set([...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => h.includes(oldHost)))],
  text: document.body.innerText,
})
"""


def norm_lines(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", l).strip().lower() for l in text.splitlines() if len(l.strip()) > 12]


def http_broken(urls):
    """The browser can report an image as broken when a proxy drops the request
    (net::ERR_TOO_MANY_RETRIES in cloud sessions). Keep only images that also fail over plain HTTP."""
    import requests
    out = []
    for u in urls:
        try:
            r = requests.get(u, timeout=30)
            if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image"):
                out.append(u)
        except Exception:
            out.append(u)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("migration_dir")
    ap.add_argument("staging")
    ap.add_argument("--map", nargs="*", default=[], help="old-path=new-path overrides")
    a = ap.parse_args()
    mig = Path(a.migration_dir)
    inv = json.loads((mig / "inventory.json").read_text())
    old_host = inv["domain"]
    overrides = dict(x.split("=", 1) for x in a.map)
    shots = mig / "qa-screenshots"
    shots.mkdir(exist_ok=True)
    results = []
    with sync_playwright() as p:
        b = launch_browser(p)
        for pg in inv["pages"]:
            if "error" in pg:
                continue
            src = json.loads((mig / "content" / f"{pg['slug']}.json").read_text())
            path = urlparse(pg["url"]).path or "/"
            path = overrides.get(path, path)
            url = urljoin(a.staging.rstrip("/") + "/", path.lstrip("/"))
            row = {"slug": pg["slug"], "source": pg["url"], "staging": url}
            for width, height in ((1440, 900), (375, 812)):
                ctx = b.new_context(viewport={"width": width, "height": height})
                page = ctx.new_page()
                resp = goto(page, url)
                for _ in range(3):  # a proxy-dropped stylesheet fakes overflow/font failures: reload
                    if page.evaluate("() => [...document.querySelectorAll('link[rel=stylesheet]')].every(l => l.sheet)"):
                        break
                    resp = goto(page, url)
                hide_consent_banners(page)
                page.wait_for_timeout(600)
                d = page.evaluate(CHECK_JS, old_host)
                page.screenshot(path=str(shots / f"{pg['slug']}-{width}.png"), full_page=True)
                if width == 1440:
                    src_lines = norm_lines(src["text"])
                    new_text = re.sub(r"\s+", " ", d["text"]).lower()
                    missing = [l for l in src_lines if l not in new_text]
                    row.update(status=resp.status if resp else None, title=d["title"], description=d["description"],
                               lang=d["lang"], h1=d["h1"], images=d["images"], broken_images=http_broken(d["broken_images"]),
                               font=d["font"], old_domain_links=d["old_domain_links"],
                               text_coverage=round(1 - len(missing) / max(1, len(src_lines)), 3),
                               missing_text=missing[:30], source_h1=sum(1 for h in src["headings"] if h["tag"] == "h1"))
                else:
                    row["mobile_overflow"] = d["overflow"]
                ctx.close()
            results.append(row)
        b.close()
    (mig / "qa.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))

    lines = ["# QA – " + inv["domain"] + " → " + a.staging, "",
             "| Strona | HTTP | Tekst | Obrazy (zepsute) | H1 (źródło) | Mobile overflow | Linki do starej domeny |",
             "|---|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| [{r['slug']}]({r['staging']}) | {r.get('status')} | {r.get('text_coverage', 0):.0%} | "
                     f"{r.get('images')} ({len(r.get('broken_images', []))}) | {r.get('h1')} ({r.get('source_h1')}) | "
                     f"{'⚠️' if r.get('mobile_overflow') else 'OK'} | {len(r.get('old_domain_links', []))} |")
    lines += ["", "## Brakujące teksty (max 30 na stronę)", ""]
    for r in results:
        if r.get("missing_text"):
            lines.append(f"**{r['slug']}**: " + " · ".join(r["missing_text"][:10]))
    lines += ["", "## Świadome różnice / do ręcznego dopracowania", "", "_(uzupełnia agent)_", ""]
    (mig / "qa-report.md").write_text("\n".join(lines))
    print(json.dumps([{k: r.get(k) for k in ("slug", "status", "text_coverage", "broken_images", "mobile_overflow")} for r in results],
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
