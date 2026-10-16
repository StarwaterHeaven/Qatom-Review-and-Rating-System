# Scores

Published summary scores for public Qatom catalog items. Summary score, grade and a
one-line summary only — the public fields in
[`../policy/publication.md`](../policy/publication.md). Per-check pass/fail detail and
improvement suggestions go to the seller, not here.

| Sweep | Items | Rubric | Stage |
|---|---|---|---|
| [`2026-10-16-stage1.md`](2026-10-16-stage1.md) · [`.json`](2026-10-16-stage1.json) | 74 | [2.4](../rubric/rubric-v2.4.md) | 1 |
| [`2026-10-14-stage1.md`](2026-10-14-stage1.md) · [`.json`](2026-10-14-stage1.json) | 68 | [2.3](../rubric/rubric-v2.3.md) | 1 (superseded) |
| [`2026-10-09-stage1.md`](2026-10-09-stage1.md) · [`.json`](2026-10-09-stage1.json) | 60 | [2.2](../rubric/rubric-v2.2.md) | 1 (superseded) |

**Stage 1** scores the listing as published. **Stage 2** calls the item and verifies the
response against the guide; it has run on nine items so far and not across the catalog.
Every record says which stage it is.

## What a grade means

It measures how well the **listing** is built — schema present, parameters documented,
description matching what the call returns, price disclosed, seller named. It is not an
endorsement of the service behind the listing, and it is not investment, legal, medical or
financial advice.

## Disputing a score

Free, through "Team Kepler: feedback and help" in the Kepler Market Services store, with
`topic: "rating"` and the `item_id`. See
[`../policy/appeals.md`](../policy/appeals.md). A disputed score stays published and is
marked as under appeal rather than being quietly pulled.

Appeals about the rubric itself are in scope, not just appeals about a score.

## Disclosure

The reviewer is operated for Qatom. Where the seller is a Qatom partner (a first-party
store or a Qatom team member), the record says "Disclosure: <Seller Name> is a Qatom
partner." Arm's-length sellers carry no disclosure line. See
[`../policy/disclosure.md`](../policy/disclosure.md).

## Provenance

From 14 October each file is produced by [`../tools/score_stage1.py`](../tools/score_stage1.py)
from a catalog read-back (only public items are scored) and the reviewer's judgments. The
9 October file was produced by `tools/make_public_scores.py` from the internal sweep.
