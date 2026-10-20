"""The AI tutor: line-by-line audits of photographed work, and explain-it-back.

The tutor only ever sees the student's own work and the course's own
verified solution. It is never given reference-manual text: AASHTO's
terms bar putting its content into AI tools, and the course does not
host licensed text at all.

Without ANTHROPIC_API_KEY, audit() returns None and the page falls back
to the verified steps and a self-audit checklist.
"""

import base64
import logging

from django.conf import settings

log = logging.getLogger(__name__)

AUDIT_SYSTEM = """You are a tutor for the PE Civil exam, Transportation module.
A student photographed their handwritten scratch work for one problem.
Compare it line by line with the verified solution you are given.

Report, in plain short sentences:
1. The first line where their work departs from the verified solution, quoting what they wrote.
2. What kind of error it is: concept, method choice, wrong lookup, setup, arithmetic, units, or misreading.
3. One concrete thing to do differently next time.

If the work is correct, say so and name the step they handled best.
If the photo is unreadable, say which part you cannot read. Do not guess.
Never invent values that are not in the photo or the verified solution.
Keep it under 150 words."""

EXPLAIN_SYSTEM = """You are a tutor for the PE Civil exam, Transportation module.
A student answered an explain-it-back question about one step of a method.
You have the question and a model explanation.
Say in two or three sentences whether their reasoning is right, what it is missing,
and correct any misconception. Be direct and kind. Under 80 words."""


def enabled():
    return bool(settings.ANTHROPIC_API_KEY)


def _client():
    import anthropic

    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _call(system, content, max_tokens=2000):
    import anthropic

    try:
        response = _client().beta.messages.create(
            model=settings.TUTOR_MODEL,
            max_tokens=max_tokens,
            system=system,
            output_config={"effort": "medium"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content": content}],
        )
    except anthropic.RateLimitError:
        return "The tutor is busy right now. Try again in a minute, or use the self-audit below."
    except (anthropic.APIStatusError, anthropic.APIConnectionError) as exc:
        log.warning("Tutor call failed: %s", exc)
        return None
    if response.stop_reason == "refusal":
        return "The tutor could not review this one. Use the self-audit checklist below."
    return "".join(b.text for b in response.content if b.type == "text").strip() or None


def solution_text(instance):
    lines = [f"Problem: {instance.stem}", f"Verified answer: {instance.answer_label}", "Verified steps:"]
    lines += [f"{i}. {s['text']}" for i, s in enumerate(instance.steps, 1)]
    return "\n".join(lines)


def audit(instance, image_bytes, media_type, chosen_label):
    """Return the tutor's audit text, or None when the tutor is off or failed."""
    if not enabled():
        return None
    data = base64.standard_b64encode(image_bytes).decode("ascii")
    content = [
        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}},
        {"type": "text", "text": f"{solution_text(instance)}\n\nThe student chose: {chosen_label or 'no answer'}."},
    ]
    return _call(AUDIT_SYSTEM, content)


def explain(prompt, model_answer, student_answer):
    if not enabled():
        return None
    text = f"Question: {prompt}\nModel explanation: {model_answer}\nStudent's explanation: {student_answer}"
    return _call(EXPLAIN_SYSTEM, [{"type": "text", "text": text}], max_tokens=1000)
