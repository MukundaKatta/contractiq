"""Tests for SuggestionEngine."""

from contractiq.models import Clause, ClauseType, Risk, Severity
from contractiq.reviewer.suggestions import SuggestionEngine


class TestSuggestionEngine:
    def setup_method(self):
        self.engine = SuggestionEngine()

    def test_suggest_for_unilateral_termination(self):
        clauses = [
            Clause(
                clause_type=ClauseType.TERMINATION,
                text="Provider may terminate immediately without cause or notice.",
            ),
        ]
        risks = [
            Risk(
                clause_type=ClauseType.TERMINATION,
                severity=Severity.HIGH,
                description="Unilateral termination",
            ),
        ]
        suggestions = self.engine.suggest(clauses, risks)
        assert len(suggestions) >= 1
        assert suggestions[0].clause_type == ClauseType.TERMINATION

    def test_suggest_for_unlimited_liability(self):
        clauses = [
            Clause(
                clause_type=ClauseType.LIMITATION_OF_LIABILITY,
                text="There is no limitation on liability. Unlimited liability applies.",
            ),
        ]
        risks = [
            Risk(
                clause_type=ClauseType.LIMITATION_OF_LIABILITY,
                severity=Severity.CRITICAL,
                description="No liability cap",
            ),
        ]
        suggestions = self.engine.suggest(clauses, risks)
        assert len(suggestions) >= 1
        assert any("liability" in s.suggested_text.lower() for s in suggestions)

    def test_suggest_for_missing_clause(self):
        clauses: list[Clause] = []
        risks = [
            Risk(
                clause_type=ClauseType.CONFIDENTIALITY,
                severity=Severity.HIGH,
                description="No confidentiality clause found",
            ),
        ]
        suggestions = self.engine.suggest(clauses, risks)
        assert len(suggestions) >= 1
        assert suggestions[0].original_text == "[MISSING]"

    def test_no_suggestions_for_safe_contract(self):
        clauses = [
            Clause(
                clause_type=ClauseType.CONFIDENTIALITY,
                text="Standard confidentiality with 3-year survival period.",
            ),
        ]
        # No risks = likely no suggestions triggered
        suggestions = self.engine.suggest(clauses, risks=[])
        assert len(suggestions) == 0

    def test_suggest_for_short_payment(self):
        clauses = [
            Clause(
                clause_type=ClauseType.PAYMENT,
                text="All invoices are due upon receipt within 5 days.",
            ),
        ]
        risks = [
            Risk(
                clause_type=ClauseType.PAYMENT,
                severity=Severity.LOW,
                description="Short payment window",
            ),
        ]
        suggestions = self.engine.suggest(clauses, risks)
        assert len(suggestions) >= 1
