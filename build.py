#!/usr/bin/env python3
"""Generate a single self-contained HTML app from positions.json."""
import json, html, os

SRC = os.path.join(os.path.dirname(__file__), "..", "data", "positions.json")
OUT = os.path.join(os.path.dirname(__file__), "index.html")

with open(SRC, encoding="utf-8") as f:
    data = json.load(f)

# Trim heavy text fields to keep the file lean but informative
def clean(p):
    out = dict(p)
    for k in ("requirements", "remarks"):
        v = (out.get(k) or "").strip()
        if len(v) > 6000:
            v = v[:6000] + "…"
        out[k] = v
    return out

data = [clean(p) for p in data]
DATA_JSON = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
# Escape for inlining inside <script> (guard against </script> in text)
DATA_JSON = DATA_JSON.replace("</", "<\\/")

HTML = r"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Merkava · משרות פומביות פתוחות</title>
<meta name="description" content="מנוי משרות פומביות פתוחות — ועדת משרתי הציבור">
<style>
:root{
  --bg:#f6f7fb; --surface:#ffffff; --ink:#15171f; --muted:#6b7280;
  --line:#e6e8ef; --accent:#3b4ce0; --accent-ink:#fff; --accent-soft:#eef0ff;
  --ok:#0f9d58; --ok-soft:#e7f6ee; --warn:#b26a00; --warn-soft:#fff3df;
  --bad:#d23b3b; --bad-soft:#fdecec; --radius:14px; --shadow:0 1px 2px rgba(20,22,30,.04),0 8px 24px rgba(20,22,30,.06);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Hebrew,"Noto Sans Hebrew",Arial,sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.55;-webkit-font-smoothing:antialiased;
}
a{color:var(--accent);text-decoration:none}

/* header */
.top{
  position:sticky;top:0;z-index:30;background:rgba(255,255,255,.82);backdrop-filter:saturate(160%) blur(12px);
  border-bottom:1px solid var(--line);
}
.top-inner{max-width:1180px;margin:0 auto;padding:14px 20px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.logo{display:flex;align-items:center;gap:11px}
.logo .mark{
  width:38px;height:38px;border-radius:11px;flex:none;
  background:linear-gradient(135deg,#3b4ce0,#6a72ff);color:#fff;display:grid;place-items:center;
  font-weight:800;font-size:19px;box-shadow:0 4px 12px rgba(59,76,224,.35);
}
.logo h1{font-size:17px;margin:0;font-weight:750;letter-spacing:.2px}
.logo .sub{font-size:12px;color:var(--muted);font-weight:500}
.stats{margin-inline-start:auto;display:flex;gap:8px;align-items:center}
.pill{background:var(--accent-soft);color:var(--accent);font-weight:700;font-size:12.5px;padding:6px 11px;border-radius:999px}
.pill b{font-weight:800}

/* controls */
.controls{max-width:1180px;margin:0 auto;padding:16px 20px 6px;display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end}
.field{display:flex;flex-direction:column;gap:5px}
.field label{font-size:11.5px;color:var(--muted);font-weight:650;padding-inline-start:2px}
.input,.select{
  appearance:none;-webkit-appearance:none;font:inherit;font-size:14px;color:var(--ink);
  background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:9px 11px;
  box-shadow:inset 0 0 0 0 rgba(0,0,0,0);transition:border-color .12s,box-shadow .12s;min-height:40px;
}
.input{width:min(360px,100%)}
.input:focus,.select:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(59,76,224,.14)}
.select{min-width:150px;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'><path d='M3 4.5 6 7.5 9 4.5' fill='none' stroke='%236b7280' stroke-width='1.6' stroke-linecap='round'/></svg>");background-repeat:no-repeat;background-position:left 11px center;padding-left:30px}
.actions{display:flex;gap:8px;margin-inline-start:auto}
.btn{font:inherit;font-size:14px;font-weight:650;border:1px solid var(--line);background:var(--surface);
  color:var(--ink);border-radius:10px;padding:9px 14px;cursor:pointer;transition:transform .05s,background .12s,border-color .12s}
.btn:hover{border-color:#cfd3e2}
.btn:active{transform:translateY(1px)}
.btn.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
.btn.primary:hover{background:#3344c9}

/* layout */
.wrap{max-width:1180px;margin:0 auto;padding:10px 20px 60px}
.row{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:15px 16px;margin-bottom:12px;box-shadow:var(--shadow);cursor:pointer;
  transition:transform .07s,border-color .12s,box-shadow .12s;
}
.row:hover{transform:translateY(-1px);border-color:#d3d7e8;box-shadow:0 2px 4px rgba(20,22,30,.05),0 12px 30px rgba(20,22,30,.09)}
.row.selected{border-color:var(--accent);box-shadow:0 0 0 2px rgba(59,76,224,.16)}
.rtop{display:flex;align-items:flex-start;gap:12px;justify-content:space-between}
.rmain{display:flex;flex-direction:column;gap:3px;min-width:0}
.rtitle{font-size:15.5px;font-weight:750;margin:0}
.rpos{font-size:13.5px;color:#374151;margin:0;font-weight:500}
.rmeta{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin-top:8px}
.badge{font-size:12px;font-weight:650;padding:4px 9px;border-radius:8px;background:var(--accent-soft);color:var(--accent);white-space:nowrap}
.badge.gray{background:#f1f2f7;color:var(--muted)}
.badge.loc{background:#eef6ff;color:#155bd6}
.deadline{font-size:12.5px;font-weight:700;padding:4px 9px;border-radius:8px;white-space:nowrap}
.dl-ok{background:var(--ok-soft);color:var(--ok)}
.dl-warn{background:var(--warn-soft);color:var(--warn)}
.dl-bad{background:var(--bad-soft);color:var(--bad)}
.dl-closed{background:#f1f2f7;color:var(--muted)}
.rnum{font-size:11.5px;color:var(--muted);white-space:nowrap}
.empty{text-align:center;color:var(--muted);padding:60px 20px;font-size:15px}
.count-line{font-size:13px;color:var(--muted);margin:6px 2px 14px}

/* detail panel */
.backdrop{position:fixed;inset:0;background:rgba(20,22,30,.42);opacity:0;visibility:hidden;transition:opacity .18s;z-index:40}
.backdrop.on{opacity:1;visibility:visible}
.detail{
  position:fixed;top:0;bottom:0;left:0;width:min(560px,100%);background:var(--surface);z-index:50;
  box-shadow:0 0 60px rgba(0,0,0,.3);transform:translateX(-104%);transition:transform .22s;
  display:flex;flex-direction:column;border-inline-end:1px solid var(--line);
}
.detail.on{transform:translateX(0)}
.d-head{padding:18px 20px;border-bottom:1px solid var(--line);display:flex;align-items:flex-start;gap:12px}
.d-head h2{font-size:18px;margin:0;font-weight:780;line-height:1.35}
.d-head .close{margin-inline-start:auto;border:1px solid var(--line);background:var(--surface);color:var(--muted);
  border-radius:9px;width:34px;height:34px;font-size:18px;cursor:pointer;flex:none;line-height:1}
.d-head .close:hover{background:#f1f2f7;color:var(--ink)}
.d-body{padding:16px 20px;overflow:auto;flex:1}
.kv{display:grid;grid-template-columns:110px 1fr;gap:9px 14px;font-size:13.5px}
.kv dt{color:var(--muted);font-weight:600}
.kv dd{margin:0;font-weight:500;word-break:break-word}
.section{margin-top:18px}
.section h3{font-size:12px;text-transform:none;color:var(--accent);font-weight:750;margin:0 0 6px;padding:6px 10px;background:var(--accent-soft);border-radius:8px;display:inline-block}
.box{white-space:pre-wrap;font-size:13px;color:#2a2f3a;background:#fafbfe;border:1px solid var(--line);border-radius:10px;padding:12px}
.d-foot{padding:12px 20px;border-top:1px solid var(--line);display:flex;gap:10px}
.d-foot .btn{flex:1}
@media (max-width:720px){
  .input{width:100%}.actions{margin-inline-start:0}
  .detail{width:100%}
}
</style>
</head>
<body>
<header class="top">
  <div class="top-inner">
    <div class="logo">
      <div class="mark">M</div>
      <div>
        <h1>Merkava · משרות פומביות</h1>
        <div class="sub">משרות פומביות פתוחות · ועדת משרתי הציבור</div>
      </div>
    </div>
    <div class="stats">
      <span class="pill"><b id="shown">0</b> מתוך <b id="total">0</b> משרות</span>
    </div>
  </div>
</header>

<section class="controls">
  <div class="field">
    <label for="q">חיפוש</label>
    <input id="q" class="input" type="search" placeholder="תאור תפקיד, יחידה, אגף, עיר, משרד…" autocomplete="off">
  </div>
  <div class="field"><label>קטגוריה</label><select id="cat" class="select"></select></div>
  <div class="field"><label>משרד/ארגון</label><select id="min" class="select"></select></div>
  <div class="field"><label>מיקום</label><select id="loc" class="select"></select></div>
  <div class="field"><label>מיון</label>
    <select id="sort" class="select">
      <option value="deadline_desc">מועד האחרון — הרחוק ביותר</option>
      <option value="deadline_asc">מועד האחרון — הקרוב ביותר</option>
      <option value="pub_desc">מתוארך לאחרונה</option>
      <option value="name">שם תפקיד</option>
      <option value="ministry">ארגון</option>
    </select>
  </div>
  <div class="actions">
    <button class="btn" id="clear">נקה הכל</button>
  </div>
</section>

<main class="wrap">
  <div id="count" class="count-line"></div>
  <div id="list"></div>
  <div id="empty" class="empty" style="display:none">אין משרות התואמות את החיפוש/סינון.</div>
</main>

<div class="backdrop" id="backdrop"></div>
<aside class="detail" id="detail" aria-hidden="true">
  <div class="d-head">
    <h2 id="d-title"></h2>
    <button class="close" id="d-close" aria-label="סגירה">×</button>
  </div>
  <div class="d-body">
    <dl class="kv" id="d-kv"></dl>
    <div class="section"><h3>דרישות</h3><div class="box" id="d-req"></div></div>
    <div class="section"><h3>הערות</h3><div class="box" id="d-rem"></div></div>
  </div>
  <div class="d-foot">
    <button class="btn primary" id="d-copy">העתק פרטים</button>
    <button class="btn" id="d-open">פתח באתר</button>
  </div>
</aside>

<script id="data" type="application/json">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const $ = (s)=>document.querySelector(s);
const listEl=$('#list'), emptyEl=$('#empty'), countEl=$('#count');

// ---- populate filters ----
function uniq(arr){return [...new Set(arr.filter(Boolean))].sort((a,b)=>a.localeCompare(b,'he'));}
function fill(id, values){
  const el=$(id);
  el.innerHTML='';
  const all=document.createElement('option'); all.value=''; all.textContent='הכל'; el.appendChild(all);
  values.forEach(v=>{ const o=document.createElement('option'); o.value=v; o.textContent=v; el.appendChild(o); });
}
fill('#cat', uniq(DATA.map(d=>d.category)));
fill('#min', uniq(DATA.map(d=>d.ministry)));
fill('#loc', uniq(DATA.map(d=>d.location)));
$('#total').textContent=DATA.length;

// ---- helpers ----
function esc(s){return (s==null?'':String(s));}
function daysUntil(dateStr){
  if(!dateStr) return null;
  const d=new Date(dateStr+'T00:00:00');
  if(isNaN(d)) return null;
  return Math.ceil((d-new Date(new Date().toISOString().slice(0,10)+'T00:00:00'))/86400000);
}
function deadlineInfo(d){
  const dls=daysUntil(d.submission_deadline);
  const date=d.submission_deadline||'—';
  if(dls===null) return {cls:'dl-closed', text:date};
  if(dls<0) return {cls:'dl-closed', text:date+' · פגה'};
  if(dls<=7) return {cls:'dl-bad', text:date+' · '+dls+' ימים'};
  if(dls<=30) return {cls:'dl-warn', text:date+' · '+dls+' ימים'};
  return {cls:'dl-ok', text:date+' · '+dls+' ימים'};
}

// ---- filtering + sorting ----
function current(){
  const q=$('#q').value.trim().toLowerCase();
  const cat=$('#cat').value, min=$('#min').value, loc=$('#loc').value;
  let out=DATA.filter(p=>{
    if(cat && p.category!==cat) return false;
    if(min && p.ministry!==min) return false;
    if(loc && p.location!==loc) return false;
    if(q){
      const hay=[p.position,p.title,p.ministry,p.unit,p.location,p.category,p.rank,p.tender_number,p.dedicated,p.publish_type].join(' ').toLowerCase();
      if(!hay.includes(q)) return false;
    }
    return true;
  });
  const sort=$('#sort').value;
  const cmp={
    deadline_desc:(a,b)=>(b.submission_deadline||'').localeCompare(a.submission_deadline||''),
    deadline_asc:(a,b)=>(a.submission_deadline||'').localeCompare(b.submission_deadline||''),
    pub_desc:(a,b)=>(b.pub_date||'').localeCompare(a.pub_date||''),
    name:(a,b)=>(a.position||'').localeCompare(b.position||'','he'),
    ministry:(a,b)=>(a.ministry||'').localeCompare(b.ministry||'','he'),
  }[sort];
  out.sort(cmp);
  return out;
}

// ---- render list ----
function render(){
  const items=current();
  $('#shown').textContent=items.length;
  countEl.textContent = items.length ? ('מוצגות '+items.length+' משרות') : '';
  emptyEl.style.display = items.length? 'none':'block';
  // rebuild
  listEl.innerHTML='';
  const frag=document.createDocumentFragment();
  items.forEach((p,i)=>{
    const row=document.createElement('div');
    row.className='row'; row.tabIndex=0;
    row.dataset.idx=i;
    const dl=deadlineInfo(p);
    row.innerHTML=
      '<div class="rtop">'+
        '<div class="rmain">'+
          '<p class="rtitle">'+esc(p.title||p.position||'')+'</p>'+
          '<p class="rpos">'+esc(p.position||'')+'</p>'+
          '<div class="rmeta">'+
            '<span class="badge gray">'+esc(p.ministry||'')+'</span>'+
            (p.location?'<span class="badge loc">'+esc(p.location)+'</span>':'')+
            (p.category?'<span class="badge">'+esc(p.category)+'</span>':'')+
            (p.rank?'<span class="badge gray">דרגה '+esc(p.rank)+'</span>':'')+
          '</div>'+
        '</div>'+
        '<div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end">'+
          '<span class="deadline '+dl.cls+'">'+dl.text+'</span>'+
          '<span class="rnum">מכרז '+esc(p.tender_number||'')+'</span>'+
        '</div>'+
      '</div>';
    row.addEventListener('click',()=>openDetail(p,row));
    row.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openDetail(p,row);}});
    frag.appendChild(row);
  });
  listEl.appendChild(frag);
  // keep selected highlight
  if(currentIdx!=null){
    const el=listEl.querySelector('[data-idx="'+currentIdx+'"]');
    if(el) el.classList.add('selected');
  }
}

// ---- detail ----
let currentIdx=null, currentPos=null;
function openDetail(p,row){
  currentIdx = row? row.dataset.idx : null;
  currentPos=p;
  listEl.querySelectorAll('.row.selected').forEach(r=>r.classList.remove('selected'));
  if(row) row.classList.add('selected');
  $('#d-title').textContent=p.title||p.position||'';
  const kv=[
    ['מכרז',p.tender_number],
    ['תפקיד',p.position],
    ['ארגון',p.ministry],
    ['אגף/יחידה',p.unit],
    ['מיקום',p.location],
    ['קטגוריה',p.category],
    ['דרגה',p.rank],
    ['מספר משרות',p.job_number],
    ['אחוז',p.percent],
    ['סוג',p.publish_type],
    ['תאריך פרסום',p.pub_date],
    ['מועד אחרון',p.submission_deadline],
    ['ID דרישה',p.request_id],
  ];
  $('#d-kv').innerHTML=kv.map(([k,v])=>'<dt>'+k+'</dt><dd>'+esc(v)+'</dd>').join('');
  $('#d-req').textContent=p.requirements||'—';
  $('#d-rem').textContent=p.remarks||'—';
  $('#detail').classList.add('on'); $('#detail').setAttribute('aria-hidden','false');
  $('#backdrop').classList.add('on');
}
function closeDetail(){
  $('#detail').classList.remove('on'); $('#detail').setAttribute('aria-hidden','true');
  $('#backdrop').classList.remove('on');
  listEl.querySelectorAll('.row.selected').forEach(r=>r.classList.remove('selected'));
  currentIdx=null;
}
function copyDetails(){
  if(!currentPos) return;
  const p=currentPos;
  const txt=['מכרז: '+p.tender_number,'תפקיד: '+(p.title||p.position),'ארגון: '+p.ministry,'אגף: '+(p.unit||''),
    'מיקום: '+p.location,'קטגוריה: '+p.category,'דרגה: '+(p.rank||''),'מועד אחרון: '+p.submission_deadline,'',
    'דרישות:',''+(p.requirements||''),'','הערות:',''+(p.remarks||'')].join('\n');
  navigator.clipboard.writeText(txt).then(()=>{
    const b=$('#d-copy'); const t=b.textContent; b.textContent='הועתק ✓'; setTimeout(()=>b.textContent=t,1200);
  }).catch(()=>{});
}

// ---- events ----
['#q','#cat','#min','#loc','#sort'].forEach(s=>$(s).addEventListener('input',render));
$('#clear').addEventListener('click',()=>{
  $('#q').value='';$('#cat').value='';$('#min').value='';$('#loc').value='';
  $('#sort').value='deadline_desc';
  render();
});
$('#d-close').addEventListener('click',closeDetail);
$('#backdrop').addEventListener('click',closeDetail);
$('#d-copy').addEventListener('click',copyDetails);
$('#d-open').addEventListener('click',()=>{
  // Merkava public portal search by tender number
  window.open('https://merkava.mrp.gov.il/','_blank','noopener');
});
document.addEventListener('keydown',e=>{ if(e.key==='Escape') closeDetail(); });

render();
</script>
</body>
</html>
"""

HTML = HTML.replace("__DATA__", DATA_JSON)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)

print("wrote", OUT, os.path.getsize(OUT), "bytes")
print("positions embedded:", len(data))
