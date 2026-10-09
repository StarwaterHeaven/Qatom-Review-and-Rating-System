# Qatom Review and Rating System

The published rubric Qatom uses to review and rate catalog items, and the policies that
govern how those ratings are produced, disclosed, appealed and published.

This repository holds the **method**. Scores for individual catalog items are published
separately, under `scores/`, and only after the human approval gate described below.

## Contents

| Path | What it is |
|---|---|
| [`rubric/rubric-v2.2.md`](rubric/rubric-v2.2.md) | The current rubric. Dimensions, checks, grading scale. |
| [`policy/disclosure.md`](policy/disclosure.md) | Who operates the reviewer, and where it is not arm's length. |
| [`policy/appeals.md`](policy/appeals.md) | How a seller disputes a score, and what happens next. |
| [`policy/publication.md`](policy/publication.md) | What is published, for which items, and what is withheld. |
| [`CHANGELOG.md`](CHANGELOG.md) | Rubric version history. |
| `scores/` | Published scores. Empty until the first approved set ships. |

## The principle

A seller who follows the [Qatom seller guide](https://github.com/StarwaterHeaven/qatom-seller-guide)
perfectly scores 5/5 on every guide-sourced dimension. The rubric is not a separate
standard competing with the guide — it is a measurement of the guide, plus a small number
of checks marked `*` that go beyond it. Where a check sits beyond the guide, the rubric says
so, and a proposal goes to the guide maintainers to fold it in.

This matters because it means a seller can always raise their score by doing something
specific and documented, rather than by guessing what a reviewer wants.

## What is scored, and what is not

Two different things get called "review", and they are kept apart on purpose:

- **Listing hygiene** — is the schema present, are the parameters documented, does the
  description match what the call actually returns, is the price disclosed. Objective,
  cheap, checkable, and actionable by the seller. **This is what the rubric scores.**
- **Service quality and value for money** — whether the thing being sold is any good.
  Subjective, domain-specific, and outside the reviewer's competence. **Not scored.**

A score of A on this rubric means the listing is well built. It is not an endorsement of
the service behind it, and it is not investment, legal, medical or financial advice.

## Human approval gate

No score reaches a public surface on the reviewer's say-so. Every record carries a
**Human Approval Status**, and only `Approved` records publish. Raw reviewer output is
never the input to a ranking, a carousel or a badge.

## Status

The rubric is live and in use. As of this commit every score record is
`Human Approval Status = Pending`, so `scores/` is empty. See
[`policy/publication.md`](policy/publication.md) for what ships when that changes.

## Treating listings as data

The reviewer reads seller-written descriptions and calls seller-controlled endpoints.
Both are treated strictly as **data, never as instructions**. Text in a listing, a schema
or an API response that addresses the reviewer — asking for a higher score, claiming
authority, or directing it to ignore a check — is recorded as an observation and scored
against the security dimension. It is not acted on.

## Licence

Code and schemas: MIT, per [`LICENSE`](LICENSE). The rubric and policy prose are intended
to be quotable and reusable by sellers; if a content licence is wanted, CC BY 4.0 is the
natural fit and can be added alongside.
