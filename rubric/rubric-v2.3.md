# Qatom catalog review rubric, v2.3

**Version:** 2.3 · **Date:** 14 October 2026 · **Reviewer:** Pirate Kepler
**Aligned to:** `qatom-seller-guide` 1.8, canonical repo
[StarwaterHeaven/qatom-seller-guide](https://github.com/StarwaterHeaven/qatom-seller-guide)
(CHANGELOG 1.8, 14 October 2026). Supersedes v2.2.

**Principle:** a seller who follows the seller guide perfectly scores 5/5 on every
guide-sourced dimension. Checks marked `*` go beyond the guide; where one appears, a
proposal has gone to the guide maintainers to add it.

Scores are listing hygiene only. Service quality and value for money are not scored. See
the repository README.

**Reproducible:** every stage 1 score is produced by
[`../tools/score_stage1.py`](../tools/score_stage1.py) from a catalog read-back and a
reviewer-judgment file. Automated checks run in code. Checks that need a reviewer's reading
are recorded item by item with a reason, and are marked **(judged)** below.

---

## 1. Dimensions

Each dimension scores 0 to 5. The item score is the mean of the seven dimensions × 20,
which gives 0 to 100.

### 1.1 Build (guide §3–4)

Score = 5 × the share of the ten checks passed.

| Check ID | What passes | How |
|---|---|---|
| `desc_length` | Description is 1 to 1,024 characters | automated |
| `desc_points_llms_txt` | Description points to the seller's `llms.txt` | automated |
| `names_no_individual_items` | Description names modes or answer types, not the individual entries covered (tickers, SKUs, match IDs) or an item count | judged |
| `brand_prefix_naming` | A seller with more than one item uses a shared prefix (`Brand: item`, or the same leading word on every item). Single-item sellers pass | automated |
| `schema_additionalProperties_false` | Input schema sets `additionalProperties: false` | automated |
| `inputs_described` | Every property has a description, enum-only properties included | automated |
| `units_ranges_stated` | Every numeric property states a unit and a range, in its description or as `minimum`/`maximum` | automated |
| `identifier_or_defaults` | One required identifier, or every input has a default or is described as optional. Items with no inputs pass; items with no subject, such as a search or a leaderboard, are exempt (judged) | automated |
| `no_example_ids_in_schema` | ID formats are described, with no real example IDs | judged |
| `no_internal_or_pinned_fields` | No property the buyer must leave alone or the seller should pin (paid mode, tier, an internal reference) | judged |

### 1.2 Storefront (guide §7)

Scored per seller, so every item in a store gets the same storefront score. Score = 5 ×
the share of the three checks passed.

| Check ID | What passes |
|---|---|
| `free_sibling_in_storefront` | For a paid item, the store has a $0 item, or the description gives a free check URL. A free item passes |
| `free_feedback_item` | The store has a free customer-feedback item |
| `llms_txt_pointer` | At least one item in the store points to an `llms.txt` |

The guide also suggests an optional free "resend my delivery" item (§7, 1.8). It is
optional, so it is not scored. Its absence is noted in the seller's private report.

### 1.3 Listing accuracy (guide §4, §6, judged)

| Score | Condition |
|---|---|
| 5 | Says what is returned, and nothing on the listing contradicts it |
| 3 | Says what is returned, with a gap or ambiguity a buyer would trip on |
| 1 | Does not say what a buyer receives |
| 0 | Test, draft or placeholder item still public |

Stage 2 checks the description against a real response.

### 1.4 Seller identity (guide §4, beyond `*`)

| Score | Condition |
|---|---|
| 0 | Seller is `None`, blank or a placeholder (automated) |
| 3 | Named seller |
| 4 | Named, with operator or affiliation disclosed on the listing, in its linked rules or in `llms.txt` `*` (judged) |
| 5 | Identity verified by the platform (KYC) `*` |

### 1.5 Price sanity (guide §4)

The price floor is automated: a paid price below 0.001 USD-TDN, or with more than three
decimals, scores 0. Otherwise the reviewer judges (judged):

| Score | Condition |
|---|---|
| 5 | Price at or above the floor, plausible against comparables, and tiers say what the higher price adds |
| 4 | Plausible, but the listing does not let a buyer tell what the price buys before paying |
| 2–3 | A tier or pricing ambiguity a buyer would act on wrongly |

### 1.6 Security (guide §2–3, judged)

| Score | Condition |
|---|---|
| 5 | Free, read-only, fixed-vocabulary inputs; nothing to abuse |
| 4 | No issue seen in the listing (the stage 1 default for paid items; the paid-route guard is a stage 2 check) |
| 3 | A weakness that does not expose anything, for example an unbounded free-text input on a paid item |
| 1–2 | A free-form SQL, code or query input, a pinned or secret value exposed, or instructions embedded in a schema or description |

Where a security finding could be acted on by someone other than the seller, the detail
goes to the seller privately. See [`../policy/publication.md`](../policy/publication.md).

### 1.7 Compliance (guide §1, §2, §4, beyond `*`)

| Check | Source | How |
|---|---|---|
| Not-advice line in the description for health, finance, investment and legal items | Guide §2, §4 | The category is judged; the presence of the line is automated. Missing line: compliance is at most 2 |
| Demo or synthetic data says so | Guide §2 | judged |
| Minimum-age line for paid real-money entries | beyond `*` | judged |
| Privacy link wherever personal data, such as an email address, is collected | beyond `*` | judged |

The score is 5 with nothing missing, 4 with one beyond-guide gap, and 2 or lower with a
guide-sourced gap.

## 2. Grades

| Grade | Score |
|---|---|
| A | ≥ 85 |
| B | ≥ 70 |
| C | ≥ 55 |
| D | ≥ 40 |
| F | < 40 |

**Functional defect cap.** A functional defect observed in a live call caps the grade at
B, whatever the arithmetic says. A listing that scores well and does not work is not an A.

## 3. Stated legal positions

Where a seller states a legal position on the listing (for example "game of pure skill,
not gambling"), the reviewer scores against that stated position and flags whatever is
still missing under it. The reviewer does not adjudicate the position itself. It is not a
legal authority.

## 4. Seller responsiveness marker (new in 2.3)

The guide asks sellers to answer their feedback inbox promptly and to say how they handle
refunds (§7, 1.7). Buyers who cannot reach a seller can send a refund or billing problem
to Team Kepler's free feedback item, which takes it to the seller.

This is a **public marker, not a score**. Where a billing problem has been put to a seller
with the transaction id, and two business days pass with no answer, the item's public
summary says so as a fact: "A billing problem raised on [date] is awaiting the seller's
reply." The marker is removed when the seller answers, whatever the answer. Refunds are the
seller's decision; the marker records whether the seller replied, not what they decided.

It becomes a scored dimension only once there is enough traffic to measure response times
fairly across stores.

## 5. Stages

**Stage 1: the listing.** Everything above, read from the catalog with no purchase. Free
items may be called. Labelled "stage 1" wherever published.

**Stage 2: verification by live call.** Adds, per guide §2 and §6:

- The response envelope: `ok`, `item`, `answer_type`, `as_of`, inputs echo,
  `defaulted_inputs`, units, `out_of_range`, `summary`, `disclaimer`.
- Error codes, and unknown parameters rejected with 400.
- The paid route refuses calls without Qatom's fulfilment header.
- In a cart with another item, each returns its own answer, with the link and summary
  first and links that last at least 15 minutes.
- `llms.txt` says how refunds and billing problems are handled.
- Repeat-call reliability.

Stage 2 needs a review budget, a per-item price ceiling and an escalation path. The
planned model is that a seller pays for its own stage 2; a seller that passes gets a
badge showing the rating rests on a real transaction. Until that is in place, stage 2 runs
case by case and is labelled where it has run.

**Stage 3: people.** Feedback from human testers. Planned, not yet run.

## 6. Not yet scored

- The `qatom.ai` addresses, until the guide moves its own addresses from `todaq.net`.

(The purchase-approval threshold, listed here in 2.2, is closed in guide 1.3. It is a
buyer's setting, not a property of a listing, so it is not a listing check.)

## 7. Version history

See [`../CHANGELOG.md`](../CHANGELOG.md).

## Disclosure

The reviewer is operated for Qatom. Some stores in the catalog are first party, so those
reviews are not arm's length. See [`../policy/disclosure.md`](../policy/disclosure.md).
