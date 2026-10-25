#!/usr/bin/env python3
"""Writes fixtures/parity-<date>.json: the Python scorer's automated results for every item
in a published catalog input, so test.mjs can prove the shared JS module agrees.

    python3 checks/make_parity_fixture.py scores/inputs/2026-10-18-catalog.json scores/inputs/2026-10-18-judgments.json
"""
import json, os, re, sys
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import score_stage1 as S

cat_path, j_path = sys.argv[1:3]
catalog = [i for i in json.load(open(cat_path))["items"] if not i.get("private")]
J = json.load(open(j_path))["items"]
def store_key(it):
    return (J.get(str(it["id"])) or {}).get("store") or S.seller_key(it)
stores = defaultdict(list)
for it in catalog:
    stores[store_key(it)].append(it)
out = []
for it in sorted(catalog, key=lambda x: x["id"]):
    items = stores[store_key(it)]
    firsts = {x.get("name", "").split()[0].lower() for x in items if x.get("name")}
    b = S.build_checks(it, len(items), shared_prefix=len(firsts) == 1)
    free = [x for x in items if float(x.get("price") or 0) == 0]
    desc = it.get("description") or ""
    is_free = float(it.get("price") or 0) == 0
    s = {
        "free_sibling_in_storefront": is_free or bool(free) or bool(re.search(r"\bfree\b[^.]{0,80}?(?:\bat\b|:)\s*(?:https?://)?[\w-]+\.[\w.-]+", desc, re.I)),
        "free_feedback_item": any("feedback" in x.get("name", "").lower() for x in free),
        "llms_txt_pointer": any("llms.txt" in (x.get("description") or "") for x in items),
    }
    price = float(it.get("price") or 0)
    l = {
        "price_floor_ok": price == 0 or (price >= 0.001 and abs(round(price, 3) - price) < 1e-12),
        "seller_named": (it.get("seller") or "").strip().lower() not in S.PLACEHOLDER_SELLERS,
        "not_advice_line": bool(S.NOT_ADVICE.search(desc)),
    }
    out.append({"id": it["id"], "store_ids": [x["id"] for x in items], "shared_prefix": len(firsts) == 1,
                "build": b, "storefront": s, "listing": l})
date = os.path.basename(cat_path)[:10]
os.makedirs(os.path.join(os.path.dirname(__file__), "fixtures"), exist_ok=True)
dst = os.path.join(os.path.dirname(__file__), "fixtures", f"parity-{date}.json")
json.dump({"catalog": os.path.relpath(cat_path), "items": out}, open(dst, "w"), indent=1)
print(f"wrote {dst}: {len(out)} items")
