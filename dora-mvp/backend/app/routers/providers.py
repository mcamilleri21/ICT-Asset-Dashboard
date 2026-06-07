from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Provider, Contract
from ..schemas import ProviderRead, ProviderCreate, ContractListItem
from ..scoring import compute_dora_score

router = APIRouter()


def _status_val(val) -> str:
    return val.value if hasattr(val, 'value') else str(val)


def _contract_to_list_item(c: Contract, provider: Provider) -> ContractListItem:
    has_critical = any(s.is_critical_or_important for s in c.services)
    dora = compute_dora_score(c.clauses, c.id, c.contract_ref)
    return ContractListItem(
        id=c.id,
        contract_ref=c.contract_ref,
        contract_name=c.contract_name,
        contract_status=_status_val(c.contract_status),
        provider_legal_name=provider.legal_name,
        provider_lei=provider.lei,
        expiry_date=c.expiry_date,
        has_critical_service=has_critical,
        dora_score=dora.score if dora.rating != 'GREY' else None,
        dora_rating=dora.rating,
    )


@router.get('/', response_model=list[ProviderRead])
def list_providers(db: Session = Depends(get_db)):
    return db.query(Provider).all()


@router.post('/', response_model=ProviderRead, status_code=201)
def create_provider(body: ProviderCreate, db: Session = Depends(get_db)):
    provider = Provider(**body.model_dump())
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@router.get('/{provider_id}')
def get_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(404, 'Provider not found')
    contracts = db.query(Contract).filter(Contract.provider_id == provider_id).all()
    return {
        **ProviderRead.model_validate(provider).model_dump(),
        'contracts': [_contract_to_list_item(c, provider).model_dump() for c in contracts],
    }
