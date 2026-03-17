"""Suggestion engine for contract clause modifications."""

from __future__ import annotations

import json
import re

import anthropic

from contractiq.models import Clause, ClauseType, Risk, Severity, Suggestion
from contractiq.templates.standard import get_template


# Rule-based suggestion mappings: clause_type -> list of (condition_pattern, suggestion)
_SUGGESTION_RULES: dict[ClauseType, list[tuple[str, str, str]]] = {
    ClauseType.TERMINATION: [
        (
            r"(?i)immediately.*without.*(?:cause|notice|reason)",
            "Add a notice period and mutual termination rights",
            'Either Party may terminate this Agreement upon [30] days\' prior written notice. '
            'For cause termination, the breaching Party shall have [30] days to cure after written notice.',
        ),
        (
            r"(?i)(?:no|without).*(?:cure|remedy|opportunity)",
            "Add a cure period before termination for breach",
            'In the event of a material breach, the non-breaching Party shall provide written notice '
            'and allow [30] days for the breaching Party to cure before termination.',
        ),
    ],
    ClauseType.LIMITATION_OF_LIABILITY: [
        (
            r"(?i)(?:unlimited|no\s+limit)",
            "Add a mutual liability cap",
            'EACH PARTY\'S TOTAL AGGREGATE LIABILITY SHALL NOT EXCEED THE AMOUNTS PAID OR PAYABLE '
            'IN THE 12-MONTH PERIOD PRECEDING THE CLAIM, EXCEPT FOR INDEMNIFICATION OBLIGATIONS, '
            'BREACH OF CONFIDENTIALITY, OR WILLFUL MISCONDUCT.',
        ),
        (
            r"(?i)(?:consequential|indirect|special|punitive).*(?:included|not\s+excluded)",
            "Add exclusion of consequential damages",
            'NEITHER PARTY SHALL BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, '
            'OR PUNITIVE DAMAGES, REGARDLESS OF THE THEORY OF LIABILITY.',
        ),
    ],
    ClauseType.CONFIDENTIALITY: [
        (
            r"(?i)(?:perpetual|indefinite|no.*(?:expir|end|limit))",
            "Add a reasonable survival period",
            'Confidentiality obligations shall survive for [3] years following the disclosure '
            'of the Confidential Information, or [5] years for trade secrets.',
        ),
    ],
    ClauseType.PAYMENT: [
        (
            r"(?i)(?:upon\s+receipt|within\s+(?:[0-9]|10)\s+days)",
            "Extend the payment window to net-30",
            'All invoices are due and payable within [30] days of the invoice date. '
            'Late payments shall accrue interest at [1.5]% per month or the maximum rate '
            'permitted by law, whichever is less.',
        ),
    ],
    ClauseType.IP: [
        (
            r"(?i)(?:all|entire|complete).*(?:rights|ownership|title).*(?:transfer|assign|belong)",
            "Retain pre-existing IP rights",
            'Each Party retains all rights in its pre-existing intellectual property. '
            'Work Product created specifically under this Agreement shall be owned by [Party B] '
            'upon full payment. [Party A] retains a license to general knowledge and techniques.',
        ),
    ],
}


class SuggestionEngine:
    """Recommends modifications to contract clauses.

    Generates suggestions based on detected risks and template comparisons,
    using either rule-based logic or LLM-powered analysis.
    """

    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        self._client = client

    def suggest(
        self,
        clauses: list[Clause],
        risks: list[Risk],
        use_llm: bool = False,
    ) -> list[Suggestion]:
        """Generate suggestions for improving contract clauses.

        Args:
            clauses: Extracted clauses.
            risks: Detected risks to address.
            use_llm: If True, use Claude for generating suggestions.

        Returns:
            List of suggested modifications.
        """
        if use_llm and self._client:
            return self._suggest_with_llm(clauses, risks)
        return self._suggest_with_rules(clauses, risks)

    def _suggest_with_rules(
        self,
        clauses: list[Clause],
        risks: list[Risk],
    ) -> list[Suggestion]:
        """Generate suggestions using rule-based matching."""
        suggestions: list[Suggestion] = []

        clause_map: dict[ClauseType, Clause] = {}
        for clause in clauses:
            clause_map.setdefault(clause.clause_type, clause)

        # Generate suggestions from risk-triggered rules
        for risk in risks:
            clause = clause_map.get(risk.clause_type)
            if clause is None:
                # Missing clause -- suggest adding from template
                template = get_template(risk.clause_type)
                if template:
                    suggestions.append(Suggestion(
                        clause_type=risk.clause_type,
                        original_text="[MISSING]",
                        suggested_text=template["template"],
                        rationale=risk.description,
                        priority=risk.severity,
                    ))
                continue

            rules = _SUGGESTION_RULES.get(clause.clause_type, [])
            for pattern, rationale, suggested_text in rules:
                if re.search(pattern, clause.text):
                    suggestions.append(Suggestion(
                        clause_type=clause.clause_type,
                        original_text=clause.text[:500],
                        suggested_text=suggested_text,
                        rationale=rationale,
                        priority=risk.severity,
                    ))
                    break  # One suggestion per clause per risk

        return suggestions

    def _suggest_with_llm(
        self,
        clauses: list[Clause],
        risks: list[Risk],
    ) -> list[Suggestion]:
        """Generate suggestions using Claude LLM."""
        assert self._client is not None

        risk_text = "\n".join(
            f"- [{r.severity.value.upper()}] {r.clause_type.value}: {r.description}"
            for r in risks
        )
        clauses_text = "\n\n".join(
            f"[{c.clause_type.value}] {c.title}\n{c.text}" for c in clauses
        )

        message = self._client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": (
                    "Based on the following contract clauses and identified risks, "
                    "suggest specific modifications to improve the contract.\n\n"
                    f"RISKS:\n{risk_text}\n\n"
                    f"CLAUSES:\n{clauses_text}\n\n"
                    "Return a JSON array of objects with keys: "
                    '"clause_type", "original_text" (brief excerpt), "suggested_text" '
                    '(replacement language), "rationale", "priority" (low/medium/high/critical).\n\n'
                    "Return ONLY valid JSON."
                ),
            }],
        )

        response_text = message.content[0].text.strip()
        if response_text.startswith("```"):
            response_text = re.sub(r"^```\w*\n?", "", response_text)
            response_text = re.sub(r"\n?```$", "", response_text)

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            return self._suggest_with_rules(clauses, risks)

        suggestions: list[Suggestion] = []
        for item in data:
            try:
                ct = ClauseType(item["clause_type"])
            except ValueError:
                ct = ClauseType.UNKNOWN
            try:
                priority = Severity(item.get("priority", "medium"))
            except ValueError:
                priority = Severity.MEDIUM
            suggestions.append(Suggestion(
                clause_type=ct,
                original_text=item.get("original_text", ""),
                suggested_text=item.get("suggested_text", ""),
                rationale=item.get("rationale", ""),
                priority=priority,
            ))

        return suggestions
