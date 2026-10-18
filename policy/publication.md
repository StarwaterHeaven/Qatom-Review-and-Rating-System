# Publication policy

## The rule

**If a catalog item is public, its summary score and a one-line review summary are public.**

If an item is not public — unlisted, draft, private, or withdrawn — nothing about it is
published. No score, no summary, no mention that it was reviewed.

A seller who lists publicly on Qatom should expect the listing to be reviewed and the
result to be visible. That is the point: a buyer's agent choosing between two items can
see how each listing measures against a published standard. A seller who has not listed
publicly has not opted into anything.

## What is published for a public item

| Field | Published |
|---|---|
| Item name and ID | Yes |
| Summary score (0–100) | Yes |
| Grade (A–F) | Yes |
| One-line review summary | Yes |
| Rubric version the score was taken against | Yes |
| Date the score was taken | Yes |
| Stage (1 = listing only, 2 = verified by live call) | Yes |
| Disclosure line ("Disclosure: <Seller Name> is a Qatom partner."), where the seller is not arm's length | Yes |
| Links to the stage definition and the rubric version | Yes |
| Under-appeal marker, where it applies | Yes |
| Seller's right-of-reply text, where submitted | Yes |
| Per-check pass/fail detail and the seven part scores (the worksheet) | Yes, from 18 October 2026 |
| The inputs each score was made from (catalog read-back and the reviewer's judged values) and a command to re-run it | Yes, from 18 October 2026 |
| Improvement suggestions | No — seller only |
| Transcripts or responses from live calls | No |

The one-line summary is a plain statement of the main finding, written so that it is still
fair when read on its own, with no score next to it. "Clear description, but no free
sibling item and no `llms.txt` pointer" — not "poor listing".

**The worksheet is public; the advice is the seller's.** From 18 October 2026 (Hassan Khan's
approval) each item's page shows which checks passed and failed and the seven part scores,
and the inputs are published so anyone can re-run the score. The grade alone is a verdict;
the worksheet is the proof. What stays with the seller: our suggestions for fixing things,
the reviewer's working notes, and security detail (below). Judged values for items that are
not public are never published.

## Security findings

Where a security finding could be acted on by someone other than the seller, the detail is
**withheld from the public summary and sent to the seller instead**. The published summary
says a security gap was found and that the detail has gone to the seller; it does not
describe how to use it. On the worksheet, the two security checks for such an item read
"Sent to the seller" (`withheld` in the published inputs).

The score still reflects the finding in full. A seller does not get a better grade because
the specifics were withheld, and a buyer is still told there is something there.

This is the one case where the public summary is deliberately less specific than the
finding behind it. Publishing a working exploit against a seller who has not had a chance
to fix it would make the rating system a hazard to the people it rates.

## Preconditions for publishing any score

All four, every time:

1. **Human Approval Status = `Approved`** on the record. `Pending` does not publish.
   Reviewer output is never the direct input to a public surface.
2. **The appeals route is live**: the free "Team Kepler: feedback and help" item in the
   Kepler Market Services store, per [`appeals.md`](appeals.md).
3. **Disclosure attached** where the review is not arm's length, per
   [`disclosure.md`](disclosure.md).
4. **The rubric version is published** in this repository before any score taken against
   it is published. No scoring against an unpublished standard.

## Rankings, carousels and badges

A published score may feed a discovery surface — a top-items carousel, a sort order, a
badge — only from `Approved` records, never from raw reviewer output.

Placement follows publication, not the other way round: an item is not scored because it
is being considered for placement, and a score is not adjusted because of what placement
it would produce.

## Withdrawal and correction

- An item that goes private has its published score removed within one sweep.
- A score corrected on appeal is replaced, and the correction is logged in
  [`../CHANGELOG.md`](../CHANGELOG.md). Corrections are not silent edits.
- A score more than one rubric version old is marked stale and re-taken at the next sweep.

## Current state

Published sweeps are listed in [`../scores/README.md`](../scores/README.md), each with its
Human Approval Status. A sweep marked `Pending` is not published.
