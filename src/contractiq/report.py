"""Report generation for contract reviews."""

from __future__ import annotations

import json
from typing import TextIO

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from contractiq.models import ReviewReport, Severity


_SEVERITY_COLORS = {
    Severity.LOW: "green",
    Severity.MEDIUM: "yellow",
    Severity.HIGH: "red",
    Severity.CRITICAL: "bold red",
}

_SEVERITY_ICONS = {
    Severity.LOW: "[LOW]",
    Severity.MEDIUM: "[MED]",
    Severity.HIGH: "[HIGH]",
    Severity.CRITICAL: "[CRIT]",
}


def render_report(report: ReviewReport, console: Console | None = None) -> None:
    """Render a review report to the terminal using Rich.

    Args:
        report: The review report to display.
        console: Optional Rich console instance.
    """
    console = console or Console()

    # Header
    score = report.overall_score
    if score >= 80:
        score_color = "green"
    elif score >= 60:
        score_color = "yellow"
    else:
        score_color = "red"

    header = Text()
    header.append("ContractIQ Review Report\n", style="bold")
    header.append(f"File: {report.contract.filename}\n")
    header.append(f"Score: ", style="bold")
    header.append(f"{score}/100", style=f"bold {score_color}")
    console.print(Panel(header, title="ContractIQ", border_style="blue"))

    # Summary
    console.print(Panel(report.summary, title="Summary", border_style="cyan"))

    # Recommendation
    console.print(Panel(report.recommendation, title="Recommendation", border_style=score_color))

    # Clauses table
    if report.contract.clauses:
        clause_table = Table(title="Extracted Clauses", show_lines=True)
        clause_table.add_column("#", width=4)
        clause_table.add_column("Type", min_width=20)
        clause_table.add_column("Title", min_width=15)
        clause_table.add_column("Preview", min_width=40)

        for i, clause in enumerate(report.contract.clauses, 1):
            preview = clause.text[:100].replace("\n", " ")
            if len(clause.text) > 100:
                preview += "..."
            clause_table.add_row(
                str(i),
                clause.clause_type.value.replace("_", " ").title(),
                clause.label,
                preview,
            )
        console.print(clause_table)

    # Risks table
    if report.risks:
        risk_table = Table(title="Detected Risks", show_lines=True)
        risk_table.add_column("Severity", width=10)
        risk_table.add_column("Clause", min_width=18)
        risk_table.add_column("Description", min_width=30)
        risk_table.add_column("Recommendation", min_width=30)

        # Sort by severity (critical first)
        severity_order = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2, Severity.LOW: 3}
        sorted_risks = sorted(report.risks, key=lambda r: severity_order.get(r.severity, 4))

        for risk in sorted_risks:
            color = _SEVERITY_COLORS[risk.severity]
            risk_table.add_row(
                Text(_SEVERITY_ICONS[risk.severity], style=color),
                risk.clause_type.value.replace("_", " ").title(),
                risk.description,
                risk.recommendation,
            )
        console.print(risk_table)

    # Suggestions table
    if report.suggestions:
        sugg_table = Table(title="Suggested Modifications", show_lines=True)
        sugg_table.add_column("Priority", width=10)
        sugg_table.add_column("Clause", min_width=18)
        sugg_table.add_column("Rationale", min_width=25)
        sugg_table.add_column("Suggested Language", min_width=35)

        for sugg in report.suggestions:
            color = _SEVERITY_COLORS.get(sugg.priority, "white")
            sugg_table.add_row(
                Text(sugg.priority.value.upper(), style=color),
                sugg.clause_type.value.replace("_", " ").title(),
                sugg.rationale,
                sugg.suggested_text[:200] + ("..." if len(sugg.suggested_text) > 200 else ""),
            )
        console.print(sugg_table)

    # Comparisons
    if report.comparisons:
        comp_table = Table(title="Template Comparisons", show_lines=True)
        comp_table.add_column("Clause", min_width=18)
        comp_table.add_column("Similarity", width=12)
        comp_table.add_column("Deviations", min_width=25)
        comp_table.add_column("Missing Protections", min_width=25)

        for comp in report.comparisons:
            sim = comp.similarity_score
            if sim >= 0.8:
                sim_style = "green"
            elif sim >= 0.5:
                sim_style = "yellow"
            else:
                sim_style = "red"

            comp_table.add_row(
                comp.clause_type.value.replace("_", " ").title(),
                Text(f"{sim:.0%}", style=sim_style),
                "\n".join(comp.deviations) if comp.deviations else "None",
                "\n".join(comp.missing_protections) if comp.missing_protections else "None",
            )
        console.print(comp_table)


def export_json(report: ReviewReport, output: TextIO | None = None) -> str:
    """Export a review report as JSON.

    Args:
        report: The review report to export.
        output: Optional file handle to write to.

    Returns:
        JSON string of the report.
    """
    data = {
        "filename": report.contract.filename,
        "word_count": report.contract.word_count,
        "overall_score": report.overall_score,
        "summary": report.summary,
        "recommendation": report.recommendation,
        "clauses": [
            {
                "type": c.clause_type.value,
                "title": c.label,
                "text_preview": c.text[:200],
            }
            for c in report.contract.clauses
        ],
        "risks": [
            {
                "severity": r.severity.value,
                "clause_type": r.clause_type.value,
                "description": r.description,
                "recommendation": r.recommendation,
            }
            for r in report.risks
        ],
        "suggestions": [
            {
                "priority": s.priority.value,
                "clause_type": s.clause_type.value,
                "rationale": s.rationale,
                "suggested_text": s.suggested_text,
            }
            for s in report.suggestions
        ],
        "comparisons": [
            {
                "clause_type": c.clause_type.value,
                "similarity_score": c.similarity_score,
                "deviations": c.deviations,
                "missing_protections": c.missing_protections,
            }
            for c in report.comparisons
        ],
        "risk_counts": report.risk_counts,
    }

    json_str = json.dumps(data, indent=2)

    if output:
        output.write(json_str)

    return json_str
