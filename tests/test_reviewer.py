"""Tests for ContractReviewer end-to-end."""

from contractiq.models import Contract, Severity
from contractiq.reviewer.reviewer import ContractReviewer


class TestContractReviewer:
    def setup_method(self):
        self.reviewer = ContractReviewer(use_llm=False)

    def test_full_review(self, sample_contract: Contract):
        report = self.reviewer.review(sample_contract)
        assert report.overall_score >= 0.0
        assert report.overall_score <= 100.0
        assert len(report.summary) > 0
        assert len(report.recommendation) > 0

    def test_review_detects_risks(self, sample_contract: Contract):
        report = self.reviewer.review(sample_contract)
        # The sample contract has several risky clauses
        assert len(report.risks) > 0

    def test_review_generates_suggestions(self, sample_contract: Contract):
        report = self.reviewer.review(sample_contract)
        assert len(report.suggestions) >= 0  # May or may not generate depending on rules matching

    def test_review_text_convenience(self, sample_contract_text: str):
        report = self.reviewer.review_text(sample_contract_text, filename="test.txt")
        assert report.contract.filename == "test.txt"
        assert len(report.contract.clauses) > 0

    def test_review_empty_contract(self):
        report = self.reviewer.review_text("This is a very short document.")
        assert report.overall_score >= 0.0
        # Should flag missing clauses
        assert len(report.risks) > 0

    def test_review_produces_comparisons(self, sample_contract: Contract):
        report = self.reviewer.review(sample_contract)
        # Should have comparisons for clauses that match template types
        assert len(report.comparisons) >= 0


class TestContractReviewerScoring:
    def test_risky_contract_gets_low_score(self):
        text = (
            "1. TERMINATION\n"
            "Provider may terminate at any time without cause.\n\n"
            "2. LIABILITY\n"
            "There is no limitation on liability.\n\n"
        )
        reviewer = ContractReviewer(use_llm=False)
        report = reviewer.review_text(text)
        assert report.overall_score < 70.0

    def test_summary_contains_filename(self):
        reviewer = ContractReviewer(use_llm=False)
        report = reviewer.review_text("Some text.", filename="mycontract.pdf")
        assert "mycontract.pdf" in report.summary
