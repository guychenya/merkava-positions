# Merkava · משרות פומביות פתוחות

A single-file static app (no server, no build step) for browsing **154 open public positions**
scraped from the Israel Civil Service Commission portal (merkava.mrp.gov.il).

## Use
Open `index.html` — everything (data + UI) is embedded. Host it anywhere:
GitHub Pages, Netlify, Vercel, or just double-click locally.

## Data
Snapshot captured **2026-09-23** from the Merkava OData endpoint
(`GIUS_PRIVATE_AREA_SRV/SearchDataIdSet`, `isPublis eq true`). Raw data in `positions.json`.

## Rebuild
`python3 build.py` regenerates `index.html` from `positions.json`.

## Files
| file | purpose |
|------|---------|
| `index.html` | The app (self-contained, ~1 MB) |
| `positions.json` | Raw 154 positions snapshot |
| `build.py` | Regenerates index.html from positions.json |
