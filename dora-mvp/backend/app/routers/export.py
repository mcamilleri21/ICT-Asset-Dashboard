import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Contract
from ..scoring import compute_dora_score

router = APIRouter()

_HEADERS = [
    'contract_ref', 'contract_name', 'contract_status', 'provider_legal_name',
    'provider_lei', 'effective_date', 'expiry_date', 'critical_or_important',
    'dora_score_rating', 'audit_rights_status', 'sla_status', 'exit_support_status',
    'incident_support_status', 'risk_rating', 'last_reviewed_date',
]


def _val(v) -> str:
    if v is None:
        return ''
    return v.value if hasattr(v, 'value') else str(v)


def _generate(db: Session):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_HEADERS, lineterminator='\n')
    writer.writeheader()
    yield buf.getvalue()

    for c in db.query(Contract).all():
        buf.seek(0)
        buf.truncate(0)
        p = c.provider
        dora = compute_dora_score(c.clauses, c.id, c.contract_ref)
        cs = dora.clause_summary
        ra = c.risk_assessment
        has_critical = any(s.is_critical_or_important for s in c.services)
        writer.writerow({
            'contract_ref':           c.contract_ref,
            'contract_name':          c.contract_name,
            'contract_status':        _val(c.contract_status),
            'provider_legal_name':    p.legal_name if p else '',
            'provider_lei':           (p.lei or '') if p else '',
            'effective_date':         str(c.effective_date) if c.effective_date else '',
            'expiry_date':            str(c.expiry_date) if c.expiry_date else '',
            'critical_or_important':  'Yes' if has_critical else 'No',
            'dora_score_rating':      dora.rating,
            'audit_rights_status':    cs.get('audit_rights', ''),
            'sla_status':             cs.get('sla', ''),
            'exit_support_status':    cs.get('exit_support', ''),
            'incident_support_status': cs.get('incident_support', ''),
            'risk_rating':            _val(ra.risk_rating) if ra else '',
            'last_reviewed_date':     str(c.last_reviewed_date) if c.last_reviewed_date else '',
        })
        yield buf.getvalue()


@router.get('/contracts-csv')
def export_contracts_csv(db: Session = Depends(get_db)):
    return StreamingResponse(
        _generate(db),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="dora_contract_register.csv"'},
    )
