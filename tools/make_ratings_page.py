#!/usr/bin/env python3
"""Build the public, searchable ratings page from the newest published sweep.

    make_ratings_page.py <scores.json> <out.html> [--fragment]

Writes a single self-contained HTML file with the scores embedded (no fetches), suitable
for GitHub Pages at docs/index.html. --fragment omits the doctype/html/head/body wrapper.
Also writes ratings.json next to it: the same public fields, which the free catalog rating
lookup item reads, so the page and the lookup can never disagree.
Only public fields are used (policy/publication.md).
"""
import html, json, os, sys

src, out = sys.argv[1], sys.argv[2]
fragment = "--fragment" in sys.argv
doc = json.load(open(src))
if doc.get("human_approval_status") != "Approved":
    sys.exit("refusing to build a public page from a sweep that is not Approved")

KEEP = ["id", "name", "seller", "score", "grade", "summary", "stage", "stage_url", "rubric_version",
        "rubric_url", "score_taken", "disclosure", "grade_cap", "detail_withheld", "under_appeal"]
items = [{k: i[k] for k in KEEP if k in i} for i in doc["items"]]
meta = {k: doc.get(k) for k in ("rubric_version", "sweep_date", "stage", "items_scored", "distribution")}
data = json.dumps({"meta": meta, "items": items}, ensure_ascii=False).replace("</", "<\\/")

REPO = "https://github.com/StarwaterHeaven/Qatom-Review-and-Rating-System"
PAGE = "https://starwaterheaven.github.io/Qatom-Review-and-Rating-System/"
pub = {
    "source": "Qatom Catalog Ratings, published by Team Kepler",
    "page": PAGE,
    "rubric": f"{REPO}/blob/main/{doc.get('rubric', 'rubric/')}",
    "appeals": f"{REPO}/blob/main/policy/appeals.md",
    "human_approval_status": doc.get("human_approval_status"),
    "approved_on": doc.get("approved_on"),
    **meta,
    "items": items,
}
with open(os.path.join(os.path.dirname(os.path.abspath(out)), "ratings.json"), "w") as f:
    json.dump(pub, f, indent=1, ensure_ascii=False)
    f.write("\n")
HERE = os.path.dirname(os.path.abspath(__file__))
# Brand OS assets: placed lockup artwork (Susana Khan's 19 Sep 2026 set, fill set to
# currentColor so CSS gives it the approved colour) and the verdigris-field favicon.
LOCKUP = open(os.path.join(HERE, "brand", "qatom-lockup-horizontal-currentcolor.svg")).read().strip()
FAVICON = "data:image/svg+xml," + __import__("urllib.parse").parse.quote(
    open(os.path.join(HERE, "brand", "qatom-favicon-verdigris.svg")).read().strip())
body = r"""<title>Qatom Catalog Ratings</title>
<meta name="description" content="Listing-quality ratings for every public Qatom catalog item, published by Team Kepler.">
<meta name="qatom:brand" content="Qatom color system and lockup construction, 19 Sep 2026">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="__FAVICON__">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500&family=Hanken+Grotesk:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Qatom Brand OS (current): verdigris is the one loud colour; pine and oxide are grounds;
   cool neutrals only. Locked values from qatom-color-system.html (19 Sep 2026). */
:root{
  --q-verd:#33BAA6; --q-verd-deep:#278A7F; --q-verd-bright:#79D2C5;
  --q-pine:#0C1A17; --q-oxide:#1C4B4B; --q-white:#FFFFFF; --q-paper:#FBFDFC; --q-mist:#F2F7F4; --q-coolgrey:#EEF3F1;
  --q-ink:#1E2B27; --q-ink-soft:#5B6A63;
  --bg:var(--q-paper); --surface:var(--q-white); --panel:var(--q-mist); --ink:var(--q-ink); --muted:var(--q-ink-soft);
  --line:rgba(30,43,39,0.12); --link:var(--q-oxide); --eyebrow:var(--q-verd-deep);
  --chip-on-bg:var(--q-verd); --chip-on-ink:var(--q-pine);
  --gA-bg:var(--q-verd); --gA-ink:var(--q-pine);
  --gB-bg:#BFE7E0; --gB-ink:var(--q-pine);
  --gC-bg:var(--q-mist); --gC-ink:var(--q-oxide);
  --gD-bg:var(--q-coolgrey); --gD-ink:var(--q-ink-soft);
  --gF-bg:transparent; --gF-ink:var(--q-ink);
  --f-display:"Source Serif 4",Georgia,serif;
  --f-sans:"Hanken Grotesk","Segoe UI",system-ui,sans-serif;
  --f-mono:"IBM Plex Mono",Consolas,ui-monospace,monospace;
  color-scheme:light;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:var(--q-pine); --surface:#12241F; --panel:#12241F; --ink:var(--q-mist); --muted:rgba(242,247,244,0.72);
  --line:rgba(242,247,244,0.16); --link:var(--q-verd-bright); --eyebrow:var(--q-verd-bright);
  --gB-bg:#2A5E57; --gB-ink:var(--q-mist); --gC-bg:var(--q-oxide); --gC-ink:var(--q-mist);
  --gD-bg:#1A2B27; --gD-ink:rgba(242,247,244,0.78); --gF-ink:var(--q-mist);
  color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:var(--q-pine); --surface:#12241F; --panel:#12241F; --ink:var(--q-mist); --muted:rgba(242,247,244,0.72);
  --line:rgba(242,247,244,0.16); --link:var(--q-verd-bright); --eyebrow:var(--q-verd-bright);
  --gB-bg:#2A5E57; --gB-ink:var(--q-mist); --gC-bg:var(--q-oxide); --gC-ink:var(--q-mist);
  --gD-bg:#1A2B27; --gD-ink:rgba(242,247,244,0.78); --gF-ink:var(--q-mist);
  color-scheme:dark}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:400 16px/1.6 var(--f-sans)}
b,strong{font-weight:500}
a{color:var(--link);text-decoration-color:var(--q-verd);text-decoration-thickness:2px;text-underline-offset:3px}
a:hover{text-decoration-color:currentColor}
:where(a,button,input,select):focus-visible{outline:2px solid var(--link);outline-offset:3px;border-radius:4px}
.wrap{max-width:1060px;margin:0 auto;padding-inline:max(16px,env(safe-area-inset-left,0px)) max(16px,env(safe-area-inset-right,0px))}
@media (min-width:720px){.wrap{padding-inline:clamp(24px,5vw,56px)}}

/* Hero: the signature pairing, verdigris on near-black. */
.hero{background:var(--q-pine);color:var(--q-mist);padding-block:28px clamp(44px,6vw,72px)}
.brandbar{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:clamp(40px,6vw,64px)}
.lockup{display:block;width:150px;height:auto;color:var(--q-verd)}
.brandbar .by{font:500 12.5px/1 var(--f-sans);letter-spacing:.14em;text-transform:uppercase;color:var(--q-verd-bright)}
.eyebrow{font:500 12.5px/1.2 var(--f-sans);letter-spacing:.14em;text-transform:uppercase;color:var(--eyebrow);margin:0 0 14px}
.hero .eyebrow{color:var(--q-verd-bright)}
h1{font:400 clamp(2.3rem,5.4vw,3.9rem)/1.08 var(--f-display);letter-spacing:-0.015em;margin:0;color:var(--q-white);text-wrap:balance}
.lede{font-size:clamp(1.05rem,1.7vw,1.22rem);max-width:60ch;margin:18px 0 0;color:rgba(242,247,244,0.86)}
.lede a{color:var(--q-verd-bright)}
.strip{display:flex;flex-wrap:wrap;gap:8px;margin-top:28px}
.stat{font:400 13px/1 var(--f-mono);padding:8px 12px;border-radius:999px;border:1px solid rgba(242,247,244,0.18);color:rgba(242,247,244,0.86);font-variant-numeric:tabular-nums}
.stat a{color:inherit}
.stat--g{display:inline-flex;gap:8px;align-items:center}
.stat--g i{font-style:normal;color:var(--q-verd-bright)}

/* Ledger */
main{padding-block:clamp(32px,5vw,56px) clamp(48px,7vw,88px)}
.bar{display:grid;grid-template-columns:minmax(0,1fr);gap:12px;margin-bottom:12px}
@media (min-width:860px){.bar{grid-template-columns:minmax(0,1fr) auto auto;align-items:end}}
.bar label{display:block;font:500 12.5px/1.2 var(--f-sans);letter-spacing:.14em;text-transform:uppercase;color:var(--eyebrow);margin-bottom:8px}
.bar input[type=search],.bar select{width:100%;font:400 16px/1.2 var(--f-sans);padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--surface);color:var(--ink);min-height:48px}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{font:500 14px/1 var(--f-sans);min-width:44px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer}
.chip[aria-pressed="true"]{background:var(--chip-on-bg);border-color:var(--chip-on-bg);color:var(--chip-on-ink)}
.count{font-size:14px;color:var(--muted);margin:16px 0 10px}
.list{border:1px solid var(--line);border-radius:20px;background:var(--surface);overflow:hidden}
.row{display:grid;grid-template-columns:52px 64px minmax(0,1fr);gap:16px;padding:18px 20px;border-top:1px solid var(--line);align-items:start}
.row:first-child{border-top:0}
.grade{font:500 22px/1 var(--f-display);width:48px;height:48px;border-radius:14px;display:grid;place-items:center}
.g-A{background:var(--gA-bg);color:var(--gA-ink)}
.g-B{background:var(--gB-bg);color:var(--gB-ink)}
.g-C{background:var(--gC-bg);color:var(--gC-ink);box-shadow:inset 0 0 0 1px var(--line)}
.g-D{background:var(--gD-bg);color:var(--gD-ink);box-shadow:inset 0 0 0 1px var(--line)}
.g-F{background:var(--gF-bg);color:var(--gF-ink);box-shadow:inset 0 0 0 1.5px currentColor}
.score{font:500 20px/1 var(--f-sans);font-variant-numeric:tabular-nums;padding-top:6px}
.score small{display:block;margin-top:4px;font:400 12px/1 var(--f-sans);color:var(--muted)}
.main{min-width:0;display:grid;gap:6px}
.name{font:500 17px/1.35 var(--f-sans);overflow-wrap:anywhere}
.meta{font:400 13px/1.5 var(--f-mono);color:var(--muted);overflow-wrap:anywhere}
.meta a{color:var(--link)}
.sum{margin:0;max-width:72ch;color:var(--ink)}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:2px}
.tag{font:400 13px/1.3 var(--f-sans);padding:4px 10px;border-radius:999px;background:var(--panel);color:var(--muted);border:1px solid var(--line)}
.tag--note{color:var(--ink)}
.empty{padding:32px 20px;color:var(--muted)}
@media (max-width:560px){
  .row{grid-template-columns:48px minmax(0,1fr);gap:12px 14px;padding:16px}
  .score{padding-top:4px}
  .main{grid-column:1 / -1}
}

/* Footer notes */
.notes{margin-top:clamp(36px,5vw,56px);display:grid;gap:14px;grid-template-columns:minmax(0,1fr)}
@media (min-width:860px){.notes{grid-template-columns:repeat(2,minmax(0,1fr))}}
.note{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px 22px}
.note h2{font:400 1.25rem/1.2 var(--f-display);margin:0 0 8px}
.note p{margin:0;font-size:15px;color:var(--muted)}
.note code{font:400 13.5px/1 var(--f-mono);color:var(--ink)}
footer{border-top:1px solid var(--line);padding-block:24px 40px;font:400 13px/1.6 var(--f-mono);color:var(--muted)}
footer .wrap{display:flex;flex-wrap:wrap;gap:8px 20px;justify-content:space-between}
@media (prefers-reduced-motion:no-preference){.chip{transition:background .15s,color .15s,border-color .15s}}
</style>
<header class="hero">
  <div class="wrap">
    <div class="brandbar">
      <a href="https://qatom.ai" aria-label="Qatom">__LOCKUP__</a>
      <span class="by">Team Kepler</span>
    </div>
    <p class="eyebrow">Catalog ratings</p>
    <h1>Qatom Catalog Ratings</h1>
    <p class="lede">How well each public Qatom catalog item is listed: schema, description, price, seller name, storefront, security and compliance, scored against the <a href="https://github.com/StarwaterHeaven/qatom-seller-guide">seller guide</a>. A grade rates the listing, not the service behind it, and is not investment, legal, medical or financial advice.</p>
    <div class="strip" id="strip"></div>
  </div>
</header>
<main>
  <div class="wrap">
    <div class="bar" role="search">
      <div><label for="q">Search items, sellers or item numbers</label>
        <input id="q" type="search" placeholder="e.g. weather, Harcourt, 24" autocomplete="off"></div>
      <div><label id="glabel">Grade</label><div class="chips" id="chips" role="group" aria-labelledby="glabel"></div></div>
      <div><label for="sort">Sort</label>
        <select id="sort"><option value="score">Score, high to low</option><option value="id">Item number</option><option value="seller">Seller</option></select></div>
    </div>
    <div class="count" id="count" aria-live="polite"></div>
    <div class="list" id="list"></div>
    <section class="notes" aria-label="About these ratings">
      <div class="note"><h2>Look up one item</h2><p>Free, through <b>Qatom Catalog Ratings: free lookup</b> on the Qatom master MCP (<code>agent_checkout</code> with <code>item_id</code>), or read the same data as <a href="ratings.json">ratings.json</a>.</p></div>
      <div class="note"><h2>Dispute a rating</h2><p>Free, through catalog item #194 <b>Team Kepler: feedback and help</b> with <code>topic: "rating"</code> and your <code>item_id</code>. A disputed score stays here, marked under appeal.</p></div>
      <div class="note"><h2>Who rates</h2><p>Ratings are produced by Pirate Kepler, an agent operated for Qatom. Where a seller is a Qatom partner, its rating says so.</p></div>
      <div class="note"><h2>How it is scored</h2><p>Rubric, policies, raw scores and the scoring tool are public at <a href="__REPO__">__REPO_SHORT__</a>. Sellers: the <code>qatom-rating-guide</code> skill there explains every check.</p></div>
    </section>
  </div>
</main>
<footer><div class="wrap"><span>Qatom Catalog Ratings · Team Kepler</span><span id="foot-sweep"></span></div></footer>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var D = JSON.parse(document.getElementById('data').textContent);
  var items = D.items, m = D.meta, grade = 'all';
  var esc = function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
  var lnk = function(u,t){return u&&/^https:\/\//.test(u)?'<a href="'+esc(u)+'" target="_blank" rel="noopener">'+esc(t)+'</a>':esc(t);};
  var first = items[0] || {};
  document.getElementById('strip').innerHTML =
    '<span class="stat">Sweep '+esc(m.sweep_date)+'</span>'+
    '<span class="stat">'+lnk(first.rubric_url,'Rubric '+m.rubric_version)+'</span>'+
    '<span class="stat">'+lnk(first.stage_url,'Stage '+m.stage+': listing as published')+'</span>'+
    '<span class="stat">'+items.length+' items</span>'+
    'ABCDF'.split('').map(function(g){return '<span class="stat stat--g"><i>'+g+'</i>'+((m.distribution||{})[g]||0)+'</span>';}).join('');
  document.getElementById('foot-sweep').textContent = 'Sweep '+m.sweep_date+' · rubric '+m.rubric_version;
  var chips = document.getElementById('chips');
  ['all','A','B','C','D','F'].forEach(function(g){
    var b=document.createElement('button'); b.className='chip'; b.type='button';
    b.textContent = g==='all'?'All':g; b.setAttribute('aria-pressed', g===grade?'true':'false');
    b.onclick=function(){grade=g; Array.prototype.forEach.call(chips.children,function(c){c.setAttribute('aria-pressed', c===b?'true':'false');}); render();};
    chips.appendChild(b);
  });
  var q=document.getElementById('q'), sort=document.getElementById('sort');
  q.addEventListener('input',render); sort.addEventListener('change',render);
  function render(){
    var t=q.value.trim().toLowerCase();
    var rows=items.filter(function(i){
      if(grade!=='all' && i.grade!==grade) return false;
      if(!t) return true;
      return (String(i.id)===t.replace('#','')) || ((i.name||'')+' '+(i.seller||'')+' '+(i.summary||'')).toLowerCase().indexOf(t)>=0;
    });
    var s=sort.value;
    rows.sort(function(a,b){ if(s==='id') return a.id-b.id; if(s==='seller') return (a.seller||'~').localeCompare(b.seller||'~')||a.id-b.id; return b.score-a.score||a.id-b.id; });
    document.getElementById('count').textContent = rows.length+' of '+items.length+' items';
    var L=document.getElementById('list');
    if(!rows.length){L.innerHTML='<div class="empty">No items match. Clear the search or pick another grade.</div>';return;}
    L.innerHTML=rows.map(function(i){
      var tags=[];
      if(i.disclosure) tags.push('<span class="tag tag--note">'+esc(i.disclosure)+'</span>');
      if(i.grade_cap) tags.push('<span class="tag">Grade capped at B: functional defect seen in a live call</span>');
      if(i.detail_withheld) tags.push('<span class="tag">Security detail sent to the seller, not published</span>');
      if(i.under_appeal) tags.push('<span class="tag">Under appeal</span>');
      return '<article class="row"><div class="grade g-'+esc(i.grade)+'" aria-label="Grade '+esc(i.grade)+'">'+esc(i.grade)+'</div>'+
        '<div class="score">'+esc(i.score)+'<small>of 100</small></div>'+
        '<div class="main"><div class="name">'+esc(i.name)+'</div>'+
        '<div class="meta">#'+esc(i.id)+' · '+esc(i.seller||'seller not set')+' · '+lnk(i.stage_url,'stage '+i.stage)+' · '+lnk(i.rubric_url,'rubric '+i.rubric_version)+' · '+esc(i.score_taken)+'</div>'+
        '<p class="sum">'+esc(i.summary)+'</p>'+(tags.length?'<div class="tags">'+tags.join('')+'</div>':'')+'</div></article>';
    }).join('');
  }
  render();
})();
</script>
"""
body = body.replace("__LOCKUP__", LOCKUP).replace("__FAVICON__", FAVICON).replace("__DATA__", data).replace("__REPO__", REPO).replace("__REPO_SHORT__", REPO.replace("https://", ""))
if not fragment:
    body = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + body.replace('<header class="hero">', '</head>\n<body>\n<header class="hero">', 1)
            + "</body>\n</html>\n")
open(out, "w").write(body)
print(f"wrote {out}: {len(items)} items")
