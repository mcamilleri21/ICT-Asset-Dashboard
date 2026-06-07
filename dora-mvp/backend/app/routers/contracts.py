from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Contract
from ..schemas import ContractCreate, ContractRead, ContractListItem, ContractDetail, DoraGapScore
from ..scoring import compute_dora_score

router = APIRouter()


def _status_val(val) -> str:
    return val.value if hasattr(val, 'value') else str(val)


def _to_list_item(c: Contract) -> ContractListItem:
    has_critical = any(s.is_critical_or_important for s in c.services)
    dora = compute_dora_score(c.clauses, c.id, c.contract_ref)
    p = c.provider
    return ContractListItem(
        id=c.id,
        contract_ref=c.contract_ref,
        contract_name=c.contract_name,
        contract_status=_status_val(c.contract_status),
        provider_legal_name=p.legal_name if p else '',
        provider_lei=p.lei if p else None,
        expiry_date=c.expiry_date,
        has_critical_service=has_critical,
        dora_score=dora.score if dora.rating != 'GREY' else None,
        dora_rating=dora.rating,
    )


@router.get('/', response_model=list[ContractListItem])
def list_contracts(
    status: Optional[str] = Query(None),
    provider_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Contract)
    if status:
        q = q.filter(Contract.contract_status == status)
    if provider_id:
        q = q.filter(Contract.provider_id == provider_id)
    return [_to_list_item(c) for c in q.all()]


@router.post('/', response_model=ContractRead, status_code=201)
def create_contract(body: ContractCreate, db: Session = Depends(get_db)):
    contract = Contract(**body.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


# Note: specific sub-path registered before /{contract_id} to avoid param capture
@router.get('/{contract_id}/dora-score', response_model=DoraGapScore)
def get_dora_score(contract_id: int, db: Session = Depends(get_db)):
    c = db.query(Contract).filter(Contract.id == contract_id).first()
    if not c:
        raise HTTPException(404, 'Contract not found')
    return compute_dora_score(c.clauses, c.id, c.contract_ref)


@router.get('/{contract_id}', response_model=ContractDetail)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    c = db.query(Contract).filter(Contract.id == contract_id).first()
    if not c:
        raise HTTPException(404, 'Contract not found')
    return c


@router.put('/{contract_id}', response_model=ContractRead)
def update_contract(contract_id: int, body: ContractCreate, db: Session = Depends(get_db)):
    c = db.query(Contract).filter(Contract.id == contract_id).first()
    if not c:
        raise HTTPException(404, 'Contract not found')
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c
