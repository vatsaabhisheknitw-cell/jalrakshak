"""Claude-generated compliance summary + recommendations.

Uses the current Sonnet model. Degrades gracefully (returns a heuristic
summary) when ANTHROPIC_API_KEY is unset or the SDK isn't installed, so the
rest of the pipeline still runs in dev/demo.
"""
from __future__ import annotations

import json
import os

from app.config import CLAUDE_MODEL


def _fallback_summary(factory_name: str, result: dict, period: str) -> dict:
    score = result["compliance_score"]
    risk = "low" if score >= 98 else "medium" if score >= 90 else "high" if score >= 75 else "critical"
    return {
        "summary": (
            f"{factory_name} scored {score}% compliance for {period} across "
            f"{result['total_readings']} readings, with {result['violation_count']} "
            f"violation(s) and {result['warning_count']} warning(s). "
            "(AI summary unavailable — set ANTHROPIC_API_KEY for detailed analysis.)"
        ),
        "recommendations": [
            "Review ETP operation logs for the days flagged as violations.",
            "Check dosing/aeration around any BOD/COD spikes.",
            "Have the NABL lab re-test any borderline parameters.",
        ],
        "risk_level": risk,
        "risk_explanation": "Heuristic estimate from the compliance score.",
        "parameter_insights": {},
    }


def generate_compliance_summary(factory_name: str, result: dict, period: str) -> dict:
    """Return {summary, recommendations, risk_level, risk_explanation, parameter_insights}."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return _fallback_summary(factory_name, result, period)

    try:
        import anthropic
    except ImportError:
        return _fallback_summary(factory_name, result, period)

    prompt = f"""You are an industrial wastewater compliance expert in India.
Analyze this factory's ETP monitoring data and provide:
1. A plain-language compliance summary (3-4 sentences) for the factory manager
2. Specific technical recommendations to fix any violations
3. Risk assessment for the next reporting period

Factory: {factory_name}
Reporting Period: {period}
Compliance Score: {result['compliance_score']}%
Total Readings: {result['total_readings']}
Violations: {result['violation_count']}
Warnings: {result['warning_count']}

Violation Details:
{json.dumps(result['violations'][:20], indent=2)}

Warning Details:
{json.dumps(result['warnings'][:20], indent=2)}

Respond with ONLY this JSON (no markdown, no backticks):
{{
  "summary": "...",
  "recommendations": ["rec1", "rec2", "rec3"],
  "risk_level": "low|medium|high|critical",
  "risk_explanation": "...",
  "parameter_insights": {{ "parameter_name": "insight" }}
}}"""

    try:
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(response.content[0].text)
    except Exception as e:  # noqa: BLE001 - never let AI break the pipeline
        fallback = _fallback_summary(factory_name, result, period)
        fallback["risk_explanation"] += f" (AI call failed: {e})"
        return fallback
