"""Shared headless-browser helpers for the migration scripts.

Works both locally and in Claude Code cloud sessions:
- honours HTTPS_PROXY / HTTP_PROXY (cloud sessions route egress through a proxy),
- finds Chromium via PLAYWRIGHT_CHROMIUM_EXECUTABLE, the Playwright cache, or /opt/pw-browsers.
"""
import os
from pathlib import Path

CONSENT_SELECTORS = [
    "#CybotCookiebotDialog", "#CybotCookiebotDialogBodyUnderlay", "#usercentrics-root", "#onetrust-consent-sdk",
    "#cookie-law-info-bar", ".cky-consent-container", "#cmplz-cookiebanner-container", ".cc-window", "#moove_gdpr_cookie_info_bar",
]


def _executable():
    env = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    if env and Path(env).exists():
        return env
    for cand in ("/opt/pw-browsers/chromium", "/usr/bin/chromium", "/usr/bin/chromium-browser"):
        if Path(cand).exists() and Path(cand).is_file():
            return cand
    return None  # let Playwright use its own downloaded browser


def launch_browser(p):
    kwargs = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
    exe = _executable()
    if exe:
        kwargs["executable_path"] = exe
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or os.environ.get("HTTP_PROXY")
    if proxy:
        bypass = [h.strip() for h in os.environ.get("NO_PROXY", "").split(",") if h.strip() and "/" not in h]
        kwargs["proxy"] = {"server": proxy, "bypass": ",".join(["<-loopback>", "localhost", "127.0.0.1"] + bypass)}
    browser = p.chromium.launch(**kwargs)
    # every context ignores TLS errors: cloud proxies may re-sign certificates
    orig = browser.new_context
    browser.new_context = lambda **kw: orig(ignore_https_errors=True, **kw)
    return browser


def hide_consent_banners(page):
    """Hide cookie banners via DOM only. Never click consent buttons."""
    sel = ",".join(CONSENT_SELECTORS)
    page.evaluate(f"""() => document.querySelectorAll('{sel}').forEach(e => e.style.setProperty('display','none','important'))""")
