"""Visit every page as a fresh student and walk each practice mode once.

Run: .venv/bin/python scripts/smoke.py  (uses the local database)
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.auth.models import User  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402

from curriculum.models import ProblemTemplate  # noqa: E402
from learning.models import Attempt, PracticeSession  # noqa: E402
from reports.models import SharedReport  # noqa: E402

setup_test_environment()
settings.ALLOWED_HOSTS.append("testserver")
User.objects.filter(username="smoke").delete()
user = User.objects.create_user("smoke", "", "x")
c = Client()
c.force_login(user)
failures = []


def check(resp, label):
    if resp.status_code >= 400:
        failures.append(label)
        print("FAIL", label, resp.status_code)
        print(resp.content.decode()[:3000])
    return resp


def get(url):
    return check(c.get(url, follow=True), url)


def post(url, data):
    return check(c.post(url, data, follow=True), f"POST {url} {data}")


def run_session(kind, item=""):
    r = post("/practice/start/", {"kind": kind, "item": item})
    m = re.search(r"/s/(\d+)/", r.redirect_chain[-1][0] if r.redirect_chain else "")
    if not m:
        print("no session for", kind)
        return None
    sid = m.group(1)
    s = PracticeSession.objects.get(id=sid)
    for pos, q in enumerate(s.items):
        get(f"/s/{sid}/?q={pos}")
        data = {"position": pos, "seconds": 120, "action": "next" if s.is_exam_style else "answer"}
        if q["type"] == "units":
            data["value"] = str(q["q"]["answer"])
        else:
            data["choice"] = "0"
        if "estimate" in q:
            data["estimate"] = "0"
        post(f"/s/{sid}/answer/", data)
    post(f"/s/{sid}/finish/", {})
    get(f"/s/{sid}/results/")
    get(f"/s/{sid}/?q=0")
    print("ran", kind, len(s.items), "questions")
    return sid


post("/start/", {"exam_date": "", "hours_per_week": 9})
for url in ["/", "/plan/", "/topics/", "/topics/TE1/", "/practice/", "/cards/", "/errors/", "/simulation/",
            "/references/", "/reports/", "/reports/readiness/", "/reports/weekly/", "/practice/explain/"]:
    get(url)

from curriculum.models import SpecItem  # noqa: E402

for code in SpecItem.objects.values_list("code", flat=True):
    get(f"/learn/{code}/")

diag = run_session("diagnostic")
post("/plan/accept/", {})
for kind in ["drill", "warmup", "lookup", "method", "estimate", "spot_error", "replay", "units", "timed_block"]:
    run_session(kind, "TE2" if kind in ("drill", "estimate") else "")
get(f"/reports/simulation/{diag}/")

# The lesson loop, end to end.
for step in range(14):
    html = get("/study/HD1/").content.decode()
    if 'action="/study/HD1/answer/"' in html:
        post("/study/HD1/answer/", {"choice": "0", "seconds": 60})
    elif "Lesson complete" in html or "Tested out" in html:
        break
    else:
        post("/study/HD1/next/", {"action": "next"})
print("lesson reached done:", "Lesson complete" in get("/study/HD1/").content.decode())

r = get("/cards/")
m = re.search(r"/cards/(\d+)/grade/", r.content.decode())
if m:
    post(f"/cards/{m.group(1)}/grade/", {"grade": "good"})
t = ProblemTemplate.objects.exclude(explain_prompt="").first()
post("/practice/explain/", {"template": t.id, "answer": "Because the units cancel."})
att = Attempt.objects.filter(student=user, kind="problem").exclude(response="").first()
post(f"/attempt/{att.id}/audit/", {"checks": ["I picked the right method for the question"], "cause": "units", "next": "/errors/"})
for kind in ["readiness", "weekly"]:
    post("/reports/share/", {"kind": kind, "recipient": "Mentor", "days": 30, "sections": ["estimate", "coverage"]})
post("/reports/share/", {"kind": "simulation", "simulation": diag, "days": 7})
for s in SharedReport.objects.filter(student=user):
    check(Client().get(f"/r/{s.token}/"), f"public {s.kind}")
for url in ["/", "/errors/", "/reports/", "/reports/readiness/", "/topics/HD1/"]:
    get(url)
print("FAILURES:", failures or "none")
