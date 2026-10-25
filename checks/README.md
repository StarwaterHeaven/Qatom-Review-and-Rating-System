# Qatom Scorecard shared checks

**One set of automated checks, read by both the Qatom Scorecard and Preflight.** Preflight is the Scorecard's "check before you list". It runs these checks, never its own copy.

| | |
|---|---|
| **Module** | [`qatom-checks.mjs`](qatom-checks.mjs) in this repo, `checks/` folder |
| **Format** | One ES module. Pure functions, no dependencies, no network. Runs in Cloudflare Workers, Node 18+ and browsers |
| **Version** | `CHECKS_VERSION` in the module (semver). Released as git tags `checks-vX.Y.Z` |
| **Owner** | Pirate Kepler, as owner of the Scorecard checklist (rubric) |
| **Tests** | `node checks/test.mjs` checks parity with the Python scorer on every published catalog input, plus calibration cases for checks 10–12 |

## What it checks

Input is one catalog item in the shape `catalog_search` returns: `{ id, name, description, price, seller, input_schema }`. Preflight can also pass an item that isn't listed yet. The schema can be plain JSON Schema or wrapped as `{ inputSchema: {...} }`.

| Export | Checklist | Result |
|---|---|---|
| `buildChecks(item, {storeSize, sharedPrefix})` | §1.1, the seven automated Build checks | `{check_id: true/false}` |
| `storefrontChecks(item, storeItems)` | §1.2 | `{check_id: true/false}` |
| `listingChecks(item)` | §1.5 price floor, §1.4 seller placeholder, §1.7 not-advice line | `{check_id: true/false}` |
| `preflightChecks(item)` | Checks 10–12 below | `[{id, result, detail}]` |
| `runAll(item, {storeItems})` | All of the above | One object, tagged with `checks_version` and `rubric_version` |

Judged checks (the ones marked **judged** in the rubric) stay with the Scorecard reviewer. They are not in this module.

### Checks 10–12 (proposed by Torque, 20 Oct 2026; final wording, Pirate Kepler, 25 Oct 2026)

**10. `no_buyer_secrets_required`.** This is the automated counterpart to §1.6, "a pinned or secret value exposed". An input is flagged only when both stages match: its **name** is secret-like (secret, password, passphrase, pw, private, key, token, credential, auth), **and** its **description** treats it as a secret. Matching is on description intent, never on names alone.
- **fail:** a flagged input is required.
- **warn:** a flagged input is optional.
- **pass:** nothing is flagged, or every flagged input falls under a carve-out.
  - *Scoped token:* the key is scoped to one match, game, order or transaction, or is single use. Example: #36 `team_token` "for this match".
  - *Payload to a third party:* the input is the payload being delivered to a third party, not a credential for the seller. Example: #199.

  Standing credentials, such as API keys and account passwords, never pass.

**11. `schema_shape_normalized`.** This extends §1.1 `schema_additionalProperties_false` and `inputs_described`. It accepts the plain schema and the `{inputSchema}` wrapper, normalizes them, and reports which shape it found. It also reports `additionalProperties` from whichever shape was found.
- **fail:** `required` names an input the schema doesn't define, or the schema is not an object.

**12. `deliverable_stated`.** This is the automated counterpart to §1.3, "says what is returned". It looks for a broad set of delivery verbs: returns, you get, you receive, delivers, provides, confirms, shows, lists, sends, gives.
- It is **info only in v1**. Verb matching can't judge noun-phrase descriptions, so the Scorecard reviewer still judges §1.3.

## How each side uses it

**Preflight (Torque's Worker, `POST {item_id}`)**
- Copy `qatom-checks.mjs` from a release tag into the Worker's source and import it. Wrangler bundles it.
- Workers can't import from a URL at run time, so pin the tag and record it in the Worker's response as `checks_version`.
- Return `runAll(item)` (or `preflightChecks(item)`) with that version. Results are advisory: Preflight never sets a score.
- To update, take a new tag. Don't edit the copy. Fixes come back here as a pull request.

**Scorecard**
- `tools/score_stage1.py` still computes the §1.1/§1.2 automated checks in Python. `test.mjs` proves the two give identical results on every published input: 158 of 158 items, sweeps of 16 and 18 Oct.
- From checklist 2.6, the scorer reads its automated results from this module (`node checks/cli.mjs`), so there is one implementation.
- Until then, the parity test is the build gate for any change to either side.

## Changing a check

- Suggest a change through the Scorekeeper path (issue form or pull request). See `CONTRIBUTING.md`.
- A change that moves a score is a scoring change: Hassan Khan approves it and it is announced 7 days ahead.
  - This includes making check 10 or 11 count toward the Build or Security score (proposed for 2.6).
- A change that only touches Preflight's advisory output, such as wording, a new warn-level check or info-level checks, needs Pirate Kepler's review only.
- Every change bumps `CHECKS_VERSION`, adds a calibration case and keeps `node checks/test.mjs` green.

**Today's catalog:** on the 18 Oct input, checks 10 and 11 pass on all 84 items. Adopting them in 2.6 would move no current score.
