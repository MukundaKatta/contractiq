"""Tests for ClauseExtractor."""

from contractiq.analyzer.clause_extractor import ClauseExtractor
from contractiq.models import ClauseType, Contract


class TestClauseExtractor:
    def setup_method(self):
        self.extractor = ClauseExtractor()

    def test_extract_from_numbered_sections(self, sample_contract: Contract):
        clauses = self.extractor.extract(sample_contract)
        assert len(clauses) > 0
        clause_types = {c.clause_type for c in clauses}
        # Should identify at least some key clause types
        assert len(clause_types) > 1

    def test_extract_identifies_termination(self, sample_contract: Contract):
        clauses = self.extractor.extract(sample_contract)
        termination_clauses = [c for c in clauses if c.clause_type == ClauseType.TERMINATION]
        assert len(termination_clauses) >= 1

    def test_extract_identifies_payment(self, sample_contract: Contract):
        clauses = self.extractor.extract(sample_contract)
        payment_clauses = [c for c in clauses if c.clause_type == ClauseType.PAYMENT]
        assert len(payment_clauses) >= 1

    def test_extract_identifies_confidentiality(self, sample_contract: Contract):
        clauses = self.extractor.extract(sample_contract)
        conf_clauses = [c for c in clauses if c.clause_type == ClauseType.CONFIDENTIALITY]
        assert len(conf_clauses) >= 1

    def test_extract_no_sections_returns_full_text(self):
        contract = Contract(raw_text="This is a simple paragraph with no section headings.")
        clauses = self.extractor.extract(contract)
        assert len(clauses) >= 1

    def test_extract_stores_clauses_on_contract(self, sample_contract: Contract):
        clauses = self.extractor.extract(sample_contract)
        assert sample_contract.clauses == clauses

    def test_classify_governing_law(self, sample_contract: Contract):
        clauses = self.extractor.extract(sample_contract)
        law_clauses = [c for c in clauses if c.clause_type == ClauseType.GOVERNING_LAW]
        assert len(law_clauses) >= 1
