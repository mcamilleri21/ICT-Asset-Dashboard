from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import IctService, ServiceLocation
from ..schemas import IctServiceCreate, IctServiceRead

router = APIRouter()


@router.get('/', response_model=list[IctServiceRead])
def list_services(
    contract_id: Optional[int] = Query(None),
    is_critical: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(IctService)
    if contract_id is not None:
        q = q.filter(IctService.contract_id == contract_id)
    if is_critical is not None:
        q = q.filter(IctService.is_critical_or_important == is_critical)
    return q.all()


@router.post('/', response_model=IctServiceRead, status_code=201)
def create_service(body: IctServiceCreate, db: Session = Depends(get_db)):
    data = body.model_dump()
    locations_data = data.pop('locations', [])
    service = IctService(**data)
    db.add(service)
    db.flush()
    for loc in locations_data:
        db.add(ServiceLocation(service_id=service.id, **loc))
    db.commit()
    db.refresh(service)
    return service


@router.put('/{service_id}', response_model=IctServiceRead)
def update_service(service_id: int, body: IctServiceCreate, db: Session = Depends(get_db)):
    service = db.query(IctService).filter(IctService.id == service_id).first()
    if not service:
        raise HTTPException(404, 'Service not found')
    data = body.model_dump(exclude_unset=True)
    data.pop('locations', None)
    for k, v in data.items():
        setattr(service, k, v)
    db.commit()
    db.refresh(service)
    return service
