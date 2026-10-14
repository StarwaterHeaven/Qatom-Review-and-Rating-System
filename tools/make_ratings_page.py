#!/usr/bin/env python3
"""Build the public, searchable ratings page from the newest published sweep.

    make_ratings_page.py <scores.json> <out.html> [--fragment]

Writes a single self-contained HTML file with the scores embedded (no fetches), suitable
for GitHub Pages at docs/index.html. --fragment omits the doctype/html/head/body wrapper.
Only public fields are used (policy/publication.md).
"""
import html, json, sys

src, out = sys.argv[1], sys.argv[2]
fragment = "--fragment" in sys.argv
doc = json.load(open(src))
if doc.get("human_approval_status") != "Approved":
    sys.exit("refusing to build a public page from a sweep that is not Approved")

KEEP = ["id", "name", "seller", "score", "grade", "summary", "stage", "rubric_version",
        "score_taken", "disclosure", "grade_cap", "detail_withheld", "under_appeal"]
items = [{k: i[k] for k in KEEP if k in i} for i in doc["items"]]
meta = {k: doc.get(k) for k in ("rubric_version", "sweep_date", "stage", "items_scored", "distribution")}
data = json.dumps({"meta": meta, "items": items}, ensure_ascii=False).replace("</", "<\\/")

REPO = "https://github.com/StarwaterHeaven/Qatom-Review-and-Rating-System"
body = r"""<title>Qatom Catalog Ratings</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="Listing-quality ratings for every public Qatom catalog item, published by Team Kepler.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: a ledger. Summary strip on top, then filter bar, then one row per catalog item. */
:root{
  --bg:#f6f7f9; --surface:#ffffff; --ink:#151a23; --muted:#5b6474; --line:#dfe3ea;
  --accent:#2b5bd7; --accent-ink:#ffffff;
  --gA:#1f7a4d; --gB:#4a7f2a; --gC:#9a6b00; --gD:#b4521e; --gF:#b3261e;
  --gA-bg:#e3f3ea; --gB-bg:#eaf3df; --gC-bg:#fbf0d6; --gD-bg:#fbe6da; --gF-bg:#fbe1df;
  --f-body:"Figtree",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --f-mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#0f131a; --surface:#161b24; --ink:#e7ebf2; --muted:#9aa4b5; --line:#283040;
  --accent:#7aa2ff; --accent-ink:#0f131a;
  --gA:#6fd3a0; --gB:#a6d37a; --gC:#e8c25a; --gD:#f09a6a; --gF:#ff8a80;
  --gA-bg:#163326; --gB-bg:#22301a; --gC-bg:#352b12; --gD-bg:#3a2216; --gF-bg:#3d1b19;
  color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#0f131a; --surface:#161b24; --ink:#e7ebf2; --muted:#9aa4b5; --line:#283040;
  --accent:#7aa2ff; --accent-ink:#0f131a;
  --gA:#6fd3a0; --gB:#a6d37a; --gC:#e8c25a; --gD:#f09a6a; --gF:#ff8a80;
  --gA-bg:#163326; --gB-bg:#22301a; --gC-bg:#352b12; --gD-bg:#3a2216; --gF-bg:#3d1b19;
  color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:15px;line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding-block:32px 56px;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));
  display:grid;gap:24px}
header{display:grid;gap:8px}
.eyebrow{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600}
h1{font-size:clamp(26px,4vw,36px);line-height:1.15;margin:0;font-weight:700;text-wrap:balance}
.lede{margin:0;color:var(--muted);max-width:68ch}
.lede a,.foot a{color:var(--accent)}
.strip{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.stat{font-family:var(--f-mono);font-size:13px;color:var(--muted);padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--surface)}
.bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.bar input[type=search]{flex:1 1 260px;min-width:0;font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink)}
.bar input:focus-visible,.chip:focus-visible,select:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{font:600 13px var(--f-mono);padding:7px 11px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer}
.chip[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
select{font:inherit;padding:9px 10px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink)}
.count{font-size:13px;color:var(--muted)}
.list{display:grid;gap:0;border:1px solid var(--line);border-radius:10px;background:var(--surface);overflow:hidden}
.row{display:grid;grid-template-columns:56px 64px minmax(0,1fr);gap:14px;padding:14px 16px;border-top:1px solid var(--line);align-items:start}
.row:first-child{border-top:0}
.grade{font:700 20px var(--f-mono);width:44px;height:44px;border-radius:8px;display:grid;place-items:center}
.g-A{color:var(--gA);background:var(--gA-bg)}.g-B{color:var(--gB);background:var(--gB-bg)}.g-C{color:var(--gC);background:var(--gC-bg)}.g-D{color:var(--gD);background:var(--gD-bg)}.g-F{color:var(--gF);background:var(--gF-bg)}
.score{font:600 18px var(--f-mono);font-variant-numeric:tabular-nums;padding-top:9px}
.score small{display:block;font-size:11px;color:var(--muted);font-weight:400}
.main{min-width:0;display:grid;gap:4px}
.name{font-weight:600;overflow-wrap:anywhere}
.meta{font-size:13px;color:var(--muted);font-family:var(--f-mono);overflow-wrap:anywhere}
.sum{margin:0;max-width:75ch}
.tags{display:flex;flex-wrap:wrap;gap:6px}
.tag{font-size:12px;padding:2px 8px;border-radius:4px;border:1px solid var(--line);color:var(--muted)}
.tag.warn{color:var(--gD);border-color:currentColor}
.empty{padding:28px 16px;color:var(--muted)}
.foot{font-size:13px;color:var(--muted);display:grid;gap:6px;max-width:80ch}
.foot p{margin:0}
code{font-family:var(--f-mono);font-size:.92em}
@media (max-width:520px){.row{grid-template-columns:48px minmax(0,1fr)}.score{grid-column:2;padding-top:0;order:2}.main{grid-column:1 / -1;order:3}}
@media (prefers-reduced-motion:no-preference){.chip{transition:background .15s,color .15s}}
</style>
<div class="wrap">
  <header>
    <div class="eyebrow">Team Kepler · Qatom catalog</div>
    <h1>Qatom Catalog Ratings</h1>
    <p class="lede">How well each public Qatom catalog item is listed: schema, description, price, seller name, storefront, security and compliance, scored against the <a href="https://github.com/StarwaterHeaven/qatom-seller-guide">seller guide</a>. A grade rates the listing, not the service behind it, and is not investment, legal, medical or financial advice.</p>
  </header>
  <div class="strip" id="strip"></div>
  <div class="bar" role="search">
    <label for="q" class="eyebrow" style="flex-basis:100%">Search items, sellers or item numbers</label>
    <input id="q" type="search" placeholder="e.g. weather, Harcourt, 24" autocomplete="off">
    <div class="chips" id="chips" aria-label="Filter by grade"></div>
    <label for="sort" class="count">Sort</label>
    <select id="sort"><option value="score">Score, high to low</option><option value="id">Item number</option><option value="seller">Seller</option></select>
  </div>
  <div class="count" id="count" aria-live="polite"></div>
  <div class="list" id="list"></div>
  <footer class="foot">
    <p><strong>Dispute a rating or ask for a re-score:</strong> free, through catalog item #194 "Team Kepler: feedback and help" on the Qatom master MCP (<code>catalog_search</code> "Team Kepler", then <code>agent_checkout</code> with <code>topic: "rating"</code> and your <code>item_id</code>). A disputed score stays here, marked under appeal.</p>
    <p><strong>Disclosure:</strong> ratings are produced by Pirate Kepler, an agent operated for Qatom. First-party stores are marked as not arm's length.</p>
    <p>Rubric, policies, raw scores and the scoring tool: <a href="__REPO__">__REPO_SHORT__</a>. Sellers: the <code>qatom-rating-guide</code> skill in that repo explains every check and how to raise a score.</p>
  </footer>
</div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var D = JSON.parse(document.getElementById('data').textContent);
  var items = D.items, m = D.meta, grade = 'all';
  var esc = function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
  document.getElementById('strip').innerHTML =
    '<span class="stat">Sweep '+esc(m.sweep_date)+'</span><span class="stat">Rubric '+esc(m.rubric_version)+'</span><span class="stat">Stage '+esc(m.stage)+' (listing as published)</span><span class="stat">'+items.length+' items</span>' +
    'ABCDF'.split('').map(function(g){return '<span class="stat">'+g+' '+((m.distribution||{})[g]||0)+'</span>';}).join('');
  var chips = document.getElementById('chips');
  ['all','A','B','C','D','F'].forEach(function(g){
    var b=document.createElement('button'); b.className='chip'; b.type='button'; b.id='chip-'+g;
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
      if(i.disclosure) tags.push('<span class="tag">'+esc(i.disclosure)+'</span>');
      if(i.grade_cap) tags.push('<span class="tag warn">Grade capped at B: functional defect seen in a live call</span>');
      if(i.detail_withheld) tags.push('<span class="tag warn">Security detail sent to the seller, not published</span>');
      if(i.under_appeal) tags.push('<span class="tag warn">Under appeal</span>');
      return '<div class="row"><div class="grade g-'+esc(i.grade)+'" aria-label="Grade '+esc(i.grade)+'">'+esc(i.grade)+'</div>'+
        '<div class="score">'+esc(i.score)+'<small>of 100</small></div>'+
        '<div class="main"><div class="name">'+esc(i.name)+'</div>'+
        '<div class="meta">#'+esc(i.id)+' · '+esc(i.seller||'seller not set')+' · stage '+esc(i.stage)+' · '+esc(i.score_taken)+'</div>'+
        '<p class="sum">'+esc(i.summary)+'</p>'+(tags.length?'<div class="tags">'+tags.join('')+'</div>':'')+'</div></div>';
    }).join('');
  }
  render();
})();
</script>
"""
body = body.replace("__DATA__", data).replace("__REPO__", REPO).replace("__REPO_SHORT__", REPO.replace("https://", ""))
if not fragment:
    body = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + body.replace("<div class=\"wrap\">", "</head>\n<body>\n<div class=\"wrap\">", 1)
            + "</body>\n</html>\n")
open(out, "w").write(body)
print(f"wrote {out}: {len(items)} items")
