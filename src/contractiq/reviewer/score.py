"""Contract risk scoring."""

from __future__ import annotations

from contractiq.models import (
    Clause,
    ClauseType,
    ComparisonResult,
    Risk,
    Severity,
)


class ContractScorer:
    """Computes an overall risk score for a contract.

    Score ranges from 0 (extremely risky) to 100 (very safe).
    The score is derived from:
    - Detected risks (weighted by severity)
    - Missing critical clauses
    - Template comparison similarity scores
    """

    # Weights for each scoring component
    RISK_WEIGHT = 0.50
    MISSING_CLAUSE_WEIGHT = 0.25
    COMPARISON_WEIGHT = 0.25

    # Critical clause types that should be present
    CRITICAL_CLAUSES = {
        ClauseType.TERMINATION,
        ClauseType.LIMITATION_OF_LIABILITY,
        ClauseType.CONFIDENTIALITY,
        ClauseType.GOVERNING_LAW,
        ClauseType.INDEMNIFICATION,
    }

    def score(
        self,
        clauses: list[Clause],
        risks: list[Risk],
        comparisons: list[ComparisonResult] | None = None,
    ) -> float:
        """Compute the overall contract risk score.

        Args:
            clauses: Extracted clauses.
            risks: Detected risks.
            comparisons: Template comparison results (optional).

        Returns:
            Score from 0.0 (worst) to 100.0 (best).
        """
        risk_score = self._score_risks(risks)
        missing_score = self._score_missing_clauses(clauses)
        comparison_score = self._score_comparisons(comparisons or [])

        overall = (
            risk_score * self.RISK_WEIGHT
            + missing_score * self.MISSING_CLAUSE_WEIGHT
            + comparison_score * self.COMPARISON_WEIGHT
        )

        return round(max(0.0, min(100.0, overall)), 1)

    def _score_risks(self, risks: list[Risk]) -> float:
        """Score based on detected risks. Starts at 100 and deducts."""
        if not risks:
            return 100.0

        total_penalty = sum(r.severity_weight for r in risks)
        # Cap penalty contribution so score doesn't go below 0
        # Each risk point removes ~3 points from the score
        penalty = min(100.0, total_penalty * 3.0)
        return max(0.0, 100.0 - penalty)

    def _score_missing_clauses(self, clauses: list[Clause]) -> float:
        """Score based on presence of critical clauses."""
        if not clauses:
            return 0.0

        present_types = {c.clause_type for c in clauses}
        found = sum(1 for ct in self.CRITICAL_CLAUSES if ct in present_types)
        return (found / len(self.CRITICAL_CLAUSES)) * 100.0

    def _score_comparisons(self, comparisons: list[ComparisonResult]) -> float:
        """Score based on template comparison similarity."""
        if not comparisons:
            return 50.0  # Neutral score when no comparisons available

        avg_similarity = sum(c.similarity_score for c in comparisons) / len(comparisons)
        # Penalize for deviations
        total_deviations = sum(len(c.deviations) for c in comparisons)
        deviation_penalty = min(30.0, total_deviations * 5.0)

        return max(0.0, avg_similarity * 100.0 - deviation_penalty)

    def get_grade(self, score: float) -> str:
        """Convert a numeric score to a letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def get_recommendation(self, score: float, risks: list[Risk]) -> str:
        """Generate a high-level recommendation based on the score."""
        critical_count = sum(1 for r in risks if r.severity == Severity.CRITICAL)
        high_count = sum(1 for r in risks if r.severity == Severity.HIGH)

        if critical_count > 0:
            return (
                f"URGENT: This contract has {critical_count} critical risk(s). "
                "Do not sign without legal counsel review and resolution of critical issues."
            )
        elif score < 60:
            return (
                f"HIGH RISK: This contract has {high_count} high-severity issue(s). "
                "Significant negotiation is recommended before signing."
            )
        elif score < 80:
            return (
                "MODERATE RISK: This contract has some areas of concern. "
                "Review the flagged issues and consider negotiating key terms."
            )
        else:
            return (
                "LOW RISK: This contract is generally well-balanced. "
                "Review any flagged items but overall terms are commercially reasonable."
            )
