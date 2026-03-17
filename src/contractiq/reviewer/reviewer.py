"""Contract review orchestrator."""

from __future__ import annotations

import anthropic

from contractiq.analyzer.clause_extractor import ClauseExtractor
from contractiq.analyzer.comparison import ContractComparator
from contractiq.analyzer.risk_detector import RiskDetector
from contractiq.models import Contract, ReviewReport
from contractiq.reviewer.score import ContractScorer
from contractiq.reviewer.suggestions import SuggestionEngine


class ContractReviewer:
    """Orchestrates a full contract review.

    Coordinates clause extraction, risk detection, template comparison,
    suggestion generation, and scoring into a unified review pipeline.
    """

    def __init__(
        self,
        api_key: str | None = None,
        use_llm: bool = False,
    ) -> None:
        """Initialize the reviewer.

        Args:
            api_key: Anthropic API key. If None, uses ANTHROPIC_API_KEY env var.
            use_llm: Whether to use LLM for analysis (requires API key).
        """
        self.use_llm = use_llm
        self._client: anthropic.Anthropic | None = None

        if use_llm:
            self._client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

        self.extractor = ClauseExtractor(client=self._client)
        self.risk_detector = RiskDetector(client=self._client)
        self.comparator = ContractComparator(client=self._client)
        self.suggestion_engine = SuggestionEngine(client=self._client)
        self.scorer = ContractScorer()

    def review(self, contract: Contract) -> ReviewReport:
        """Perform a full contract review.

        Args:
            contract: The contract to review.

        Returns:
            A complete review report.
        """
        # Step 1: Extract clauses
        clauses = self.extractor.extract(contract, use_llm=self.use_llm)

        # Step 2: Detect risks
        risks = self.risk_detector.detect(clauses, use_llm=self.use_llm)

        # Step 3: Compare against templates
        comparisons = self.comparator.compare(clauses, use_llm=self.use_llm)

        # Step 4: Generate suggestions
        suggestions = self.suggestion_engine.suggest(
            clauses, risks, use_llm=self.use_llm
        )

        # Step 5: Compute score
        score = self.scorer.score(clauses, risks, comparisons)
        grade = self.scorer.get_grade(score)
        recommendation = self.scorer.get_recommendation(score, risks)

        # Step 6: Build summary
        summary = self._build_summary(contract, clauses, risks, score, grade)

        return ReviewReport(
            contract=contract,
            risks=risks,
            suggestions=suggestions,
            comparisons=comparisons,
            overall_score=score,
            summary=summary,
            recommendation=recommendation,
        )

    def review_text(self, text: str, filename: str = "contract.txt") -> ReviewReport:
        """Convenience method to review raw contract text.

        Args:
            text: Raw contract text.
            filename: Optional filename for the report.

        Returns:
            A complete review report.
        """
        contract = Contract(filename=filename, raw_text=text)
        return self.review(contract)

    def _build_summary(self, contract, clauses, risks, score, grade) -> str:
        """Build a human-readable summary."""
        risk_counts = {}
        for r in risks:
            risk_counts[r.severity.value] = risk_counts.get(r.severity.value, 0) + 1

        lines = [
            f"Contract Review Summary for: {contract.filename}",
            f"Word count: {contract.word_count:,}",
            f"Clauses identified: {len(clauses)}",
            f"Risks detected: {len(risks)}",
        ]

        if risk_counts:
            breakdown = ", ".join(f"{v} {k}" for k, v in sorted(risk_counts.items()))
            lines.append(f"Risk breakdown: {breakdown}")

        lines.append(f"Overall Score: {score}/100 (Grade: {grade})")

        return "\n".join(lines)
