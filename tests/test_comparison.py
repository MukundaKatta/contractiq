"""Tests for ContractComparator."""

from contractiq.analyzer.comparison import ContractComparator
from contractiq.models import Clause, ClauseType


class TestContractComparator:
    def setup_method(self):
        self.comparator = ContractComparator()

    def test_compare_termination_clause(self):
        clauses = [
            Clause(
                clause_type=ClauseType.TERMINATION,
                text=(
                    "Either Party may terminate this Agreement for convenience upon "
                    "30 days prior written notice. For cause, the breaching Party "
                    "shall have 30 days to cure after written notice. Sections 5 and 7 "
                    "shall survive termination."
                ),
            ),
        ]
        results = self.comparator.compare(clauses)
        assert len(results) == 1
        assert results[0].clause_type == ClauseType.TERMINATION
        assert 0.0 <= results[0].similarity_score <= 1.0

    def test_compare_skips_unknown_types(self):
        clauses = [
            Clause(clause_type=ClauseType.UNKNOWN, text="Random text."),
        ]
        results = self.comparator.compare(clauses)
        assert len(results) == 0

    def test_compare_detects_short_clause(self):
        clauses = [
            Clause(
                clause_type=ClauseType.CONFIDENTIALITY,
                text="Keep things confidential.",
            ),
        ]
        results = self.comparator.compare(clauses)
        assert len(results) == 1
        # Short clause should have deviations
        assert any("shorter" in d.lower() for d in results[0].deviations)

    def test_compare_detects_waiver(self):
        clauses = [
            Clause(
                clause_type=ClauseType.GOVERNING_LAW,
                text=(
                    "Governed by Delaware law. Client waives all rights and claims "
                    "related to dispute resolution."
                ),
            ),
        ]
        results = self.comparator.compare(clauses)
        assert len(results) == 1
        assert any("waiver" in d.lower() for d in results[0].deviations)

    def test_compare_multiple_clauses(self):
        clauses = [
            Clause(clause_type=ClauseType.PAYMENT, text="Pay within 30 days of invoice."),
            Clause(clause_type=ClauseType.TERM, text="Initial term of 12 months with auto-renewal."),
        ]
        results = self.comparator.compare(clauses)
        assert len(results) == 2
        types = {r.clause_type for r in results}
        assert ClauseType.PAYMENT in types
        assert ClauseType.TERM in types
