# Build log

Built in one session on 2026-10-20 by Claude (Opus 5.5) from the course design plan, without check-ins. This file records the decisions made along the way and what is left.

## Decisions made without you

| Area | Decision | Why |
| --- | --- | --- |
| Scope | Transportation only: 6 areas, 12 topics, 23 problem templates, 51 flashcards, 14 lookup drills | Enough to exercise every mode; content quality matters more than volume |
| Area weights | Placeholders (25/20/20/10/15/10%) | The current NCEES specification needs checking before these mean anything |
| Problems | Template plus a solver function per problem type; every wrong choice is produced by a named mistake | New numbers every time, a correct answer key, and diagnosis of misses without AI |
| Answer format | Four-choice multiple choice | Matches most exam items and makes cause tagging exact |
| Diagnostic | 2 problems per topic (24) plus 6 lookup questions, timed at 6 min each | 80 questions over 12 topics would repeat each type about 7 times; `COURSE["DIAGNOSTIC_PER_ITEM"]` in settings scales it |
| Simulations | Full = 80 questions and 8 hours; half = 40 and 4 hours; block = 10 and 1 hour | Matches the plan; with 23 templates, a full simulation repeats types with new numbers |
| Mastery | Thresholds exactly as in the plan; "spaced review 7 days later" approximated as "the last 5 attempts span 7+ days and the latest is correct" | Simplest rule that matches the intent |
| Readiness | Recency half-life 21 days, shrinkage toward the student's average with k = 4, unstudied topic = 25% (guessing), simulations blended up to 60% | Tunable constants at the top of `reports/readiness.py` |
| Working target | 70% correct, labelled as an assumption everywhere it appears | NCEES publishes no fixed passing percentage |
| References | No licensed text anywhere; locations by chapter or part name; MUTCD linked as public domain; students open their own PDFs in a viewer that never uploads | Licensing, and AASHTO's bar on use with AI tools |
| AI tutor | `claude-opus-5-5`, effort medium, server-side refusal fallback on; photos read in memory and never stored; the tutor never sees reference text | Default current model; privacy; licensing |
| Without an API key | Self-audit checklist, and the student can re-tag the cause | The course works fully without the tutor |
| Reports | Server-drawn SVG charts; PDF by the browser's print; share links are a snapshot by default, live as an option (readiness only) | No chart library; a snapshot is the honest default for a third party |
| Design | AceVoz staff layout (white sidebar, warm page, rounded cards, Unbounded + Plus Jakarta Sans, pill segments), recoloured road-sign green and amber | "Draw inspiration", not a copy; fonts are OFL and their licences are in `static/fonts/` |
| reStructuredText | Lessons stored as RST and rendered with django-docutils; admindocs enabled at `/admin/doc/` | As requested |
| Render | Blueprint with free web and Postgres plans | Cheapest to try. Render's free Postgres expires after 30 days, so switch to a paid plan to keep data |

## Second pass: interactive tutorials

The first version taught with roughly 300-word summaries per topic, which made the course mostly practice questions. Each topic now has an interactive tutorial of about 30 minutes, in the lesson loop's Learn step and at `/learn/<code>/`.

| Decision | Why |
| --- | --- |
| A tutorial is an ordered list of blocks (text, figure, explorer, check, worked example), stored as `TutorialBlock` rows and editable in the admin under each lesson | Content stays data, and a PE reviewer can fix one block without touching code |
| One widget function per diagram draws the explorer, the fixed figure and the illustration under each explanation | The picture a student explores is the same one that explains their answer |
| Widgets are plain JavaScript returning SVG, checked headlessly in Node | No chart library, and every widget is tested across its slider ranges |
| Checks are graded in the browser, give one retry with a hint, then the full explanation | They are for learning, not evidence; they are logged as `check` attempts but never count toward mastery |
| VD1 was written first as the reference; the other 11 topics were written in parallel to the same pattern and then reviewed | Consistency across topics |
| The old summary stays as each topic's "cheat sheet", beside the tutorial | Quick review before an exam |

## PE review workflow

| Decision | Why |
| --- | --- |
| Review in units per topic: lesson and tutorial, each problem type, flashcards as a group, lookup drills as a group (59 units) | Small enough to review in one sitting each; large enough not to be tedious |
| An approval stores a fingerprint of the content, including a problem's solver source code | Any later change, by admin edit, reseed or code change, sends it back for review instead of keeping a stale approval |
| Only users with a Content reviewer record (name and PE license) can decide; the admin shows review fields read-only | Approvals are attributable, and stamped with a license students can see |
| "Needs changes" requires notes; every decision is kept in Review events | A reviewer's correction can't get lost, and there is an audit trail |
| Students see badges on tutorials, topics, problem feedback and flashcards; shared reports state how much is reviewed | Unreviewed content is clearly labelled where it is used |

## How it was checked

- 27 unit tests (`tests/`): every solver against hand-worked values, every template drawn 50 times (four distinct choices, one correct, every wrong one explained, at least one flawed step for Spot the error), mastery levels, decay, the review ladder and readiness zones.
- `scripts/smoke.py`: a fresh student signs up, takes the diagnostic, accepts the plan, runs all 13 session types, completes a lesson loop, grades a card, explains a step, self-audits, creates three share links and opens them logged out. All pass.
- Pages checked in a browser at desktop and phone width: overview, practice hub, runner and feedback, exam-style runner, lesson, readiness report, public report and admin.
- `collectstatic` with production settings (hashed, compressed files) and `check --deploy`. The two remaining warnings (HSTS, SSL redirect) are left to Render's HTTPS edge.

## Not done or not verified

- **The AI tutor has not been called.** No API key was available here. The code path matches the current SDK's parameters (checked against the installed `anthropic` 1.16), but the first real call happens on Render.
- **No content has been reviewed by a licensed PE.** The formulas are standard textbook forms, but table values (side friction by speed), editions and reference locators all need checking. Each lesson and template has a "reviewed by PE" flag, plus an admin action to set it.
- **Real exam fidelity is approximate.** The reference panel mimics "one document at a time" by showing one PDF, but it doesn't reproduce the Pearson VUE viewer.
- **Sag and crest lengths ignore practical minimums** (such as 3 × design speed), which a reviewer may want added.
- **The calibration loop is not built.** Asking students to report pass or fail, and refitting the weights, needs real students first.
- **No email, password reset or employer accounts.** Share links cover the employer case for now.

## To deploy

1. Merge `build/course-poc`, or point Render at that branch.
2. In Render: New, then Blueprint, then this repository.
3. Optional: set `ANTHROPIC_API_KEY` on the `pe-prep` service.
4. In the service's Shell, create an admin account with `python manage.py createsuperuser`. Optionally run `python manage.py seed_demo --password <choose>` for a demo student.
