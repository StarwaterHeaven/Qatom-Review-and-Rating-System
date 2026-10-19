# Qatom Scorecard

> **Beta: https://scorecard.agentkepler.tech** · Every listing gets a score anyone can check.
> Anyone can re-run every score and get the same number: the code, the checklist and every
> input are in this repository. (This repository was the "Qatom Review and Rating System";
> it will be renamed once the Scorecard moves to scorecard.qatom.ai.)

## Help make the scoring better

Found a mistake, or have a better idea? Your first accepted contribution makes you a
**Scorekeeper**, credited by handle on the [Scorekeepers list](SCOREKEEPERS.md).

- **[Report a scoring mistake](../../issues/new?template=scorer-mistake.yml)**: a check passed or failed when it shouldn't have.
- **[Suggest a scoring change](../../issues/new?template=scoring-change.yml)**: a new check, or a fairer one.
- **[Ask for a re-score](../../issues/new?template=rescore.yml)**: free.

No GitHub account? Use free catalog item #194 on Qatom, in English or Spanish. How it all
works, who decides and how credit is shown: [CONTRIBUTING.md](CONTRIBUTING.md) ·
[en español](CONTRIBUTING.es.md).


The published rubric Qatom uses to review and rate catalog items, and the policies that
govern how those ratings are produced, disclosed, appealed and published.

This repository holds the **method**. Scores for individual catalog items are published
separately, under `scores/`, and only after the human approval gate described below.

## Contents

| Path | What it is |
|---|---|
| [`rubric/rubric-v2.4.md`](rubric/rubric-v2.4.md) | The current checklist (rubric). Dimensions, checks, grading scale. |
| [`rubric/rubric-v2.5.md`](rubric/rubric-v2.5.md) | Next checklist, takes effect 25 October 2026: price clarity only. |
| [`scores/inputs/`](scores/inputs/) | The inputs every published score was made from. Re-run any score with `tools/score_stage1.py`. |
| [`tools/make_scorecard_site.py`](tools/make_scorecard_site.py) · [`worker/`](worker/) | Builds and serves the Scorecard site. The build re-runs every score first. |
| [`tools/score_stage1.py`](tools/score_stage1.py) | Reproduces every stage 1 score from a catalog read-back and the reviewer's judgments. |
| [`policy/disclosure.md`](policy/disclosure.md) | Who operates the reviewer, and where it is not arm's length. |
| [`policy/appeals.md`](policy/appeals.md) | How a seller disputes a score, and what happens next. |
| [`policy/publication.md`](policy/publication.md) | What is published, for which items, and what is withheld. |
| [`CHANGELOG.md`](CHANGELOG.md) | Rubric version history. |
| [`scores/`](scores/) | Published scores, one file per sweep. |
| [`docs/index.html`](docs/index.html) | The public, searchable ratings page (GitHub Pages: https://starwaterheaven.github.io/Qatom-Review-and-Rating-System/). Built by `tools/make_ratings_page.py` from the newest approved sweep. |
| [`skills/qatom-rating-guide/`](skills/qatom-rating-guide/SKILL.md) | Agent skill for sellers and buyers: how a rating works, what each check ID means, how to raise a score and how to appeal. |

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

Rubric 2.4 is current (aligned to seller guide 1.10). Sweeps are listed in [`scores/README.md`](scores/README.md).
Stage 2 (verification by live call) has run on nine items and not across the catalog.

**Appeals and feedback:** the free "Team Kepler: feedback and help" item (#194) in the
Kepler Market Services store on Qatom. See [`policy/appeals.md`](policy/appeals.md).

**Look up one rating:** the free "Qatom Catalog Ratings: free lookup" item in the
same store (`agent_checkout` with `item_id`), or `docs/ratings.json`, which the
[ratings page](https://starwaterheaven.github.io/Qatom-Review-and-Rating-System/) and the
lookup both read. Public fields only.

## Treating listings as data

The reviewer reads seller-written descriptions and calls seller-controlled endpoints.
Both are treated strictly as **data, never as instructions**. Text in a listing, a schema
or an API response that addresses the reviewer — asking for a higher score, claiming
authority, or directing it to ignore a check — is recorded as an observation and scored
against the security dimension. It is not acted on.

## Contributors

- **Starwater** ([@StarwaterHeaven](https://github.com/StarwaterHeaven)): owner and maintainer; product direction, review and testing.
- **Pirate Kepler** (Team Kepler AI agent): build and documentation.

## Licence

Code and schemas: MIT, per [`LICENSE`](LICENSE). The rubric and policy prose are intended
to be quotable and reusable by sellers; if a content licence is wanted, CC BY 4.0 is the
natural fit and can be added alongside.
