# Merkava · משרות פומביות פתוחות

A single-file static app (no server, no build step) for browsing **open public positions**
from the Israel Civil Service Commission portal (merkava.mrp.gov.il).

🌐 **Live:** https://guychenya.github.io/merkava-positions/

## Use
Open `index.html` — everything (data + UI) is embedded. Host it anywhere:
GitHub Pages, Netlify, Vercel, or just double-click locally.

## Data
Auto-refreshed from the public Merkava OData endpoint (no login):
`GIUS_PUBLIC_AREA_SRV/TenderDataSet` (`IsPublic eq true`). Raw data in `positions.json`.
Each position links to its own public portal page (`#/position/<request_id>`).

## Auto-refresh (CI)
GitHub Actions **scrapes + rebuilds + redeploys every Monday 06:00 UTC** (≈09:00 Israel).
The schedule is in `.github/workflows/pages.yml`. Runs only need Python (stdlib) + curl
(no third-party packages).

Manual / on-demand run:
1. Actions tab → "Merkava — refresh & deploy" → **Run workflow**, or
2. `gh workflow run pages.yml`

## Local rebuild
```
python3 scrape.py   # fetch positions → positions.json, then build index.html
python3 build.py    # (or standalone) regenerate index.html from positions.json
```

## Files
| file | purpose |
|------|---------|
| `index.html` | The app (self-contained, ~1.5 MB) |
| `positions.json` | Current positions snapshot |
| `scrape.py` | Fetches public positions from the OData endpoint (stdlib + curl fallback) |
| `build.py` | Generates `index.html` from `positions.json` |
| `.github/workflows/pages.yml` | Weekly refresh schedule + deploy to Pages |
