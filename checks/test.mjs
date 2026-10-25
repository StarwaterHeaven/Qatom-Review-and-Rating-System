// node checks/test.mjs   (Node 18+). Exits 1 on any mismatch.
// 1) Parity: the shared module gives the Python scorer's results on every published catalog item.
// 2) Calibration: checks 10-12 on the live items Torque and Wizard named.
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as C from "./qatom-checks.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..");
let fails = 0;
const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);

for (const f of readdirSync(join(here, "fixtures")).filter((n) => n.startsWith("parity-"))) {
  const fx = JSON.parse(readFileSync(join(here, "fixtures", f)));
  const cat = JSON.parse(readFileSync(join(root, fx.catalog))).items;
  const byId = new Map(cat.map((i) => [i.id, i]));
  let n = 0;
  for (const e of fx.items) {
    const it = byId.get(e.id);
    const store = e.store_ids.map((id) => byId.get(id));
    const got = {
      build: C.buildChecks(it, { storeSize: store.length, sharedPrefix: e.shared_prefix }),
      storefront: C.storefrontChecks(it, store),
      listing: C.listingChecks(it),
    };
    for (const k of ["build", "storefront", "listing"]) {
      if (!eq(got[k], e[k])) { fails++; console.log(`PARITY FAIL ${f} #${e.id} ${k}\n  py ${JSON.stringify(e[k])}\n  js ${JSON.stringify(got[k])}`); }
    }
    n++;
  }
  console.log(`parity ${f}: ${n} items checked`);
}

const cal = JSON.parse(readFileSync(join(here, "fixtures", "calibration.json")));
const cat = new Map(JSON.parse(readFileSync(join(root, cal.catalog))).items.map((i) => [i.id, i]));
for (const c of cal.cases) {
  const it = c.item ?? cat.get(c.id);
  const r = C.preflightChecks(it).find((x) => x.id === c.check);
  const ok = r.result === c.expect;
  if (!ok) fails++;
  console.log(`${ok ? "ok  " : "FAIL"} ${c.check} #${c.id ?? c.label}: ${r.result} (expect ${c.expect}) ${c.why}`);
}
console.log(fails ? `\n${fails} failure(s)` : "\nall checks agree");
process.exit(fails ? 1 : 0);
