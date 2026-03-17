"""Tests for RiskDetector."""

from contractiq.analyzer.risk_detector import RiskDetector
from contractiq.models import Clause, ClauseType, Severity


class TestRiskDetector:
    def setup_method(self):
        self.detector = RiskDetector()

    def test_detect_unilateral_termination(self):
        clause = Clause(
            clause_type=ClauseType.TERMINATION,
            text="Provider may terminate this Agreement at any time without notice.",
        )
        risks = self.detector.detect_clause(clause)
        assert len(risks) >= 1
        assert any(r.severity in (Severity.HIGH, Severity.CRITICAL) for r in risks)

    def test_detect_unlimited_liability(self):
        clause = Clause(
            clause_type=ClauseType.LIMITATION_OF_LIABILITY,
            text="There shall be no limitation on liability under this agreement.",
        )
        risks = self.detector.detect_clause(clause)
        assert len(risks) >= 1
        assert any(r.severity == Severity.CRITICAL for r in risks)

    def test_detect_short_payment_terms(self):
        clause = Clause(
            clause_type=ClauseType.PAYMENT,
            text="All invoices are due upon receipt within 5 days of invoice.",
        )
        risks = self.detector.detect_clause(clause)
        assert len(risks) >= 1

    def test_detect_jury_trial_waiver(self):
        clause = Clause(
            clause_type=ClauseType.GOVERNING_LAW,
            text="Each party waives the right to a jury trial.",
        )
        risks = self.detector.detect_clause(clause)
        assert len(risks) >= 1
        assert any("jury" in r.description.lower() for r in risks)

    def test_detect_sole_discretion(self):
        clause = Clause(
            clause_type=ClauseType.TERMINATION,
            text="Provider may, at its sole discretion, modify the terms.",
        )
        risks = self.detector.detect_clause(clause)
        assert any("sole discretion" in r.description.lower() for r in risks)

    def test_detect_missing_clauses(self):
        # Empty clause list -- should flag missing critical clauses
        risks = self.detector.detect([])
        assert len(risks) >= 3  # At least liability, confidentiality, termination

    def test_no_false_positive_on_safe_clause(self):
        clause = Clause(
            clause_type=ClauseType.CONFIDENTIALITY,
            text=(
                "Confidential Information shall be protected with reasonable care "
                "and not disclosed to third parties for a period of three years."
            ),
        )
        risks = self.detector.detect_clause(clause)
        assert len(risks) == 0

    def test_detect_broad_indemnification(self):
        clause = Clause(
            clause_type=ClauseType.INDEMNIFICATION,
            text=(
                "Client shall indemnify Provider against any and all claims, "
                "damages, losses arising from any cause."
            ),
        )
        risks = self.detector.detect_clause(clause)
        assert len(risks) >= 1

    def test_detect_long_non_compete(self):
        clause = Clause(
            clause_type=ClauseType.NON_COMPETE,
            text="Non-compete restriction applies for 36 months after termination.",
        )
        risks = self.detector.detect_clause(clause)
        assert len(risks) >= 1
        assert any(r.severity == Severity.HIGH for r in risks)
