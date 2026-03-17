"""Clause extraction from contract text."""

from __future__ import annotations

import json
import re

import anthropic

from contractiq.models import Clause, ClauseType, Contract


# Regex patterns for common section headings
_SECTION_PATTERNS: dict[ClauseType, list[str]] = {
    ClauseType.PARTIES: [
        r"(?i)\b(parties|recitals|between)\b",
    ],
    ClauseType.TERM: [
        r"(?i)\b(term|duration|effective\s+date|commencement)\b",
    ],
    ClauseType.PAYMENT: [
        r"(?i)\b(payment|fees|compensation|pricing|invoic)\b",
    ],
    ClauseType.TERMINATION: [
        r"(?i)\b(terminat|cancel|expir)\b",
    ],
    ClauseType.IP: [
        r"(?i)\b(intellectual\s+property|ip\s+rights|ownership|copyright|patent|trademark)\b",
    ],
    ClauseType.CONFIDENTIALITY: [
        r"(?i)\b(confidential|non-disclosure|nda|proprietary\s+information)\b",
    ],
    ClauseType.INDEMNIFICATION: [
        r"(?i)\b(indemnif|hold\s+harmless)\b",
    ],
    ClauseType.LIMITATION_OF_LIABILITY: [
        r"(?i)\b(limitation\s+of\s+liability|liability\s+cap|limit.{0,15}liab)\b",
    ],
    ClauseType.GOVERNING_LAW: [
        r"(?i)\b(governing\s+law|jurisdiction|dispute\s+resolution|arbitrat|choice\s+of\s+law)\b",
    ],
    ClauseType.FORCE_MAJEURE: [
        r"(?i)\b(force\s+majeure|act.{0,5}of\s+god|unforeseeable)\b",
    ],
}


class ClauseExtractor:
    """Extracts and classifies clauses from contract text.

    Supports two modes:
    - Pattern-based extraction using regex (no API key needed)
    - LLM-powered extraction using Claude for higher accuracy
    """

    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        self._client = client

    def extract(self, contract: Contract, use_llm: bool = False) -> list[Clause]:
        """Extract clauses from a contract.

        Args:
            contract: The contract to analyze.
            use_llm: If True, use Claude for extraction. Otherwise use regex.

        Returns:
            List of extracted clauses.
        """
        if use_llm and self._client:
            clauses = self._extract_with_llm(contract.raw_text)
        else:
            clauses = self._extract_with_patterns(contract.raw_text)
        contract.clauses = clauses
        return clauses

    def _extract_with_patterns(self, text: str) -> list[Clause]:
        """Extract clauses using regex pattern matching on section headings."""
        sections = self._split_into_sections(text)
        clauses: list[Clause] = []

        for title, body, start, end in sections:
            clause_type = self._classify_section(title, body)
            clauses.append(Clause(
                clause_type=clause_type,
                title=title.strip(),
                text=body.strip(),
                start_position=start,
                end_position=end,
            ))

        return clauses

    def _split_into_sections(self, text: str) -> list[tuple[str, str, int, int]]:
        """Split contract text into sections based on headings.

        Returns list of (title, body, start_pos, end_pos).
        """
        # Match numbered sections like "1.", "1.1", "Section 1", "ARTICLE I"
        # or standalone uppercase headings
        heading_pattern = re.compile(
            r"^(?:"
            r"(?:Section|Article|SECTION|ARTICLE)\s+[\dIVXivx]+[.\s]+"
            r"|[\d]+(?:\.[\d]+)*[.\s]+"
            r"|[A-Z][A-Z\s]{2,}(?:\n|$)"
            r")",
            re.MULTILINE,
        )

        matches = list(heading_pattern.finditer(text))
        if not matches:
            # No clear sections found; treat the whole text as one block
            return [("Full Contract", text, 0, len(text))]

        sections: list[tuple[str, str, int, int]] = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            heading = match.group().strip().rstrip(".")
            body = text[match.end():end]
            sections.append((heading, body, start, end))

        return sections

    def _classify_section(self, title: str, body: str) -> ClauseType:
        """Classify a section into a clause type using pattern matching."""
        combined = f"{title} {body[:500]}"
        best_type = ClauseType.UNKNOWN
        best_score = 0

        for clause_type, patterns in _SECTION_PATTERNS.items():
            score = 0
            for pattern in patterns:
                title_matches = len(re.findall(pattern, title))
                body_matches = len(re.findall(pattern, combined))
                # Title matches are weighted more heavily
                score += title_matches * 3 + body_matches
            if score > best_score:
                best_score = score
                best_type = clause_type

        return best_type

    def _extract_with_llm(self, text: str) -> list[Clause]:
        """Extract clauses using Claude LLM for higher accuracy."""
        assert self._client is not None

        clause_types_str = ", ".join(ct.value for ct in ClauseType if ct != ClauseType.UNKNOWN)

        message = self._client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": (
                    "Analyze the following contract and extract all clauses. "
                    f"Classify each clause into one of these types: {clause_types_str}. "
                    "Return a JSON array of objects with keys: "
                    '"clause_type", "title", "text" (the clause text verbatim from the contract).\n\n'
                    "Return ONLY valid JSON, no other text.\n\n"
                    f"CONTRACT:\n{text}"
                ),
            }],
        )

        response_text = message.content[0].text.strip()
        # Strip markdown code fences if present
        if response_text.startswith("```"):
            response_text = re.sub(r"^```\w*\n?", "", response_text)
            response_text = re.sub(r"\n?```$", "", response_text)

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            return self._extract_with_patterns(text)

        clauses: list[Clause] = []
        for item in data:
            try:
                ct = ClauseType(item["clause_type"])
            except ValueError:
                ct = ClauseType.UNKNOWN
            clauses.append(Clause(
                clause_type=ct,
                title=item.get("title", ""),
                text=item.get("text", ""),
            ))

        return clauses
