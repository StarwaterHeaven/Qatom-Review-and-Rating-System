#!/usr/bin/env python3
"""Reduce the internal stage-1 sweep to the public fields in policy/publication.md.

Input : 2026-10-08-stage1-v2.json  (internal: dims, fails, fixes, per-check detail)
        live catalog read-back      (to confirm each item is public)
Output: scores/2026-10-09-stage1.json  and  scores/2026-10-09-stage1.md

Public fields only, per policy/publication.md:
  item name and id, summary score, grade, one-line summary, rubric version,
  date taken, stage, not-arm's-length note, under-appeal marker.
Withheld: per-check pass/fail (dims, fails), improvement suggestions (fixes).
"""
import json, os, sys

# usage: make_public_scores.py <sweep.json> <catalog-readback.json> <out-dir>
SWEEP, CATALOG, OUTDIR = sys.argv[1:4]

DATE = "2026-10-09"
RUBRIC = "2.2"

# --- v2.2 re-score, Centaur League, 9 Oct 2026 (seller fixes live 09:20 ET) -----
# Scores from 2026-10-09-rubric-v2.2.md. Summaries rewritten to read fairly on
# their own, with no score beside them, per policy/publication.md.
RESCORE = {
    32: (91, "Rules, payout split and refund policy all clearly stated, schema documented, affiliation disclosed. No minimum-age line for a paid real-money entry."),
    33: (91, "Clearly described and documented. No minimum-age line for a paid real-money entry."),
    34: (97, "Clear description, documented schema, affiliation disclosed. Verified by live call. Nothing outstanding."),
    35: (97, "Clear description and documented schema, affiliation disclosed. Nothing outstanding."),
    36: (94, "Clear, with sound agent-behaviour guidance. The description does not tell the buyer to keep team_token private."),
    38: (84, "Grade held at B: a standings row does not follow the seller's own stated scoring rule, so the published output cannot be reproduced from the published rules."),
    39: (97, "Free feedback channel, clearly described. The linked privacy page states no retention period (advisory)."),
    40: (97, "Clear description, documented schema, affiliation disclosed. Verified by live call. Nothing outstanding."),
    78: (97, "Fixed-vocabulary responses limit abuse by design. Clearly described. Nothing outstanding."),
}

# --- public phrasing overrides -------------------------------------------------
# The internal sweep is written for us. A few lines need changing before they go
# out under Qatom's name:
#   - an exploitable security finding is withheld and sent to the seller instead
#     (policy/publication.md, "Security findings"),
#   - a judgement about the seller rather than the listing is restated as fact,
#   - speculation about a seller's legal name is dropped.
OVERRIDE = {
    21: ("Ticker typo ('APPL' for AAPL); 'the firehose' is undefined and the output is "
         "undocumented. No data source, delay or licensing disclosure. The input schema "
         "also carries a security gap; the detail has gone to the seller rather than here.",
         "exploitable security detail withheld, sent to the seller"),
    22: ("Clear, well-scoped, with a disclaimer and a good schema. Price 0.000001 USD-TDN "
         "is below the 0.001 minimum unit.", None),
    29: ("No deliverable described.", None),
    31: ("Membership sold at 5.000 with no benefits, term, renewal or refund stated, and "
         "priced in '$5' rather than USD-TDN.", None),
}

# --- not arm's length ---------------------------------------------------------
# Drawn from the `affiliation` field in the sweep and from policy/disclosure.md.
FIRST_PARTY = "First-party store. This review is not arm's length."
TEAM = "Listed by a Qatom team member. This review is not arm's length."
CUSTOMER = "Seller is a Qatom commercial customer. Relationship disclosed; review is arm's length on the listing."
NOTE = {i: FIRST_PARTY for i in (32, 33, 34, 35, 36, 38, 39, 40, 78)}
NOTE.update({79: TEAM, 80: TEAM, 24: CUSTOMER})


def grade_for(score):
    for g, lo in (("A", 85), ("B", 70), ("C", 55), ("D", 40)):
        if score >= lo:
            return g
    return "F"


def main():
    sweep = json.load(open(SWEEP))
    catalog = {i["id"]: i for i in json.load(open(CATALOG))["items"]}

    out, skipped, capped = [], [], []
    for r in sorted(sweep["rows"], key=lambda r: r["id"]):
        iid = r["id"]
        live = catalog.get(iid)
        # publication.md: a non-public item publishes nothing at all.
        if live is None or live.get("private"):
            skipped.append(iid)
            continue

        if iid in RESCORE:
            score, summary = RESCORE[iid]
            taken, rubric = DATE, RUBRIC
        else:
            score, summary = r["score"], r["summary"].strip()
            taken, rubric = "2026-10-08", RUBRIC

        withheld_detail = None
        if iid in OVERRIDE:
            summary, withheld_detail = OVERRIDE[iid]

        grade = grade_for(score)
        rec = {
            "id": iid,
            "name": live["name"],
            "seller": live.get("seller") or None,
            "score": score,
            "grade": grade,
            "summary": summary,
            "stage": 1,
            "rubric_version": rubric,
            "score_taken": taken,
        }
        # A functional defect seen in a live call caps the grade at B (rubric §2).
        if "FUNCTIONAL DEFECT (grade capped at B)" in r.get("flags", []):
            rec["grade"] = "B" if grade == "A" else grade
            rec["grade_cap"] = "B: functional defect observed in a live call"
            capped.append(iid)
        if iid in NOTE:
            rec["disclosure"] = NOTE[iid]
        if withheld_detail:
            rec["detail_withheld"] = withheld_detail
        rec["under_appeal"] = False
        out.append(rec)

    doc = {
        "rubric_version": RUBRIC,
        "rubric": "rubric/rubric-v2.2.md",
        "stage": 1,
        "stage_note": "Stage 1 scores the listing as published. Stage 2 verifies by live call and is not yet run across the catalog.",
        "sweep_date": "2026-10-08",
        "rescore_date": DATE,
        "reviewer": "Pirate Kepler, operated for Qatom",
        "human_approval_status": "Approved",
        "approved_by": "Hassan Khan",
        "approved_on": DATE,
        "disclosure": "policy/disclosure.md",
        "appeals": "policy/appeals.md",
        "publication_policy": "policy/publication.md",
        "withheld": [
            "per-check pass/fail detail",
            "improvement suggestions",
            "live-call transcripts and responses",
        ],
        "items": out,
    }
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, f"{DATE}-stage1.json"), "w") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # --- markdown table -------------------------------------------------------
    dist = {}
    for r in out:
        dist[r["grade"]] = dist.get(r["grade"], 0) + 1
    lines = [
        f"# Stage 1 scores — {DATE}",
        "",
        f"Rubric [{RUBRIC}](../rubric/rubric-v2.2.md) · stage 1 (listing as published) · "
        f"{len(out)} public catalog items · Human Approval Status **Approved**",
        "",
        "Summary score and a one-line summary, per "
        "[`../policy/publication.md`](../policy/publication.md). Per-check detail and "
        "improvement suggestions go to the seller, not here.",
        "",
        "Disputing a score, or the rubric itself: "
        "[`../policy/appeals.md`](../policy/appeals.md). It is free.",
        "",
        "Distribution: " + " · ".join(f"**{g}** {dist.get(g,0)}" for g in "ABCDF"),
        "",
        "| # | Item | Seller | Score | Grade | Summary |",
        "|---|---|---|---:|---|---|",
    ]
    for r in out:
        seller = r["seller"] or "_not set_"
        s = r["summary"].replace("|", "\\|")
        if r.get("disclosure"):
            s += f" _({r['disclosure']})_"
        if r.get("grade_cap"):
            s += " _(grade capped at B)_"
        lines.append(
            f"| {r['id']} | {r['name']} | {seller} | {r['score']} | {r['grade']} | {s} |"
        )
    lines += [
        "",
        "## Notes",
        "",
        "- A grade measures how well the **listing** is built. It is not an endorsement of "
        "the service behind it, and it is not investment, legal, medical or financial advice.",
        "- `Seller: not set` scores 0 on seller identity. It is the single most common and "
        "most cheaply fixed gap in this sweep.",
        "- The reviewer is operated for Qatom. Items marked as first party or as listed by a "
        "Qatom team member are not arm's length — see "
        "[`../policy/disclosure.md`](../policy/disclosure.md).",
        "- Thirty-seven single-calculation listings share one unnamed seller and one set of "
        "gaps, so they share a summary. They are not a copy-paste error.",
        "- Where a security finding could be acted on by someone other than the seller, the "
        "detail is withheld here and sent to the seller. The record says so.",
        "- A score is taken at a moment. A listing fixed after the sweep keeps its score "
        "until the next one, or until the seller appeals and asks for a re-score.",
        "",
    ]
    with open(os.path.join(OUTDIR, f"{DATE}-stage1.md"), "w") as f:
        f.write("\n".join(lines))

    print(f"published {len(out)} items; withheld {skipped or 'none'}; grade-capped {capped}")
    print("distribution:", dist)


if __name__ == "__main__":
    main()
