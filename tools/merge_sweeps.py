#!/usr/bin/env python3
"""Merge a delta sweep (new items only) onto the last full published sweep.

    merge_sweeps.py <base.json> <delta.json> <catalog.json> <out-dir> --approved-by NAME --approved-on YYYY-MM-DD

<base.json>    the last published full sweep (scores/<date>-stage1.json).
<delta.json>   score_stage1.py --delta output for items created since the base sweep.
<catalog.json> the read-back the delta was scored from; base items no longer public are
               dropped (policy/publication.md: a non-public item publishes nothing).
Base items keep their own score_taken date, so every record still says when it was scored.
A delta item replaces a base item with the same id (a re-score).
"""
import json, os, sys

args = sys.argv[1:]
def opt(name):
    i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
by, on = opt("--approved-by"), opt("--approved-on")
BASE, DELTA, CATALOG, OUTDIR = args
base, delta = json.load(open(BASE)), json.load(open(DELTA))
public = {i["id"] for i in json.load(open(CATALOG))["items"] if not i.get("private")}
items = {r["id"]: r for r in base["items"] if r["id"] in public}
dropped = sorted(r["id"] for r in base["items"] if r["id"] not in public)
for r in delta["items"]:
    items[r["id"]] = r
out = [items[k] for k in sorted(items)]
DATE = delta["sweep_date"]
dist = {g: sum(r["grade"] == g for r in out) for g in "ABCDF"}
doc = {k: base[k] for k in base if k != "items"}
doc.update({
    "rubric_version": delta["rubric_version"], "rubric": delta["rubric"],
    "sweep_date": DATE, "items_scored": len(out), "distribution": dist,
    "merged_from": {"base": os.path.basename(BASE), "base_sweep_date": base["sweep_date"],
                    "delta_items": [r["id"] for r in delta["items"]], "dropped_not_public": dropped},
    "human_approval_status": "Approved", "approved_by": by, "approved_on": on,
    "items": out,
})
os.makedirs(OUTDIR, exist_ok=True)
with open(os.path.join(OUTDIR, f"{DATE}-stage1.json"), "w") as f:
    json.dump(doc, f, indent=2, ensure_ascii=False); f.write("\n")
new = {r["id"] for r in delta["items"]}
L = [f"# Stage 1 scores, {DATE}", "",
     f"Rubric [{doc['rubric_version']}](../rubric/rubric-v{doc['rubric_version']}.md) · [stage 1](../rubric/rubric-v{doc['rubric_version']}.md#5-stages) (listing as published) · "
     f"{len(out)} public catalog items · Human Approval Status **Approved**", "",
     f"This sweep scores the {len(new)} items listed since the {base['sweep_date']} sweep and carries the "
     f"other items forward with their {base['sweep_date']} scores. Each row's date column says when it was scored.", "",
     "Summary score and a one-line summary, per [`../policy/publication.md`](../policy/publication.md). "
     "Per-check detail and improvement suggestions go to the seller, not here.", "",
     "Disputing a score, or the rubric itself: [`../policy/appeals.md`](../policy/appeals.md). It is free.", "",
     "Distribution: " + " · ".join(f"**{g}** {dist[g]}" for g in "ABCDF"), "",
     "| # | Item | Seller | Score | Grade | Scored | Summary |", "|---|---|---|---:|---|---|---|"]
for r in out:
    s = r["summary"].replace("|", "\\|")
    if r.get("disclosure"): s += f" _({r['disclosure']})_"
    if r.get("grade_cap"): s += " _(grade capped at B)_"
    if r.get("under_appeal"): s += " **Under appeal.**"
    L.append(f"| {r['id']} | {r['name']} | {r['seller'] or '_not set_'} | {r['score']} | {r['grade']} | {r['score_taken']} | {s} |")
L += ["", "## Notes", "",
      "- A grade measures how well the **listing** is built. It is not an endorsement of the service behind it, "
      "and it is not investment, legal, medical or financial advice.",
      "- Scores are reproducible: `tools/score_stage1.py` (with `--delta` for new items) and `tools/merge_sweeps.py`.",
      "- The reviewer is operated for Qatom. Items whose seller is a Qatom partner carry a disclosure line, and are "
      "scored by the same code as every other item. See [`../policy/disclosure.md`](../policy/disclosure.md).",
      "- A score is taken at a moment. A listing fixed after it was scored keeps its score until the next full sweep, "
      "or until the seller asks for a re-score through the feedback item.", ""]
open(os.path.join(OUTDIR, f"{DATE}-stage1.md"), "w").write("\n".join(L))
print(f"merged {len(out)} items ({len(new)} new); dropped {dropped or 'none'}; {dist}")
