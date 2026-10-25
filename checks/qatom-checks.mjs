// Qatom Scorecard shared checks, v1.0.0
// One set of automated checks, read by both the Scorecard and Preflight.
// Pure functions, no dependencies, no network. Runs in Cloudflare Workers, Node 18+ and browsers.
//
// Input: one catalog item in the shape Qatom's catalog_search returns
//   { id, name, description, price, seller, input_schema }
// Preflight may also pass an item that is not listed yet, with the schema as the plain
// JSON Schema or wrapped as { inputSchema: {...} }.
//
// Owner: Pirate Kepler (Scorecard checklist). Checklist: rubric 2.5; checks 10-12 proposed
// for 2.6. Changes that move a score follow the Scorecard rule: approved by Hassan Khan,
// announced 7 days ahead.

export const CHECKS_VERSION = "1.0.0";
export const RUBRIC_VERSION = "2.5";

const NUMERIC = new Set(["number", "integer"]);
const PLACEHOLDER_SELLERS = new Set(["", "none", "null", "asdfasdf", "test", "seller"]);
const NOT_ADVICE =
  /not (?:[\w,-]+ ){0,5}advice|informational only|not a (?:forecast|trade recommendation)|estimate only/i;
const RANGE_TEXT = /\d\s*(?:-|to|–)\s*\d|range|between|at least|up to/i;
const DEFAULTED_TEXT = /default|optional|omit|leave (?:this|it) out/i;
const FREE_URL_TEXT = /\bfree\b[^.]{0,80}?(?:\bat\b|:)\s*(?:https?:\/\/)?[\w-]+\.[\w.-]+/i;

// ---------------------------------------------------------------------------
// Schema shape (check 11 reads this; nothing else changes shape in 1.0)

/** Returns { schema, shape } where shape is "plain", "wrapped:inputSchema",
 *  "wrapped:input_schema" or "none". */
export function normalizeSchema(raw) {
  if (raw == null) return { schema: {}, shape: "none" };
  if (typeof raw !== "object") return { schema: {}, shape: "invalid" };
  for (const k of ["inputSchema", "input_schema"]) {
    if (raw[k] && typeof raw[k] === "object" && !("properties" in raw) && !("type" in raw)) {
      return { schema: raw[k], shape: `wrapped:${k}` };
    }
  }
  return { schema: raw, shape: "plain" };
}

// ---------------------------------------------------------------------------
// Checklist 2.5, §1.1 Build: the seven automated checks.
// Byte-for-byte the same results as tools/score_stage1.py build_checks() (parity test in test.mjs).
// ctx: { storeSize, sharedPrefix }

export function buildChecks(item, ctx = {}) {
  const storeSize = ctx.storeSize ?? 1;
  const sharedPrefix = !!ctx.sharedPrefix;
  const desc = item.description || "";
  const schema = item.input_schema || {};
  const props = schema.properties || {};
  const req = schema.required || [];
  const vals = Object.values(props).map((p) => p || {});

  const numericOk = (p) => {
    if (!NUMERIC.has(p.type)) return true;
    const hasBounds = ["minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"].some((k) => k in p);
    return hasBounds || RANGE_TEXT.test(p.description || "");
  };
  const defaulted = (p) => "default" in p || DEFAULTED_TEXT.test(p.description || "");

  return {
    desc_length: desc.length >= 1 && desc.length <= 1024,
    desc_points_llms_txt: desc.includes("llms.txt"),
    brand_prefix_naming: storeSize <= 1 || (item.name || "").includes(":") || sharedPrefix,
    schema_additionalProperties_false: schema.additionalProperties === false,
    inputs_described: vals.every((p) => !!p.description),
    units_ranges_stated: vals.every(numericOk),
    identifier_or_defaults: vals.length === 0 || req.length > 0 || vals.every(defaulted),
  };
}

// §1.2 Storefront. storeItems: every public item in the same store, this one included.
export function storefrontChecks(item, storeItems) {
  const isFree = (x) => Number(x.price || 0) === 0;
  const free = storeItems.filter(isFree);
  return {
    free_sibling_in_storefront: isFree(item) || free.length > 0 || FREE_URL_TEXT.test(item.description || ""),
    free_feedback_item: free.some((x) => (x.name || "").toLowerCase().includes("feedback")),
    llms_txt_pointer: storeItems.some((x) => (x.description || "").includes("llms.txt")),
  };
}

// §1.5 price floor, §1.4 seller placeholder, §1.7 not-advice line (presence only).
export function listingChecks(item) {
  const price = Number(item.price || 0);
  const threeDp = Math.abs(Number(price.toFixed(3)) - price) < 1e-12;
  return {
    price_floor_ok: price === 0 || (price >= 0.001 && threeDp),
    seller_named: !PLACEHOLDER_SELLERS.has((item.seller || "").trim().toLowerCase()),
    not_advice_line: NOT_ADVICE.test(item.description || ""),
  };
}

// ---------------------------------------------------------------------------
// Checks 10-12 (proposed by Torque, 20 Oct 2026; wording final per Pirate Kepler 25 Oct 2026).
// Each returns { id, result: "pass"|"warn"|"fail"|"info", detail, ... }.

const SECRET_NAME = /secret|passw|^pwd?$|passphrase|private|api_?key|key|token|credential|auth/i;
const SECRET_DESC = /\b(?:secret|password|passphrase|private|key|token|credential)s?\b/i;
// Carve-out 1: a key scoped to one match, game, order or transaction, or single use.
const SCOPED = /\b(?:for (?:this|your own|one|that)|per)[- ](?:match|game|order|transaction|call|session|purchase)\b|\bone[- ]time\b|\bsingle[- ]use\b/i;
// Carve-out 2: the input is the payload being delivered to a third party, not a credential for the seller.
const PAYLOAD = /\b(?:recipient|receiving (?:agent|party)|third party|delivered to|sent to|shown to the (?:sender|recipient)|give to the (?:sender|recipient))\b/i;

// Check 10, automated counterpart to §1.6 "a pinned or secret value exposed".
export function noBuyerSecretsRequired(item) {
  const { schema } = normalizeSchema(item.input_schema);
  const props = schema.properties || {};
  const req = new Set(schema.required || []);
  const findings = [];
  for (const [name, p0] of Object.entries(props)) {
    const p = p0 || {};
    const d = p.description || "";
    if (!SECRET_NAME.test(name) || !SECRET_DESC.test(d)) continue; // both stages must match
    let carve = null;
    if (PAYLOAD.test(d)) carve = "payload_to_third_party";
    else if (SCOPED.test(d)) carve = "scoped_per_transaction";
    findings.push({ input: name, required: req.has(name), carve_out: carve });
  }
  const live = findings.filter((f) => !f.carve_out);
  const result = live.some((f) => f.required) ? "fail" : live.length ? "warn" : "pass";
  const detail =
    result === "pass"
      ? findings.length
        ? `Secret-like input allowed by carve-out: ${findings.map((f) => `${f.input} (${f.carve_out})`).join(", ")}.`
        : "No input asks the buyer for a standing credential."
      : `Asks the buyer for what reads as a standing credential: ${live.map((f) => `${f.input}${f.required ? " (required)" : " (optional)"}`).join(", ")}. Buyers should never hand a seller an API key or password. Use a scoped per-transaction token, or say the value is a payload delivered to a third party.`;
  return { id: "no_buyer_secrets_required", result, detail, findings };
}

// Check 11, extends §1.1 schema_additionalProperties_false and inputs_described.
export function schemaShapeNormalized(item) {
  const raw = item.input_schema;
  const { schema, shape } = normalizeSchema(raw);
  const props = schema.properties || {};
  const missing = (schema.required || []).filter((r) => !(r in props));
  const ap = "additionalProperties" in schema ? schema.additionalProperties : "unset";
  if (shape === "invalid") {
    return { id: "schema_shape_normalized", result: "fail", shape, additionalProperties: "unset", detail: "Input schema is not a JSON object." };
  }
  if (missing.length) {
    return { id: "schema_shape_normalized", result: "fail", shape, additionalProperties: ap, detail: `"required" names inputs the schema does not define: ${missing.join(", ")}.` };
  }
  const note = shape.startsWith("wrapped") ? ` Found wrapped in ${shape.split(":")[1]}; checked the inner schema.` : "";
  return { id: "schema_shape_normalized", result: "pass", shape, additionalProperties: ap, detail: `Schema shape ${shape}; additionalProperties is ${ap}.${note}` };
}

// Check 12, automated counterpart to §1.3 "says what is returned". INFO only in v1:
// verb matching cannot judge noun-phrase descriptions, so the Scorecard reviewer still judges §1.3.
const DELIVERS = /\b(?:returns?|you get|you receive|delivers?|provides?|confirms?|shows?|lists?|sends?|gives?)\b/i;
export function deliverableStated(item) {
  const found = DELIVERS.test(item.description || "");
  return {
    id: "deliverable_stated",
    result: "info",
    stated: found,
    detail: found
      ? "Description says what the buyer gets back."
      : "No delivery verb found (returns, you get, delivers...). Informational only: a noun-phrase description can still be clear. Make sure a buyer can tell what they receive.",
  };
}

export function preflightChecks(item) {
  return [noBuyerSecretsRequired(item), schemaShapeNormalized(item), deliverableStated(item)];
}

/** Everything the module can check on one item.
 *  storeItems is optional; without it, storefront checks are skipped (Preflight on a single item). */
export function runAll(item, { storeItems, storeSize, sharedPrefix } = {}) {
  const out = {
    checks_version: CHECKS_VERSION,
    rubric_version: RUBRIC_VERSION,
    item_id: item.id ?? null,
    build: buildChecks(item, { storeSize: storeSize ?? storeItems?.length ?? 1, sharedPrefix }),
    listing: listingChecks(item),
    preflight: preflightChecks(item),
  };
  if (storeItems) out.storefront = storefrontChecks(item, storeItems);
  return out;
}
