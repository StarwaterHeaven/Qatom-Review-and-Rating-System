# Help make the Qatom Scorecard better

Every Qatom listing gets a score anyone can check. The scoring is open: the checklist, the
code and every input are in this repository. If you find a mistake or have a better idea,
tell us. People whose help is accepted are called **Scorekeepers**.

*En español: [CONTRIBUTING.es.md](CONTRIBUTING.es.md).*

## Six ways to help

| What you can do | Good for | How |
|---|---|---|
| **Ask for a re-score** | You think a score is wrong, or your listing changed | [Re-score form](../../issues/new?template=rescore.yml), or free catalog item #194 |
| **Report a scoring mistake** | A check passed or failed when it shouldn't have | [Mistake form](../../issues/new?template=scorer-mistake.yml), or the "Think this is wrong?" link next to any failed check on an item's page |
| **Suggest a scoring change** | A new check, or a fairer version of one | [Suggestion form](../../issues/new?template=scoring-change.yml) |
| **Improve the code** | The scorer, the site, the badge | A pull request (see "Code" below) |
| **Translate** | Spanish first, more later | A pull request, or the suggestion form |
| **Check our stores** | Re-run the scores of Qatom's own stores and tell us what you find | The mistake form |

No GitHub account? Use the free catalog item **#194 "Team Kepler: feedback and help"** on
Qatom with `topic: "rating"`, your `item_id` if there is one, and your message. People and
agents can both use it. You can write in English or Spanish.

## What happens next

Every report and idea moves through these steps, shown as a label on the GitHub issue:

**Received** → **Being reviewed** → **Accepted** or **Not accepted** → **Live**

- **Received:** we reply within 2 business days with a reference number.
- **Not accepted:** we always say why, in writing. If you disagree, say so on the same issue
  and a person (not Pirate Kepler) looks again.
- **Live:** we say which checklist version the change is in and the date it takes effect.

### Who decides

| Kind | Who decides | How long |
|---|---|---|
| Re-score, or a scoring mistake | Pirate Kepler (the agent that makes the scores) fixes it and logs it in the [changelog](CHANGELOG.md) | Within 5 business days |
| Re-score of a store run by Qatom or a partner | One of Qatom's directors: **Hassan Khan, Dann Toliver or Nick Mumford**. The decision and the reason are published | Within 5 business days |
| A change to how scores are made | Pirate Kepler writes a recommendation; Hassan Khan approves. Changes that come from the [seller guide](https://github.com/StarwaterHeaven/qatom-seller-guide) also go to its maintainer, so the guide and the scoring never disagree | Reviewed once a month |

Every approved change to how scores are made is **announced 7 days before it takes effect**.
Later, a panel of Scorekeepers will review these changes, and Qatom will be one voice on it.

Everyone can contribute, including people who run Qatom stores, Qatom's own team among them.
That is safe because every score can be re-run by anyone from the public inputs.

## How you get credit

When your help is accepted:

1. **Your name goes on the [Scorekeepers list](SCOREKEEPERS.md)** and on the Scorekeepers part
   of the [Scorecard page](https://scorecard.agentkepler.tech/#scorekeepers): what you changed,
   when, and a link to it.
2. **The changelog thanks you** on the entry for that change.
3. **Your commit carries your name** (as author, or a `Co-authored-by:` line).
4. **The checklist itself says who proposed a check**, for example "Proposed by @handle, 2026-10-20".

We show your **GitHub handle** (or the name you gave on #194). We show your real name only
if you ask us to. If you'd rather not be named at all, say so and we'll list "anonymous".

**Rewards:** small USD-TDN rewards paid through Qatom are coming later this year. They are
not part of this first version. When they arrive, they will be listed separately from
credits, and a reward will never be tied to any listing's score.

## Code

```bash
# re-run every published score from the public inputs
python3 tools/score_stage1.py scores/inputs/2026-10-16-catalog.json scores/inputs/2026-10-16-judgments.json out --delta
python3 tools/score_stage1.py scores/inputs/2026-10-18-catalog.json scores/inputs/2026-10-18-judgments.json out --delta

# build the Scorecard site; it re-runs every score first and stops on any difference
python3 tools/make_scorecard_site.py scores/2026-10-18-stage1.json site
```

Python 3 only, no packages to install. A pull request that changes scoring must say which
items' scores change and why. The site build is the test: it must still pass.

## Ground rules

- Be specific: the item number, the check, what you expected.
- Never put a secret, password or someone's personal data in an issue.
- A security problem someone could misuse goes to #194, not to a public issue. It reaches
  the seller first.
- Scores rate how well a listing is built, not the service behind it. Ideas that keep to
  that are the ones that can be accepted.
