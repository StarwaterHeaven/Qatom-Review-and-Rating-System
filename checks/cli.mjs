// node checks/cli.mjs <catalog.json>  -> JSON array of runAll() results on stdout.
// Store grouping here is by seller name; the Scorecard scorer applies reviewer store overrides itself.
import { readFileSync } from "node:fs";
import { runAll } from "./qatom-checks.mjs";
const items = JSON.parse(readFileSync(process.argv[2])).items.filter((i) => !i.private);
const key = (i) => (i.seller || "").trim().toLowerCase() || `__unnamed_${i.id}`;
const stores = new Map();
for (const i of items) stores.set(key(i), [...(stores.get(key(i)) || []), i]);
const out = items.map((i) => {
  const s = stores.get(key(i));
  const firsts = new Set(s.filter((x) => x.name).map((x) => x.name.split(/\s+/)[0].toLowerCase()));
  return runAll(i, { storeItems: s, sharedPrefix: firsts.size === 1 });
});
process.stdout.write(JSON.stringify(out, null, 1) + "\n");
