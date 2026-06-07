import enum as py_enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime,
    ForeignKey, UniqueConstraint, Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from .database import Base


# ── Enum helpers ─────────────────────────────────────────────────────────────

def _sa_enum(enum_class):
    """SAEnum that stores Python enum values (not names) as the column strings."""
    return SAEnum(
        enum_class,
        values_callable=lambda x: [e.value for e in x],
        create_constraint=True,
    )


# ── Python enum definitions ───────────────────────────────────────────────────

class ProviderType(str, py_enum.Enum):
    ict_third_party = 'ict_third_party'
    intra_group     = 'intra_group'
    subcontractor   = 'subcontractor'


class ContractStatus(str, py_enum.Enum):
    draft      = 'draft'
    active     = 'active'
    expired    = 'expired'
    terminated = 'terminated'


class RenewalType(str, py_enum.Enum):
    auto_renewal = 'auto_renewal'
    fixed_term   = 'fixed_term'
    evergreen    = 'evergreen'


class IctServiceCategory(str, py_enum.Enum):
    SaaS             = 'SaaS'
    IaaS             = 'IaaS'
    PaaS             = 'PaaS'
    managed_service  = 'managed_service'
    cybersecurity    = 'cybersecurity'
    data_service     = 'data_service'
    software_licence = 'software_licence'
    hosting          = 'hosting'
    support          = 'support'
    other            = 'other'


class LocationType(str, py_enum.Enum):
    service_delivery = 'service_delivery'
    data_processing  = 'data_processing'
    data_storage     = 'data_storage'


class ClauseType(str, py_enum.Enum):
    service_description          = 'service_description'
    sla                          = 'sla'
    incident_support             = 'incident_support'
    authority_cooperation        = 'authority_cooperation'
    audit_rights                 = 'audit_rights'
    subcontracting_controls      = 'subcontracting_controls'
    data_return                  = 'data_return'
    business_continuity          = 'business_continuity'
    exit_support                 = 'exit_support'
    termination_rights           = 'termination_rights'
    location_change_notification = 'location_change_notification'
    data_processing_location     = 'data_processing_location'


class ClauseStatus(str, py_enum.Enum):
    yes            = 'yes'
    no             = 'no'
    partial        = 'partial'
    not_applicable = 'not_applicable'


class ApprovalStatus(str, py_enum.Enum):
    approved = 'approved'
    rejected = 'rejected'
    pending  = 'pending'


class RiskRating(str, py_enum.Enum):
    low      = 'low'
    medium   = 'medium'
    high     = 'high'
    critical = 'critical'


class LowMedHighLevel(str, py_enum.Enum):
    low    = 'low'
    medium = 'medium'
    high   = 'high'


# ── Models ───────────────────────────────────────────────────────────────────

class LegalEntity(Base):
    __tablename__ = 'legal_entities'

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(255), nullable=False)
    lei         = Column(String(20), nullable=True)
    country_code= Column(String(2), nullable=True)
    entity_type = Column(String(100), default='regulated_firm')
    created_at  = Column(DateTime, default=datetime.utcnow)

    contracts = relationship('Contract', back_populates='legal_entity')

    def __repr__(self):
        return f"<LegalEntity id={self.id} name={self.name!r}>"


class Provider(Base):
    __tablename__ = 'providers'

    id                       = Column(Integer, primary_key=True, index=True)
    legal_name               = Column(String(255), unique=True, nullable=False)
    trading_name             = Column(String(255), nullable=True)
    lei                      = Column(String(20), nullable=True)
    country_of_incorporation = Column(String(2), nullable=True)
    parent_company           = Column(String(255), nullable=True)
    provider_type            = Column(_sa_enum(ProviderType), default=ProviderType.ict_third_party)
    is_regulated             = Column(Boolean, default=False)
    created_at               = Column(DateTime, default=datetime.utcnow)

    contracts = relationship('Contract', back_populates='provider')

    def __repr__(self):
        return f"<Provider id={self.id} legal_name={self.legal_name!r}>"


class Contract(Base):
    __tablename__ = 'contracts'

    id                 = Column(Integer, primary_key=True, index=True)
    contract_ref       = Column(String(20), unique=True, nullable=False)
    contract_name      = Column(String(500), nullable=False)
    contract_owner     = Column(String(255), nullable=True)
    legal_entity_id    = Column(Integer, ForeignKey('legal_entities.id'), nullable=False, index=True)
    provider_id        = Column(Integer, ForeignKey('providers.id'), nullable=False, index=True)
    contract_status    = Column(_sa_enum(ContractStatus), default=ContractStatus.active)
    effective_date     = Column(Date, nullable=True)
    expiry_date        = Column(Date, nullable=True)
    renewal_type       = Column(_sa_enum(RenewalType), nullable=True)
    notice_period_days = Column(Integer, nullable=True)
    document_url       = Column(String(1000), nullable=True)
    version            = Column(String(20), default='1.0')
    last_reviewed_date = Column(Date, nullable=True)
    created_at         = Column(DateTime, default=datetime.utcnow)
    updated_at         = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    provider      = relationship('Provider', back_populates='contracts')
    legal_entity  = relationship('LegalEntity', back_populates='contracts')
    services      = relationship('IctService', back_populates='contract', cascade='all, delete-orphan')
    clauses       = relationship('ContractClause', back_populates='contract', cascade='all, delete-orphan')
    risk_assessment = relationship('RiskAssessment', back_populates='contract', uselist=False, cascade='all, delete-orphan')
    evidence_files  = relationship('EvidenceFile', back_populates='contract', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Contract id={self.id} ref={self.contract_ref!r}>"


class IctService(Base):
    __tablename__ = 'ict_services'

    id                        = Column(Integer, primary_key=True, index=True)
    service_ref               = Column(String(20), unique=True, nullable=False)
    service_description       = Column(Text, nullable=False)
    ict_service_category      = Column(_sa_enum(IctServiceCategory), nullable=False)
    contract_id               = Column(Integer, ForeignKey('contracts.id'), nullable=False, index=True)
    supported_application     = Column(String(500), nullable=True)
    supported_business_process= Column(String(500), nullable=True)
    supported_function        = Column(String(500), nullable=True)
    is_critical_or_important  = Column(Boolean, default=False, nullable=False)
    personal_data_involved    = Column(Boolean, default=False)
    sensitive_data_involved   = Column(Boolean, default=False)
    created_at                = Column(DateTime, default=datetime.utcnow)

    contract      = relationship('Contract', back_populates='services')
    locations     = relationship('ServiceLocation', back_populates='service', cascade='all, delete-orphan')
    subcontractors= relationship('Subcontractor', back_populates='service', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<IctService id={self.id} ref={self.service_ref!r}>"


class ServiceLocation(Base):
    __tablename__ = 'service_locations'

    id            = Column(Integer, primary_key=True, index=True)
    service_id    = Column(Integer, ForeignKey('ict_services.id'), nullable=False, index=True)
    location_type = Column(_sa_enum(LocationType), nullable=False)
    country_code  = Column(String(2), nullable=False)
    country_name  = Column(String(100), nullable=False)

    service = relationship('IctService', back_populates='locations')

    def __repr__(self):
        return f"<ServiceLocation id={self.id} country={self.country_code!r} type={self.location_type!r}>"


class ContractClause(Base):
    __tablename__ = 'contract_clauses'
    __table_args__ = (
        UniqueConstraint('contract_id', 'clause_type', name='uq_contract_clause_type'),
    )

    id               = Column(Integer, primary_key=True, index=True)
    contract_id      = Column(Integer, ForeignKey('contracts.id'), nullable=False, index=True)
    clause_type      = Column(_sa_enum(ClauseType), nullable=False)
    status           = Column(_sa_enum(ClauseStatus), nullable=False, default=ClauseStatus.no)
    clause_reference = Column(String(500), nullable=True)
    reviewer         = Column(String(255), nullable=True)
    review_date      = Column(Date, nullable=True)
    notes            = Column(Text, nullable=True)

    contract = relationship('Contract', back_populates='clauses')

    def __repr__(self):
        return f"<ContractClause id={self.id} type={self.clause_type!r} status={self.status!r}>"


class Subcontractor(Base):
    __tablename__ = 'subcontractors'

    id                        = Column(Integer, primary_key=True, index=True)
    service_id                = Column(Integer, ForeignKey('ict_services.id'), nullable=False, index=True)
    subcontractor_name        = Column(String(255), nullable=False)
    subcontractor_role        = Column(String(500), nullable=True)
    country_code              = Column(String(2), nullable=True)
    country_name              = Column(String(100), nullable=True)
    supports_critical_function= Column(Boolean, default=False)
    notification_date         = Column(Date, nullable=True)
    approval_status           = Column(_sa_enum(ApprovalStatus), default=ApprovalStatus.pending)
    alternative_available     = Column(Boolean, nullable=True)
    created_at                = Column(DateTime, default=datetime.utcnow)

    service = relationship('IctService', back_populates='subcontractors')

    def __repr__(self):
        return f"<Subcontractor id={self.id} name={self.subcontractor_name!r}>"


class RiskAssessment(Base):
    __tablename__ = 'risk_assessments'

    id                      = Column(Integer, primary_key=True, index=True)
    contract_id             = Column(Integer, ForeignKey('contracts.id'), nullable=False, unique=True, index=True)
    risk_rating             = Column(_sa_enum(RiskRating), nullable=False)
    substitutability        = Column(_sa_enum(LowMedHighLevel), nullable=True)
    concentration_risk      = Column(_sa_enum(LowMedHighLevel), nullable=True)
    last_due_diligence_date = Column(Date, nullable=True)
    next_review_date        = Column(Date, nullable=True)
    assessed_by             = Column(String(255), nullable=True)
    notes                   = Column(Text, nullable=True)
    created_at              = Column(DateTime, default=datetime.utcnow)

    contract = relationship('Contract', back_populates='risk_assessment')

    def __repr__(self):
        return f"<RiskAssessment id={self.id} contract_id={self.contract_id} rating={self.risk_rating!r}>"


class EvidenceFile(Base):
    __tablename__ = 'evidence_files'

    id            = Column(Integer, primary_key=True, index=True)
    contract_id   = Column(Integer, ForeignKey('contracts.id'), nullable=False, index=True)
    document_name = Column(String(500), nullable=False)
    document_type = Column(String(100), nullable=True)
    file_url      = Column(String(1000), nullable=True)
    uploaded_by   = Column(String(255), nullable=True)
    uploaded_at   = Column(DateTime, default=datetime.utcnow)

    contract = relationship('Contract', back_populates='evidence_files')

    def __repr__(self):
        return f"<EvidenceFile id={self.id} name={self.document_name!r}>"
