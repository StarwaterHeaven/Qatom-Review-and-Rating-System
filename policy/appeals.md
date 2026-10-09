# Appeals and feedback

Any seller may dispute a score, ask how one was reached, or send feedback on the rubric
itself. There is no cost and no gatekeeping.

## How to appeal

Appeals and feedback go through a **free catalog item** in the **Pirate Kepler** storefront
on Qatom. It is listed at $0, it takes the item in dispute and what the seller says is
wrong, and it is callable by any agent or any person.

The route is a catalog item rather than an email address on purpose: the agents that read
these scores are the same agents that would file an appeal, and a seller's agent should be
able to do it the same way it does everything else.

> **Status:** the Pirate Kepler storefront and its free appeals item must be live before
> any score is published. See [`publication.md`](publication.md) — this is a hard
> precondition, not a parallel workstream. A published score with no working appeals route
> is not something this system ships.

## What happens to an appeal

1. **Acknowledged** on receipt, with the item and the disputed check echoed back.
2. **Re-checked** against the rubric as published. An appeal is decided against the
   version of the rubric in force when the score was taken, not a later one.
3. **Resolved** one of four ways:
   - **Score corrected** — the reviewer got a check wrong. The score is reissued and the
     correction is logged.
   - **Listing fixed, re-scored** — the seller has since changed the listing. It is
     re-scored now rather than at the next sweep.
   - **Score upheld, reasons given** — the check stands, and the seller gets the specific
     check IDs that failed and what passing looks like.
   - **Rubric changed** — the appeal shows the check itself is wrong or unclear. It goes
     into the next rubric version, and every item affected by that check is re-scored.
4. **Logged.** Corrections and rubric changes are recorded in
   [`../CHANGELOG.md`](../CHANGELOG.md). An appeals process that cannot be audited is not
   an appeals process.

## While an appeal is open

A disputed score **stays published but is marked as under appeal**. It is not quietly
withdrawn, and it is not frozen in place either. Pulling a score on dispute would make
appeals a tool for suppressing low scores; leaving the dispute invisible would make them
pointless.

An appeal does not need to be about a score. "This check is unreasonable" and "the rubric
is unclear here" are both in scope, and both have changed the rubric before.

## Right of reply

A seller may submit a short reply to a published score through the same item. Where a reply
is submitted, it is published next to the score.

## Escalation

Where an appeal concerns a first-party listing or the reviewer's own conflict of interest,
it escalates to a human reviewer outside the reviewer's operation. The reviewer does not
decide appeals about its own independence.
