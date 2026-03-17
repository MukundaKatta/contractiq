"""Pydantic models for ContractIQ."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ClauseType(str, Enum):
    """Standard contract clause types."""

    PARTIES = "parties"
    TERM = "term"
    PAYMENT = "payment"
    TERMINATION = "termination"
    IP = "intellectual_property"
    CONFIDENTIALITY = "confidentiality"
    INDEMNIFICATION = "indemnification"
    LIMITATION_OF_LIABILITY = "limitation_of_liability"
    GOVERNING_LAW = "governing_law"
    FORCE_MAJEURE = "force_majeure"
    NON_COMPETE = "non_compete"
    DATA_PROTECTION = "data_protection"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    """Risk severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Clause(BaseModel):
    """A single extracted clause from a contract."""

    clause_type: ClauseType
    title: str = ""
    text: str
    section_number: Optional[str] = None
    start_position: int = 0
    end_position: int = 0

    @property
    def label(self) -> str:
        return self.title or self.clause_type.value.replace("_", " ").title()


class Risk(BaseModel):
    """A detected risk within a contract clause."""

    clause_type: ClauseType
    severity: Severity
    description: str
    clause_text: str = ""
    recommendation: str = ""

    @property
    def severity_weight(self) -> float:
        weights = {
            Severity.LOW: 1.0,
            Severity.MEDIUM: 3.0,
            Severity.HIGH: 7.0,
            Severity.CRITICAL: 10.0,
        }
        return weights[self.severity]


class Suggestion(BaseModel):
    """A recommended modification to a contract clause."""

    clause_type: ClauseType
    original_text: str
    suggested_text: str
    rationale: str
    priority: Severity = Severity.MEDIUM


class ComparisonResult(BaseModel):
    """Result of comparing a clause against a standard template."""

    clause_type: ClauseType
    contract_text: str
    template_text: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    deviations: list[str] = Field(default_factory=list)
    missing_protections: list[str] = Field(default_factory=list)


class Contract(BaseModel):
    """A parsed contract document."""

    filename: str = ""
    raw_text: str
    clauses: list[Clause] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)

    @property
    def clause_map(self) -> dict[ClauseType, list[Clause]]:
        result: dict[ClauseType, list[Clause]] = {}
        for clause in self.clauses:
            result.setdefault(clause.clause_type, []).append(clause)
        return result

    @property
    def word_count(self) -> int:
        return len(self.raw_text.split())


class ReviewReport(BaseModel):
    """Complete contract review report."""

    contract: Contract
    risks: list[Risk] = Field(default_factory=list)
    suggestions: list[Suggestion] = Field(default_factory=list)
    comparisons: list[ComparisonResult] = Field(default_factory=list)
    overall_score: float = Field(default=50.0, ge=0.0, le=100.0)
    summary: str = ""
    recommendation: str = ""

    @property
    def critical_risks(self) -> list[Risk]:
        return [r for r in self.risks if r.severity == Severity.CRITICAL]

    @property
    def high_risks(self) -> list[Risk]:
        return [r for r in self.risks if r.severity == Severity.HIGH]

    @property
    def risk_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self.risks:
            counts[r.severity.value] = counts.get(r.severity.value, 0) + 1
        return counts
