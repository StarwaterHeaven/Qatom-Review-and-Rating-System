// Qatom Scorecard (beta) -- one Worker for the site, the data, the badges and the free lookup.
//
// Permanent, item-number links (they never change, whatever the domain or repo is called):
//   GET  /                    the list of every scored item
//   GET  /item/{id}           one item: grade, score, worksheet, how to re-run it
//   GET  /item/{id}.json      the same, as data (unscored: 200, ok:false, status not_scored)
//   GET  /badge/{id}.svg      opt-in badge (unscored: 200, grey "not scored yet")
//   GET  /scorecard.json      every item, as data
// Free lookup, catalog item #200 (unchanged contract):
//   POST /  {item_id}         what Qatom calls;  GET /?item_id=N also works
//   GET  /rating?item_id=N    direct, no Qatom transaction (kept forever as an alias)
//   GET  /llms.txt, /health
// Data is built into this Worker (../site), so nothing depends on GitHub Pages.

const ITEM = "team-kepler-rating-lookup";
const VERSION = "2.0.0";
const ALLOWED = new Set(["item_id"]);
const DISCLAIMER = "A score shows how well a listing is built against the Qatom seller guide. It does not tell you if the service is good, and it is not investment, legal, medical or financial advice. Scores are made by Pirate Kepler, an agent operated for Qatom; where a seller is a Qatom partner, the score says so.";
const HDR = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "access-control-allow-origin": "*" };
const json = (body, status = 200) => new Response(JSON.stringify(body, null, 2), { status, headers: HDR });
const err = (status, code, message, next_step) => json({ ok: false, item: ITEM, error: { code, message, next_step }, read_me: "/llms.txt" }, status);

async function asset(env, request, path) {
  const u = new URL(request.url); u.pathname = path; u.search = "";
  return env.ASSETS.fetch(new Request(u.toString(), { method: "GET" }));
}

let cache = { at: 0, data: null };
async function scorecard(env, request) {
  if (cache.data && Date.now() - cache.at < 300000) return cache.data;
  const r = await asset(env, request, "/scorecard.json");
  if (!r.ok) throw new Error(`scorecard_${r.status}`);
  const d = await r.json();
  if (!d || !Array.isArray(d.items) || d.human_approval_status !== "Approved") throw new Error("scorecard_not_approved");
  cache = { at: Date.now(), data: d };
  return d;
}

async function readArgs(request) {
  const url = new URL(request.url);
  const args = {};
  for (const [k, v] of url.searchParams) args[k] = v;
  if (request.method === "POST") {
    const text = await request.text();
    if (text.trim()) {
      let body;
      try { body = JSON.parse(text); } catch { throw new Error("body_not_json"); }
      if (!body || typeof body !== "object" || Array.isArray(body)) throw new Error("body_not_json");
      Object.assign(args, body);
    }
  }
  return args;
}

function rescore(env, id, message) {
  return { catalog_item_id: Number(env.FEEDBACK_ITEM_ID || 194), arguments: { topic: "rating", item_id: id, message } };
}

async function lookup(request, env) {
  let args;
  try { args = await readArgs(request); }
  catch { return err(400, "wrong_input", "The request body must be a JSON object.", "Send {\"item_id\": <catalog item number>}."); }
  const unknown = Object.keys(args).filter((k) => !ALLOWED.has(k));
  if (unknown.length) return err(400, "unknown_parameter", `Unknown input(s): ${unknown.join(", ")}.`, "Send only item_id.");
  if (args.item_id === undefined || args.item_id === "") return err(400, "item_required", "item_id is required.", "Send item_id: the catalog item number from catalog_search.");
  const id = Number(args.item_id);
  if (!Number.isInteger(id) || id < 1 || id > 9999999) return err(400, "bad_value", "item_id must be a whole catalog item number, 1 or more.", "Send the id field from catalog_search, for example 24.");
  const origin = new URL(request.url).origin;
  let d;
  try { d = await scorecard(env, request); }
  catch (e) {
    console.error("scorecard_unavailable", String(e));
    return json({ ok: false, item: ITEM, answer_type: "current", as_of: new Date().toISOString(), inputs: { item_id: id },
      result: { status: "temporarily_unavailable" }, summary: "The scores could not be read just now. Try again in a few minutes.",
      next_steps: [{ action: "Open the Qatom Scorecard", url: origin + "/" }], disclaimer: DISCLAIMER });
  }
  const base = { ok: true, item: ITEM, answer_type: "current", as_of: d.sweep_date, inputs: { item_id: id }, defaulted_inputs: {} };
  const r = d.items.find((i) => i.id === id);
  if (!r) {
    return json({ ...base, ok: false,
      result: { status: "not_rated", item_id: id, sweep_date: d.sweep_date, rubric_version: d.rubric_version, items_rated: d.items.length },
      summary: `Item ${id} has no score in the Qatom Scorecard of ${d.sweep_date}. It may be newer than those scores, private to its seller, or not a catalog item.`,
      next_steps: [{ action: "Ask for it to be scored (free)", ...rescore(env, id, "Please score this item.") }],
      links: { scorecard: origin + "/", how_each_score_is_made: d.how_each_score_is_made }, disclaimer: DISCLAIMER });
  }
  const notes = [r.disclosure, r.grade_cap && "Grade held at B: a live call found a problem.",
    r.detail_withheld && "A security detail was sent to the seller and is not published.",
    r.under_appeal && "A re-score has been requested."].filter(Boolean);
  const { worksheet, rerun, id: _drop, ...pub } = r;
  return json({ ...base, ok: true,
    result: { ...pub, item_id: r.id, seller: r.seller ?? null, score_out_of: 100,
      stage_meaning: r.stage === 2 ? "Stage 2: checked by a live paid call." : "Stage 1: the listing as published, without a purchase.",
      sweep_date: r.score_taken || d.sweep_date, disclosure: r.disclosure ?? null, grade_cap: r.grade_cap ?? null,
      detail_withheld: Boolean(r.detail_withheld), under_appeal: Boolean(r.under_appeal),
      grade_bands: { A: ">= 85", B: ">= 70", C: ">= 55", D: ">= 40", F: "< 40" },
      page: `${origin}/item/${r.id}`, worksheet: `${origin}/item/${r.id}.json`, badge: `${origin}/badge/${r.id}.svg` },
    summary: `#${r.id} ${r.name} (${r.seller || "seller not named"}): grade ${r.grade}, ${r.score}/100, stage ${r.stage}, checklist ${r.rubric_version}, ${r.score_taken || d.sweep_date}. ${r.summary}${notes.length ? " " + notes.join(" ") : ""}`,
    next_steps: [{ action: "Ask for a re-score (free)", ...rescore(env, id, "<what you dispute and why>") }],
    links: { scorecard: origin + "/", item_page: `${origin}/item/${r.id}`, how_each_score_is_made: d.how_each_score_is_made }, disclaimer: DISCLAIMER });
}

function llms(request, env) {
  const o = new URL(request.url).origin;
  return `# Qatom Scorecard (beta)

> Every public Qatom catalog listing gets a score anyone can check: grade A to F, a score out of 100, the checks it passed and failed, and how to re-run it. A score shows how well the listing is built against the Qatom seller guide, not whether the service is good. Made by Pirate Kepler, an agent operated for Qatom. Beta at ${o}; moving to ${env.OFFICIAL_HOME || "scorecard.qatom.ai"} with the same item links.

Version ${VERSION}.

## Links that never change

| Link | What you get |
|---|---|
| ${o}/item/{id} | The item's page: grade, score, worksheet, how to re-run it |
| ${o}/item/{id}.json | The same, as JSON. Unscored item: 200, ok:false, status not_scored |
| ${o}/badge/{id}.svg | Opt-in badge. Unscored item: 200, grey "not scored yet" |
| ${o}/scorecard.json | Every scored item |
| ${o}/rating?item_id={id} | Free lookup, same answer as catalog item #200, no Qatom transaction |

## Free lookup through Qatom (catalog item #200)

Qatom master MCP: \`catalog_search\` for "Qatom Catalog Ratings", then \`agent_checkout\` with \`{"item_id": 24}\`. Only input: item_id (integer, 1 or more). Anything else: 400 unknown_parameter. An item with no score answers 200 with ok:false and result.status "not_rated".

## Errors

| Code | Status | Next step |
|---|---|---|
| item_required | 400 | Send item_id |
| bad_value | 400 | Send a whole catalog item number |
| unknown_parameter | 400 | Send only item_id |
| wrong_input | 400 | Send a JSON object |
| internal_error | 500 | Try again; if it persists, email support@todaq.net |

## Re-run any score

Code and every input are public: https://github.com/StarwaterHeaven/Qatom-Review-and-Rating-System . Each item's JSON has the exact command and the sha256 of the listing, the judgment and the scoring code.

## Ask for a re-score

Free, through catalog item #${env.FEEDBACK_ITEM_ID || 194} "Team Kepler: feedback and help" with \`topic: "rating"\` and the \`item_id\`.

## Privacy

No personal data is collected. Requests are logged by path and status only.
`;
}

const ITEM_PAGE = /^\/item\/(\d{1,7})\/?$/;
const ITEM_JSON = /^\/item\/(\d{1,7})\.json$/;
const BADGE = /^\/badge\/(\d{1,7})\.svg$/;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const p = url.pathname;
    try {
      if (p === "/" && (request.method === "POST" || (request.method === "GET" && [...url.searchParams.keys()].length))) return await lookup(request, env);
      if (p === "/rating" && request.method === "GET") return await lookup(request, env);
      if (request.method !== "GET" && request.method !== "HEAD") return new Response("Method not allowed", { status: 405 });
      if (p === "/llms.txt") return new Response(llms(request, env), { headers: { "content-type": "text/markdown; charset=utf-8", "access-control-allow-origin": "*" } });
      if (p === "/health") {
        let sweep = null; try { sweep = (await scorecard(env, request)).sweep_date; } catch {}
        return json({ ok: true, item: ITEM, version: VERSION, sweep_served: sweep });
      }
      let m;
      if ((m = p.match(ITEM_PAGE))) {
        const r = await asset(env, request, `/item/${Number(m[1])}/index.html`);
        if (r.ok) return new Response(r.body, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=300" } });
        return new Response(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Not scored yet · Qatom Scorecard</title><body style="font:16px/1.6 system-ui,sans-serif;max-width:40rem;margin:3rem auto;padding:0 16px"><h1>Item #${Number(m[1])} has no score yet</h1><p>It may be newer than the latest scores, private to its seller, or not a catalog item. Ask for a score, free, through catalog item #${env.FEEDBACK_ITEM_ID || 194} with <code>topic: "rating"</code>.</p><p><a href="/">All scores</a></p></body>`,
          { status: 404, headers: { "content-type": "text/html; charset=utf-8" } });
      }
      if ((m = p.match(ITEM_JSON))) {
        const r = await asset(env, request, `/item/${Number(m[1])}.json`);
        if (r.ok) return new Response(r.body, { headers: { ...HDR, "cache-control": "public, max-age=300" } });
        return json({ ok: false, item_id: Number(m[1]), status: "not_scored", summary: "This item has no score yet.",
          next_steps: [{ action: "Ask for a score (free)", ...rescore(env, Number(m[1]), "Please score this item.") }] });
      }
      if ((m = p.match(BADGE))) {
        let r = await asset(env, request, `/badge/${Number(m[1])}.svg`);
        if (!r.ok) r = await asset(env, request, "/badge/not-scored.svg");
        return new Response(r.body, { headers: { "content-type": "image/svg+xml; charset=utf-8", "cache-control": "public, max-age=3600", "access-control-allow-origin": "*" } });
      }
      return env.ASSETS.fetch(request);
    } catch (e) {
      console.error("scorecard_error", e && e.stack ? e.stack : String(e));
      return err(500, "internal_error", "Something went wrong on our side.", "Try again; if it persists, email support@todaq.net.");
    }
  },
};
