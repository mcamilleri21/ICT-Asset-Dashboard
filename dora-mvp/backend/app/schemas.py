from __future__ import annotations
from datetime import date, datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict


# ── LegalEntity ───────────────────────────────────────────────────────────────

class LegalEntityBase(BaseModel):
    name: str
    lei: Optional[str] = None
    country_code: Optional[str] = None
    entity_type: str = 'regulated_firm'


class LegalEntityCreate(LegalEntityBase):
    pass


class LegalEntityRead(LegalEntityBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ── Provider ──────────────────────────────────────────────────────────────────

class ProviderBase(BaseModel):
    legal_name: str
    trading_name: Optional[str] = None
    lei: Optional[str] = None
    country_of_incorporation: Optional[str] = None
    parent_company: Optional[str] = None
    provider_type: str = 'ict_third_party'
    is_regulated: bool = False


class ProviderCreate(ProviderBase):
    pass


class ProviderRead(ProviderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ── ServiceLocation ───────────────────────────────────────────────────────────

class ServiceLocationBase(BaseModel):
    location_type: str
    country_code: str
    country_name: str


class ServiceLocationCreate(ServiceLocationBase):
    pass


class ServiceLocationRead(ServiceLocationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    service_id: int


# ── IctService ────────────────────────────────────────────────────────────────

class IctServiceBase(BaseModel):
    service_ref: str
    service_description: str
    ict_service_category: str
    contract_id: int
    supported_application: Optional[str] = None
    supported_business_process: Optional[str] = None
    supported_function: Optional[str] = None
    is_critical_or_important: bool = False
    personal_data_involved: bool = False
    sensitive_data_involved: bool = False


class IctServiceCreate(IctServiceBase):
    locations: list[ServiceLocationCreate] = []


class IctServiceRead(IctServiceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    locations: list[ServiceLocationRead] = []


# ── ContractClause ────────────────────────────────────────────────────────────

class ContractClauseBase(BaseModel):
    clause_type: str
    status: str = 'no'
    clause_reference: Optional[str] = None
    reviewer: Optional[str] = None
    review_date: Optional[date] = None
    notes: Optional[str] = None


class ContractClauseCreate(ContractClauseBase):
    contract_id: int


class ContractClauseRead(ContractClauseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    contract_id: int


# ── Subcontractor ─────────────────────────────────────────────────────────────

class SubcontractorBase(BaseModel):
    subcontractor_name: str
    subcontractor_role: Optional[str] = None
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    supports_critical_function: bool = False
    notification_date: Optional[date] = None
    approval_status: str = 'pending'
    alternative_available: Optional[bool] = None


class SubcontractorCreate(SubcontractorBase):
    service_id: int


class SubcontractorRead(SubcontractorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    service_id: int
    created_at: datetime


# ── RiskAssessment ────────────────────────────────────────────────────────────

class RiskAssessmentBase(BaseModel):
    risk_rating: str
    substitutability: Optional[str] = None
    concentration_risk: Optional[str] = None
    last_due_diligence_date: Optional[date] = None
    next_review_date: Optional[date] = None
    assessed_by: Optional[str] = None
    notes: Optional[str] = None


class RiskAssessmentCreate(RiskAssessmentBase):
    contract_id: int


class RiskAssessmentRead(RiskAssessmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    contract_id: int
    created_at: datetime


# ── EvidenceFile ──────────────────────────────────────────────────────────────

class EvidenceFileBase(BaseModel):
    document_name: str
    document_type: Optional[str] = None
    file_url: Optional[str] = None
    uploaded_by: Optional[str] = None


class EvidenceFileCreate(EvidenceFileBase):
    contract_id: int


class EvidenceFileRead(EvidenceFileBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    contract_id: int
    uploaded_at: datetime


# ── Contract ──────────────────────────────────────────────────────────────────

class ContractBase(BaseModel):
    contract_ref: str
    contract_name: str
    contract_owner: Optional[str] = None
    legal_entity_id: int
    provider_id: int
    contract_status: str = 'active'
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    renewal_type: Optional[str] = None
    notice_period_days: Optional[int] = None
    document_url: Optional[str] = None
    version: str = '1.0'
    last_reviewed_date: Optional[date] = None


class ContractCreate(ContractBase):
    pass


class ContractRead(ContractBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class ContractListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    contract_ref: str
    contract_name: str
    contract_status: str
    provider_legal_name: str
    provider_lei: Optional[str] = None
    expiry_date: Optional[date] = None
    has_critical_service: bool
    dora_score: Optional[int] = None
    dora_rating: Optional[str] = None


class ContractDetail(ContractBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    provider: ProviderRead
    services: list[IctServiceRead] = []
    clauses: list[ContractClauseRead] = []
    risk_assessment: Optional[RiskAssessmentRead] = None


# ── Aggregate / utility schemas ───────────────────────────────────────────────

class DoraGapScore(BaseModel):
    contract_id: int
    contract_ref: str
    score: int
    max_score: int
    rating: Literal['GREEN', 'AMBER', 'RED', 'GREY']
    clause_summary: dict[str, str]


class DashboardSummary(BaseModel):
    total_contracts: int
    active_contracts: int
    critical_services: int
    contracts_with_gaps: int
    expiring_soon_count: int
    score_distribution: dict


class ImportResult(BaseModel):
    contracts_created: int
    providers_created: int
    services_created: int
    errors: list[str]


class ProviderDoraScore(BaseModel):
    contract_ref: str
    provider_name: str
    rating: str
