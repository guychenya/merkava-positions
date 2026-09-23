#!/usr/bin/env python3
"""Merkava public-positions scraper (no login required).

Pulls every published public tender from the Merkava SAP OData endpoint,
normalizes the fields, and rebuilds the static site.

Endpoint:
  https://merkava.mrp.gov.il/sap/opu/odata/ILG/GIUS_PUBLIC_AREA_SRV/TenderDataSet
  (IsPublic eq true  → public tenders only)

Usage:
    python3 scrape.py

Writes:
  ./positions.json   (canonical data, same dir as this script)
  ./index.html       (regenerated via build.py)

No external dependencies — uses the Python stdlib only.
Exit code 0 on success (>=1 position), 1 on endpoint error / zero results
(so callers never overwrite good data with a bad fetch).
"""
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "positions.json")
BUILD = os.path.join(HERE, "build.py")

SVC = "https://merkava.mrp.gov.il/sap/opu/odata/ILG/GIUS_PUBLIC_AREA_SRV/TenderDataSet"
HEADERS = {
    "sap-language": "he",
    "Accept": "application/json;odata=verbose",
    "User-Agent": "Mozilla/5.0 (merkava-scraper/1.0)",
}


def sap_date(s):
    """SAP OData date '/Date(1791072000000)/' → 'YYYY-MM-DD' (Israel TZ, UTC+3)."""
    if not s or not isinstance(s, str):
        return ""
    m = re.match(r"/Date\((-?\d+)\)/", s)
    if not m:
        try:
            return s[:10]
        except Exception:
            return ""
    ms = int(m.group(1))
    dt = datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc) + timedelta(hours=3)
    return dt.strftime("%Y-%m-%d")


def strip_html(s):
    if not s:
        return ""
    t = re.sub(r"<\s*br\s*/?\s*>", "\n", s, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">")):
        t = t.replace(a, b)
    return t.strip()


def rank(from_, to_):
    parts = []
    if from_:
        parts.append(str(from_).lstrip("0") or "0")
    if to_:
        parts.append(str(to_).lstrip("0") or "0")
    if len(parts) == 2:
        return f"{parts[0]}-{parts[1]}"
    if len(parts) == 1:
        return parts[0]
    return ""


def _permissive_context():
    """TLS context that copes with older servers.

    GitHub-hosted runners use OpenSSL 3 (Ubuntu 24.04) with a strict
    cipher/SECLEVEL default that the Merkava server's TLS stack rejects
    (SSLV3_ALERT_HANDSHAKE_FAILURE). Allowing TLS 1.2 with a relaxed
    cipher set gets the handshake through, while still rejecting TLS 1.0/1.1.
    """
    ctx = ssl.create_default_context()
    try:
        ctx.set_ciphers("DEFAULT:@SECLEVEL=0")
    except (ssl.SSLError, OSError):
        pass
    try:
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        # Allow up to TLS 1.3 — keep the default max.
    except AttributeError:
        pass
    return ctx


def _http_get(url):
    """Return response body bytes via stdlib urllib (permissive TLS)."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=45, context=_permissive_context()) as r:
        if r.status != 200:
            raise RuntimeError(f"HTTP {r.status}")
        return r.read()


def _curl_get(url):
    """Fallback: fetch via curl (present on CI, independent TLS stack / curl-openssl)."""
    out = subprocess.run(
        ["curl", "-fsSL", "--tlsv1.2", "--retry", "2", "--retry-delay", "3",
         "--max-time", "60", url],
        capture_output=True, text=False,
    )
    if out.returncode != 0:
        raise RuntimeError(f"curl failed ({out.returncode}): {out.stderr.decode(errors='replace')[:200]}")
    return out.stdout


def fetch_all():
    url = SVC + "?" + urllib.parse.urlencode({"$format": "json"})
    last_err = None
    for attempt in (1, 2):
        try:
            body = _http_get(url)
        except Exception as e:  # noqa: BLE001 — fallback to curl below
            last_err = e
        else:
            return json.loads(body.decode("utf-8"))
        # Try the curl fallback for this round.
        try:
            body = _curl_get(url)
            return json.loads(body.decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last_err = e
    raise RuntimeError(f"all fetch attempts failed: {last_err}")


def map_record(r):
    return {
        "tender_number": r.get("TenderNumber") or "",
        "position": r.get("JobName") or "",
        "title": r.get("TenderName") or "",
        "ministry": r.get("OfficeName") or "",
        "unit": r.get("OfficeUnitName") or "",
        "location": r.get("LocationName") or "",
        "category": (r.get("Tags1") or "").strip(),
        "rank": rank(r.get("RankFrom"), r.get("RankTo")),
        "job_number": r.get("NumberOfJobs") or "",
        "percent": r.get("JobPercent") or "",
        "publish_type": r.get("PublishmenTypeName") or "",
        "pub_date": sap_date(r.get("TenderPublicationDate")),
        "submission_deadline": sap_date(r.get("LastSubmittingDate")),
        "dedicated": r.get("DedicatedPosition") or "",
        "cluster": r.get("ClusterName") or "",
        "area": r.get("Area") or "",
        "request_id": r.get("RequestId") or "",
        "hot": bool(r.get("HotJobFlg") or (r.get("HotJob") in ("H", "D"))),
        "days_left": r.get("DaysLeft", "") if r.get("DaysLeft") is not None else "",
        "description": strip_html(r.get("JobDes") or ""),
        "requirements": strip_html(r.get("JobRequirements") or ""),
        "remarks": strip_html(r.get("JobRemarks") or ""),
    }


def main():
    try:
        data = fetch_all()
    except Exception as e:
        print(f"[scrape] ERROR fetching endpoint: {e}", file=sys.stderr)
        return 1

    results = data.get("d", {}).get("results", [])
    if not results:
        print("[scrape] WARNING: endpoint returned 0 records — not overwriting", file=sys.stderr)
        return 1

    public = [r for r in results if r.get("IsPublic") is True]
    if not public:
        print("[scrape] WARNING: 0 public positions found — not overwriting", file=sys.stderr)
        return 1

    mapped = [map_record(r) for r in public]
    mapped.sort(
        key=lambda x: (x.get("submission_deadline") or "", x.get("pub_date") or ""),
        reverse=True,
    )
    print(f"[scrape] {len(mapped)} public positions fetched")

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(mapped, f, ensure_ascii=False, indent=2)
    print(f"[scrape] wrote {OUT_JSON} ({os.path.getsize(OUT_JSON):,} bytes)")

    r = subprocess.run([sys.executable, BUILD], cwd=HERE, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[scrape] build failed:\n{r.stdout}\n{r.stderr}", file=sys.stderr)
        return 1
    print(r.stdout.strip())
    print("[scrape] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
