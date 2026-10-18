#!/usr/bin/env python3
"""Stage 1 scorer, rubric 2.4.

    score_stage1.py <catalog.json> <judgments.json> <out-dir> [--private <dir>] [--delta]

<catalog.json>   a read-back of the public catalog: Qatom master MCP `catalog_search` with
                 no query ({"items": [...], "total": n}).
<judgments.json> the reviewer's judged values per item (rubric 2.4, checks marked "judged"):
                 judged_fails, listing_accuracy, seller_identity, price, security,
                 compliance, category, functional_defect, summary, fixes, and the
                 guide 1.10 checks (wrapped_routes_closed, sensitive_item_assurance,
                 expected_miss_ok_false: pass | fail | n/a | not_assessed;
                 sensitive_missing: count of missing assurance elements;
                 stage: 2 where the item was checked by a live paid call, default 1).
<out-dir>        writes <date>-stage1.json and <date>-stage1.md (public fields only).
--private <dir>  also writes the per-item check detail and suggestions (seller-only).
--delta          score only the items that have a judgment (a sweep of new items), while
                 still reading every item in the catalog for the storefront checks. Merge
                 the result onto the last full sweep with tools/merge_sweeps.py.

Automated here: desc_length, desc_points_llms_txt, brand_prefix_naming,
schema_additionalProperties_false, inputs_described, units_ranges_stated,
identifier_or_defaults, the three storefront checks, the price floor, the seller
placeholder test and the not-advice line test. Everything else comes from the judgments
file, so a re-run on the same two inputs gives the same scores.
"""
import json, os, re, sys
from collections import defaultdict

RUBRIC = "2.4"
CHECKS_110 = ("wrapped_routes_closed", "sensitive_item_assurance", "expected_miss_ok_false")
BUILD_CHECKS = [
    "desc_length", "desc_points_llms_txt", "names_no_individual_items", "brand_prefix_naming",
    "schema_additionalProperties_false", "inputs_described", "units_ranges_stated",
    "identifier_or_defaults", "no_example_ids_in_schema", "no_internal_or_pinned_fields",
]
JUDGED_BUILD = {"names_no_individual_items", "no_example_ids_in_schema", "no_internal_or_pinned_fields"}
PLACEHOLDER_SELLERS = {"", "none", "null", "asdfasdf", "test", "seller"}
NOT_ADVICE = re.compile(
    r"not (?:[\w,-]+ ){0,5}advice|informational only|not a (?:forecast|trade recommendation)|estimate only",
    re.I)
NUMERIC = {"number", "integer"}

# Disclosure (policy/disclosure.md, format set by Hassan Khan 16 Oct 2026): a seller that is
# not arm's length from Qatom (first-party stores, Qatom team members) carries
# "Disclosure: <Seller Name> is a Qatom partner." Arm's-length sellers, commercial customers
# included, carry nothing.
PARTNERS = {
    "Centaur League Game Studios", "Qatom Demo", "Qatom Logistics Demo", "Dobox",
    "Kepler Market Services", "Kepler Market Services on Qatom", "Secure Secrets Exchange",
    "Matthew Mihok",
}
def partner_note(name):
    return f"Disclosure: {name} is a Qatom partner."

REPO = "https://github.com/StarwaterHeaven/Qatom-Review-and-Rating-System"
def rubric_url(v):
    return f"{REPO}/blob/main/rubric/rubric-v{v}.md"
def stage_url(v, stage):
    return f"{rubric_url(v)}#5-stages"


def grade_for(score):
    for g, lo in (("A", 85), ("B", 70), ("C", 55), ("D", 40)):
        if score >= lo:
            return g
    return "F"


def seller_key(item):
    s = (item.get("seller") or "").strip()
    return s if s.lower() not in PLACEHOLDER_SELLERS else f"__none__{s.lower()}"


def build_checks(item, store_size, shared_prefix=False):
    desc = item.get("description") or ""
    schema = item.get("input_schema") or {}
    props = schema.get("properties") or {}
    req = schema.get("required") or []
    res = {}
    res["desc_length"] = 1 <= len(desc) <= 1024
    res["desc_points_llms_txt"] = "llms.txt" in desc
    res["brand_prefix_naming"] = store_size <= 1 or ":" in item.get("name", "") or shared_prefix
    res["schema_additionalProperties_false"] = schema.get("additionalProperties") is False
    res["inputs_described"] = all((p or {}).get("description") for p in props.values())

    def numeric_ok(p):
        if p.get("type") not in NUMERIC:
            return True
        has_bounds = any(k in p for k in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"))
        d = p.get("description") or ""
        has_range_text = bool(re.search(r"\d\s*(?:-|to|–)\s*\d|range|between|at least|up to", d, re.I))
        return has_bounds or has_range_text

    res["units_ranges_stated"] = all(numeric_ok(p or {}) for p in props.values())
    def defaulted(p):
        return "default" in p or bool(re.search(r"default|optional|omit|leave (?:this|it) out", p.get("description") or "", re.I))
    res["identifier_or_defaults"] = (not props) or bool(req) or all(defaulted(p or {}) for p in props.values())
    return res


def main():
    args = sys.argv[1:]
    private_dir = None
    delta = "--delta" in args
    if delta:
        args.remove("--delta")
    if "--private" in args:
        i = args.index("--private")
        private_dir = args[i + 1]
        del args[i:i + 2]
    CATALOG, JUDGMENTS, OUTDIR = args
    catalog = [i for i in json.load(open(CATALOG))["items"] if not i.get("private")]
    jdoc = json.load(open(JUDGMENTS))
    J = jdoc["items"]
    DATE = jdoc["sweep_date"]

    # Items with no seller name cannot be told apart by seller. Where the reviewer has
    # established that an unnamed item belongs to a distinct store (its own llms.txt and
    # endpoint), the judgment sets "store" so it is not pooled with other unnamed items.
    def store_key(it):
        return (J.get(str(it["id"])) or {}).get("store") or seller_key(it)

    stores = defaultdict(list)
    for it in catalog:
        stores[store_key(it)].append(it)

    def store_checks(it):
        items = stores[store_key(it)]
        free = [x for x in items if float(x.get("price") or 0) == 0]
        desc = it.get("description") or ""
        is_free = float(it.get("price") or 0) == 0
        return {
            "free_sibling_in_storefront": is_free or bool(free) or bool(re.search(r"\bfree\b[^.]{0,80}?(?:\bat\b|:)\s*(?:https?://)?[\w-]+\.[\w.-]+", desc, re.I)),
            "free_feedback_item": any("feedback" in x.get("name", "").lower() for x in free),
            "llms_txt_pointer": any("llms.txt" in (x.get("description") or "") for x in items),
        }

    out, private, missing = [], [], []
    for it in sorted(catalog, key=lambda x: x["id"]):
        iid = it["id"]
        j = J.get(str(iid))
        if j is None:
            if not delta:
                missing.append(iid)
            continue
        size = len(stores[store_key(it)])
        firsts = {x.get("name", "").split()[0].lower() for x in stores[store_key(it)] if x.get("name")}
        b = build_checks(it, size, shared_prefix=len(firsts) == 1)
        for c in JUDGED_BUILD:
            b[c] = c not in j.get("judged_fails", [])
        if j.get("subjectless"):
            b["identifier_or_defaults"] = True  # rubric 1.1: subjectless items exempt (judged)
        s = store_checks(it)
        build = round(5 * sum(b[c] for c in BUILD_CHECKS) / len(BUILD_CHECKS), 1)
        store = round(5 * sum(s.values()) / 3, 1)

        seller = (it.get("seller") or "").strip()
        identity = 0 if seller.lower() in PLACEHOLDER_SELLERS else j["seller_identity"]
        price = float(it.get("price") or 0)
        price_ok = price == 0 or (price >= 0.001 and abs(round(price, 3) - price) < 1e-12)
        price_score = j["price"] if price_ok else 0

        compliance = j["compliance"]
        advice_line = bool(NOT_ADVICE.search(it.get("description") or ""))
        if j.get("category") in ("finance", "health", "legal") and not advice_line:
            compliance = min(compliance, 2)

        # Guide 1.10 checks (rubric 2.4): ceilings on Security; an expected miss answered
        # with a non-2xx is a functional defect. "not_assessed" never lowers a score.
        c110 = {c: j.get(c, "not_assessed") for c in CHECKS_110}
        security = j["security"]
        if c110["wrapped_routes_closed"] == "fail":
            security = min(security, 2)
        if c110["sensitive_item_assurance"] == "fail":
            security = min(security, 3 if j.get("sensitive_missing", 1) <= 2 else 2)
        defect = bool(j.get("functional_defect")) or c110["expected_miss_ok_false"] == "fail"

        dims = {
            "Build": build, "Storefront": store, "Listing accuracy": j["listing_accuracy"],
            "Seller identity": identity, "Price sanity": price_score, "Security": security,
            "Compliance": compliance,
        }
        score = round(sum(dims.values()) / 7 * 20)
        grade = grade_for(score)
        rec = {
            "id": iid, "name": it["name"], "seller": seller or None,
            "score": score, "grade": grade, "summary": j["summary"],
            "stage": j.get("stage", 1), "stage_url": stage_url(RUBRIC, j.get("stage", 1)),
            "rubric_version": RUBRIC, "rubric_url": rubric_url(RUBRIC), "score_taken": DATE,
        }
        if defect and grade == "A":
            rec["grade"] = "B"
        if defect:
            rec["grade_cap"] = "B: functional defect observed in a live call"
        # A judgment can name the partner where the catalog shows no seller name.
        partner = j.get("partner_name") or (seller if seller in PARTNERS else None)
        note = partner_note(partner) if partner else None
        if note:
            rec["disclosure"] = note
        if j.get("detail_withheld"):
            rec["detail_withheld"] = j["detail_withheld"]
        rec["under_appeal"] = bool(j.get("under_appeal"))
        out.append(rec)

        private.append({
            **rec, "dimensions": dims,
            "build_checks": b, "storefront_checks": s,
            "price_floor_ok": price_ok, "not_advice_line": advice_line,
            "category": j.get("category"),
            "guide_1_10_checks": c110,
            "failed": [c for c, ok in {**b, **s}.items() if not ok]
                      + ([] if price_ok else ["price_floor"])
                      + ([] if identity else ["seller_display_name"])
                      + (["not_advice_line"] if j.get("category") and not advice_line else [])
                      + [c for c, v in c110.items() if v == "fail"],
            "suggestions": j.get("fixes", ""),
            "basis": j.get("basis", ""),
        })

    if missing:
        sys.exit(f"no judgment for items {missing}: judge them before publishing")

    dist = {g: sum(r["grade"] == g for r in out) for g in "ABCDF"}
    doc = {
        "rubric_version": RUBRIC,
        "rubric": "rubric/rubric-v2.4.md",
        "stage": 1,
        "stage_note": "Stage 1 scores the listing as published. Stage 2 verifies by live call and is not yet run across the catalog.",
        "sweep_date": DATE,
        "items_scored": len(out),
        "distribution": dist,
        "reviewer": "Pirate Kepler, operated for Qatom",
        "human_approval_status": jdoc.get("human_approval_status", "Pending"),
        "approved_by": jdoc.get("approved_by"),
        "approved_on": jdoc.get("approved_on"),
        "disclosure": "policy/disclosure.md",
        "appeals": "policy/appeals.md",
        "publication_policy": "policy/publication.md",
        "withheld": ["per-check pass/fail detail", "improvement suggestions", "live-call transcripts and responses"],
        "items": out,
    }
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, f"{DATE}-stage1.json"), "w") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    lines = [
        f"# Stage 1 scores, {DATE}",
        "",
        f"Rubric [{RUBRIC}](../rubric/rubric-v{RUBRIC}.md) · [stage 1](../rubric/rubric-v{RUBRIC}.md#5-stages) (listing as published) · "
        f"{len(out)} public catalog items · Human Approval Status **{doc['human_approval_status']}**",
        "",
        "Summary score and a one-line summary, per [`../policy/publication.md`](../policy/publication.md). "
        "Per-check detail and improvement suggestions go to the seller, not here.",
        "",
        "Disputing a score, or the rubric itself: [`../policy/appeals.md`](../policy/appeals.md). It is free.",
        "",
        "Distribution: " + " · ".join(f"**{g}** {dist[g]}" for g in "ABCDF"),
        "",
        "| # | Item | Seller | Score | Grade | Summary |",
        "|---|---|---|---:|---|---|",
    ]
    for r in out:
        s = r["summary"].replace("|", "\\|")
        if r.get("disclosure"):
            s += f" _({r['disclosure']})_"
        if r.get("grade_cap"):
            s += " _(grade capped at B)_"
        if r.get("under_appeal"):
            s += " **Under appeal.**"
        lines.append(f"| {r['id']} | {r['name']} | {r['seller'] or '_not set_'} | {r['score']} | {r['grade']} | {s} |")
    lines += [
        "",
        "## Notes",
        "",
        "- A grade measures how well the **listing** is built. It is not an endorsement of the service behind it, "
        "and it is not investment, legal, medical or financial advice.",
        "- Scores are reproducible: `tools/score_stage1.py` with the catalog read-back and the reviewer's judgments.",
        "- The reviewer is operated for Qatom. Items whose seller is a Qatom partner (a first-party store or a Qatom "
        "team member) carry a disclosure line. See [`../policy/disclosure.md`](../policy/disclosure.md).",
        "- The single-calculation listings share one unnamed seller and one set of gaps, so they share a summary.",
        "- Where a security finding could be acted on by someone other than the seller, the detail is withheld "
        "here and sent to the seller. The record says so.",
        "- A score is taken at a moment. A listing fixed after the sweep keeps its score until the next sweep, "
        "or until the seller asks for a re-score through the feedback item.",
        "",
    ]
    with open(os.path.join(OUTDIR, f"{DATE}-stage1.md"), "w") as f:
        f.write("\n".join(lines))

    if private_dir:
        os.makedirs(private_dir, exist_ok=True)
        with open(os.path.join(private_dir, f"{DATE}-stage1-private.json"), "w") as f:
            json.dump(private, f, indent=1, ensure_ascii=False)

    print(f"scored {len(out)}; distribution {dist}")


if __name__ == "__main__":
    main()
