#!/usr/bin/env python3
"""Build the Qatom Scorecard site: one page per item, a badge per item, and the data files.

    make_scorecard_site.py <sweep.json> <out-dir> [--base-url URL]

<sweep.json>  the newest approved sweep (scores/<date>-stage1.json).
<out-dir>     static files for the Scorecard Worker (worker/wrangler.toml serves this folder).

Before writing anything, the build re-runs tools/score_stage1.py on the published inputs in
scores/inputs/ and stops if any score differs from the sweep. So every page it writes has
been re-run from public inputs, and says so.

Writes:
  index.html              the searchable list
  item/<id>/index.html    one page per item: grade, score, the checks it passed and failed,
                          and how to re-run it
  item/<id>.json          the same, as data
  badge/<id>.svg          the opt-in badge
  scorecard.json          every item, as data
  ratings.json            the old lookup format, kept so existing readers keep working
  _headers                cache rules
Public fields only (policy/publication.md): no improvement suggestions, no reviewer notes,
and security check values stay "withheld" where the detail went to the seller.
"""
import hashlib, html, json, os, re, subprocess, sys, tempfile, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
args = sys.argv[1:]
BASE = "https://scorecard.agentkepler.tech"
if "--base-url" in args:
    i = args.index("--base-url"); BASE = args[i + 1].rstrip("/"); del args[i:i + 2]
SWEEP, OUT = args
REPO = "https://github.com/StarwaterHeaven/Qatom-Review-and-Rating-System"
OFFICIAL = "https://scorecard.qatom.ai"
doc = json.load(open(SWEEP))
if doc.get("human_approval_status") != "Approved":
    sys.exit("refusing to build from a sweep that is not Approved")
esc = lambda s: html.escape(str("" if s is None else s), quote=True)

# ---- 1. Re-run every score from the published inputs ---------------------------------
SCORER = os.path.join(HERE, "score_stage1.py")
scorer_sha = hashlib.sha256(open(SCORER, "rb").read()).hexdigest()
canon = lambda o: json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
sha = lambda o: hashlib.sha256(canon(o)).hexdigest()
inputs_dir = os.path.join(ROOT, "scores", "inputs")
dates = sorted({r["score_taken"] for r in doc["items"]})
work = {}      # id -> private-format record from the re-run
provenance = {}
with tempfile.TemporaryDirectory() as tmp:
    for d in dates:
        cat = os.path.join(inputs_dir, f"{d}-catalog.json")
        jud = os.path.join(inputs_dir, f"{d}-judgments.json")
        if not (os.path.exists(cat) and os.path.exists(jud)):
            sys.exit(f"inputs for {d} are not published in scores/inputs/: publish them first")
        subprocess.run([sys.executable, "-I", SCORER, cat, jud, os.path.join(tmp, d), "--delta",
                        "--private", os.path.join(tmp, d, "p")], check=True, capture_output=True)
        catalog = {i["id"]: i for i in json.load(open(cat))["items"]}
        judg = json.load(open(jud))["items"]
        for r in json.load(open(os.path.join(tmp, d, "p", f"{d}-stage1-private.json"))):
            work[(d, r["id"])] = r
            provenance[(d, r["id"])] = {
                "inputs": {"catalog": f"scores/inputs/{d}-catalog.json", "judgments": f"scores/inputs/{d}-judgments.json"},
                "listing_sha256": sha(catalog[r["id"]]),
                "judgment_sha256": sha(judg[str(r["id"])]),
            }
mismatch = []
for r in doc["items"]:
    w = work.get((r["score_taken"], r["id"]))
    if not w or (w["score"], w["grade"], w["stage"]) != (r["score"], r["grade"], r["stage"]):
        mismatch.append(r["id"])
if mismatch:
    sys.exit(f"re-run does not match the published sweep for items {mismatch}: fix before publishing")

# ---- 2. Public worksheet per item ------------------------------------------------------
CHECKS = {
    "desc_length": "Description is 1 to 1,024 characters",
    "desc_points_llms_txt": "Description links to a read-me for agents (llms.txt)",
    "names_no_individual_items": "Description names kinds of answers, not every single entry",
    "brand_prefix_naming": "Items in the same store share a name prefix",
    "schema_additionalProperties_false": "The list of inputs is closed: no surprise extra inputs",
    "inputs_described": "Every input has a description",
    "units_ranges_stated": "Number inputs say their unit and range",
    "identifier_or_defaults": "One required ID, or every input has a default",
    "no_example_ids_in_schema": "No real IDs used as examples",
    "no_internal_or_pinned_fields": "No inputs the buyer should leave alone",
    "free_sibling_in_storefront": "A free way to try before paying",
    "free_feedback_item": "The store has a free feedback item",
    "llms_txt_pointer": "The store links a read-me for agents",
}
GUIDE = {
    "wrapped_routes_closed": "Only the routes the item needs are open",
    "sensitive_item_assurance": "Extra safety for items that handle secrets or personal data",
    "expected_miss_ok_false": "“Not found” answers come back as a normal reply",
}
GUIDE_WORD = {"pass": "Pass", "fail": "Fail", "n/a": "Doesn't apply", "not_assessed": "Not checked yet", "withheld": "Sent to the seller"}
DIMS = ["Build", "Storefront", "Listing accuracy", "Seller identity", "Price sanity", "Security", "Compliance"]
DIM_PLAIN = {"Build": "How the listing is built", "Storefront": "The seller's store", "Listing accuracy": "Says what you get",
             "Seller identity": "Seller is named", "Price sanity": "Price is clear", "Security": "Safe to use",
             "Compliance": "Required notices"}

def worksheet(r):
    w = work[(r["score_taken"], r["id"])]
    checks = [{"id": k, "check": CHECKS[k], "result": "Pass" if w["build_checks"].get(k, w["storefront_checks"].get(k)) else "Fail"}
              for k in CHECKS if k in w["build_checks"] or k in w["storefront_checks"]]
    checks.append({"id": "price_floor", "check": "Price is 0 or at least 0.001 USD-TDN, with no more than 3 decimals",
                   "result": "Pass" if w["price_floor_ok"] else "Fail"})
    if w.get("category"):
        checks.append({"id": "not_advice_line", "check": "Says it is not financial, health or legal advice",
                       "result": "Pass" if w["not_advice_line"] else "Fail"})
    guide = [{"id": k, "check": GUIDE[k], "result": GUIDE_WORD.get(v, v)} for k, v in w["guide_1_10_checks"].items()]
    return {"parts": [{"part": d, "plain": DIM_PLAIN[d], "score": w["dimensions"][d], "out_of": 5} for d in DIMS],
            "checks": checks, "guide_checks": guide}

items = []
for r in doc["items"]:
    rec = dict(r)
    rec["worksheet"] = worksheet(r)
    p = provenance[(r["score_taken"], r["id"])]
    rec["rerun"] = {"result": "match", "scorer": "tools/score_stage1.py", "scorer_sha256": scorer_sha, **p,
                    "command": f"python3 tools/score_stage1.py {p['inputs']['catalog']} {p['inputs']['judgments']} out --delta"}
    rec["page"] = f"{BASE}/item/{r['id']}"
    rec["badge"] = f"{BASE}/badge/{r['id']}.svg"
    items.append(rec)

partner = [i["score"] for i in items if i.get("disclosure")]
outside = [i["score"] for i in items if not i.get("disclosure")]
avg = lambda xs: round(sum(xs) / len(xs), 1) if xs else None
side = {"qatom_and_partner_stores": {"items": len(partner), "average_score": avg(partner)},
        "outside_stores": {"items": len(outside), "average_score": avg(outside)}}
meta = {k: doc.get(k) for k in ("rubric_version", "sweep_date", "items_scored", "distribution", "approved_by", "approved_on")}
meta.update({"side_by_side": side, "scorer_sha256": scorer_sha, "beta": BASE, "official_home": OFFICIAL})

SK = json.load(open(os.path.join(ROOT, "scorekeepers.json")))["scorekeepers"]
def sk_rows():
    if not SK:
        return "<p class=\"count\">No one yet. Be the first.</p>"
    TEAM = ' <span class="tag">Qatom team</span>'
    rows = "".join("<tr><td><b>" + esc(k["handle"]) + "</b>" + (TEAM if k.get("qatom_team") else "") + "</td><td>" + esc(k["change"]) + '</td><td class="mono">' + esc(k["date"]) + "</td></tr>" for k in SK)
    return f"<table><thead><tr><th>Who</th><th>What they changed</th><th>When</th></tr></thead><tbody>{rows}</tbody></table>"
ISSUE_NEW = f"{REPO}/issues/new"
CONTRIB = f"{REPO}/blob/main/CONTRIBUTING.md"

# ---- 3. Write files ----------------------------------------------------------------------
os.makedirs(os.path.join(OUT, "item"), exist_ok=True)
os.makedirs(os.path.join(OUT, "badge"), exist_ok=True)
def write(path, text):
    full = os.path.join(OUT, path); os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(text)

DISCLAIMER = ("A score shows how well a listing is built. It does not tell you if the service is good, "
              "and it is not investment, legal, medical or financial advice.")
write("scorecard.json", json.dumps({"source": "Qatom Scorecard (beta), published by Team Kepler", "page": BASE,
      "how_each_score_is_made": f"{REPO}/blob/main/rubric/rubric-v{doc['rubric_version']}.md", "disclaimer": DISCLAIMER,
      **meta, "human_approval_status": "Approved", "items": items}, indent=1, ensure_ascii=False) + "\n")
KEEP = ["id", "name", "seller", "score", "grade", "summary", "stage", "stage_url", "rubric_version", "rubric_url",
        "score_taken", "disclosure", "grade_cap", "detail_withheld", "under_appeal"]
write("ratings.json", json.dumps({"source": "Qatom Scorecard (beta), published by Team Kepler", "page": BASE,
      "rubric": f"{REPO}/blob/main/{doc['rubric']}", "appeals": f"{REPO}/blob/main/policy/appeals.md",
      "human_approval_status": "Approved", "approved_on": doc.get("approved_on"),
      **{k: doc.get(k) for k in ("rubric_version", "sweep_date", "stage", "items_scored", "distribution")},
      "items": [{k: i[k] for k in KEEP if k in i} for i in items]}, indent=1, ensure_ascii=False) + "\n")
write("_headers", "/badge/*\n  Cache-Control: public, max-age=3600\n  Access-Control-Allow-Origin: *\n"
      "/*.json\n  Cache-Control: public, max-age=300\n  Access-Control-Allow-Origin: *\n"
      "/item/*\n  Cache-Control: public, max-age=300\n")

# badge
GCOL = {"A": ("#33BAA6", "#0C1A17"), "B": ("#BFE7E0", "#0C1A17"), "C": ("#1C4B4B", "#FFFFFF"),
        "D": ("#EEF3F1", "#1E2B27"), "F": ("#FFFFFF", "#1E2B27"), "?": ("#9AA6A1", "#0C1A17")}
def badge(value, grade, title):
    left, right = "Qatom Scorecard", value
    lw = round(len(left) * 6.4 + 14); rw = round(len(right) * 7.2 + 14); w = lw + rw
    bg, ink = GCOL[grade]
    stroke = '<rect x="%d" y="0.5" width="%d" height="19" rx="2.5" fill="none" stroke="#1E2B27"/>' % (lw, rw - 0.5) if grade == "F" else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="{esc(left)}: {esc(right)}">'
            f'<title>{esc(title)}</title><clipPath id="r"><rect width="{w}" height="20" rx="3"/></clipPath>'
            f'<g clip-path="url(#r)"><rect width="{lw}" height="20" fill="#0C1A17"/><rect x="{lw}" width="{rw}" height="20" fill="{bg}"/></g>{stroke}'
            f'<g font-family="Verdana,DejaVu Sans,Geneva,sans-serif" font-size="11" text-anchor="middle">'
            f'<text x="{lw/2}" y="14" fill="#F2F7F4">{esc(left)}</text>'
            f'<text x="{lw + rw/2}" y="14" fill="{ink}" font-weight="bold">{esc(right)}</text></g></svg>\n')
for i in items:
    write(f"badge/{i['id']}.svg", badge(f"{i['grade']} {i['score']}", i["grade"],
          f"Qatom Scorecard: grade {i['grade']}, {i['score']} out of 100. Checklist {i['rubric_version']}, scored {i['score_taken']}, stage {i['stage']}."))
write("badge/not-scored.svg", badge("not scored yet", "?", "Qatom Scorecard: this item has not been scored yet."))

# shared page chrome (Brand OS styles from the ratings page builder)
src = open(os.path.join(HERE, "make_ratings_page.py")).read()
CSS = src[src.index("<style>") + 7: src.index("</style>")]
CSS += """
.beta{background:var(--q-verd);color:var(--q-pine);font:500 14px/1.5 var(--f-sans);padding:8px 0}
.beta a{color:var(--q-pine)}
.big{font:400 clamp(1.15rem,2vw,1.35rem)/1.4 var(--f-display);color:var(--q-white);margin:22px 0 0;max-width:46ch}
.intro{margin:14px 0 0;max-width:62ch;color:rgba(242,247,244,0.86)}
.intro p{margin:0 0 8px}
.row a.name{color:var(--ink);text-decoration:none}.row a.name:hover{text-decoration:underline}
.rules{margin:clamp(36px,5vw,56px) 0 0;padding:22px 24px;border:1px solid var(--line);border-radius:16px;background:var(--surface)}
.rules h2,.sheet h2{font:400 1.45rem/1.2 var(--f-display);margin:0 0 10px}
.rules ol{margin:0;padding-left:1.2em;display:grid;gap:6px;color:var(--muted)}
.rules b{color:var(--ink)}
.notice{margin:0 0 16px;padding:14px 18px;border-radius:12px;background:var(--panel);border:1px solid var(--line);font-size:15px}
.sheet{margin-top:28px;padding:22px 24px;border:1px solid var(--line);border-radius:16px;background:var(--surface)}
.sheet table{width:100%;border-collapse:collapse;font-size:15px}
.sheet th,.sheet td{text-align:left;padding:9px 8px;border-top:1px solid var(--line);vertical-align:top}
.sheet th{font:500 12.5px/1.2 var(--f-sans);letter-spacing:.1em;text-transform:uppercase;color:var(--eyebrow);border-top:0}
.ok{color:var(--link);font-weight:500}.no{color:var(--ink);font-weight:500}
.mono{font:400 13px/1.55 var(--f-mono);overflow-wrap:anywhere;color:var(--muted)}
.snip{display:block;padding:12px 14px;border-radius:10px;background:var(--panel);border:1px solid var(--line);font:400 13px/1.5 var(--f-mono);overflow-wrap:anywhere;white-space:pre-wrap}
.head{display:flex;gap:18px;align-items:center;margin-top:8px;flex-wrap:wrap}
.head .grade{width:64px;height:64px;font-size:30px;border-radius:18px}
"""
LOCKUP = open(os.path.join(HERE, "brand", "qatom-lockup-horizontal-currentcolor.svg")).read().strip()
FAV = "data:image/svg+xml," + urllib.parse.quote(open(os.path.join(HERE, "brand", "qatom-favicon-verdigris.svg")).read().strip())
RUBRIC_URL = f"{REPO}/blob/main/rubric/rubric-v{doc['rubric_version']}.md"
NEXT_RUBRIC = f"{REPO}/blob/main/rubric/rubric-v2.5.md"

def page(title, desc, hero, main_html, data=None):
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            f"<title>{esc(title)}</title>\n<meta name=\"description\" content=\"{esc(desc)}\">\n"
            "<meta name=\"color-scheme\" content=\"light dark\">\n"
            f"<link rel=\"icon\" href=\"{FAV}\">\n<link rel=\"canonical\" href=\"{esc(BASE)}\">\n"
            "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">\n<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>\n"
            "<link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500&family=Hanken+Grotesk:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap\">\n"
            f"<style>{CSS}</style>\n</head>\n<body>\n"
            f"<div class=\"beta\"><div class=\"wrap\">Beta. The Qatom Scorecard is tested here first and moves to {esc(OFFICIAL.replace('https://',''))} once it is ready. Item links stay the same.</div></div>\n"
            f"<header class=\"hero\"><div class=\"wrap\"><div class=\"brandbar\"><a href=\"https://qatom.ai\" aria-label=\"Qatom\">{LOCKUP}</a><span class=\"by\"><a href=\"/\" style=\"color:inherit;text-decoration:none\">Qatom Scorecard</a></span></div>{hero}</div></header>\n"
            f"<main><div class=\"wrap\">{main_html}</div></main>\n"
            f"<footer><div class=\"wrap\"><span>Qatom Scorecard (beta) · Team Kepler</span><span>Scores of {esc(doc['sweep_date'])} · checklist {esc(doc['rubric_version'])} · <a href=\"/scorecard.json\">scorecard.json</a> · <a href=\"/llms.txt\">llms.txt</a> · <a href=\"{REPO}\">code</a></span></div></footer>\n"
            + (f"<script id=\"data\" type=\"application/json\">{data}</script>\n" if data else "")
            + "</body>\n</html>\n")

RULES = """<section class="rules" aria-label="Fairness rules"><h2>How we keep it fair</h2><ol>
<li><b>Anyone can re-run it.</b> Every score lists the code and the inputs it came from, so you can run it yourself and get the same number.</li>
<li><b>You can see the worksheet.</b> Each item's page shows which checks passed and failed. Two things go only to the seller: security problems someone could misuse, and our tips for fixing things.</li>
<li><b>Our own stores are marked.</b> Stores run by Qatom or its partners say so on every score. Their average is shown next to everyone else's, below.</li>
<li><b>Our own items get no special handling.</b> When one of our listings scores badly, the page says so plainly. Re-scores of stores run by Qatom or a partner are decided by Qatom's directors (Hassan Khan, Dann Toliver or Nick Mumford), and the reason is published.</li>
<li><b>The rules don't change quietly.</b> Changes to how scores are made are announced 7 days ahead.</li>
<li><b>Money never buys points.</b> Paying for anything on Qatom never raises a score.</li>
<li><b>Qatom is one voice.</b> A panel of Scorekeepers will review changes to how scores are made. Qatom will be one voice on it.</li>
<li><b>Clear prices, not cheap prices.</b> From 25 October the score checks that a price is clear, not whether it is high or low.</li>
</ol></section>"""

# index
idx_data = json.dumps({"meta": meta, "items": [{k: i[k] for k in KEEP if k in i} for i in items]}, ensure_ascii=False).replace("</", "<\\/")
hero = (f"<p class=\"eyebrow\">Every listing gets a score anyone can check</p><h1>Qatom Scorecard</h1>"
        f"<p class=\"big\">Anyone can re-run every score and get the same number.</p>"
        "<div class=\"intro\"><p>Every item for sale on Qatom has a page. The Qatom Scorecard gives each page a score. "
        "The score shows if the page is clear and honest: does it say what you get, is the price clear, is it safe to use, is the seller named.</p>"
        "<p>It does <b>not</b> tell you if the service is good. It tells you if the listing is honest and clear. It scores listings, not AI models.</p>"
        "<p>Anyone can help make the scoring better. People who do are called Scorekeepers. <a href=\"#scorekeepers\">Become one</a>.</p></div>"
        "<div class=\"strip\" id=\"strip\"></div>")
main_idx = (f"<p class=\"notice\"><b>Coming 25 October:</b> the price check will look only at whether a price is clear, not whether it is high or low. "
            f"<a href=\"{NEXT_RUBRIC}\">See the change</a>.</p>"
            "<div class=\"bar\" role=\"search\"><div><label for=\"q\">Search items, sellers or item numbers</label>"
            "<input id=\"q\" type=\"search\" placeholder=\"e.g. weather, Harcourt, 24\" autocomplete=\"off\"></div>"
            "<div><label id=\"glabel\">Grade</label><div class=\"chips\" id=\"chips\" role=\"group\" aria-labelledby=\"glabel\"></div></div>"
            "<div><label for=\"sort\">Sort</label><select id=\"sort\"><option value=\"score\">Score, high to low</option><option value=\"id\">Item number</option><option value=\"seller\">Seller</option></select></div></div>"
            "<div class=\"count\" id=\"count\" aria-live=\"polite\"></div><div class=\"list\" id=\"list\"></div>"
            + RULES + "<section class=\"sheet\" id=\"scorekeepers\"><h2>Become a Scorekeeper</h2>"
            "<p>Scorekeepers help make the scoring better. Your first accepted report, idea or fix makes you one. No sign-up.</p>"
            "<table><thead><tr><th>You can</th><th>How</th></tr></thead><tbody>"
            f"<tr><td>Ask for a re-score</td><td><a href=\"{ISSUE_NEW}?template=rescore.yml\">Re-score form</a>, or free catalog item #194</td></tr>"
            f"<tr><td>Report a scoring mistake</td><td><a href=\"{ISSUE_NEW}?template=scorer-mistake.yml\">Mistake form</a>, or \u201cThink this is wrong?\u201d next to any failed check</td></tr>"
            f"<tr><td>Suggest a scoring change</td><td><a href=\"{ISSUE_NEW}?template=scoring-change.yml\">Suggestion form</a></td></tr>"
            f"<tr><td>Improve the code or translate</td><td>A pull request on <a href=\"{REPO}\">GitHub</a></td></tr>"
            "<tr><td>Check our stores</td><td>Re-run the scores of Qatom's own stores and tell us what you find</td></tr>"
            "</tbody></table>"
            "<p style=\"margin-top:14px\"><b>What happens next:</b> Received \u2192 Being reviewed \u2192 Accepted or Not accepted (always with a reason) \u2192 Live. We reply within 2 business days. Mistakes and re-scores are decided within 5 business days; ideas are reviewed once a month and announced 7 days before they take effect.</p>"
            "<p><b>Your credit:</b> your handle goes on this list, in the changelog and on your commit. We show your real name only if you ask.</p>"
            "<p>No GitHub account? Use free catalog item #194 on Qatom with <code>topic: \"rating\"</code>. English or Spanish. "
            f"<a href=\"{CONTRIB}\">Full guide</a> \u00b7 <a href=\"{REPO}/blob/main/CONTRIBUTING.es.md\">En espa\u00f1ol</a></p>"
            "<h2 style=\"margin-top:24px\">Scorekeepers</h2>" + sk_rows() + "</section>"
            + 
            "<section class=\"notes\" aria-label=\"More\">"
            "<div class=\"note\"><h2>Our stores, side by side</h2><p id=\"side\"></p></div>"
            "<div class=\"note\"><h2>Ask for a re-score</h2><p>Free, through catalog item #194 <b>Team Kepler: feedback and help</b> with <code>topic: \"rating\"</code> and your <code>item_id</code>. While we look, the score stays here, marked as under review.</p></div>"
            "<div class=\"note\"><h2>Look up one item</h2><p>Free on Qatom with item #200, or open <code>/item/&lt;number&gt;</code> here. All scores as data: <a href=\"/scorecard.json\">scorecard.json</a>.</p></div>"
            f"<div class=\"note\"><h2>How each score is made</h2><p>The checklist, the scoring code and every input are public at <a href=\"{REPO}\">{REPO.replace('https://','')}</a>. Scores are made by Pirate Kepler, an agent operated for Qatom.</p></div>"
            "</section>")
script = r"""<script>
(function(){
  var D=JSON.parse(document.getElementById('data').textContent),items=D.items,m=D.meta,grade='all';
  var esc=function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
  document.getElementById('strip').innerHTML='<span class="stat">Scores of '+esc(m.sweep_date)+'</span><span class="stat">Checklist '+esc(m.rubric_version)+'</span><span class="stat">'+items.length+' items</span>'+'ABCDF'.split('').map(function(g){return '<span class="stat stat--g"><i>'+g+'</i>'+((m.distribution||{})[g]||0)+'</span>';}).join('');
  var s=m.side_by_side;document.getElementById('side').textContent='Qatom and partner stores: '+s.qatom_and_partner_stores.items+' items, average '+s.qatom_and_partner_stores.average_score+'. Outside stores: '+s.outside_stores.items+' items, average '+s.outside_stores.average_score+'. Our stores follow the seller guide we wrote, so they tend to score higher. Anyone can re-run them to check. Updated every time scores are published.';
  var chips=document.getElementById('chips');
  ['all','A','B','C','D','F'].forEach(function(g){var b=document.createElement('button');b.className='chip';b.type='button';b.textContent=g==='all'?'All':g;b.setAttribute('aria-pressed',g===grade?'true':'false');b.onclick=function(){grade=g;Array.prototype.forEach.call(chips.children,function(c){c.setAttribute('aria-pressed',c===b?'true':'false');});render();};chips.appendChild(b);});
  var q=document.getElementById('q'),sort=document.getElementById('sort');q.addEventListener('input',render);sort.addEventListener('change',render);
  function render(){
    var t=q.value.trim().toLowerCase();
    var rows=items.filter(function(i){if(grade!=='all'&&i.grade!==grade)return false;if(!t)return true;return String(i.id)===t.replace('#','')||((i.name||'')+' '+(i.seller||'')+' '+(i.summary||'')).toLowerCase().indexOf(t)>=0;});
    var so=sort.value;rows.sort(function(a,b){if(so==='id')return a.id-b.id;if(so==='seller')return (a.seller||'~').localeCompare(b.seller||'~')||a.id-b.id;return b.score-a.score||a.id-b.id;});
    document.getElementById('count').textContent=rows.length+' of '+items.length+' items';
    var L=document.getElementById('list');
    if(!rows.length){L.innerHTML='<div class="empty">No items match. Clear the search or pick another grade.</div>';return;}
    L.innerHTML=rows.map(function(i){var tags=[];
      if(i.disclosure)tags.push('<span class="tag tag--note">'+esc(i.disclosure)+'</span>');
      if(i.grade_cap)tags.push('<span class="tag">Grade held at B: a live call found a problem</span>');
      if(i.detail_withheld)tags.push('<span class="tag">Security detail sent to the seller</span>');
      if(i.under_appeal)tags.push('<span class="tag">Re-score requested</span>');
      if(i.stage===2)tags.push('<span class="tag">Checked by a live paid call</span>');
      return '<article class="row"><div class="grade g-'+esc(i.grade)+'" aria-label="Grade '+esc(i.grade)+'">'+esc(i.grade)+'</div><div class="score">'+esc(i.score)+'<small>of 100</small></div><div class="main"><a class="name" href="/item/'+i.id+'">'+esc(i.name)+'</a><div class="meta">#'+esc(i.id)+' · '+esc(i.seller||'seller not named')+' · scored '+esc(i.score_taken)+' · <a href="/item/'+i.id+'">worksheet</a></div><p class="sum">'+esc(i.summary)+'</p>'+(tags.length?'<div class="tags">'+tags.join('')+'</div>':'')+'</div></article>';}).join('');
  }
  render();
})();
</script>"""
write("index.html", page("Qatom Scorecard", "Every Qatom catalog listing gets a score anyone can check.", hero, main_idx, idx_data).replace("</body>", script + "\n</body>"))

# item pages
for i in items:
    ws = i["worksheet"]
    tags = []
    if i.get("disclosure"): tags.append(f'<span class="tag tag--note">{esc(i["disclosure"])}</span>')
    if i.get("grade_cap"): tags.append('<span class="tag">Grade held at B: a live call found a problem</span>')
    if i.get("detail_withheld"): tags.append('<span class="tag">Security detail sent to the seller</span>')
    if i.get("under_appeal"): tags.append('<span class="tag">Re-score requested</span>')
    stage_txt = "Checked by a live paid call (stage 2)" if i["stage"] == 2 else "Listing read as published, no purchase (stage 1)"
    hero_i = (f"<p class=\"eyebrow\">Item #{i['id']}</p><h1>{esc(i['name'])}</h1>"
              f"<p class=\"intro\">Sold by {esc(i['seller'] or 'a seller who has not set a name')}.</p>")
    parts = "".join(f"<tr><td>{esc(p['plain'])}</td><td class=\"mono\">{esc(p['part'])}</td><td>{p['score']} of 5</td></tr>" for p in ws["parts"])
    def wrong(c):
        q = urllib.parse.urlencode({"template": "scorer-mistake.yml", "title": f"Mistake: item #{i['id']}, {c['id']}", "item_id": i["id"], "check_id": c["id"]})
        return f' <a class=\"count\" href=\"{ISSUE_NEW}?{q}\">Think this is wrong?</a>'
    checks = "".join(f"<tr><td>{esc(c['check'])}</td><td class=\"{'ok' if c['result']=='Pass' else 'no'}\">{esc(c['result'])}{wrong(c) if c['result']=='Fail' else ''}</td></tr>" for c in ws["checks"])
    guide = "".join(f"<tr><td>{esc(c['check'])}</td><td>{esc(c['result'])}</td></tr>" for c in ws["guide_checks"])
    rr = i["rerun"]
    snippet = f'<a href="{BASE}/item/{i["id"]}"><img src="{BASE}/badge/{i["id"]}.svg" alt="Qatom Scorecard: {i["grade"]} {i["score"]}"></a>'
    main_i = (f"<div class=\"head\"><div class=\"grade g-{esc(i['grade'])}\" aria-label=\"Grade {esc(i['grade'])}\">{esc(i['grade'])}</div>"
              f"<div class=\"score\" style=\"font-size:28px\">{i['score']}<small>of 100</small></div>"
              f"<div class=\"meta\">Scored {esc(i['score_taken'])} · {stage_txt} · <a href=\"{esc(i['rubric_url'])}\">checklist {esc(i['rubric_version'])}</a></div></div>"
              f"<p class=\"sum\" style=\"margin-top:16px;font-size:17px\">{esc(i['summary'])}</p>"
              + (f"<div class=\"tags\" style=\"margin-top:10px\">{''.join(tags)}</div>" if tags else "")
              + f"<section class=\"sheet\"><h2>The worksheet</h2><p class=\"count\">The score is the average of seven parts, each out of 5, times 20.</p>"
              f"<table><thead><tr><th>Part</th><th>Name in the code</th><th>Score</th></tr></thead><tbody>{parts}</tbody></table>"
              f"<h2 style=\"margin-top:24px\">Checks</h2><table><thead><tr><th>Check</th><th>Result</th></tr></thead><tbody>{checks}</tbody></table>"
              f"<h2 style=\"margin-top:24px\">Safety checks from the seller guide</h2><table><thead><tr><th>Check</th><th>Result</th></tr></thead><tbody>{guide}</tbody></table>"
              "<p class=\"count\">Our tips for fixing things go to the seller, not here.</p>"
              f"<p>See a better way to check this? <a href=\"{ISSUE_NEW}?template=scoring-change.yml\">Suggest a scoring change</a> and become a <a href=\"/#scorekeepers\">Scorekeeper</a>.</p></section>"
              f"<section class=\"sheet\"><h2>Re-run this score yourself</h2><p>Get the <a href=\"{REPO}\">code</a>, then run:</p>"
              f"<code class=\"snip\">{esc(rr['command'])}</code>"
              f"<p class=\"mono\">Listing as read: sha256 {rr['listing_sha256']}<br>Reviewer's judgment: sha256 {rr['judgment_sha256']}<br>Scoring code: sha256 {rr['scorer_sha256']}<br>Re-run when this page was built: same score.</p></section>"
              f"<section class=\"sheet\"><h2>For the seller</h2><p>Want a re-score? Free, through catalog item #194 with <code>topic: \"rating\"</code> and <code>item_id: {i['id']}</code>.</p>"
              f"<p>Show your score (optional). Paste this where you like:</p><p><img src=\"/badge/{i['id']}.svg\" alt=\"Qatom Scorecard: {i['grade']} {i['score']}\"></p>"
              f"<code class=\"snip\">{esc(snippet)}</code><p class=\"count\">The badge always shows the current score and links back here, so it can't be faked.</p></section>"
              f"<p class=\"count\" style=\"margin-top:24px\">{esc(DISCLAIMER)} <a href=\"/item/{i['id']}.json\">This page as data</a>.</p>")
    write(f"item/{i['id']}/index.html", page(f"#{i['id']} {i['name']} · Qatom Scorecard", f"Qatom Scorecard for item {i['id']}: grade {i['grade']}, {i['score']} of 100.", hero_i, main_i))
    write(f"item/{i['id']}.json", json.dumps({"ok": True, "item_id": i["id"], **{k: v for k, v in i.items() if k != "id"},
          "score_out_of": 100, "disclaimer": DISCLAIMER}, indent=1, ensure_ascii=False) + "\n")

print(f"built {len(items)} items into {OUT}; re-run matched all; side by side {side}")
