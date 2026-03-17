"""Tests for report generation."""

import json

from contractiq.models import (
    Clause,
    ClauseType,
    Contract,
    ReviewReport,
    Risk,
    Severity,
    Suggestion,
)
from contractiq.report import export_json, render_report


class TestExportJson:
    def test_export_produces_valid_json(self):
        report = ReviewReport(
            contract=Contract(
                filename="test.txt",
                raw_text="sample text",
                clauses=[
                    Clause(clause_type=ClauseType.PAYMENT, title="Payment", text="Pay now."),
                ],
            ),
            risks=[
                Risk(
                    clause_type=ClauseType.PAYMENT,
                    severity=Severity.HIGH,
                    description="Risk found",
                    recommendation="Fix it",
                ),
            ],
            suggestions=[
                Suggestion(
                    clause_type=ClauseType.PAYMENT,
                    original_text="old",
                    suggested_text="new",
                    rationale="better",
                ),
            ],
            overall_score=65.0,
            summary="Test summary",
            recommendation="Test recommendation",
        )
        json_str = export_json(report)
        data = json.loads(json_str)
        assert data["filename"] == "test.txt"
        assert data["overall_score"] == 65.0
        assert len(data["risks"]) == 1
        assert len(data["suggestions"]) == 1
        assert len(data["clauses"]) == 1

    def test_export_empty_report(self):
        report = ReviewReport(contract=Contract(raw_text="text"))
        json_str = export_json(report)
        data = json.loads(json_str)
        assert data["risks"] == []
        assert data["suggestions"] == []


class TestRenderReport:
    def test_render_does_not_raise(self):
        """Smoke test: rendering should not crash."""
        from rich.console import Console
        import io

        report = ReviewReport(
            contract=Contract(
                filename="test.txt",
                raw_text="sample text",
                clauses=[
                    Clause(clause_type=ClauseType.PAYMENT, title="Payment", text="Pay now."),
                ],
            ),
            risks=[
                Risk(
                    clause_type=ClauseType.PAYMENT,
                    severity=Severity.HIGH,
                    description="Risk",
                    recommendation="Fix",
                ),
            ],
            overall_score=70.0,
            summary="Summary",
            recommendation="Recommendation",
        )
        console = Console(file=io.StringIO(), force_terminal=True)
        render_report(report, console=console)
        output = console.file.getvalue()
        assert "ContractIQ" in output
