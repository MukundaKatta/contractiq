"""Shared test fixtures for ContractIQ."""

import pytest

from contractiq.models import Clause, ClauseType, Contract


SAMPLE_CONTRACT_TEXT = """\
SERVICES AGREEMENT

This Agreement is entered into as of January 1, 2026 by and between \
Acme Corporation, a Delaware corporation with its principal place of business \
at 123 Main St, Anytown, DE ("Provider"), and Beta Inc., a California \
corporation with its principal place of business at 456 Oak Ave, Somewhere, CA ("Client").

1. TERM AND DURATION

This Agreement shall commence on the Effective Date and continue for an \
initial term of twelve (12) months. This Agreement shall automatically renew \
for successive twelve-month periods unless either Party provides written notice \
of non-renewal at least thirty (30) days prior to the end of the then-current term.

2. PAYMENT TERMS

Client shall pay Provider the fees set forth in Exhibit A. All invoices are \
due and payable within thirty (30) days of the invoice date. Late payments \
shall accrue interest at 1.5% per month.

3. CONFIDENTIALITY

"Confidential Information" means all non-public information disclosed by \
either Party. The receiving Party shall use Confidential Information solely \
for purposes of this Agreement and protect it with reasonable care. These \
obligations shall survive for three (3) years following disclosure.

4. TERMINATION

Provider may terminate this Agreement immediately without cause or notice. \
Client has no right to cure any breach.

5. INTELLECTUAL PROPERTY

All intellectual property created under this Agreement, including all rights, \
title, and ownership, shall transfer entirely to Provider, including any \
pre-existing IP contributed by Client.

6. LIMITATION OF LIABILITY

There is no limitation on liability under this Agreement. Provider shall have \
unlimited liability for any and all claims.

7. INDEMNIFICATION

Client shall indemnify, defend, and hold harmless Provider from and against \
any and all claims, damages, losses, and expenses arising from any cause \
whatsoever related to this Agreement.

8. GOVERNING LAW

This Agreement shall be governed by the laws of the State of Delaware. \
Each Party hereby waives the right to a jury trial.

9. FORCE MAJEURE

Neither Party shall be liable for any failure or delay in performance due \
to causes beyond its reasonable control, including acts of God, war, \
terrorism, epidemics, or government actions. The affected Party shall \
provide prompt notice.

10. NON-COMPETE

During the Term and for a period of 36 months following termination, \
Client shall not engage in any business that competes with Provider \
within the United States.
"""


@pytest.fixture
def sample_contract_text() -> str:
    return SAMPLE_CONTRACT_TEXT


@pytest.fixture
def sample_contract(sample_contract_text: str) -> Contract:
    return Contract(filename="test_contract.txt", raw_text=sample_contract_text)


@pytest.fixture
def sample_clauses() -> list[Clause]:
    return [
        Clause(
            clause_type=ClauseType.PARTIES,
            title="Parties",
            text='This Agreement is entered into by Acme Corp ("Provider") and Beta Inc ("Client").',
        ),
        Clause(
            clause_type=ClauseType.TERMINATION,
            title="Termination",
            text="Provider may terminate this Agreement immediately without cause or notice.",
        ),
        Clause(
            clause_type=ClauseType.LIMITATION_OF_LIABILITY,
            title="Limitation of Liability",
            text="There is no limitation on liability. Provider shall have unlimited liability.",
        ),
        Clause(
            clause_type=ClauseType.CONFIDENTIALITY,
            title="Confidentiality",
            text="Confidential Information shall be protected with reasonable care for 3 years.",
        ),
        Clause(
            clause_type=ClauseType.PAYMENT,
            title="Payment",
            text="All invoices are due upon receipt within 5 days.",
        ),
        Clause(
            clause_type=ClauseType.GOVERNING_LAW,
            title="Governing Law",
            text="Governed by Delaware law. Each party waives the right to a jury trial.",
        ),
    ]
