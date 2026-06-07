from .schemas import DoraGapScore

ALL_CLAUSE_TYPES = [
    'service_description',
    'sla',
    'incident_support',
    'authority_cooperation',
    'audit_rights',
    'subcontracting_controls',
    'data_return',
    'business_continuity',
    'exit_support',
    'termination_rights',
    'location_change_notification',
    'data_processing_location',
]

_POINTS = {'yes': 10, 'partial': 5, 'no': 0, 'not_applicable': 10}
MAX_SCORE = len(ALL_CLAUSE_TYPES) * 10  # 120


def _str(val) -> str:
    return val.value if hasattr(val, 'value') else str(val)


def compute_dora_score(clauses, contract_id: int, contract_ref: str) -> DoraGapScore:
    if not clauses:
        return DoraGapScore(
            contract_id=contract_id,
            contract_ref=contract_ref,
            score=0,
            max_score=MAX_SCORE,
            rating='GREY',
            clause_summary={ct: 'no' for ct in ALL_CLAUSE_TYPES},
        )

    clause_map = {_str(c.clause_type): _str(c.status) for c in clauses}
    clause_summary: dict[str, str] = {}
    score = 0

    for ct in ALL_CLAUSE_TYPES:
        status = clause_map.get(ct, 'no')
        clause_summary[ct] = status
        score += _POINTS.get(status, 0)

    if score >= 90:
        rating = 'GREEN'
    elif score >= 50:
        rating = 'AMBER'
    else:
        rating = 'RED'

    return DoraGapScore(
        contract_id=contract_id,
        contract_ref=contract_ref,
        score=score,
        max_score=MAX_SCORE,
        rating=rating,
        clause_summary=clause_summary,
    )
