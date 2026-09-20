---
name: planalyzer
description: >-
  Use when the user pastes a plan, PRD, proposal, or improvement plan and wants
  a critical Jev/TypeSafe panel review (pass|review|block) rather than cheerleading.
---

# planalyzer

Run a **diversified Jev System One panel** over a plan/PRD. Code owns aggregation.

## Setup

```bash
export TYPESAFE_API_KEY=…   # or JEV_API_KEY
# from this repo:
python3 planalyze.py path/to/plan.md
# or:
python3 planalyze.py --context product_reality.md <<'PLAN'
…paste plan…
PLAN
```

Install skill (agent environments):

```bash
npx skills add austindixson/planalyzer --skill planalyzer
```

## Behavior

1. Build `state` = `{ plan, product_context }`.
2. One batched `POST https://api.typesafe.ai/v1/systemone` with seats from `panel.json`.
3. Aggregate in `planalyze.py` → `pass` | `review` | `block` on **pursue as stated**.
4. Surface `recommended_next_step` Choice as advisory.
5. Return JSON + one plain-English paragraph. Do not invent API keys or hide low-confidence seats.

## Seats

literalist · skeptic · reward_hack · scope · severity · strategic_coherence · execution_risk · product_fit · recommended_next_step

## Anti-patterns

- Single “is this a good plan?” Noul
- Letting Jev emit the final pass/block string without code thresholds
- Cheerleading — this skill is adversarial by design
