"""Standard contract clause templates.

Contains 12 industry-standard clause templates used for comparison
and risk analysis. These represent balanced, commercially reasonable terms.
"""

from __future__ import annotations

from contractiq.models import ClauseType

CLAUSE_TEMPLATES: dict[ClauseType, dict[str, str]] = {
    ClauseType.PARTIES: {
        "name": "Parties",
        "description": "Identifies the contracting parties with full legal names and addresses.",
        "template": (
            'This Agreement is entered into as of [Effective Date] by and between '
            '[Party A Full Legal Name], a [state/jurisdiction] [entity type] with its '
            'principal place of business at [Address] ("Party A"), and [Party B Full '
            'Legal Name], a [state/jurisdiction] [entity type] with its principal '
            'place of business at [Address] ("Party B"). Each of Party A and Party B '
            'may be referred to individually as a "Party" and collectively as the "Parties."'
        ),
        "key_elements": "Full legal names, entity types, jurisdictions, addresses, defined short names",
    },
    ClauseType.TERM: {
        "name": "Term and Duration",
        "description": "Defines the contract duration, renewal, and expiration terms.",
        "template": (
            "This Agreement shall commence on the Effective Date and continue for an "
            "initial term of [duration] (the \"Initial Term\"). Thereafter, this Agreement "
            "shall automatically renew for successive [renewal period] periods (each a "
            "\"Renewal Term\"), unless either Party provides written notice of non-renewal "
            "at least [notice period, e.g., 30 days] prior to the end of the then-current "
            "term. The Initial Term and any Renewal Terms are collectively the \"Term.\""
        ),
        "key_elements": "Start date, initial duration, auto-renewal, renewal periods, notice period for non-renewal",
    },
    ClauseType.PAYMENT: {
        "name": "Payment Terms",
        "description": "Specifies fees, payment schedule, and late payment consequences.",
        "template": (
            "Party B shall pay Party A the fees set forth in Exhibit A (the \"Fees\"). "
            "All invoices are due and payable within [30] days of the invoice date. "
            "Late payments shall accrue interest at the lesser of [1.5]% per month or "
            "the maximum rate permitted by law. Party A may suspend services upon [15] "
            "days' written notice of overdue payment. All Fees are non-refundable except "
            "as expressly stated herein. Fees may be adjusted upon [60] days' prior "
            "written notice, effective at the start of the next Renewal Term."
        ),
        "key_elements": "Fee reference, payment window, late interest, suspension rights, refund policy, price adjustment notice",
    },
    ClauseType.TERMINATION: {
        "name": "Termination",
        "description": "Defines grounds and procedures for ending the contract.",
        "template": (
            "Either Party may terminate this Agreement: (a) for convenience upon [30] "
            "days' prior written notice; (b) for cause if the other Party materially "
            "breaches this Agreement and fails to cure such breach within [30] days of "
            "written notice; or (c) immediately if the other Party becomes insolvent, "
            "files for bankruptcy, or ceases operations. Upon termination, each Party "
            "shall return or destroy all Confidential Information of the other Party. "
            "Sections [list surviving sections] shall survive termination."
        ),
        "key_elements": "Termination for convenience, cure period, insolvency clause, post-termination obligations, survival clause",
    },
    ClauseType.IP: {
        "name": "Intellectual Property",
        "description": "Addresses ownership and licensing of intellectual property.",
        "template": (
            "Each Party retains all rights, title, and interest in its pre-existing "
            "intellectual property. Any work product created by Party A specifically for "
            'Party B under this Agreement ("Work Product") shall be owned by Party B upon '
            "full payment. Party A hereby assigns all rights in the Work Product to Party B. "
            "Party A retains a non-exclusive, royalty-free license to use any general "
            "knowledge, skills, techniques, and tools developed during performance. "
            "Neither Party shall use the other's trademarks without prior written consent."
        ),
        "key_elements": "Pre-existing IP retained, work product ownership, assignment, residual knowledge license, trademark restrictions",
    },
    ClauseType.CONFIDENTIALITY: {
        "name": "Confidentiality",
        "description": "Protects proprietary and sensitive information shared between parties.",
        "template": (
            '"Confidential Information" means all non-public information disclosed by '
            "either Party, whether orally, in writing, or electronically, that is designated "
            "as confidential or that a reasonable person would understand to be confidential. "
            "The receiving Party shall: (a) use Confidential Information solely for purposes "
            "of this Agreement; (b) protect it with at least the same degree of care used for "
            "its own confidential information, but no less than reasonable care; and (c) not "
            "disclose it to third parties except to employees and contractors with a need to "
            "know who are bound by confidentiality obligations. These obligations shall "
            "survive for [3] years following disclosure."
        ),
        "key_elements": "Broad definition, use restriction, standard of care, permitted disclosures, survival period",
    },
    ClauseType.INDEMNIFICATION: {
        "name": "Indemnification",
        "description": "Defines obligations to compensate for losses and third-party claims.",
        "template": (
            "Each Party (the \"Indemnifying Party\") shall indemnify, defend, and hold "
            "harmless the other Party and its officers, directors, and employees (the "
            "\"Indemnified Parties\") from and against any third-party claims, damages, "
            "losses, and reasonable expenses (including attorneys' fees) arising from: "
            "(a) the Indemnifying Party's material breach of this Agreement; (b) the "
            "Indemnifying Party's negligence or willful misconduct; or (c) the Indemnifying "
            "Party's violation of applicable law. The Indemnified Party shall provide prompt "
            "written notice, reasonable cooperation, and sole control of the defense to "
            "the Indemnifying Party."
        ),
        "key_elements": "Mutual indemnification, covered claims, defense obligations, notice requirements, cooperation duties",
    },
    ClauseType.LIMITATION_OF_LIABILITY: {
        "name": "Limitation of Liability",
        "description": "Caps potential damages and excludes certain damage types.",
        "template": (
            "EXCEPT FOR A PARTY'S INDEMNIFICATION OBLIGATIONS, BREACH OF CONFIDENTIALITY, "
            "OR WILLFUL MISCONDUCT: (A) NEITHER PARTY SHALL BE LIABLE FOR ANY INDIRECT, "
            "INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, REGARDLESS OF THE "
            "CAUSE OF ACTION OR THEORY OF LIABILITY; AND (B) EACH PARTY'S TOTAL AGGREGATE "
            "LIABILITY UNDER THIS AGREEMENT SHALL NOT EXCEED THE AMOUNTS PAID OR PAYABLE "
            "BY PARTY B IN THE [12]-MONTH PERIOD PRECEDING THE CLAIM. This limitation "
            "applies regardless of whether a Party has been advised of the possibility "
            "of such damages."
        ),
        "key_elements": "Mutual cap, excluded damage types, carve-outs for indemnification/confidentiality/willful misconduct, aggregate cap formula",
    },
    ClauseType.GOVERNING_LAW: {
        "name": "Governing Law",
        "description": "Specifies jurisdiction and dispute resolution mechanisms.",
        "template": (
            "This Agreement shall be governed by and construed in accordance with the "
            "laws of the State of [State], without regard to its conflict of law provisions. "
            "Any dispute arising under this Agreement shall first be submitted to good-faith "
            "mediation. If mediation is unsuccessful within [30] days, the dispute shall "
            "be resolved by binding arbitration administered by [arbitration body] in "
            "[city, state], in accordance with its Commercial Arbitration Rules. Each "
            "Party shall bear its own costs, and arbitration fees shall be shared equally."
        ),
        "key_elements": "Choice of law, conflict of law exclusion, mediation first, arbitration fallback, cost allocation",
    },
    ClauseType.FORCE_MAJEURE: {
        "name": "Force Majeure",
        "description": "Addresses unforeseeable events preventing contract performance.",
        "template": (
            "Neither Party shall be liable for any failure or delay in performance due "
            "to causes beyond its reasonable control, including but not limited to acts "
            "of God, natural disasters, war, terrorism, epidemics, pandemics, government "
            "actions, labor disputes, power failures, or internet disruptions (each a "
            "\"Force Majeure Event\"). The affected Party shall provide prompt written "
            "notice and use commercially reasonable efforts to mitigate the impact. If a "
            "Force Majeure Event continues for more than [90] days, either Party may "
            "terminate this Agreement upon written notice without liability."
        ),
        "key_elements": "Broad event list including pandemics, notice requirement, mitigation duty, termination right after extended event",
    },
    ClauseType.NON_COMPETE: {
        "name": "Non-Compete",
        "description": "Restricts competitive activities during and after the contract.",
        "template": (
            "During the Term and for a period of [12] months following termination, "
            "Party B shall not, directly or indirectly, engage in or assist any business "
            "that competes with the services provided under this Agreement within "
            "[geographic scope]. This restriction applies only to the specific business "
            "activities that are the subject of this Agreement. Nothing in this section "
            "shall prevent Party B from owning less than [5]% of a publicly traded company."
        ),
        "key_elements": "Reasonable time limit, geographic scope, narrow activity scope, passive investment exception",
    },
    ClauseType.DATA_PROTECTION: {
        "name": "Data Protection",
        "description": "Governs handling of personal and sensitive data.",
        "template": (
            "Each Party shall comply with all applicable data protection and privacy laws, "
            "including but not limited to GDPR, CCPA, and other relevant regulations. "
            "Where a Party processes personal data on behalf of the other, it shall: "
            "(a) process data only as instructed; (b) implement appropriate technical "
            "and organizational security measures; (c) notify the other Party of any data "
            "breach within [72] hours; (d) assist with data subject rights requests; and "
            "(e) delete or return all personal data upon termination. A Data Processing "
            "Agreement is attached as Exhibit [X]."
        ),
        "key_elements": "Regulatory compliance, processing restrictions, security measures, breach notification, data subject rights, DPA reference",
    },
}


def get_template(clause_type: ClauseType) -> dict[str, str] | None:
    """Get the standard template for a clause type."""
    return CLAUSE_TEMPLATES.get(clause_type)


def list_templates() -> list[dict[str, str]]:
    """List all available clause templates with their names and descriptions."""
    result = []
    for clause_type, template_data in CLAUSE_TEMPLATES.items():
        result.append({
            "clause_type": clause_type.value,
            "name": template_data["name"],
            "description": template_data["description"],
            "key_elements": template_data["key_elements"],
        })
    return result
