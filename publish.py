#!/usr/bin/env python3
"""Pull the latest Kaizenvest Sector Brief edition from the Supabase relay
and write the site files (index.html, dated archive, snapshot PDFs).

Run by .github/workflows/publish.yml — the weekly cloud routine publishes each
edition into Supabase (table newsletter_editions, via the publish_edition RPC);
this script is the read-only consumer. The anon key below is a Supabase
publishable key: safe to commit, read-only (RLS allows SELECT only).
"""
import base64, json, pathlib, urllib.request

SUPABASE_URL = "https://ipbloexynslsjovwjjzs.supabase.co"
ANON_KEY = "sb_publishable_IaAPP8jjULdslJEKWc0zAA_9QbYwkQ6"


def fetch_latest():
    url = (f"{SUPABASE_URL}/rest/v1/newsletter_editions"
           f"?select=edition_date,html,snapshot_pdf_base64&order=edition_date.desc&limit=1")
    req = urllib.request.Request(url, headers={"apikey": ANON_KEY})
    with urllib.request.urlopen(req, timeout=60) as r:
        rows = json.load(r)
    return rows[0] if rows else None


def main():
    root = pathlib.Path(__file__).resolve().parent
    row = fetch_latest()
    if not row:
        print("relay is empty; nothing to publish")
        return
    date = row["edition_date"]
    pdf_b64 = row.get("snapshot_pdf_base64") or ""
    stamp = f"{date}:{len(row['html'])}:{len(pdf_b64)}"
    marker = root / "latest.txt"
    if marker.exists() and marker.read_text().strip() == stamp:
        print(f"already up to date ({stamp})")
        return
    (root / f"{date}.html").write_text(row["html"], encoding="utf-8")
    (root / "index.html").write_text(row["html"], encoding="utf-8")
    if pdf_b64:
        pdf = base64.b64decode(pdf_b64)
        (root / f"snapshot-{date}.pdf").write_bytes(pdf)
        (root / "snapshot-latest.pdf").write_bytes(pdf)
    marker.write_text(stamp + "\n")
    print(f"published {stamp}")


if __name__ == "__main__":
    main()
