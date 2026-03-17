"""Risk detection for contract clauses."""

from __future__ import annotations

import json
import re

import anthropic

from contractiq.models import Clause, ClauseType, Risk, Severity


# Rule-based risk indicators: (pattern, severity, description, recommendation)
_RISK_RULES: list[tuple[str, ClauseType | None, Severity, str, str]] = [
    # Unilateral termination
    (
        r"(?i)may\s+terminate\s+(?:this\s+agreement\s+)?(?:at\s+any\s+time|immediately|without\s+(?:cause|reason|notice))",
        ClauseType.TERMINATION,
        Severity.HIGH,
        "Allows unilateral termination without cause or notice",
        "Require a reasonable notice period (e.g., 30 days) and mutual termination rights",
    ),
    # No cure period
    (
        r"(?i)terminat\w+.*without.*(?:opportunity|right)\s+to\s+cure",
        ClauseType.TERMINATION,
        Severity.HIGH,
        "No cure period for breach before termination",
        "Add a 30-day cure period for material breaches before termination",
    ),
    # Unlimited liability
    (
        r"(?i)(?:unlimited|no\s+limit(?:ation)?)\s+(?:on\s+)?liability",
        ClauseType.LIMITATION_OF_LIABILITY,
        Severity.CRITICAL,
        "No limitation on liability -- exposes party to unlimited financial risk",
        "Add a mutual liability cap, typically 12 months of fees paid",
    ),
    # One-sided indemnification
    (
        r"(?i)(?:shall|will|agrees?\s+to)\s+indemnif\w+.*(?:all|any\s+and\s+all)\s+(?:claims|losses|damages|liabilit)",
        ClauseType.INDEMNIFICATION,
        Severity.MEDIUM,
        "Broad indemnification language may be one-sided",
        "Ensure indemnification is mutual and limited to third-party claims from material breach",
    ),
    # Auto-renewal without notice
    (
        r"(?i)auto(?:matic(?:ally)?)\s+renew(?:s|al)?\b(?!.*(?:notice|written|days?\s+prior))",
        ClauseType.TERM,
        Severity.MEDIUM,
        "Auto-renewal without clear notice period for opt-out",
        "Add a notice period (e.g., 30-60 days before renewal) to opt out",
    ),
    # Non-compete over 2 years
    (
        r"(?i)(?:non[- ]?compet\w+|restrict\w+).*(?:24|36|48)\s*months|(?:2|3|4)\s*years",
        ClauseType.NON_COMPETE,
        Severity.HIGH,
        "Non-compete period may exceed reasonable duration",
        "Limit non-compete to 12 months with narrowly defined scope",
    ),
    # Waiver of jury trial
    (
        r"(?i)waiv\w+.*(?:right.*(?:jury|trial)|jury\s+trial)",
        ClauseType.GOVERNING_LAW,
        Severity.MEDIUM,
        "Jury trial waiver may limit legal options",
        "Consider whether jury trial waiver is appropriate for your situation",
    ),
    # Sole discretion
    (
        r"(?i)(?:sole|absolute|exclusive)\s+discretion",
        None,
        Severity.MEDIUM,
        "Grants one party sole discretion, which may lead to arbitrary decisions",
        "Replace with 'reasonable discretion' or add objective criteria",
    ),
    # Consequential damages not excluded
    (
        r"(?i)(?:including|shall\s+include)\s+(?:consequential|indirect|special|punitive)\s+damages",
        ClauseType.LIMITATION_OF_LIABILITY,
        Severity.HIGH,
        "Consequential damages are not excluded, creating open-ended liability",
        "Add standard exclusion of indirect, consequential, and punitive damages",
    ),
    # Very short payment terms
    (
        r"(?i)(?:due|payable)\s+(?:upon\s+receipt|within\s+(?:[0-9]|10)\s+days)",
        ClauseType.PAYMENT,
        Severity.LOW,
        "Very short payment window (10 days or less)",
        "Negotiate net-30 payment terms",
    ),
    # Perpetual license grant
    (
        r"(?i)(?:perpetual|irrevocable|permanent)\s+(?:license|right|grant)",
        ClauseType.IP,
        Severity.MEDIUM,
        "Perpetual or irrevocable license grant may be overly broad",
        "Limit license duration to the contract term unless perpetual is justified",
    ),
    # No data breach notification
    (
        r"(?i)(?:data|security)\s+breach(?!.*(?:notif|inform|report|within))",
        ClauseType.DATA_PROTECTION,
        Severity.HIGH,
        "No data breach notification obligation specified",
        "Require breach notification within 72 hours with details of affected data",
    ),
]


class RiskDetector:
    """Detects risks and unfavorable terms in contract clauses.

    Supports two modes:
    - Rule-based detection using regex patterns
    - LLM-powered detection using Claude for deeper analysis
    """

    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        self._client = client

    def detect(self, clauses: list[Clause], use_llm: bool = False) -> list[Risk]:
        """Detect risks across all clauses.

        Args:
            clauses: Extracted clauses to analyze.
            use_llm: If True, use Claude for risk detection.

        Returns:
            List of identified risks.
        """
        if use_llm and self._client:
            return self._detect_with_llm(clauses)
        return self._detect_with_rules(clauses)

    def detect_clause(self, clause: Clause) -> list[Risk]:
        """Detect risks in a single clause using rules."""
        risks: list[Risk] = []
        for pattern, target_type, severity, description, recommendation in _RISK_RULES:
            # If rule targets a specific clause type, only apply if matching
            if target_type is not None and clause.clause_type != target_type:
                continue
            if re.search(pattern, clause.text):
                risks.append(Risk(
                    clause_type=clause.clause_type,
                    severity=severity,
                    description=description,
                    clause_text=clause.text[:500],
                    recommendation=recommendation,
                ))
        return risks

    def _detect_with_rules(self, clauses: list[Clause]) -> list[Risk]:
        """Detect risks using pattern-matching rules."""
        risks: list[Risk] = []
        for clause in clauses:
            risks.extend(self.detect_clause(clause))

        # Check for missing critical clauses
        present_types = {c.clause_type for c in clauses}
        critical_missing = [
            (ClauseType.LIMITATION_OF_LIABILITY, "No limitation of liability clause found"),
            (ClauseType.CONFIDENTIALITY, "No confidentiality clause found"),
            (ClauseType.TERMINATION, "No termination clause found"),
            (ClauseType.GOVERNING_LAW, "No governing law or dispute resolution clause found"),
        ]
        for clause_type, desc in critical_missing:
            if clause_type not in present_types:
                risks.append(Risk(
                    clause_type=clause_type,
                    severity=Severity.HIGH,
                    description=desc,
                    recommendation=f"Add a standard {clause_type.value.replace('_', ' ')} clause",
                ))

        return risks

    def _detect_with_llm(self, clauses: list[Clause]) -> list[Risk]:
        """Detect risks using Claude LLM for deeper analysis."""
        assert self._client is not None

        clauses_text = "\n\n".join(
            f"[{c.clause_type.value}] {c.title}\n{c.text}" for c in clauses
        )

        message = self._client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": (
                    "Analyze the following contract clauses for risks and unfavorable terms. "
                    "For each risk found, assign a severity: low, medium, high, or critical.\n\n"
                    "Return a JSON array of objects with keys: "
                    '"clause_type", "severity", "description", "clause_text", "recommendation".\n\n'
                    "Return ONLY valid JSON.\n\n"
                    f"CLAUSES:\n{clauses_text}"
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
            return self._detect_with_rules(clauses)

        risks: list[Risk] = []
        for item in data:
            try:
                ct = ClauseType(item["clause_type"])
            except ValueError:
                ct = ClauseType.UNKNOWN
            try:
                sev = Severity(item["severity"])
            except ValueError:
                sev = Severity.MEDIUM
            risks.append(Risk(
                clause_type=ct,
                severity=sev,
                description=item.get("description", ""),
                clause_text=item.get("clause_text", "")[:500],
                recommendation=item.get("recommendation", ""),
            ))

        return risks
