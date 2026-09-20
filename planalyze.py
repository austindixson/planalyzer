#!/usr/bin/env python3
"""planalyzer — critically analyze a plan/PRD with a diversified Jev panel.

Requires TYPESAFE_API_KEY or JEV_API_KEY. No third-party deps.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_URL = "https://api.typesafe.ai/v1/systemone"
ROOT = Path(__file__).resolve().parent


def api_key() -> str:
    for name in ("TYPESAFE_API_KEY", "JEV_API_KEY"):
        v = (os.environ.get(name) or "").strip()
        if v:
            return v
    raise SystemExit(
        "Set TYPESAFE_API_KEY (or JEV_API_KEY). Never commit secrets."
    )


def load_panel(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def seat_to_question(seat: dict[str, Any]) -> dict[str, Any]:
    q: dict[str, Any] = {
        "type": seat["primitive"].lower(),
        "instructions": seat["instructions"],
    }
    if seat.get("criteria") is not None:
        q["criteria"] = seat["criteria"]
    return q


def normalize(raw: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for sid, ans in raw.items():
        if not isinstance(ans, dict):
            continue
        if "noul" in ans:
            out[sid] = {"noul": float(ans["noul"]), "type": "noul"}
        elif "score" in ans:
            out[sid] = {
                "score": float(ans["score"]),
                "type": "score",
                "confidence": ans.get("confidence"),
            }
        elif "choice" in ans:
            out[sid] = {
                "choice": ans.get("choice"),
                "type": "choice",
                "confidence": ans.get("confidence"),
                "probabilities": ans.get("probabilities"),
            }
        else:
            out[sid] = ans
    return out


def route(panel: dict[str, Any], answers: dict[str, Any]) -> tuple[str, set[str]]:
    agg = panel["aggregation"]
    invert = set(agg.get("invert_for_fire") or [])
    block_at = float(agg["noul_block_threshold"])
    review_at = float(agg["noul_review_threshold"])
    sev_block = float(agg["severity_block_at"])
    fired: set[str] = set()
    block_votes = review_votes = 0

    for seat in panel["seats"]:
        sid = seat["id"]
        if seat["primitive"] == "choice":
            continue
        ans = answers.get(sid) or {}
        if seat["primitive"] == "score":
            score = float(ans.get("score", 0))
            if sid == "severity":
                if score >= sev_block:
                    fired.add(sid)
                    block_votes += 1
                elif score >= max(0.0, sev_block - 1):
                    fired.add(sid)
                    review_votes += 1
            continue
        p = float(ans.get("noul", 0.0))
        problem = (1.0 - p) if sid in invert else p
        if problem >= block_at:
            fired.add(sid)
            block_votes += 1
        elif problem >= review_at:
            fired.add(sid)
            review_votes += 1

    if block_votes:
        return "block", fired
    if review_votes:
        return "review", fired
    return "pass", fired


def call_jev(state: Any, questions: dict[str, Any], model: str) -> dict[str, Any]:
    body = json.dumps({"state": state, "model": model, "questions": questions}).encode()
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode(errors='replace')}") from e


def plain_english(verdict: str, fired: set[str], rec: dict[str, Any] | None, scores: dict[str, float]) -> str:
    rec_s = (rec or {}).get("choice") or "n/a"
    return (
        f"Verdict on pursuing the plan as stated: {verdict.upper()}. "
        f"Fired seats: {', '.join(sorted(fired)) or 'none'}. "
        f"Advisory next step: {rec_s}. "
        f"Scores — coherence {scores.get('strategic_coherence', 'n/a')}, "
        f"execution_risk {scores.get('execution_risk', 'n/a')}, "
        f"product_fit {scores.get('product_fit', 'n/a')}, "
        f"severity {scores.get('severity', 'n/a')}."
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("plan", nargs="?", type=Path, help="Plan markdown/text file (default: stdin)")
    ap.add_argument("--context", type=Path, help="Optional product/context file")
    ap.add_argument("--panel", type=Path, default=ROOT / "panel.json")
    ap.add_argument("--model", default="jev-latest")
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()

    plan_text = args.plan.read_text() if args.plan else sys.stdin.read()
    if not plan_text.strip():
        raise SystemExit("empty plan")
    context = args.context.read_text() if args.context else ""

    panel = load_panel(args.panel)
    questions = {s["id"]: seat_to_question(s) for s in panel["seats"]}
    state = {"plan": plan_text, "product_context": context or "(none provided)"}

    result = call_jev(state, questions, args.model)
    raw = result.get("answers") or {}
    norm = normalize(raw)
    verdict, fired = route(panel, norm)
    rec = norm.get("recommended_next_step")
    scores = {
        sid: float(norm[sid]["score"])
        for sid in ("strategic_coherence", "execution_risk", "product_fit", "severity")
        if sid in norm and "score" in norm[sid]
    }

    out = {
        "verdict": verdict,
        "fired": sorted(fired),
        "recommended_next_step": rec,
        "scores": scores,
        "seats": raw,
        "model": result.get("model"),
        "usage": result.get("usage"),
        "plain_english": plain_english(verdict, fired, rec, scores),
    }

    if args.json_only:
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(out, indent=2))
        print()
        print(out["plain_english"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
