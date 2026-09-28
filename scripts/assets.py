#!/usr/bin/env python3
"""Prepare and upload images to Webflow WITHOUT the Designer.

Webflow's `upload_image_by_url` needs an open Designer and rejects files whose
server sends no Content-Type (common for WordPress .webp). This script uses the
headless Data API path instead:

  1. prepare  - download each image (same browser context as the audit),
                convert webp/unknown formats to PNG (alpha) or JPEG, compute MD5,
                write assets/manifest.json
  2. (agent)  - for each manifest entry call Webflow MCP
                data_assets_tool > create_asset(site_id, file_name, file_hash)
                and save the returned object to assets/uploads/<file_name>.json
  3. upload   - POST each file to S3 with the presigned uploadDetails, verify the
                CDN URL answers 200, write assets/asset-map.json (source URL -> asset id/url)

Usage:
  python3 scripts/assets.py prepare migrations/<domain> [--only URL ...]
  python3 scripts/assets.py upload  migrations/<domain>
"""
import argparse
import hashlib
import io
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image

WP_SIZE_SUFFIX = re.compile(r"-\d{2,4}x\d{2,4}(?=\.[a-z]+$)", re.I)


def collect_image_urls(mig: Path) -> list[dict]:
    """All <img> sources and background images from content/*.json, deduplicated, with alt text."""
    seen = {}
    for f in sorted((mig / "content").glob("*.json")):
        data = json.loads(f.read_text())
        for img in data.get("images", []):
            if img["src"].startswith("http"):
                seen.setdefault(img["src"], img.get("alt", ""))
        for s in data.get("sections", []):
            for it in s.get("items", []):
                for img in it.get("images", []) or []:
                    seen.setdefault(img["src"], img.get("alt", ""))
                for bg in it.get("background_images", []) or []:
                    seen.setdefault(bg, "")
        og = (data.get("meta") or {}).get("og_image")
        if og:
            seen.setdefault(og, "")
    return [{"src": k, "alt": v} for k, v in seen.items() if not k.startswith("data:")]


def safe_name(url: str, ext: str) -> str:
    stem = Path(urlparse(url).path).stem or "image"
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", stem).strip("-")[:70] or "image"
    return f"{stem}.{ext}"


def fetch(url: str, session: requests.Session) -> bytes:
    r = session.get(url, timeout=60)
    r.raise_for_status()
    return r.content


def normalise(raw: bytes) -> tuple[bytes, str]:
    """Return (bytes, ext). Keep jpg/png/gif/svg as-is, convert everything else."""
    head = raw[:512].lstrip()
    if head.startswith(b"<svg") or b"<svg" in head[:256]:
        return raw, "svg"
    img = Image.open(io.BytesIO(raw))
    fmt = (img.format or "").upper()
    if fmt in ("JPEG", "PNG", "GIF"):
        return raw, {"JPEG": "jpg", "PNG": "png", "GIF": "gif"}[fmt]
    buf = io.BytesIO()
    if img.mode in ("RGBA", "LA", "P") and ("transparency" in img.info or img.mode != "P"):
        img.convert("RGBA").save(buf, "PNG", optimize=True)
        return buf.getvalue(), "png"
    img.convert("RGB").save(buf, "JPEG", quality=88, optimize=True)
    return buf.getvalue(), "jpg"


def cmd_prepare(mig: Path, only: list[str] | None):
    out = mig / "assets"
    out.mkdir(exist_ok=True)
    items = [{"src": u, "alt": ""} for u in only] if only else collect_image_urls(mig)
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (migration-kit)"
    manifest, used, by_md5 = [], set(), {}
    for it in items:
        entry = {"src": it["src"], "alt": it["alt"]}
        try:
            raw, used_url = None, it["src"]
            original = WP_SIZE_SUFFIX.sub("", it["src"])
            for cand in ([original] if original != it["src"] else []) + [it["src"]]:
                try:
                    raw, used_url = fetch(cand, s), cand
                    break
                except Exception:
                    continue
            if raw is None:
                raise RuntimeError("download failed (404/blocked)")
            entry["downloaded_from"] = used_url
            data, ext = normalise(raw)
            md5 = hashlib.md5(data).hexdigest()
            if md5 in by_md5:  # same image in another WP size -> reuse one Webflow asset
                entry.update(dup_of=by_md5[md5], md5=md5)
                manifest.append(entry)
                continue
            name = safe_name(used_url, ext)
            i = 2
            while name in used:
                name = safe_name(used_url, ext).replace(f".{ext}", f"-{i}.{ext}")
                i += 1
            used.add(name)
            (out / name).write_bytes(data)
            by_md5[md5] = name
            entry.update(file=name, md5=md5, bytes=len(data), converted=not raw == data)
        except Exception as e:  # 404 etc. -> recorded, agent decides (e.g. WP media search)
            entry["error"] = str(e)[:200]
            entry["hint"] = "WordPress: search /wp-json/wp/v2/media?search=<name> for a replacement; check if it is missing on the source too"
        manifest.append(entry)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    ok = [m for m in manifest if "file" in m]  # dup_of entries need no create_asset
    print(json.dumps({"prepared": len(ok), "failed": [m for m in manifest if "error" in m],
                      "next": "for each entry call data_assets_tool > create_asset(site_id, file_name=file, file_hash=md5) "
                              "and save the result JSON to assets/uploads/<file>.json"}, indent=2, ensure_ascii=False))


FIELD_MAP = {  # uploadDetails key -> S3 form field
    "acl": "acl", "bucket": "bucket", "xAmzAlgorithm": "X-Amz-Algorithm", "xAmzCredential": "X-Amz-Credential",
    "xAmzDate": "X-Amz-Date", "key": "key", "policy": "Policy", "xAmzSignature": "X-Amz-Signature",
    "successActionStatus": "success_action_status", "contentType": "Content-Type", "cacheControl": "Cache-Control",
}


def cmd_upload(mig: Path):
    assets = mig / "assets"
    manifest = json.loads((assets / "manifest.json").read_text())
    up_dir = assets / "uploads"
    amap_path = assets / "asset-map.json"
    amap = json.loads(amap_path.read_text()) if amap_path.exists() else {}
    results = []
    for m in manifest:
        if "file" not in m:
            continue
        meta_file = up_dir / f"{m['file']}.json"
        if not meta_file.exists():
            results.append({"file": m["file"], "status": "missing create_asset result"})
            continue
        meta = json.loads(meta_file.read_text())
        meta = meta.get("result", meta)
        if m["src"] in amap and amap[m["src"]].get("verified"):
            results.append({"file": m["file"], "status": "already uploaded"})
            continue
        details = meta["uploadDetails"]
        form = {FIELD_MAP.get(k, k): str(v) for k, v in details.items()}
        # S3 requires 'file' to be the last field
        files = {"file": (m["file"], (assets / m["file"]).read_bytes(), details.get("contentType", "application/octet-stream"))}
        r = requests.post(meta["uploadUrl"], data=form, files=files, timeout=120)
        ok = r.status_code in (200, 201, 204)
        cdn = meta.get("hostedUrl")
        verified = False
        if ok and cdn:
            for _ in range(5):
                if requests.get(cdn, timeout=30).status_code == 200:
                    verified = True
                    break
                time.sleep(2)
        amap[m["src"]] = {"asset_id": meta["id"], "file": m["file"], "url": cdn, "alt": m.get("alt", ""), "verified": verified}
        results.append({"file": m["file"], "s3_status": r.status_code, "verified": verified,
                        **({"s3_error": r.text[:300]} if not ok else {})})
    by_file = {v["file"]: v for v in amap.values()}
    for m in manifest:
        if "dup_of" in m and m["dup_of"] in by_file:
            amap[m["src"]] = {**by_file[m["dup_of"]], "alt": m.get("alt", "")}
    amap_path.write_text(json.dumps(amap, indent=2, ensure_ascii=False))
    print(json.dumps(results, indent=2, ensure_ascii=False))
    if any(not x.get("verified") and x.get("status") != "already uploaded" for x in results):
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prepare", "upload"])
    ap.add_argument("migration_dir")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    mig = Path(a.migration_dir)
    if a.cmd == "prepare":
        cmd_prepare(mig, a.only)
    else:
        cmd_upload(mig)


if __name__ == "__main__":
    main()
