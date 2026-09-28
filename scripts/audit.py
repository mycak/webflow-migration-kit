#!/usr/bin/env python3
"""Audit a live website for migration to Webflow (no repository access needed).

Reads the source site with headless Chromium (Playwright) and writes a
reproducible snapshot to migrations/<domain>/:

  inventory.json        pages, sections, texts, links, images, embeds, meta
  tokens.json           design tokens (colors, fonts, Elementor kit vars)
  scripts.json          tracking / consent scripts found on the site
  urls.json             discovered URLs (WP REST, sitemap, navigation)
  screenshots/<slug>-{1440,375}.png

Usage:
  python3 scripts/audit.py https://example.com [--pages / /about] [--max-pages 30]

Exit codes: 0 ok, 2 bad input, 3 source blocked (bot protection / geo / network).
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

from _browser import launch_browser, hide_consent_banners

BLOCK_MARKERS = re.compile(
    r"(just a moment|attention required|cf-browser-verification|captcha|access denied|"
    r"verify you are human|ddos protection)", re.I)

EXTRACT_JS = r"""
() => {
  const cs = (el, props) => { if (!el) return null; const s = getComputedStyle(el); const o = {}; props.forEach(p => o[p] = s.getPropertyValue(p)); return o; };
  const T = ['font-family','font-size','font-weight','line-height','color','letter-spacing','text-transform','text-align'];
  const meta = n => document.querySelector(`meta[name="${n}"],meta[property="${n}"]`)?.content || null;
  const abs = u => { try { return new URL(u, location.href).href } catch(e) { return u } };

  // ---- sections: Elementor-aware, generic fallback ----
  const root = document.querySelector('[data-elementor-type="wp-page"],[data-elementor-type="wp-post"]')
            || document.querySelector('main') || document.body;
  const topLevel = [...root.children].filter(e => e.offsetHeight > 0 && !['SCRIPT','STYLE','NOSCRIPT','LINK'].includes(e.tagName));
  function widgetList(el) {
    const ws = [...el.querySelectorAll('[data-widget_type]')];
    if (ws.length) return ws.map(w => {
      const t = w.dataset.widget_type;
      const o = { type: t, text: (w.innerText || '').trim() };
      const imgs = [...w.querySelectorAll('img')].map(i => ({ src: abs(i.currentSrc || i.src), alt: i.alt || '' }));
      const bgs = [...w.querySelectorAll('*')].map(x => getComputedStyle(x).backgroundImage).filter(b => b && b.startsWith('url('))
                    .map(b => abs(b.slice(4, -1).replace(/["']/g, '')));
      if (imgs.length) o.images = imgs;
      if (bgs.length) o.background_images = [...new Set(bgs)];
      const links = [...w.querySelectorAll('a[href]')].map(a => ({ text: a.innerText.trim(), href: a.getAttribute('href') }));
      if (links.length) o.links = links;
      if (t && t.startsWith('html')) o.html = w.querySelector('.elementor-widget-container')?.innerHTML || w.innerHTML;
      const tx = w.querySelector('h1,h2,h3,h4,h5,h6,p,a,span,li');
      if (tx) o.style = cs(tx, T);
      return o;
    });
    // generic: headings, paragraphs, lists, images, links in order
    return [...el.querySelectorAll('h1,h2,h3,h4,h5,h6,p,li,img,a.button,a[class*=btn],button,iframe')]
      .map(n => n.tagName === 'IMG' ? { type: 'img', src: abs(n.currentSrc || n.src), alt: n.alt || '' }
             : n.tagName === 'IFRAME' ? { type: 'iframe', src: n.src }
             : { type: n.tagName.toLowerCase(), text: (n.innerText || '').trim(), href: n.getAttribute('href') || undefined, style: cs(n, T) });
  }
  const sections = topLevel.map((s, i) => {
    const st = getComputedStyle(s); const r = s.getBoundingClientRect();
    return { index: i, tag: s.tagName.toLowerCase(), classes: String(s.className).slice(0, 200),
      height: Math.round(r.height), background_color: st.backgroundColor, background_image: st.backgroundImage !== 'none' ? st.backgroundImage : null,
      padding: st.padding, items: widgetList(s) };
  });

  // ---- tokens ----
  const kitVars = [];
  for (const ss of document.styleSheets) { let rules; try { rules = ss.cssRules } catch (e) { continue }
    for (const r of rules) if (r.selectorText && /\.elementor-kit-\d+$/.test(r.selectorText.trim())) kitVars.push(r.cssText); }
  const rootVars = {}; const rs = getComputedStyle(document.documentElement);
  for (const p of rs) if (p.startsWith('--')) rootVars[p] = rs.getPropertyValue(p).trim();

  const scripts = [...document.querySelectorAll('script,noscript')].map(s => ({ tag: s.tagName.toLowerCase(), src: s.src || null,
      attrs: Object.fromEntries([...s.attributes].map(a => [a.name, a.value])), text: (s.text || s.innerHTML || '').trim().slice(0, 4000) }))
    .filter(s => /gtm|gtag|googletagmanager|fbq|facebook\.net|cookiebot|usercentrics|onetrust|clarity|hotjar|tiktok|linkedin|taboola|outbrain|matomo|plausible/i.test((s.src||'') + s.text + JSON.stringify(s.attrs)));

  return {
    url: location.href, title: document.title, lang: document.documentElement.lang || null,
    meta: { description: meta('description'), robots: meta('robots'), og_title: meta('og:title'), og_description: meta('og:description'),
            og_image: meta('og:image'), canonical: document.querySelector('link[rel=canonical]')?.href || null,
            generator: [...document.querySelectorAll('meta[name=generator]')].map(m => m.content),
            favicon: document.querySelector('link[rel*=icon]')?.href || null },
    headings: [...document.querySelectorAll('h1,h2,h3')].map(h => ({ tag: h.tagName.toLowerCase(), text: h.innerText.trim() })),
    text: document.body.innerText,
    links: [...new Set([...document.querySelectorAll('a[href]')].map(a => abs(a.getAttribute('href'))))],
    images: [...document.images].map(i => ({ src: abs(i.currentSrc || i.src), alt: i.alt || '', w: i.naturalWidth, h: i.naturalHeight })),
    iframes: [...document.querySelectorAll('iframe')].map(f => f.src),
    forms: [...document.querySelectorAll('form')].map(f => ({ action: f.action, fields: [...f.elements].map(e => ({ name: e.name, type: e.type, required: e.required })) })),
    sections,
    styles: { body: cs(document.body, [...T, 'background-color']), h1: cs(document.querySelector('h1'), T), h2: cs(document.querySelector('h2'), T),
              h3: cs(document.querySelector('h3'), T), p: cs(document.querySelector('p'), T),
              button: cs(document.querySelector('.elementor-button, .button, .btn, button'), [...T, 'background-color', 'border-radius', 'padding']) },
    elementor_kit: kitVars, root_vars: rootVars,
    fonts: [...document.querySelectorAll('link[href*="fonts.googleapis"],link[href*="use.typekit"]')].map(l => l.href),
    scripts,
    platform: {
      wordpress: !!document.querySelector('link[href*="wp-content"],script[src*="wp-content"]'),
      elementor: !!document.querySelector('[data-elementor-type]'),
      nextjs: !!document.querySelector('script#__NEXT_DATA__'), wix: /wix/i.test(document.documentElement.outerHTML.slice(0, 20000)),
      webflow: !!document.documentElement.dataset.wfSite, squarespace: /squarespace/i.test(document.documentElement.outerHTML.slice(0, 20000)),
    },
  };
}
"""


def slugify(url: str) -> str:
    path = urlparse(url).path.strip("/")
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", path) or "home"


def check_blocked(resp, page) -> str | None:
    if resp is None:
        return "no response"
    if resp.status in (401, 403, 407, 429, 451, 503):
        return f"HTTP {resp.status} (blocked: bot protection, geo-blocking or network allowlist)"
    if resp.status >= 400:
        return f"HTTP {resp.status}"
    head = (page.title() or "") + " " + page.content()[:5000]
    if BLOCK_MARKERS.search(head):
        return "bot protection page detected"
    return None


def discover_urls(page, base: str) -> dict:
    found = {"wp_pages": [], "wp_posts": [], "sitemap": [], "nav": []}
    req = page.context.request
    for kind, ep in (("wp_pages", "/wp-json/wp/v2/pages?per_page=100&_fields=id,slug,link,title,parent,status"),
                     ("wp_posts", "/wp-json/wp/v2/posts?per_page=100&_fields=id,slug,link,title,date,categories,featured_media")):
        try:
            r = req.get(urljoin(base, ep), timeout=20000)
            if r.ok and "json" in (r.headers.get("content-type") or ""):
                found[kind] = [{"link": x["link"], "slug": x["slug"], "title": x["title"]["rendered"],
                                **({"date": x["date"], "categories": x.get("categories")} if kind == "wp_posts" else {})}
                               for x in r.json()]
        except Exception:
            pass
    for sm in ("/sitemap.xml", "/sitemap_index.xml", "/wp-sitemap.xml"):
        try:
            r = req.get(urljoin(base, sm), timeout=20000)
            if r.ok:
                locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r.text())
                found["sitemap"].extend(locs)
        except Exception:
            pass
    host = urlparse(base).netloc
    found["nav"] = sorted({u.split("#")[0].split("?")[0] for u in page.eval_on_selector_all(
        "header a[href], nav a[href], footer a[href]", "els => els.map(a => a.href)") if urlparse(u).netloc == host})
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--pages", nargs="*", help="paths or URLs to audit (default: home + nav links)")
    ap.add_argument("--max-pages", type=int, default=30)
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-screenshots", action="store_true")
    a = ap.parse_args()

    base = a.url.rstrip("/") + "/"
    domain = urlparse(base).netloc
    if not domain:
        print("Invalid URL", file=sys.stderr)
        sys.exit(2)
    out = Path(a.out or f"migrations/{domain}")
    (out / "screenshots").mkdir(parents=True, exist_ok=True)
    (out / "content").mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = launch_browser(p)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, locale="de-CH",
                                  user_agent=None)
        page = ctx.new_page()
        try:
            resp = page.goto(base, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(json.dumps({"blocked": True, "reason": f"network: {e}".splitlines()[0]}))
            sys.exit(3)
        reason = check_blocked(resp, page)
        if reason:
            print(json.dumps({"blocked": True, "reason": reason, "url": base}))
            sys.exit(3)

        urls = discover_urls(page, base)
        (out / "urls.json").write_text(json.dumps(urls, indent=2, ensure_ascii=False))

        if a.pages:
            targets = [urljoin(base, x) for x in a.pages]
        else:
            nav = urls["nav"] or [u for u in urls["sitemap"] if urlparse(u).netloc == domain]
            targets = [base] + [u for u in nav if u.rstrip("/") + "/" != base]
        seen, ordered = set(), []
        for t in targets:
            k = t.rstrip("/")
            if k not in seen:
                seen.add(k)
                ordered.append(t)
        ordered = ordered[: a.max_pages]

        inventory = {"source": base, "domain": domain, "discovered": {k: len(v) for k, v in urls.items()}, "pages": []}
        all_scripts, tokens = {}, {}
        for url in ordered:
            try:
                resp = page.goto(url, wait_until="networkidle", timeout=60000)
            except Exception:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
            reason = check_blocked(resp, page)
            slug = slugify(url)
            if reason:
                inventory["pages"].append({"url": url, "slug": slug, "error": reason})
                continue
            hide_consent_banners(page)
            page.wait_for_timeout(800)
            data = page.evaluate(EXTRACT_JS)
            data["status"] = resp.status if resp else None
            data["slug"] = slug
            (out / "content" / f"{slug}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
            for s in data.pop("scripts"):
                all_scripts[(s["src"] or "") + s["text"][:200]] = s
            if not tokens:
                tokens = {"styles": data["styles"], "elementor_kit": data["elementor_kit"], "root_vars": data["root_vars"], "fonts": data["fonts"]}
            if not a.no_screenshots:
                page.screenshot(path=str(out / "screenshots" / f"{slug}-1440.png"), full_page=True)
                page.set_viewport_size({"width": 375, "height": 812})
                page.wait_for_timeout(500)
                page.screenshot(path=str(out / "screenshots" / f"{slug}-375.png"), full_page=True)
                page.set_viewport_size({"width": 1440, "height": 900})
            inventory["pages"].append({
                "url": url, "slug": slug, "title": data["title"], "lang": data["lang"], "meta": data["meta"],
                "headings": data["headings"], "sections": len(data["sections"]), "images": len(data["images"]),
                "forms": len(data["forms"]), "platform": data["platform"],
                "html_widgets": sum(1 for s in data["sections"] for i in s["items"] if str(i.get("type", "")).startswith("html")),
            })
        browser.close()

    (out / "inventory.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False))
    (out / "tokens.json").write_text(json.dumps(tokens, indent=2, ensure_ascii=False))
    (out / "scripts.json").write_text(json.dumps(list(all_scripts.values()), indent=2, ensure_ascii=False))
    print(json.dumps({"ok": True, "out": str(out), "pages": [p["slug"] for p in inventory["pages"]],
                      "errors": [p for p in inventory["pages"] if "error" in p], "discovered": inventory["discovered"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
