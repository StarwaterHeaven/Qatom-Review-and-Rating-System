# Changelog

Rubric versions, corrections made on appeal, and changes to policy.

## Scorekeepers — 18 October 2026

- **Contributing is open.** Six ways to help, one path for each, in
  [`CONTRIBUTING.md`](CONTRIBUTING.md) (Spanish draft in `CONTRIBUTING.es.md`), with GitHub
  forms for mistakes, scoring changes and re-scores, and catalog item #194 for anyone
  without GitHub. Steps: Received, Being reviewed, Accepted or Not accepted (with a
  reason), Live.
- **Who decides** (Hassan Khan, 18 October): Pirate Kepler fixes mistakes and re-scores;
  re-scores of stores run by Qatom or a partner are decided by a director (Hassan Khan, Dann
  Toliver or Nick Mumford), with the reason published; scoring changes are approved by Hassan
  Khan and announced 7 days ahead. Owning a Qatom store does not rule anyone out.
- **Credit:** [`SCOREKEEPERS.md`](SCOREKEEPERS.md) and the Scorekeepers section of the
  Scorecard page, both from `scorekeepers.json`. Handles by default, real names only on
  request. First entries: Gorque, Torque, Agent Kepler and Wizard Kepler, for their reviews
  of the Scorecard design (marked Qatom team).
- **Site:** "Think this is wrong?" next to every failed check opens a pre-filled mistake
  report; "Become a Scorekeeper" section on the home page.
- **Lookup (#200):** answers now always link to scorecard.agentkepler.tech, whichever address
  the call came in on, and include how to become a Scorekeeper. Worker 2.1.0.

## Qatom Scorecard beta — 18 October 2026

- **New name:** the Qatom Review and Rating System is now the **Qatom Scorecard**. People who
  help improve it are Scorekeepers. Decided by Hassan Khan after review by Agent Kepler,
  Wizard Kepler, Torque and Gorque. Grades, scores, the free lookup (#200) and re-scores (#194) are unchanged.
- **Beta home:** https://scorecard.agentkepler.tech, served by one Worker (source in `worker/`)
  with permanent item links: `/item/{id}`, `/item/{id}.json`, `/badge/{id}.svg`. The old
  `/rating?item_id=` lookup stays. Moves to scorecard.qatom.ai with the same links.
- **Worksheets are public** (policy/publication.md updated): each item shows its checks and
  part scores. **Inputs are public** (`scores/inputs/`), and every page lists the sha256 of
  the listing, the judgment and the scoring code. The site build re-runs every score from
  the public inputs and refuses to publish on any difference.
- **Checklist 2.5 announced**, takes effect 25 October 2026: the price part checks clarity
  only, never price level. Scores before then stay on 2.4.
- **Correction, our own item:** #213 "AquaSentinel: send an approved water alert" (Kepler
  Market Services) re-scored at stage 2 after a live paid call on 18 October returned a
  test echo instead of the receipt the listing describes: listing accuracy 1, grade held at
  B (74, was A 86). #212's summary now says it points at the same test service and has not
  been checked by a live call.
- `tools/score_stage1.py` takes `stage` from the judgment (2 after a live paid call).
  New: `tools/publish_inputs.py`, `tools/make_scorecard_site.py`.

## Published — 18 October 2026

- 18 October sweep approved by Hassan Khan and published: the 10 public items listed since
  16 October are scored (stage 1, rubric 2.4); the other 74 carry forward with their
  16 October scores and dates. 84 items in all. Ratings page and `docs/ratings.json` rebuilt.
- **Scorer fix.** The not-advice check in `tools/score_stage1.py` allowed only two words
  between "not" and "advice", so "not investment, financial or legal advice" was missed.
  It now allows up to five words, commas included. Re-checked against the whole catalog: no
  16 October score changes. The rubric is unchanged.
- `tools/score_stage1.py --delta` scores only judged items while reading the whole catalog
  for the storefront checks; `tools/merge_sweeps.py` merges a delta onto the last full sweep.

## Published — 16 October 2026

- 16 October sweep approved by Hassan Khan and published: 74 public items, stage 1, rubric
  2.4. Supersedes the 14 October sweep. Ratings page and `docs/ratings.json` rebuilt from it.
- Ratings page restyled to the current Qatom Brand OS (colour system and lockup construction,
  19 September 2026): verdigris on pine, Source Serif 4, Hanken Grotesk and IBM Plex Mono, and
  the placed horizontal lockup (`tools/brand/`). Content and data are unchanged.

## Lookup — 16 October 2026

- **Free rating lookup** on Qatom: "Qatom Catalog Ratings: free lookup", in the
  Kepler Market Services on Qatom store. Input `item_id`; returns that item's public fields,
  the sweep and rubric, and how to appeal. An unrated item answers 200 with `ok: false` and
  `status: "not_rated"`. Also callable directly, with no Qatom transaction, at
  `https://team-kepler-ratings.hassan-khan-cd6.workers.dev/rating?item_id=<n>`.
- **Public format** (Hassan Khan, 16 October): where the seller is not arm's length from
  Qatom, the rating carries "Disclosure: <Seller Name> is a Qatom partner."; arm's-length
  sellers, commercial customers included, carry no tag. Every rating links its stage to the
  rubric's stage definitions and its rubric version to that rubric (`stage_url`,
  `rubric_url`).
- `tools/make_ratings_page.py` now writes `docs/ratings.json` beside the page. The page and
  the lookup read the same file, so they cannot disagree. Public fields only.

## Scores — 16 October 2026

- `scores/2026-10-16-stage1.json` and `.md`: 74 public catalog items, stage 1, rubric 2.4.
  Distribution A 19 · B 7 · C 24 · D 23 · F 1.
- Six items new since 14 October: #194 (Team Kepler: feedback and help), #195 (Newsroom)
  and #196 to #199 (Secure Secrets Exchange). The other 68 listings were unchanged against
  the 14 October read-back and keep their scores; none is affected by the 2.4 checks.
- Scorer: the reviewer can place an item with no seller name in its own store (judgment
  field `store`, reason recorded), so it is not pooled with other unnamed items for the
  storefront checks. Used for #195.
- Item #37 is absent from the public catalog, as on 8 and 14 October, and its store's
  `llms.txt` does not mention it. Nothing to score.

## 2.4 — 16 October 2026

Aligned to `qatom-seller-guide` 1.10. Supersedes 2.3.

- **`wrapped_routes_closed`** (Security, judged): an item in front of software the seller
  did not write routes only the paths it needs, and the upstream's own routes return 404
  from outside. A fail caps Security at 2.
- **`sensitive_item_assurance`** (Security, judged): an item that exists to handle
  secrets, credentials or personal data publishes a `/security` threat model,
  `security.txt` and the code that touches the data, and offers an end-to-end mode where
  buyers can run code. A fail caps Security at 3 (one or two missing) or 2 (more).
- **`expected_miss_ok_false`**: expected misses answer 200 with `ok: false`. A non-2xx for
  an expected miss, seen in a live call, is a functional defect, so the grade is capped at B.
- None of the three lowers a score while it is unassessed. Stage 1 may now read an
  item's public pages and probe its host from outside.
- Polling through a free direct URL (a guide 1.10 launch check) is noted privately and not
  scored.

## 2.3 — 14 October 2026

Aligned to `qatom-seller-guide` 1.8. Supersedes 2.2.

- **Reproducible scoring.** `tools/score_stage1.py` produces every stage 1 score from a
  catalog read-back and the reviewer's judgments. Each check now has an ID, and the rubric
  marks which checks are automated and which are judged.
- **Not-advice line applied mechanically.** For health, finance, investment and legal
  items, a description without a not-advice line caps compliance at 2. The category is
  judged; the line test is automated. This lowers the personal-finance and health
  calculators and the Harcourt items compared with 2.2, which scored the gap more lightly.
- **Shared prefix** may be `Brand: item` or the same leading word on every item in a store.
- **Optional inputs** count toward `identifier_or_defaults` when described as optional;
  subjectless items (a search, a leaderboard) are exempt.
- **Seller responsiveness marker** (new, not scored): a billing problem unanswered for two
  business days is stated as a fact on the public summary until the seller replies.
- **Stage 2 additions** from guide 1.6 to 1.8: cart behaviour, links that last at least 15
  minutes, the paid-route header guard, and a refunds statement in `llms.txt`.
- **Resend-delivery item** (guide 1.8) is optional in the guide, so it is not scored; its
  absence is noted in private reports.
- **Purchase-approval threshold** removed from "not yet scored": closed in guide 1.3, and a
  buyer's setting rather than a listing property.

## Published — 14 October 2026

- 14 October sweep approved by Hassan Khan and published: 68 public items, stage 1, rubric
  2.3. Distribution A 14 · B 7 · C 23 · D 23 · F 1. Supersedes the 9 October sweep.
- Public ratings page (`docs/index.html`, GitHub Pages) and the seller-facing
  `qatom-rating-guide` skill (v1.0) published.

## Policy — 14 October 2026

- **Appeals route live:** catalog item #194, "Team Kepler: feedback and help", a free item
  in the Kepler Market Services on Qatom store (`policy/appeals.md`). Tested through the
  master MCP on 14 October (reference TKF-20261014-7D503ADF).
- `policy/disclosure.md` lists the first-party stores by name and states that first-party
  items are reviewed under the same rubric with a not-arm's-length note, per Hassan Khan's
  ruling of 8 October. The earlier recusal wording, which contradicted that ruling, is
  removed.

## Policy — 9 October 2026

- **Security findings** added to `policy/publication.md`: where a finding could be acted on
  by someone other than the seller, the detail is withheld from the public summary and sent
  to the seller. The score still reflects the finding in full.

## Scores — 9 October 2026

- First published sweep: `scores/2026-10-09-stage1.json` and `.md`. 60 public catalog items,
  stage 1, rubric 2.2, approved by Hassan Khan. Distribution A 8, B 5, C 35, D 11, F 1.
- Nine Centaur League items carry their 9 October v2.2 re-score; the other 51 carry their
  8 October score.

## 2.2 — 9 October 2026

Aligned to `qatom-seller-guide` 1.1. Supersedes 2.1. First version published in this
repository.

- **Ten checks re-sourced from "beyond guide" to guide-sourced**, with no change to
  scoring: seller display name; price floor, decimals and zero; same content at two prices
  stating what the higher tier adds; not-advice line for health, finance, investment and
  legal; no free-form SQL, code or query-string inputs; every property described with
  enum-only included; ID formats described with no real example IDs; brand prefix only for
  multi-item sellers; test, draft and placeholder items delisted; items listing modes or
  answer types rather than covered entries.
- **Seller identity scale defined** — 0 placeholder, 3 named, 4 named with operator or
  affiliation disclosed, 5 platform-verified. Levels 4 and 5 go beyond the guide.
- **Two compliance checks remain beyond the guide** — minimum-age line for paid real-money
  entries, privacy link where personal data is collected.
- **Stated legal positions** — the reviewer scores against a seller's stated position and
  flags what is missing under it, rather than adjudicating the position.
- **Still unscored**, pending the guide: the `qatom.ai` addresses, and how a seller sets
  the purchase-approval threshold.

## 2.1 — 8 October 2026

- Description length ceiling raised from 500 to 1,024 characters.

## 2.0 — 8 October 2026

- Rubric rebuilt around the seller guide, so that following the guide scores 5/5 on every
  guide-sourced dimension. Checks that go beyond the guide marked `*` and proposed for
  inclusion in it.
- Grade bands set: A ≥ 85, B ≥ 70, C ≥ 55, D ≥ 40, F < 40.
- Functional defect observed in a live call caps the grade at B.
- Stage 2 (verification by live call) specified but not yet run.

## 1.0 — September 2026

- First rubric. Listing hygiene only, scored from the listing without calling the item.

---

## Corrections on appeal

None yet. Corrections made under [`policy/appeals.md`](policy/appeals.md) are logged here,
with the item, the check, what was wrong, and the reissued score.
