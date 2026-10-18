#!/usr/bin/env python3
"""Publish the inputs of a sweep so anyone can re-run every score.

    publish_inputs.py <catalog.json> <judgments.json> <out-dir>

Writes <out-dir>/<date>-catalog.json (public catalog items only, as read back) and
<out-dir>/<date>-judgments.json (the reviewer's judged values). Removed before publishing,
per policy/publication.md: judgments for items that are not public, improvement suggestions ("fixes"), the reviewer's working notes
("basis"), and, for items whose security detail went to the seller ("detail_withheld"),
the values of the two security checks (published as "withheld").
"""
import json, os, sys

CAT, JUD, OUT = sys.argv[1:4]
jd = json.load(open(JUD))
date = jd["sweep_date"]
cat = json.load(open(CAT))
items = [i for i in cat["items"] if not i.get("private")]
public_ids = {str(i["id"]) for i in items}
pub_j = {}
for k, v in jd["items"].items():
    if k not in public_ids:  # a non-public item publishes nothing, not even its judgment
        continue
    v = {kk: vv for kk, vv in v.items() if kk not in ("fixes", "basis")}
    if v.get("detail_withheld"):
        for c in ("wrapped_routes_closed", "sensitive_item_assurance"):
            if c in v:
                v[c] = "withheld"
    pub_j[k] = v
os.makedirs(OUT, exist_ok=True)
json.dump({"read_back": "Qatom master MCP catalog_search, no query", "sweep_date": date, "total": len(items), "items": items},
          open(os.path.join(OUT, f"{date}-catalog.json"), "w"), indent=1, ensure_ascii=False)
json.dump({k: jd[k] for k in jd if k not in ("items", "note")} | {"items": pub_j},
          open(os.path.join(OUT, f"{date}-judgments.json"), "w"), indent=1, ensure_ascii=False)
print(f"{date}: {len(items)} catalog items, {len(pub_j)} judgments")
