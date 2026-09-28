#!/usr/bin/env python3
"""PreToolUse guard for Webflow MCP calls (works for plugin and repo hooks).

Reads the hook payload on stdin and:
  - BLOCKS publishing to custom domains (only *.webflow.io staging is allowed)
  - BLOCKS writes to sites that are not the claimed migration target
    (MIGRATION_SITE_ID in migrations/.active-site, when present)
  - ASKS the user before destructive actions (delete_*, remove_*, clear_*)
    and before writing site-wide custom code (tracking scripts need consent)
Everything else passes through to the normal permission rules.
"""
import json
import os
import sys
from pathlib import Path

DESTRUCTIVE_PREFIXES = ("delete_", "remove_", "clear_")
CUSTOM_CODE = ("set_site_freeform_code", "set_site_scripts", "add_site_script", "set_page_scripts", "add_page_script",
               "set_page_freeform_code", "register_inline_script", "register_hosted_script")
TRACKING_MARKERS = ("googletagmanager", "gtag(", "fbq(", "cookiebot", "clarity", "hotjar", "tiktok", "linkedin")


def decide(kind, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": kind, "permissionDecisionReason": reason}}))
    sys.exit(0)


def active_site():
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    f = root / "migrations" / ".active-site"
    return f.read_text().strip() if f.exists() else None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    tool = payload.get("tool_name", "")
    if "webflow" not in tool.lower():
        sys.exit(0)
    ti = payload.get("tool_input", {}) or {}
    actions = ti.get("actions", []) or []
    site_ids = {ti.get("siteId"), ti.get("site_id")}
    target = active_site()

    for act in actions:
        for key, body in act.items():
            if key == "label" or not isinstance(body, dict):
                continue
            sid = body.get("site_id") or body.get("siteId")
            if sid:
                site_ids.add(sid)
            if key == "publish_site":
                if body.get("customDomains"):
                    decide("deny", "Publishing to custom domains is blocked by the migration kit. "
                                   "Publish only with publishToWebflowSubdomain=true and customDomains=[]; "
                                   "the domain switch is done by a human.")
            if key.startswith(DESTRUCTIVE_PREFIXES):
                decide("ask", f"Destructive Webflow action '{key}' – confirm before running.")
            if key in CUSTOM_CODE:
                content = json.dumps(body).lower()
                if any(m in content for m in TRACKING_MARKERS) and os.environ.get("MIGRATION_TRACKING_APPROVED") != "1":
                    decide("ask", "This adds tracking/consent scripts (GTM, pixel, Cookiebot …). "
                                  "The client must approve tracking before it is added.")

    writes = any(not k.startswith(("get_", "list_", "query_", "label")) for a in actions for k in a)
    site_ids.discard(None)
    if target and writes and site_ids and site_ids != {target}:
        decide("deny", f"Write to site(s) {sorted(site_ids)} blocked: the claimed migration target is {target} "
                       "(migrations/.active-site). Claim another pool site explicitly if this is intended.")
    sys.exit(0)


if __name__ == "__main__":
    main()
