"""ContractIQ CLI interface."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from contractiq.models import Contract
from contractiq.report import export_json, render_report
from contractiq.reviewer.reviewer import ContractReviewer
from contractiq.templates.standard import list_templates

console = Console()


def _read_contract(file: str) -> Contract:
    """Read a contract file and return a Contract model."""
    path = Path(file)
    if not path.exists():
        console.print(f"[red]Error: File not found: {file}[/red]")
        sys.exit(1)
    text = path.read_text(encoding="utf-8")
    return Contract(filename=path.name, raw_text=text)


@click.group()
@click.version_option(package_name="contractiq")
def cli() -> None:
    """ContractIQ -- AI-powered contract review and risk analysis."""


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--llm", is_flag=True, help="Use Claude LLM for deeper analysis")
@click.option("--api-key", envvar="ANTHROPIC_API_KEY", help="Anthropic API key")
@click.option("--format", "fmt", type=click.Choice(["rich", "json"]), default="rich")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def review(file: str, llm: bool, api_key: str | None, fmt: str, output: str | None) -> None:
    """Perform a full contract review."""
    contract = _read_contract(file)

    with console.status("[bold blue]Analyzing contract..."):
        reviewer = ContractReviewer(api_key=api_key, use_llm=llm)
        report = reviewer.review(contract)

    if fmt == "json":
        if output:
            with open(output, "w") as f:
                export_json(report, f)
            console.print(f"[green]Report saved to {output}[/green]")
        else:
            json_str = export_json(report)
            console.print(json_str)
    else:
        render_report(report, console)
        if output:
            with open(output, "w") as f:
                export_json(report, f)
            console.print(f"\n[green]JSON report also saved to {output}[/green]")


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--llm", is_flag=True, help="Use Claude LLM for extraction")
@click.option("--api-key", envvar="ANTHROPIC_API_KEY", help="Anthropic API key")
def extract(file: str, llm: bool, api_key: str | None) -> None:
    """Extract and classify clauses from a contract."""
    contract = _read_contract(file)

    from contractiq.analyzer.clause_extractor import ClauseExtractor
    import anthropic as anthropic_mod

    client = None
    if llm and api_key:
        client = anthropic_mod.Anthropic(api_key=api_key)

    extractor = ClauseExtractor(client=client)

    with console.status("[bold blue]Extracting clauses..."):
        clauses = extractor.extract(contract, use_llm=llm)

    table = Table(title=f"Clauses in {contract.filename}", show_lines=True)
    table.add_column("#", width=4)
    table.add_column("Type", min_width=20)
    table.add_column("Title", min_width=15)
    table.add_column("Preview", min_width=50)

    for i, clause in enumerate(clauses, 1):
        preview = clause.text[:120].replace("\n", " ")
        if len(clause.text) > 120:
            preview += "..."
        table.add_row(
            str(i),
            clause.clause_type.value.replace("_", " ").title(),
            clause.label,
            preview,
        )

    console.print(table)
    console.print(f"\n[bold]{len(clauses)}[/bold] clause(s) extracted.")


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--llm", is_flag=True, help="Use Claude LLM for comparison")
@click.option("--api-key", envvar="ANTHROPIC_API_KEY", help="Anthropic API key")
def compare(file: str, llm: bool, api_key: str | None) -> None:
    """Compare contract clauses against standard templates."""
    contract = _read_contract(file)

    import anthropic as anthropic_mod
    from contractiq.analyzer.clause_extractor import ClauseExtractor
    from contractiq.analyzer.comparison import ContractComparator

    client = None
    if llm and api_key:
        client = anthropic_mod.Anthropic(api_key=api_key)

    extractor = ClauseExtractor(client=client)
    comparator = ContractComparator(client=client)

    with console.status("[bold blue]Comparing against templates..."):
        clauses = extractor.extract(contract, use_llm=llm)
        results = comparator.compare(clauses, use_llm=llm)

    table = Table(title="Template Comparison Results", show_lines=True)
    table.add_column("Clause", min_width=18)
    table.add_column("Similarity", width=12)
    table.add_column("Deviations", min_width=30)
    table.add_column("Missing Protections", min_width=30)

    for comp in results:
        sim = comp.similarity_score
        if sim >= 0.8:
            sim_str = f"[green]{sim:.0%}[/green]"
        elif sim >= 0.5:
            sim_str = f"[yellow]{sim:.0%}[/yellow]"
        else:
            sim_str = f"[red]{sim:.0%}[/red]"

        table.add_row(
            comp.clause_type.value.replace("_", " ").title(),
            sim_str,
            "\n".join(comp.deviations) if comp.deviations else "[green]None[/green]",
            "\n".join(comp.missing_protections) if comp.missing_protections else "[green]None[/green]",
        )

    console.print(table)


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["rich", "json"]), default="rich")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--llm", is_flag=True, help="Use Claude LLM for analysis")
@click.option("--api-key", envvar="ANTHROPIC_API_KEY", help="Anthropic API key")
def report(file: str, fmt: str, output: str | None, llm: bool, api_key: str | None) -> None:
    """Generate a full risk report."""
    contract = _read_contract(file)

    with console.status("[bold blue]Generating report..."):
        reviewer = ContractReviewer(api_key=api_key, use_llm=llm)
        review_report = reviewer.review(contract)

    if fmt == "json":
        if output:
            with open(output, "w") as f:
                export_json(review_report, f)
            console.print(f"[green]Report saved to {output}[/green]")
        else:
            json_str = export_json(review_report)
            console.print(json_str)
    else:
        render_report(review_report, console)


@cli.command("templates")
def list_templates_cmd() -> None:
    """List all available standard clause templates."""
    templates = list_templates()

    table = Table(title="Standard Clause Templates", show_lines=True)
    table.add_column("#", width=4)
    table.add_column("Clause Type", min_width=22)
    table.add_column("Name", min_width=18)
    table.add_column("Description", min_width=35)
    table.add_column("Key Elements", min_width=30)

    for i, tmpl in enumerate(templates, 1):
        table.add_row(
            str(i),
            tmpl["clause_type"].replace("_", " ").title(),
            tmpl["name"],
            tmpl["description"],
            tmpl["key_elements"],
        )

    console.print(table)
    console.print(f"\n[bold]{len(templates)}[/bold] template(s) available.")


if __name__ == "__main__":
    cli()
