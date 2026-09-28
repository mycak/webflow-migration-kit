#!/usr/bin/env python3
"""Preflight for a migration run: tools, browser, network.

Usage: python3 scripts/preflight.py [SOURCE_URL]
Prints JSON with ok/fail per check and a 'fix' hint. Exit 1 if anything required fails.
"""
import importlib
import json
import sys

REQUIRED_HOSTS = [
    "https://webflow-prod-assets.s3.amazonaws.com/",  # image upload (presigned S3 POST)
    "https://cdn.prod.website-files.com/",            # uploaded asset verification
    "https://webflow.io/",                            # staging QA (*.webflow.io)
    "https://fonts.googleapis.com/",
]


def check_http(url):
    import requests
    try:
        r = requests.get(url, timeout=20, allow_redirects=True)
        return {"ok": r.status_code < 500 and r.status_code not in (403, 407), "status": r.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e).splitlines()[0][:200]}


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else None
    res = {}
    for mod in ("playwright", "PIL", "requests"):
        try:
            importlib.import_module(mod)
            res[f"python:{mod}"] = {"ok": True}
        except Exception as e:
            res[f"python:{mod}"] = {"ok": False, "error": str(e), "fix": "pip install -r requirements.txt"}
    try:
        from playwright.sync_api import sync_playwright
        sys.path.insert(0, __file__.rsplit("/", 1)[0])
        from _browser import launch_browser
        with sync_playwright() as p:
            b = launch_browser(p)
            b.close()
        res["chromium"] = {"ok": True}
    except Exception as e:
        res["chromium"] = {"ok": False, "error": str(e).splitlines()[0][:300], "fix": "python3 -m playwright install chromium"}
    for h in REQUIRED_HOSTS:
        r = check_http(h)
        if not r["ok"]:
            r["fix"] = "Cloud environment network access must be Full, or Custom including this host (see README)."
        res[f"net:{h}"] = r
    if source:
        r = check_http(source)
        if not r["ok"]:
            r["fix"] = ("Source site not reachable: add its domain to the environment allowlist (Custom) or use Full. "
                        "If it answers 403/429/503 with bot protection, stop and ask for a WordPress export / client access.")
        res[f"net:source:{source}"] = r
    ok = all(v["ok"] for v in res.values())
    print(json.dumps({"ok": ok, "checks": res}, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
