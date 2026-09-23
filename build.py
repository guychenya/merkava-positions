#!/usr/bin/env python3
"""Generate a single self-contained index.html from positions.json (same directory).

Usage:
    python3 build.py
Reads ./positions.json (or ../data/positions.json as a fallback) and writes ./index.html.
Self-contained — no external dependencies, safe to run in CI.

UI: a modern, macOS-styled single-file app (window chrome, frosted bars,
right-hand filter sidebar, Spotlight-style search, slide-in inspector).
"""
import json, os
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "positions.json")
if not os.path.exists(SRC):
    alt = os.path.join(HERE, "..", "data", "positions.json")
    if os.path.exists(alt):
        SRC = alt
OUT = os.path.join(HERE, "index.html")

with open(SRC, encoding="utf-8") as f:
    data = json.load(f)

# Keep only the fields the UI actually uses (drop heavy/unused ones).
KEEP = {
    "tender_number", "position", "title", "ministry", "unit", "location",
    "category", "rank", "job_number", "percent", "publish_type", "pub_date",
    "submission_deadline", "dedicated", "cluster", "request_id", "hot",
    "days_left", "description", "requirements", "remarks",
}
def clean(p):
    out = {k: p[k] for k in KEEP if k in p}
    for k in ("requirements", "remarks", "description"):
        v = (out.get(k) or "").strip()
        if len(v) > 6000:
            v = v[:6000] + "…"
        out[k] = v
    return out

data = [clean(p) for p in data]
DATA_JSON = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
# Escape for inlining inside <script> (guard against </script> in text)
DATA_JSON = DATA_JSON.replace("</", "<\\/")

# Build timestamp (Israel time) for the "last updated" chip.
AS_OF = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%d/%m/%Y · %H:%M")

HTML = r"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#ececf1">
<title>Merkava · משרות פומביות</title>
<meta name="description" content="מנוי משרות פומביות פתוחות — ועדת משרתי הציבור">
<style>
:root{
  --bg1:#f7f7fb; --bg2:#eef0f5;
  --surface:#ffffff; --surface-2:#f2f3f7;
  --ink:#1d1d1f; --ink-2:#3a3a3f; --muted:#86868b; --faint:#b0b0b6;
  --line:rgba(0,0,0,.09); --line-2:rgba(0,0,0,.05);
  --accent:#0a84ff; --accent-press:#0060d6;
  --accent-soft:rgba(10,132,255,.12);
  --ok:#30d158; --warn:#ff9f0a; --bad:#ff453a;
  --ok-soft:rgba(48,209,88,.14); --warn-soft:rgba(255,159,10,.16); --bad-soft:rgba(255,69,58,.14);
  --glass:rgba(250,250,252,.72);
  --r-lg:16px; --r-md:12px; --r-sm:9px;
  --shadow-card:0 1px 2px rgba(15,18,25,.04),0 6px 20px rgba(15,18,25,.06);
  --shadow-pop:0 8px 40px rgba(15,18,25,.18);
  --tl-red:#ff5f57; --tl-yellow:#febc2e; --tl-green:#28c840;
  --font:-apple-system,BlinkMacSystemFont,"SF Pro Text","Noto Sans Hebrew","Segoe UI",Arial,sans-serif;
  --mono:"SF Mono",ui-monospace,Menlo,monospace;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;height:100%}
body{
  font-family:var(--font);color:var(--ink);background:linear-gradient(180deg,var(--bg1),var(--bg2));
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;line-height:1.5;
  -webkit-tap-highlight-color:transparent;
}
button,input,select{font-family:inherit}

/* ---------- app frame (macOS window) ---------- */
.app{
  max-width:1240px;margin:22px auto 40px;height:calc(100vh - 40px);min-height:520px;
  background:var(--surface);border:1px solid rgba(0,0,0,.10);border-radius:var(--r-lg);
  box-shadow:0 1px 0 rgba(255,255,255,.6) inset,0 30px 80px rgba(20,24,40,.20);
  overflow:hidden;display:flex;flex-direction:column;position:relative;
}

/* ---------- title bar ---------- */
.titlebar{
  flex:none;height:52px;display:flex;align-items:center;gap:14px;padding:0 18px;
  background:var(--glass);backdrop-filter:saturate(180%) blur(24px);-webkit-backdrop-filter:saturate(180%) blur(24px);
  border-bottom:1px solid var(--line);z-index:6;
}
.lights{display:flex;gap:8px;align-items:center}
.dot{width:12px;height:12px;border-radius:50%;border:1px solid rgba(0,0,0,.05)}
.dot.r{background:var(--tl-red);border-color:#e0443e}
.dot.y{background:var(--tl-yellow);border-color:#d9a120}
.dot.g{background:var(--tl-green);border-color:#1ea534}
.titles{display:flex;flex-direction:column;line-height:1.15;margin-inline-start:4px;min-width:0}
.titles h1{font-size:14.5px;font-weight:650;margin:0;letter-spacing:.1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.titles .sub{font-size:11.5px;color:var(--muted);font-weight:500}
.tb-actions{margin-inline-start:auto;display:flex;align-items:center;gap:10px}
.asof{font-size:11.5px;color:var(--muted);font-weight:550;background:var(--surface-2);border:1px solid var(--line-2);
  padding:4px 10px;border-radius:999px;white-space:nowrap}
.count-pill{display:flex;align-items:center;gap:7px;font-size:12.5px;font-weight:650;color:var(--accent);
  background:var(--accent-soft);padding:5px 11px;border-radius:999px;white-space:nowrap}
.count-pill::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 3px rgba(10,132,255,.14)}
.icon-btn{width:32px;height:32px;border-radius:9px;border:1px solid var(--line);background:var(--surface);
  display:grid;place-items:center;cursor:pointer;color:var(--ink-2);transition:background .12s,transform .05s}
.icon-btn:hover{background:var(--surface-2)}
.icon-btn:active{transform:scale(.94)}
.icon-btn svg{width:16px;height:16px}

/* ---------- body ---------- */
.body{flex:1;display:flex;min-height:0}

/* sidebar */
.sidebar{
  flex:0 0 264px;width:264px;border-inline-end:1px solid var(--line);
  background:linear-gradient(180deg,rgba(247,247,251,.6),rgba(240,241,246,.6));
  padding:16px 14px;overflow-y:auto;display:flex;flex-direction:column;gap:18px;
}
.grp{display:flex;flex-direction:column;gap:8px}
.grp-label{font-size:11px;font-weight:700;letter-spacing:.5px;color:var(--muted);
  text-transform:uppercase;margin:2px 4px 0}
.popup{
  appearance:none;-webkit-appearance:none;width:100%;font-size:13.5px;color:var(--ink);
  background:var(--surface);border:1px solid var(--line);border-radius:var(--r-sm);
  padding:9px 30px 9px 12px;cursor:pointer;transition:border-color .12s,box-shadow .12s;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='11' height='11' viewBox='0 0 11 11'><path d='M2.5 4.2 5.5 7l3-2.8' fill='none' stroke='%2386868b' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/></svg>");
  background-repeat:no-repeat;background-position:left 11px center;
}
.popup:hover{border-color:rgba(0,0,0,.16)}
.popup:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(10,132,255,.22)}
.sidebar-foot{margin-top:auto;padding-top:14px;border-top:1px solid var(--line-2)}
.legend{display:flex;flex-direction:column;gap:8px;font-size:12px;color:var(--muted)}
.legend .li{display:flex;align-items:center;gap:8px}
.swatch{width:10px;height:10px;border-radius:3px;flex:none}
.link{font-size:12px;color:var(--accent);text-decoration:none;font-weight:600}
.link:hover{text-decoration:underline}

/* main */
.main{flex:1;min-width:0;display:flex;flex-direction:column}
.searchwrap{flex:none;padding:16px 20px 12px;border-bottom:1px solid var(--line-2);background:var(--surface)}
.searchrow{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.searchbox{
  flex:1;min-width:220px;display:flex;align-items:center;gap:10px;
  background:var(--surface-2);border:1px solid transparent;border-radius:var(--r-md);
  padding:0 14px;transition:border-color .14s,background .14s,box-shadow .14s;
}
.searchbox:focus-within{background:var(--surface);border-color:var(--accent);box-shadow:0 0 0 4px rgba(10,132,255,.16)}
.searchbox svg{width:18px;height:18px;color:var(--muted);flex:none}
.searchbox input{flex:1;border:0;background:transparent;font-size:15px;color:var(--ink);padding:11px 0}
.searchbox input:focus{outline:none}
.searchbox input::placeholder{color:var(--faint)}
.clearbtn{border:0;background:var(--surface);width:20px;height:20px;border-radius:50%;cursor:pointer;
  display:grid;place-items:center;color:var(--muted);opacity:0;pointer-events:none;transition:opacity .12s}
.clearbtn.on{opacity:1;pointer-events:auto}
.clearbtn:hover{color:var(--ink)}
.clearbtn svg{width:11px;height:11px}
.btn{
  font-size:13.5px;font-weight:600;border-radius:var(--r-sm);padding:9px 15px;cursor:pointer;
  border:1px solid var(--line);background:var(--surface);color:var(--ink-2);white-space:nowrap;
  transition:background .12s,border-color .12s,transform .05s;
}
.btn:hover{background:var(--surface-2)}
.btn:active{transform:translateY(1px)}
.btn.primary{background:var(--accent);color:#fff;border-color:transparent;box-shadow:0 1px 2px rgba(10,132,255,.3)}
.btn.primary:hover{background:var(--accent-press)}
.btn.ghost{background:transparent;border-color:transparent;color:var(--muted)}
.btn.ghost:hover{background:var(--surface-2);color:var(--ink)}

.listhead{flex:none;display:flex;align-items:center;gap:10px;padding:12px 22px 8px}
.listhead .n{font-size:13px;color:var(--muted);font-weight:600}
.listhead .n b{color:var(--ink);font-weight:750}

.scroll{flex:1;overflow-y:auto;padding:6px 20px 28px;display:flex;flex-direction:column;gap:11px}

/* cards */
.card{
  position:relative;background:var(--surface);border:1px solid var(--line);border-radius:var(--r-md);
  padding:15px 17px;box-shadow:var(--shadow-card);cursor:pointer;
  transition:transform .07s ease,border-color .14s,box-shadow .14s,background .14s;
}
.card::before{content:"";position:absolute;inset-inline-start:0;top:14px;bottom:14px;width:3px;border-radius:3px;
  background:transparent;transition:background .14s}
.card:hover{transform:translateY(-1px);border-color:rgba(0,0,0,.14);box-shadow:0 2px 6px rgba(20,24,40,.06),0 14px 34px rgba(20,24,40,.10)}
.card.sel{border-color:var(--accent);box-shadow:0 0 0 3px rgba(10,132,255,.18)}
.card.sel::before{background:var(--accent)}
.c-top{display:flex;align-items:flex-start;gap:12px;justify-content:space-between}
.c-titlewrap{min-width:0;display:flex;flex-direction:column;gap:2px}
.c-title{font-size:15.5px;font-weight:700;margin:0;line-height:1.3;letter-spacing:-.1px}
.c-pos{font-size:13.5px;color:var(--ink-2);margin:0;font-weight:500}
.c-urgent{display:inline-flex;align-items:center;gap:4px;font-size:10.5px;font-weight:700;color:var(--bad);
  background:var(--bad-soft);padding:2px 7px;border-radius:999px;width:max-content;letter-spacing:.2px}
.c-urgent svg{width:11px;height:11px}
.deadline{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;font-weight:650;white-space:nowrap;
  padding:5px 10px;border-radius:999px}
.deadline .d{width:8px;height:8px;border-radius:50%}
.dl-ok{background:var(--ok-soft);color:#147a35}.dl-ok .d{background:var(--ok)}
.dl-warn{background:var(--warn-soft);color:#9a5a00}.dl-warn .d{background:var(--warn)}
.dl-bad{background:var(--bad-soft);color:#b1251b}.dl-bad .d{background:var(--bad)}
.dl-closed{background:var(--surface-2);color:var(--muted)}.dl-closed .d{background:var(--faint)}
.c-meta{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin-top:11px}
.tag{font-size:12px;font-weight:600;padding:4px 10px;border-radius:999px;background:var(--surface-2);color:var(--ink-2);
  border:1px solid var(--line-2);white-space:nowrap}
.tag.org{background:rgba(10,132,255,.07);color:var(--accent);border-color:rgba(10,132,255,.12)}
.tag.loc{background:rgba(0,122,255,.06);color:#0a6cd0}
.tnum{font-family:var(--mono);font-size:11.5px;color:var(--faint);margin-inline-start:auto;letter-spacing:.2px}

/* empty / loading */
.empty{text-align:center;color:var(--muted);padding:70px 20px;font-size:15px}
.empty .ic{width:56px;height:56px;margin:0 auto 16px;border-radius:16px;background:var(--surface-2);
  display:grid;place-items:center;color:var(--faint)}
.empty .ic svg{width:26px;height:26px}

/* ---------- inspector (detail) ---------- */
.scrim{position:absolute;inset:0;background:rgba(20,24,35,.28);opacity:0;visibility:hidden;transition:opacity .22s;z-index:20}
.scrim.on{opacity:1;visibility:visible}
.inspector{
  position:absolute;top:0;bottom:0;inset-inline-end:0;width:min(560px,100%);background:var(--surface);z-index:30;
  box-shadow:var(--shadow-pop);transform:translateX(-101%);transition:transform .26s cubic-bezier(.22,.61,.36,1);
  display:flex;flex-direction:column;
}
[dir=rtl] .inspector{transform:translateX(-101%)}
.inspector.on{transform:translateX(0)}
.i-head{flex:none;padding:18px 20px;border-bottom:1px solid var(--line);display:flex;align-items:flex-start;gap:12px;
  background:var(--glass);backdrop-filter:saturate(170%) blur(16px)}
.i-head .txt{min-width:0}
.i-head h2{font-size:18px;font-weight:750;margin:0;line-height:1.32}
.i-head .pos{font-size:13px;color:var(--ink-2);margin-top:2px}
.i-close{margin-inline-start:auto;width:34px;height:34px;border-radius:10px;border:1px solid var(--line);
  background:var(--surface);cursor:pointer;display:grid;place-items:center;color:var(--muted);flex:none;transition:background .12s,color .12s}
.i-close:hover{background:var(--surface-2);color:var(--ink)}
.i-close svg{width:14px;height:14px}
.i-body{flex:1;overflow-y:auto;padding:18px 20px 8px}
.kv{display:grid;grid-template-columns:auto 1fr;gap:10px 18px;font-size:13.5px;align-items:baseline}
.kv dt{color:var(--muted);font-weight:600;white-space:nowrap}
.kv dd{margin:0;font-weight:520;word-break:break-word}
.sec{margin-top:20px}
.sec h3{font-size:12px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--accent);margin:0 0 9px;display:flex;align-items:center;gap:8px}
.sec h3::after{content:"";flex:1;height:1px;background:var(--line-2)}
.box{white-space:pre-wrap;font-size:13.5px;line-height:1.62;color:var(--ink-2);background:var(--surface-2);
  border:1px solid var(--line-2);border-radius:var(--r-md);padding:13px 15px;word-break:break-word}
.box.muted{color:var(--muted)}
.i-foot{flex:none;padding:12px 20px;border-top:1px solid var(--line);display:flex;gap:10px;background:var(--glass);
  backdrop-filter:saturate(170%) blur(16px)}
.i-foot .btn{flex:1;text-align:center}

/* ---------- responsive ---------- */
@media (max-width:900px){
  .app{margin:0;border-radius:0;height:100vh;height:100dvh;box-shadow:none;border:0}
  .body{flex-direction:column}
  .sidebar{flex:none;width:auto;border-inline-end:0;border-bottom:1px solid var(--line);
    flex-direction:row;overflow-x:auto;overflow-y:hidden;gap:18px;padding:12px 16px;align-items:flex-end}
  .grp{gap:6px;flex:0 0 auto}
  .grp-label{white-space:nowrap}
  .popup{min-width:140px}
  .sidebar-foot{display:none}
  .inspector{width:100%}
}
</style>
</head>
<body>
<div class="app" role="application" aria-label="מנוי משרות פומביות">
  <!-- title bar -->
  <header class="titlebar">
    <div class="lights" aria-hidden="true"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span></div>
    <div class="titles">
      <h1>Merkava · משרות פומביות</h1>
      <span class="sub">ועדת משרתי הציבור · חפשו, סינונו והגישו</span>
    </div>
    <div class="tb-actions">
      <span class="count-pill" id="pill"><b id="total">0</b> משרות פתוחות</span>
      <span class="asof">עדכון <b id="asof">__ASOF__</b></span>
      <button class="icon-btn" id="refresh" title="עדכון נתונים (דוחף מחדש)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-2.64-6.36"/><path d="M21 3v6h-6"/></svg>
      </button>
    </div>
  </header>

  <div class="body">
    <!-- sidebar -->
    <aside class="sidebar" aria-label="סינון">
      <div class="grp">
        <span class="grp-label">מיון</span>
        <select id="sort" class="popup" aria-label="מיון">
          <option value="deadline_desc">מועד — הרחוק ביותר</option>
          <option value="deadline_asc">מועד — הקרוב ביותר</option>
          <option value="pub_desc">מתוארך לאחרונה</option>
          <option value="name">שם תפקיד</option>
          <option value="ministry">ארגון</option>
        </select>
      </div>
      <div class="grp">
        <span class="grp-label">קטגוריה</span>
        <select id="cat" class="popup" aria-label="קטגוריה"></select>
      </div>
      <div class="grp">
        <span class="grp-label">משרד / ארגון</span>
        <select id="min" class="popup" aria-label="ארגון"></select>
      </div>
      <div class="grp">
        <span class="grp-label">מיקום</span>
        <select id="loc" class="popup" aria-label="מיקום"></select>
      </div>
      <div class="sidebar-foot">
        <div class="legend">
          <span class="li"><span class="swatch" style="background:var(--ok)"></span>זמינה · 30+ ימים</span>
          <span class="li"><span class="swatch" style="background:var(--warn)"></span>8–30 ימים להגשה</span>
          <span class="li"><span class="swatch" style="background:var(--bad)"></span>פחות מ-8 ימים</span>
        </div>
        <div style="margin-top:14px;display:flex;gap:10px;align-items:center">
          <a class="link" href="https://merkava.mrp.gov.il/giusp/index.html" target="_blank" rel="noopener">לקראת הפומבי ↗</a>
        </div>
      </div>
    </aside>

    <!-- main -->
    <section class="main">
      <div class="searchwrap">
        <div class="searchrow">
          <div class="searchbox">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
            <input id="q" type="search" placeholder="חפשו תפקיד, יחידה, עיר, משרד, מכרז…" autocomplete="off" spellcheck="false">
            <button class="clearbtn" id="qclear" title="נקה חיפוש" aria-label="נקה חיפוש">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <button class="btn" id="reset">איפוס</button>
        </div>
      </div>

      <div class="listhead">
        <span class="n"><b id="listcount">0</b></span>
        <span class="n" id="sortlabel" style="margin-inline-start:10px"></span>
      </div>

      <div class="scroll" id="scroll">
        <div id="list" style="display:flex;flex-direction:column;gap:11px"></div>
        <div id="empty" class="empty" style="display:none">
          <div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3M8 11h6"/></svg></div>
          לא נמצאו משרות שעולות על החיפוש / הסינון.<br>ניסו למחוק סינון או לשנות מילות חיפוש.
        </div>
      </div>
    </section>
  </div>

  <!-- inspector -->
  <div class="scrim" id="scrim"></div>
  <aside class="inspector" id="inspector" aria-hidden="true" aria-label="פרטי משרה">
    <div class="i-head">
      <div class="txt">
        <h2 id="i-title"></h2>
        <div class="pos" id="i-pos"></div>
      </div>
      <button class="i-close" id="i-close" aria-label="סגירה">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
      </button>
    </div>
    <div class="i-body">
      <dl class="kv" id="i-kv"></dl>
      <div class="sec" id="i-desc-wrap" style="display:none">
        <h3>תיאור תפקיד</h3><div class="box" id="i-desc"></div>
      </div>
      <div class="sec"><h3>דרישות</h3><div class="box" id="i-req"></div></div>
      <div class="sec"><h3>הערות</h3><div class="box" id="i-rem"></div></div>
    </div>
    <div class="i-foot">
      <button class="btn" id="i-copy">העתק פרטים</button>
      <button class="btn primary" id="i-open">פתח באתר הממשלתי</button>
    </div>
  </aside>
</div>

<script id="data" type="application/json">__DATA__</script>
<script>
"use strict";
const DATA = JSON.parse(document.getElementById('data').textContent);
const $ = (s)=>document.querySelector(s);
const listEl=$('#list'), emptyEl=$('#empty'), scrollEl=$('#scroll');

// ---- populate filter pickers ----
function uniq(arr){return [...new Set(arr.filter(v=>v&&String(v).trim()))].sort((a,b)=>String(a).localeCompare(String(b),'he'));}
function fill(id, values){
  const el=$(id); el.innerHTML='';
  const all=document.createElement('option'); all.value=''; all.textContent='הכל'; el.appendChild(all);
  values.forEach(v=>{ const o=document.createElement('option'); o.value=v; o.textContent=v; el.appendChild(o); });
}
fill('#cat', uniq(DATA.map(d=>d.category)));
fill('#min', uniq(DATA.map(d=>d.ministry)));
fill('#loc', uniq(DATA.map(d=>d.location)));
const TOTAL=DATA.length;
$('#total').textContent=TOTAL; $('#total2').textContent=TOTAL;

// ---- helpers ----
function esc(s){return (s==null?'':String(s));}
function daysUntil(dateStr){
  if(!dateStr) return null;
  const d=new Date(dateStr+'T00:00:00'); if(isNaN(d)) return null;
  const today=new Date(); today.setHours(0,0,0,0);
  return Math.round((d-today)/86400000);
}
function deadlineInfo(p){
  const dls=daysUntil(p.submission_deadline);
  const date=p.submission_deadline||'ללא מועד';
  if(dls===null) return {cls:'dl-closed', txt:date};
  if(dls<0)   return {cls:'dl-closed', txt:date+' · פגה'};
  if(dls===0) return {cls:'dl-bad', txt:'היום!'};
  if(dls<=7)  return {cls:'dl-bad',  txt:dls+' ימים'};
  if(dls<=30) return {cls:'dl-warn', txt:dls+' ימים'};
  return {cls:'dl-ok', txt:date+' · '+dls};
}

// ---- filter + sort ----
const SORT_LABEL={
  deadline_desc:'מיון: מועד רחוק', deadline_asc:'מיון: מועד קרוב',
  pub_desc:'מיון: חדש', name:'מיון: שם תפקיד', ministry:'מיון: ארגון'
};
function current(){
  const q=$('#q').value.trim().toLowerCase();
  const cat=$('#cat').value, min=$('#min').value, loc=$('#loc').value;
  let out=DATA.filter(p=>{
    if(cat && p.category!==cat) return false;
    if(min && p.ministry!==min) return false;
    if(loc && p.location!==loc) return false;
    if(q){
      const hay=[p.position,p.title,p.ministry,p.unit,p.location,p.category,p.rank,
                 p.tender_number,p.dedicated,p.publish_type,p.cluster].join(' ').toLowerCase();
      if(!hay.includes(q)) return false;
    }
    return true;
  });
  const cmp={
    deadline_desc:(a,b)=>(b.submission_deadline||'').localeCompare(a.submission_deadline||''),
    deadline_asc:(a,b)=>(a.submission_deadline||'').localeCompare(b.submission_deadline||''),
    pub_desc:(a,b)=>(b.pub_date||'').localeCompare(a.pub_date||''),
    name:(a,b)=>(a.position||a.title||'').localeCompare(b.position||b.title||'','he'),
    ministry:(a,b)=>(a.ministry||'').localeCompare(b.ministry||'','he'),
  }[$('#sort').value]||(()=>0);
  out.sort(cmp);
  return out;
}

// ---- render ----
let currentPos=null, selKey=null;
function render(){
  const items=current();
  $('#shown').textContent=items.length;
  emptyEl.style.display=items.length? 'none':'block';
  $('#sortlabel').textContent=SORT_LABEL[$('#sort').value]||'';
  listEl.innerHTML='';
  const frag=document.createDocumentFragment();
  items.forEach(p=>{
    const key=p.tender_number||p.title||p.position;
    const card=document.createElement('div');
    card.className='card'+(key===selKey?' sel':''); card.tabIndex=0; card.dataset.key=key;
    const dl=deadlineInfo(p);
    const isUrgent=(p.hot||((dl.cls==='dl-bad')&&daysUntil(p.submission_deadline)!=null&&daysUntil(p.submission_deadline)<=7));
    const urgent=isUrgent?'<span class="c-urgent"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/></svg>דורש</span>':'';
    card.innerHTML=
      '<div class="c-top">'+
        '<div class="c-titlewrap">'+
          '<h3 class="c-title">'+esc(p.title||p.position||'—')+'</h3>'+
          '<p class="c-pos">'+esc(p.position||'')+'</p>'+
          (urgent?'<div style="margin-top:6px">'+urgent+'</div>':'')+
        '</div>'+
        '<span class="deadline '+dl.cls+'"><span class="d"></span>'+dl.txt+'</span>'+
      '</div>'+
      '<div class="c-meta">'+
        (p.ministry?'<span class="tag org">'+esc(p.ministry)+'</span>':'')+
        (p.location?'<span class="tag loc">'+esc(p.location)+'</span>':'')+
        (p.category?'<span class="tag">'+esc(p.category)+'</span>':'')+
        (p.rank?'<span class="tag">דרגה '+esc(p.rank)+'</span>':'')+
        '<span class="tnum">'+esc(p.tender_number||'')+'</span>'+
      '</div>';
    const open=()=>openInspector(p);
    card.addEventListener('click',open);
    card.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open();}});
    frag.appendChild(card);
  });
  listEl.appendChild(frag);
  if(!items.length) listEl.style.display='none'; else listEl.style.display='flex';
}

// ---- inspector ----
function openInspector(p){
  currentPos=p;
  const key=p.tender_number||p.title||p.position; selKey=key;
  document.querySelectorAll('.card.sel').forEach(c=>c.classList.remove('sel'));
  const el=listEl.querySelector('[data-key="'+CSS.escape(key)+'"]');
  if(el) el.classList.add('sel');
  $('#i-title').textContent=p.title||p.position||'';
  $('#i-pos').textContent=[p.ministry,p.unit,p.location].filter(Boolean).join(' · ');
  const kv=[
    ['מכרז',p.tender_number],['ארגון',p.ministry],['אגף/יחידה',p.unit],['מיקום',p.location],
    ['קטגוריה',p.category],['דרגה',p.rank],['מספר משרות',p.job_number],['אחוז',p.percent],
    ['סוג',p.publish_type],['תאריך פרסום',p.pub_date],['מועד אחרון',p.submission_deadline],
  ].filter(([,v])=>v!=null&&v!=='');
  $('#i-kv').innerHTML=kv.map(([k,v])=>'<dt>'+k+'</dt><dd>'+esc(v)+'</dd>').join('');
  const desc=(p.description||'').trim();
  $('#i-desc-wrap').style.display=desc?'':'none'; $('#i-desc').textContent=desc||'—';
  $('#i-req').textContent=(p.requirements||'').trim()||'—';
  $('#i-rem').textContent=(p.remarks||'').trim()||'—';
  $('#i-open').onclick=()=>{
    if(p.request_id) window.open('https://merkava.mrp.gov.il/giusp/index.html#/position/'+p.request_id,'_blank','noopener');
    else window.open('https://merkava.mrp.gov.il/giusp/index.html','_blank','noopener');
  };
  $('#inspector').classList.add('on'); $('#inspector').setAttribute('aria-hidden','false');
  $('#scrim').classList.add('on');
  scrollEl.scrollTop=scrollEl.scrollTop; // keep list scroll
}
function closeInspector(){
  $('#inspector').classList.remove('on'); $('#inspector').setAttribute('aria-hidden','true');
  $('#scrim').classList.remove('on');
  document.querySelectorAll('.card.sel').forEach(c=>c.classList.remove('sel'));
  selKey=null; currentPos=null;
}

// ---- copy ----
$('#i-copy').addEventListener('click',()=>{
  if(!currentPos) return;
  const p=currentPos;
  const txt=[
    'מכרז: '+p.tender_number, 'תפקיד: '+(p.title||p.position), 'ארגון: '+p.ministry,
    'אגף: '+(p.unit||''), 'מיקום: '+p.location, 'קטגוריה: '+p.category,
    'דרגה: '+(p.rank||''), 'מועד אחרון: '+p.submission_deadline, '',
    'דרישות:',''+(p.requirements||''),'','הערות:',''+(p.remarks||'')
  ].join('\n');
  (navigator.clipboard?navigator.clipboard.writeText(txt):Promise.reject()).then(()=>{
    const b=$('#i-copy'), t=b.textContent; b.textContent='הועתק ✓'; setTimeout(()=>b.textContent=t,1300);
  }).catch(()=>{});
});

// ---- events ----
['#q','#cat','#min','#loc','#sort'].forEach(s=>$(s).addEventListener('input',render));
$('#q').addEventListener('input',()=>$('#qclear').classList.toggle('on', !!$('#q').value));
$('#qclear').addEventListener('click',()=>{ $('#q').value=''; $('#qclear').classList.remove('on'); $('#q').focus(); render(); });
$('#reset').addEventListener('click',()=>{
  $('#q').value=''; $('#qclear').classList.remove('on');
  $('#cat').value=''; $('#min').value=''; $('#loc').value=''; $('#sort').value='deadline_desc';
  render();
});
$('#i-close').addEventListener('click',closeInspector);
$('#scrim').addEventListener('click',closeInspector);
$('#refresh').addEventListener('click',()=>{
  const b=$('#refresh'); b.style.transform='rotate(360deg)'; setTimeout(()=>b.style.transform='',500);
  location.reload();
});
document.addEventListener('keydown',e=>{
  if(e.key==='Escape') closeInspector();
  if(e.key==='/' && !/input|textarea|select/i.test((e.target.tagName||''))){ e.preventDefault(); $('#q').focus(); }
});

render();
</script>
</body>
</html>
"""

HTML = HTML.replace("__DATA__", DATA_JSON)
HTML = HTML.replace("__ASOF__", AS_OF)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)

print("wrote", OUT, os.path.getsize(OUT), "bytes")
print("positions embedded:", len(data))
