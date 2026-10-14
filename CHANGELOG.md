# Changelog

Rubric versions, corrections made on appeal, and changes to policy.

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

## Policy — 14 October 2026

- Appeals route named: "Team Kepler: feedback and help", a free item in the Kepler Market
  Services store (`policy/appeals.md`).
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
