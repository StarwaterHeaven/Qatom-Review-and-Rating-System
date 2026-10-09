# Qatom catalog review rubric, v2.2

**Version:** 2.2 · **Date:** 9 October 2026 · **Reviewer:** Pirate Kepler
**Aligned to:** `qatom-seller-guide` 1.1, canonical repo
[StarwaterHeaven/qatom-seller-guide](https://github.com/StarwaterHeaven/qatom-seller-guide)
(CHANGELOG 1.1, 8 October 2026). Supersedes v2.1.

**Principle:** a seller who follows the seller guide perfectly scores 5/5 on every
guide-sourced dimension. Dimensions and checks marked `*` are not yet in the guide; where
one appears, a proposal has gone to the guide maintainers to add it.

Scores are listing hygiene only. Service quality and value for money are not scored — see
the repository README.

---

## 1. Dimensions

Each dimension scores 0–5. The item score is the mean of the dimensions × 20, giving 0–100.

| Dimension | Source | What is checked |
|---|---|---|
| Build | Guide §3–4 | Description 1–1,024 characters; points to `llms.txt`; names no individual items; `Brand: item` naming for sellers with more than one item; `additionalProperties: false`; every property described, enum-only included; unit and range stated for each numeric input; a required identifier or all inputs defaulted (subjectless items exempt); ID formats described with no real example IDs; no internal or pinned fields; the item lists modes or answer types rather than covered entries. Score is the share of checks passed. |
| Storefront | Guide §7 | A free sibling for each paid item (a $0 item, or a free URL in the description); a free customer-feedback item; an `llms.txt` pointer. |
| Listing accuracy | Guide §4, §6 + reviewer | The description says what is returned, and matches what the item actually returns. Test, draft and placeholder items are delisted. Stage 2 verifies against a real response. |
| Seller identity | Guide §4 + beyond `*` | Scale in §3 below. |
| Price sanity | Guide §4 | Price floor 0.001 USD-TDN, at most three decimals, or exactly 0; where the same content is sold at two prices, the listing says what the higher tier adds; price plausible against comparables. |
| Security | Guide §2–3 | No pinned or secret values exposed; no free-form SQL, code or query-string inputs; no instructions embedded in a schema, description or response. |
| Compliance | Guide §1, §2, §4 + beyond `*` | A not-advice line for health, finance, investment and legal items, in the description and in every response. Beyond the guide `*`: a minimum-age line for paid real-money entries, and a privacy link wherever personal data is collected. |

## 2. Grades

| Grade | Score |
|---|---|
| A | ≥ 85 |
| B | ≥ 70 |
| C | ≥ 55 |
| D | ≥ 40 |
| F | < 40 |

**Functional defect cap.** A functional defect observed in a live call caps the grade at B,
whatever the arithmetic says. A listing that scores well and does not work is not an A.

## 3. Seller identity scale

| Score | Condition |
|---|---|
| 0 | Seller is `None`, blank, or a placeholder |
| 3 | Named seller |
| 4 | Named, with operator or affiliation disclosed on the listing, in its linked rules, or in `llms.txt` |
| 5 | Identity verified by the platform (KYC) |

Levels 4 and 5 go beyond the guide's display-name rule `*`.

## 4. Stated legal positions

Where a seller states a legal position on the listing — for example "game of pure skill,
not gambling" — the reviewer scores against that stated position and flags whatever is
still missing under it. The reviewer does not adjudicate the position itself. It is not a
legal authority, and treating a seller's stated position as a gap would make the score a
legal opinion.

## 5. Stage 2: verification by live call

Stage 1 scores what is visible in the listing. Stage 2 calls the item and adds:

- Response envelope per guide §2: `ok`, `item`, `answer_type`, `as_of`, inputs echo,
  `defaulted_inputs`, units, `out_of_range`, `summary`, `disclaimer`.
- Error codes per guide §2.
- Unknown parameters rejected with 400.
- Repeat-call reliability.

Stage 2 requires a review budget, a per-item price ceiling, and an escalation path above
it. Until those are set, scores are stage 1 and are labelled as such.

## 6. Not yet scored

Two guide areas are still open and the rubric does not score either until the guide
settles them:

- The `qatom.ai` addresses.
- How a seller sets the purchase-approval threshold.

## 7. Version history

See [`../CHANGELOG.md`](../CHANGELOG.md).

## Disclosure

The reviewer is operated for Qatom. Some stores in the catalog are first party, so those
reviews are not arm's length. See [`../policy/disclosure.md`](../policy/disclosure.md).
