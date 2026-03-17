"""Tests for ContractIQ models."""

from contractiq.models import (
    Clause,
    ClauseType,
    ComparisonResult,
    Contract,
    ReviewReport,
    Risk,
    Severity,
    Suggestion,
)


class TestClause:
    def test_create_clause(self):
        clause = Clause(
            clause_type=ClauseType.TERMINATION,
            title="Termination",
            text="Either party may terminate with 30 days notice.",
        )
        assert clause.clause_type == ClauseType.TERMINATION
        assert clause.title == "Termination"
        assert clause.label == "Termination"

    def test_label_fallback_to_clause_type(self):
        clause = Clause(clause_type=ClauseType.FORCE_MAJEURE, text="Force majeure clause.")
        assert clause.label == "Force Majeure"


class TestRisk:
    def test_severity_weight(self):
        risk = Risk(
            clause_type=ClauseType.TERMINATION,
            severity=Severity.CRITICAL,
            description="Critical risk",
        )
        assert risk.severity_weight == 10.0

    def test_severity_weight_low(self):
        risk = Risk(
            clause_type=ClauseType.PAYMENT,
            severity=Severity.LOW,
            description="Minor issue",
        )
        assert risk.severity_weight == 1.0


class TestContract:
    def test_word_count(self):
        contract = Contract(raw_text="This is a five word sentence right here now.")
        assert contract.word_count == 9

    def test_clause_map(self):
        contract = Contract(
            raw_text="text",
            clauses=[
                Clause(clause_type=ClauseType.PAYMENT, text="payment clause"),
                Clause(clause_type=ClauseType.PAYMENT, text="another payment"),
                Clause(clause_type=ClauseType.TERM, text="term clause"),
            ],
        )
        cmap = contract.clause_map
        assert len(cmap[ClauseType.PAYMENT]) == 2
        assert len(cmap[ClauseType.TERM]) == 1


class TestReviewReport:
    def test_risk_counts(self):
        report = ReviewReport(
            contract=Contract(raw_text="text"),
            risks=[
                Risk(clause_type=ClauseType.PAYMENT, severity=Severity.HIGH, description="a"),
                Risk(clause_type=ClauseType.TERM, severity=Severity.HIGH, description="b"),
                Risk(clause_type=ClauseType.IP, severity=Severity.LOW, description="c"),
            ],
        )
        assert report.risk_counts == {"high": 2, "low": 1}

    def test_critical_risks(self):
        report = ReviewReport(
            contract=Contract(raw_text="text"),
            risks=[
                Risk(clause_type=ClauseType.PAYMENT, severity=Severity.CRITICAL, description="a"),
                Risk(clause_type=ClauseType.TERM, severity=Severity.LOW, description="b"),
            ],
        )
        assert len(report.critical_risks) == 1
        assert len(report.high_risks) == 0


class TestSuggestion:
    def test_create_suggestion(self):
        sugg = Suggestion(
            clause_type=ClauseType.TERMINATION,
            original_text="old text",
            suggested_text="new text",
            rationale="better terms",
        )
        assert sugg.priority == Severity.MEDIUM


class TestComparisonResult:
    def test_similarity_bounds(self):
        result = ComparisonResult(
            clause_type=ClauseType.PAYMENT,
            contract_text="text",
            template_text="template",
            similarity_score=0.75,
        )
        assert 0.0 <= result.similarity_score <= 1.0
