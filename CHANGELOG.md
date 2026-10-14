# Changelog

Rubric versions, corrections made on appeal, and changes to policy.

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
