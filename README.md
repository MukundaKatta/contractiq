# ContractIQ

AI-powered contract review and risk analysis tool.

ContractIQ analyzes legal contracts to extract clauses, detect risks, compare against standard templates, and generate actionable recommendations — all powered by Claude.

## Features

- **Clause Extraction** -- Identifies 10+ standard contract sections (parties, term, payment, termination, IP, confidentiality, indemnification, limitation of liability, governing law, force majeure)
- **Risk Detection** -- Flags unfavorable terms with severity levels (low, medium, high, critical)
- **Template Comparison** -- Compares contract clauses against industry-standard templates
- **AI-Powered Review** -- Orchestrates full contract review using Claude LLM
- **Suggestion Engine** -- Recommends specific clause modifications
- **Risk Scoring** -- Computes overall contract risk score (0-100)
- **Rich Reports** -- Generates detailed review reports in terminal or JSON

## Installation

```bash
pip install -e .
```

## Configuration

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Usage

### Review a contract

```bash
contractiq review contract.txt
```

### Extract clauses only

```bash
contractiq extract contract.txt
```

### Compare against a template

```bash
contractiq compare contract.txt --template standard_saas
```

### Generate a risk report

```bash
contractiq report contract.txt --format json --output report.json
```

### List available templates

```bash
contractiq templates
```

## Built-in Templates

ContractIQ ships with 12 standard clause templates covering:

- Parties, Term/Duration, Payment Terms
- Termination, Intellectual Property, Confidentiality
- Indemnification, Limitation of Liability
- Governing Law, Force Majeure
- Non-Compete, Data Protection

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Author

Mukunda Katta

## License

MIT
