from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Contract, ContractClause
from ..schemas import ContractClauseCreate, ContractClauseRead

router = APIRouter()


@router.get('/contracts/{contract_id}/clauses', response_model=list[ContractClauseRead])
def list_clauses(contract_id: int, db: Session = Depends(get_db)):
    return db.query(ContractClause).filter(ContractClause.contract_id == contract_id).all()


@router.put('/contracts/{contract_id}/clauses/{clause_type}', response_model=ContractClauseRead)
def upsert_clause(
    contract_id: int,
    clause_type: str,
    body: ContractClauseCreate,
    db: Session = Depends(get_db),
):
    if not db.query(Contract).filter(Contract.id == contract_id).first():
        raise HTTPException(404, 'Contract not found')

    clause = db.query(ContractClause).filter(
        ContractClause.contract_id == contract_id,
        ContractClause.clause_type == clause_type,
    ).first()

    if clause:
        for k, v in body.model_dump(exclude={'contract_id'}, exclude_unset=True).items():
            setattr(clause, k, v)
    else:
        data = body.model_dump()
        data['contract_id'] = contract_id
        data['clause_type'] = clause_type
        clause = ContractClause(**data)
        db.add(clause)

    db.commit()
    db.refresh(clause)
    return clause
