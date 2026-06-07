from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Contract, IctService, Provider, RiskAssessment, ContractClause
from ..schemas import DashboardSummary, ProviderDoraScore
from ..scoring import compute_dora_score, ALL_CLAUSE_TYPES

router = APIRouter()

_RISK_ORDER = ['critical', 'high', 'medium', 'low']


def _str(val) -> str:
    return val.value if hasattr(val, 'value') else str(val)


@router.get('/summary', response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)):
    all_contracts = db.query(Contract).all()
    active = [c for c in all_contracts if _str(c.contract_status) == 'active']

    critical_services = db.query(IctService).filter(IctService.is_critical_or_important == True).count()

    soon = date.today() + timedelta(days=90)
    expiring_soon = sum(1 for c in active if c.expiry_date and c.expiry_date <= soon)

    dist: dict[str, int] = {'GREEN': 0, 'AMBER': 0, 'RED': 0, 'GREY': 0}
    gaps = 0
    for c in active:
        dora = compute_dora_score(c.clauses, c.id, c.contract_ref)
        dist[dora.rating] = dist.get(dora.rating, 0) + 1
        if dora.rating in ('RED', 'AMBER'):
            gaps += 1

    return DashboardSummary(
        total_contracts=len(all_contracts),
        active_contracts=len(active),
        critical_services=critical_services,
        contracts_with_gaps=gaps,
        expiring_soon_count=expiring_soon,
        score_distribution=dist,
    )


@router.get('/clause-gaps')
def clause_gaps(db: Session = Depends(get_db)):
    result = []
    for ct in ALL_CLAUSE_TYPES:
        missing = db.query(ContractClause).filter(
            ContractClause.clause_type == ct,
            ContractClause.status == 'no',
        ).count()
        partial = db.query(ContractClause).filter(
            ContractClause.clause_type == ct,
            ContractClause.status == 'partial',
        ).count()
        result.append({'clause_type': ct, 'missing_count': missing, 'partial_count': partial})
    return sorted(result, key=lambda x: x['missing_count'] + x['partial_count'], reverse=True)


@router.get('/provider-risk')
def provider_risk(db: Session = Depends(get_db)):
    result = []
    for p in db.query(Provider).all():
        contracts = p.contracts
        critical_count = sum(
            1 for c in contracts for s in c.services if s.is_critical_or_important
        )
        ratings_found = []
        for c in contracts:
            ra = db.query(RiskAssessment).filter(RiskAssessment.contract_id == c.id).first()
            if ra:
                ratings_found.append(_str(ra.risk_rating))
        top_risk = next((r for r in _RISK_ORDER if r in ratings_found), None)
        result.append({
            'provider_id': p.id,
            'provider_name': p.legal_name,
            'contract_count': len(contracts),
            'critical_service_count': critical_count,
            'risk_rating': top_risk,
        })
    return result


@router.get('/provider-dora-scores', response_model=list[ProviderDoraScore])
def provider_dora_scores(db: Session = Depends(get_db)):
    active = db.query(Contract).filter(Contract.contract_status == 'active').all()
    return [
        ProviderDoraScore(
            contract_ref=c.contract_ref,
            provider_name=c.provider.legal_name if c.provider else '',
            rating=compute_dora_score(c.clauses, c.id, c.contract_ref).rating,
        )
        for c in active
    ]
