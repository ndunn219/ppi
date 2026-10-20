# PE Prep: PE Civil Transportation

A proof-of-concept prep course for the PE Civil exam (Transportation depth module), built from the course design plan. Django, custom CSS and custom JavaScript, no front-end framework.

## What is in it

- **Five phases with gates:** Diagnose, Build, Strengthen, Simulate, Taper. The gates are computed from evidence.
- **The learning loop for each topic:** prime, interactive tutorial, worked example with fading, three try problems, then spaced review. A student can test out after a correct prime.
- **Interactive tutorials for every topic** (`/learn/<code>/`), about 30 minutes each. Each mixes explanation in reStructuredText (rendered with django-docutils), explorers with sliders, figures, "Try it" questions with a retry, a hint and an illustrated explanation, and worked examples revealed one step at a time. The engine is `static/js/tutorials.js`, each topic's diagrams are in `static/js/widgets/<code>.js`, and the content is in `curriculum/tutorials/<code>.py`.
- **Fifteen practice modes:** daily warm-up, flashcards (SM-2), parametric drills, worked-example fading, lookup sprints, which method?, estimate first, spot the error, explain it back, error replay, units drill, mixed timed blocks, half-exam set, full simulation, and the diagnostic.
- **Problem templates whose numbers change.** Each solver in `curriculum/solvers.py` computes the answer, the worked steps, and wrong answers produced by named mistakes, so a wrong pick is diagnosed (units, setup, method and so on).
- **Mastery levels per topic:** Not started, Introduced, Practicing, Proficient, Exam-ready. Hints halve credit, and a level decays while its review is overdue.
- **Readiness estimate:** a likely score range and a zone (Not yet, Building, Approaching, Ready) with guardrails, in `reports/readiness.py`.
- **Shareable reports:** readiness, weekly and simulation. Links expire, can be revoked, can be live or a snapshot, and can be printed to PDF.
- **AI tutor (optional):** line-by-line audits of photographed scratch work, and explain-it-back feedback, using Claude. Without `ANTHROPIC_API_KEY` the course falls back to the verified solution and a self-audit checklist.
- **Django admin for every model** (`/admin/`) and admin docs (`/admin/doc/`).

## Run locally

```bash
python3.14 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

```bash
.venv/bin/python manage.py migrate && .venv/bin/python manage.py seed_course
```

```bash
.venv/bin/python manage.py runserver
```

To see the reports with data, create the demo student. It has five weeks of simulated practice, and you choose its password:

```bash
.venv/bin/python manage.py seed_demo --password choose-a-password
```

Validate tutorial content and widgets after editing them:

```bash
.venv/bin/python manage.py check_tutorials --export build/widget-configs.json
```

```bash
node scripts/check_widgets.js build/widget-configs.json
```

Run the tests and the end-to-end walk:

```bash
.venv/bin/python manage.py test tests
```

```bash
.venv/bin/python scripts/smoke.py
```

## Deploy on Render

`render.yaml` is a Blueprint for one web service and one Postgres database. In the Render dashboard, choose New, then Blueprint, and pick this repository. Then set `ANTHROPIC_API_KEY` on the web service if you want the AI tutor. `build.sh` migrates and loads any missing course content on each deploy. It never overwrites edits made in the admin.

To get into the admin, open the web service's Shell in Render and run:

```bash
python manage.py createsuperuser
```

## PE review

Licensed reviewers approve content at `/review/`, one unit at a time: each topic's lesson and tutorial, each problem type (including its solver code), its flashcards and its lookup drills. To add a reviewer, create a user, then add a Content reviewer record for them in the admin with their name and PE license. Approval stamps the reviewer, license and date on the content, and students see a "PE-reviewed" badge. An approval covers the exact content approved: if it is edited later, or reseeded with different text, it goes back to the queue as "Changed since review". Every decision is kept in Review events.

## Content status

None of the content has been reviewed by a licensed PE yet (see PE review above). Area weights are placeholders. Reference locators point to chapters and parts by name and need checking against the editions the exam supplies. The course never hosts or quotes licensed reference text, and the AI tutor never sees it. Only the public-domain MUTCD is linked. Students open their own PDFs in a viewer that runs entirely in their browser.

See `BUILD_LOG.md` for the decisions made while building it.

## Local test accounts

The local SQLite database used while building has test accounts that exist only in `db.sqlite3`, which is not committed: `demo` (the demo student, created with `demo-local-2026`), `admin` (the superuser, created with `admin-local-2026`), and `reviewer`, whose generated password is in the git-ignored `.local-test-account` file. Render starts with an empty database, so create your own accounts there.
