"""Tests for ContractScorer."""

from contractiq.models import Clause, ClauseType, ComparisonResult, Risk, Severity
from contractiq.reviewer.score import ContractScorer


class TestContractScorer:
    def setup_method(self):
        self.scorer = ContractScorer()

    def test_perfect_score_no_risks(self):
        clauses = [
            Clause(clause_type=ct, text="clause text")
            for ct in ContractScorer.CRITICAL_CLAUSES
        ]
        score = self.scorer.score(clauses, risks=[])
        assert score >= 80.0

    def test_zero_score_all_critical_risks(self):
        clauses = [Clause(clause_type=ClauseType.PAYMENT, text="text")]
        risks = [
            Risk(clause_type=ClauseType.PAYMENT, severity=Severity.CRITICAL, description=f"risk {i}")
            for i in range(10)
        ]
        score = self.scorer.score(clauses, risks)
        assert score < 30.0

    def test_missing_clauses_lower_score(self):
        # No critical clauses present
        clauses = [Clause(clause_type=ClauseType.PARTIES, text="text")]
        score_missing = self.scorer.score(clauses, risks=[])

        # All critical clauses present
        clauses_full = [Clause(clause_type=ct, text="text") for ct in ContractScorer.CRITICAL_CLAUSES]
        score_full = self.scorer.score(clauses_full, risks=[])

        assert score_full > score_missing

    def test_grade_a(self):
        assert self.scorer.get_grade(95.0) == "A"

    def test_grade_f(self):
        assert self.scorer.get_grade(50.0) == "F"

    def test_recommendation_critical(self):
        risks = [Risk(clause_type=ClauseType.PAYMENT, severity=Severity.CRITICAL, description="bad")]
        rec = self.scorer.get_recommendation(30.0, risks)
        assert "URGENT" in rec

    def test_recommendation_low_risk(self):
        rec = self.scorer.get_recommendation(90.0, [])
        assert "LOW RISK" in rec

    def test_comparison_affects_score(self):
        clauses = [Clause(clause_type=ct, text="text") for ct in ContractScorer.CRITICAL_CLAUSES]

        good_comparisons = [
            ComparisonResult(
                clause_type=ClauseType.PAYMENT,
                contract_text="text",
                template_text="template",
                similarity_score=0.95,
            ),
        ]
        bad_comparisons = [
            ComparisonResult(
                clause_type=ClauseType.PAYMENT,
                contract_text="text",
                template_text="template",
                similarity_score=0.1,
                deviations=["bad1", "bad2", "bad3"],
            ),
        ]

        score_good = self.scorer.score(clauses, [], good_comparisons)
        score_bad = self.scorer.score(clauses, [], bad_comparisons)
        assert score_good > score_bad
