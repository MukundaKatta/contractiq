"""Contract comparison against standard templates."""

from __future__ import annotations

import json
import re

import anthropic

from contractiq.models import Clause, ClauseType, ComparisonResult
from contractiq.templates.standard import CLAUSE_TEMPLATES, get_template


class ContractComparator:
    """Compares contract clauses against standard templates.

    Identifies deviations, missing protections, and computes
    similarity scores.
    """

    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        self._client = client

    def compare(
        self,
        clauses: list[Clause],
        use_llm: bool = False,
    ) -> list[ComparisonResult]:
        """Compare clauses against their corresponding standard templates.

        Args:
            clauses: Extracted clauses to compare.
            use_llm: If True, use Claude for comparison.

        Returns:
            List of comparison results.
        """
        results: list[ComparisonResult] = []
        for clause in clauses:
            template = get_template(clause.clause_type)
            if template is None:
                continue
            if use_llm and self._client:
                result = self._compare_with_llm(clause, template)
            else:
                result = self._compare_with_heuristics(clause, template)
            results.append(result)
        return results

    def _compare_with_heuristics(
        self,
        clause: Clause,
        template: dict[str, str],
    ) -> ComparisonResult:
        """Compare a clause against a template using keyword-based heuristics."""
        template_text = template["template"]
        key_elements = template.get("key_elements", "")

        # Check which key elements are present in the clause
        elements = [e.strip() for e in key_elements.split(",")]
        found = 0
        missing: list[str] = []
        for element in elements:
            # Check if key words from the element appear in the clause
            keywords = [w.lower() for w in element.split() if len(w) > 3]
            if any(kw in clause.text.lower() for kw in keywords):
                found += 1
            else:
                missing.append(element)

        similarity = found / max(len(elements), 1)

        # Check for deviations by looking at template-specific patterns
        deviations = self._find_deviations(clause, template_text)

        return ComparisonResult(
            clause_type=clause.clause_type,
            contract_text=clause.text[:1000],
            template_text=template_text,
            similarity_score=round(similarity, 2),
            deviations=deviations,
            missing_protections=missing,
        )

    def _find_deviations(self, clause: Clause, template_text: str) -> list[str]:
        """Identify specific deviations from the template."""
        deviations: list[str] = []

        # Check for unusually short clauses
        template_word_count = len(template_text.split())
        clause_word_count = len(clause.text.split())
        if clause_word_count < template_word_count * 0.3:
            deviations.append(
                f"Clause is significantly shorter than standard "
                f"({clause_word_count} vs {template_word_count} words)"
            )

        # Check for one-sided language
        one_sided_patterns = [
            (r"(?i)\bsolely\s+(?:responsible|liable)\b", "Contains one-sided liability language"),
            (r"(?i)\bno\s+obligation\b", "Contains 'no obligation' language"),
            (r"(?i)\birrevocabl[ey]\b", "Contains irrevocable commitments"),
            (r"(?i)\bwaive\w*\s+(?:all|any)\s+(?:rights?|claims?)\b", "Contains broad waiver of rights"),
        ]
        for pattern, desc in one_sided_patterns:
            if re.search(pattern, clause.text) and not re.search(pattern, template_text):
                deviations.append(desc)

        return deviations

    def _compare_with_llm(
        self,
        clause: Clause,
        template: dict[str, str],
    ) -> ComparisonResult:
        """Compare using Claude LLM for nuanced analysis."""
        assert self._client is not None

        message = self._client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": (
                    "Compare this contract clause against the standard template.\n\n"
                    f"CONTRACT CLAUSE ({clause.clause_type.value}):\n{clause.text}\n\n"
                    f"STANDARD TEMPLATE:\n{template['template']}\n\n"
                    f"KEY ELEMENTS expected: {template.get('key_elements', '')}\n\n"
                    "Return a JSON object with:\n"
                    '- "similarity_score": float 0-1\n'
                    '- "deviations": list of strings describing differences\n'
                    '- "missing_protections": list of strings for missing safeguards\n\n'
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
            return self._compare_with_heuristics(clause, template)

        return ComparisonResult(
            clause_type=clause.clause_type,
            contract_text=clause.text[:1000],
            template_text=template["template"],
            similarity_score=min(1.0, max(0.0, float(data.get("similarity_score", 0.5)))),
            deviations=data.get("deviations", []),
            missing_protections=data.get("missing_protections", []),
        )
