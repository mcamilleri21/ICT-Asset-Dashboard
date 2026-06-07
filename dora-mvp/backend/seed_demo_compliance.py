"""
Demo compliance enrichment script.
Run after uploading Sample_Data.xlsx via the web UI:

  cd dora-mvp/backend
  source venv/bin/activate          # Mac/Linux
  venv\\Scripts\\activate            # Windows
  python seed_demo_compliance.py
"""

import sys
import os
from datetime import date

# Allow 'from app.xxx import ...' when running from backend/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Contract, ContractClause, RiskAssessment

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dora.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# ── Clause helpers ────────────────────────────────────────────────────────────

ALL_CLAUSE_TYPES = [
    "service_description", "sla", "incident_support", "authority_cooperation",
    "audit_rights", "subcontracting_controls", "data_return", "business_continuity",
    "exit_support", "termination_rights", "location_change_notification",
    "data_processing_location",
]


def _c(clause_type, status, reviewer=None, review_date=None, notes=None):
    """Build a clause dict."""
    return dict(
        clause_type=clause_type, status=status,
        reviewer=reviewer, review_date=review_date, notes=notes,
    )


def _all_yes(reviewer, review_date, overrides=None):
    """Return 12 clauses, all 'yes', with selective overrides.

    overrides: dict of clause_type → {'status': ..., 'notes': ...}
    """
    overrides = overrides or {}
    clauses = []
    for ct in ALL_CLAUSE_TYPES:
        ov = overrides.get(ct, {})
        clauses.append(_c(
            ct,
            ov.get("status", "yes"),
            ov.get("reviewer", reviewer),
            ov.get("review_date", review_date),
            ov.get("notes"),
        ))
    return clauses


def _risk(risk_rating, substitutability, concentration_risk,
          last_due_diligence_date, next_review_date, assessed_by, notes=None):
    return dict(
        risk_rating=risk_rating,
        substitutability=substitutability,
        concentration_risk=concentration_risk,
        last_due_diligence_date=last_due_diligence_date,
        next_review_date=next_review_date,
        assessed_by=assessed_by,
        notes=notes,
    )


# ── Contract compliance datasets ─────────────────────────────────────────────
# Expected ratings (computed from clause statuses):
#   yes=10, partial=5, no=0, not_applicable=10  /  max=120
#   GREEN≥90, AMBER 50–89, RED<50, GREY=no clauses

CONTRACT_DATA = [

    # ── CLOUD_01 — GREEN ──────────────────────────────────────────────────────
    {
        "ref": "CLOUD_01",
        "clauses": _all_yes("Legal", date(2026, 3, 1), overrides={
            "audit_rights":  {"status": "partial",
                              "notes": "Pooled audit mechanism only; direct audit 30 days notice"},
            "exit_support":  {"status": "partial",
                              "notes": "6-month transition period; no detailed exit plan attached"},
        }),
        "risk": _risk("high", "low", "high",
                      date(2026, 3, 1), date(2026, 9, 1), "Third-Party Risk"),
    },

    # ── SCR_01 — GREEN ───────────────────────────────────────────────────────
    {
        "ref": "SCR_01",
        "clauses": _all_yes("Compliance", date(2026, 1, 15), overrides={
            "subcontracting_controls": {
                "status": "partial",
                "notes": "Named subcontractors listed annually; no prior approval right",
            },
            "data_processing_location": {
                "status": "partial",
                "notes": "EU and US data processing; adequacy reliance documented",
            },
        }),
        "risk": _risk("critical", "medium", "low",
                      date(2026, 1, 15), date(2026, 7, 15), "Compliance"),
    },

    # ── ACCPKG_01 — GREEN ────────────────────────────────────────────────────
    {
        "ref": "ACCPKG_01",
        "clauses": _all_yes("Legal", date(2025, 11, 1), overrides={
            "exit_support": {
                "status": "partial",
                "notes": "Standard wind-down terms only; no bespoke exit plan",
            },
        }),
        "risk": _risk("medium", "medium", "low",
                      date(2025, 11, 1), date(2026, 5, 1), "Finance"),
    },

    # ── DocSys_01 — AMBER (actual score ~100; spec note: 80/120) ─────────────
    {
        "ref": "DocSys_01",
        "clauses": [
            _c("service_description",          "yes",     "Legal", date(2025, 10, 15)),
            _c("sla",                           "yes",     "Legal", date(2025, 10, 15)),
            _c("incident_support",              "yes",     "Legal", date(2025, 10, 15)),
            _c("authority_cooperation",         "yes",     "Legal", date(2025, 10, 15)),
            _c("audit_rights",                  "partial", "Legal", date(2025, 10, 15),
               "Right to audit with 30 days notice; no pooled mechanism available"),
            _c("subcontracting_controls",       "partial", "Legal", date(2025, 10, 15),
               "General permission; subcontractor list on request only"),
            _c("data_return",                   "yes",     "Legal", date(2025, 10, 15)),
            _c("business_continuity",           "yes",     "Legal", date(2025, 10, 15)),
            _c("exit_support",                  "no",      "Legal", date(2025, 10, 15),
               "No exit assistance clause — REMEDIATION REQUIRED"),
            _c("termination_rights",            "yes",     "Legal", date(2025, 10, 15)),
            _c("location_change_notification",  "yes",     "Legal", date(2025, 10, 15)),
            _c("data_processing_location",      "yes",     "Legal", date(2025, 10, 15)),
        ],
        "risk": _risk("medium", "medium", "low",
                      date(2025, 10, 15), date(2026, 4, 15), "IT"),
    },

    # ── MKT_01 — AMBER (score ~50) ───────────────────────────────────────────
    {
        "ref": "MKT_01",
        "clauses": [
            _c("service_description",          "yes",     "Compliance", date(2025, 6, 1)),
            _c("sla",                           "yes",     "Compliance", date(2025, 6, 1)),
            _c("incident_support",              "partial", "Compliance", date(2025, 6, 1)),
            _c("authority_cooperation",         "no",      "Compliance", date(2025, 6, 1),
               "Standard commercial terms only; no regulatory cooperation clause"),
            _c("audit_rights",                  "no",      "Compliance", date(2025, 6, 1),
               "No audit rights — REMEDIATION REQUIRED"),
            _c("subcontracting_controls",       "no",      "Compliance", date(2025, 6, 1),
               "No subcontracting visibility — REMEDIATION REQUIRED"),
            _c("data_return",                   "partial", "Compliance", date(2025, 6, 1)),
            _c("business_continuity",           "no",      "Compliance", date(2025, 6, 1),
               "No BC obligations in contract"),
            _c("exit_support",                  "no",      "Compliance", date(2025, 6, 1),
               "Auto-renewal only; no exit support — REMEDIATION REQUIRED"),
            _c("termination_rights",            "yes",     "Compliance", date(2025, 6, 1)),
            _c("location_change_notification",  "partial", "Compliance", date(2025, 6, 1)),
            _c("data_processing_location",      "partial", "Compliance", date(2025, 6, 1),
               "US data processing; no explicit safeguard in contract"),
        ],
        "risk": _risk("high", "high", "low",
                      date(2025, 6, 1), date(2025, 12, 1), "Third-Party Risk"),
    },

    # ── HR_01 — AMBER (score ~80) ────────────────────────────────────────────
    {
        "ref": "HR_01",
        "clauses": [
            _c("service_description",          "yes",     "HR/Legal", date(2026, 2, 1)),
            _c("sla",                           "yes",     "HR/Legal", date(2026, 2, 1)),
            _c("incident_support",              "yes",     "HR/Legal", date(2026, 2, 1)),
            _c("authority_cooperation",         "no",      "HR/Legal", date(2026, 2, 1)),
            _c("audit_rights",                  "no",      "HR/Legal", date(2026, 2, 1)),
            _c("subcontracting_controls",       "partial", "HR/Legal", date(2026, 2, 1)),
            _c("data_return",                   "yes",     "HR/Legal", date(2026, 2, 1)),
            _c("business_continuity",           "no",      "HR/Legal", date(2026, 2, 1)),
            _c("exit_support",                  "partial", "HR/Legal", date(2026, 2, 1)),
            _c("termination_rights",            "yes",     "HR/Legal", date(2026, 2, 1)),
            _c("location_change_notification",  "yes",     "HR/Legal", date(2026, 2, 1)),
            _c("data_processing_location",      "yes",     "HR/Legal", date(2026, 2, 1)),
        ],
        "risk": _risk("medium", "medium", "low",
                      date(2026, 2, 1), date(2026, 8, 1), "HR"),
    },

    # ── SEC_01 — AMBER (score 80) ─────────────────────────────────────────────
    {
        "ref": "SEC_01",
        "clauses": [
            _c("service_description",          "yes",  "CISO", date(2025, 12, 1)),
            _c("sla",                           "yes",  "CISO", date(2025, 12, 1)),
            _c("incident_support",              "yes",  "CISO", date(2025, 12, 1)),
            _c("authority_cooperation",         "yes",  "CISO", date(2025, 12, 1)),
            _c("audit_rights",                  "no",   "CISO", date(2025, 12, 1),
               "Annual report in lieu of audit; no direct audit right"),
            _c("subcontracting_controls",       "yes",  "CISO", date(2025, 12, 1)),
            _c("data_return",                   "yes",  "CISO", date(2025, 12, 1)),
            _c("business_continuity",           "no",   "CISO", date(2025, 12, 1),
               "BC plan provided annually; no testing obligation"),
            _c("exit_support",                  "no",   "CISO", date(2025, 12, 1),
               "No exit support clause — raise at renewal"),
            _c("termination_rights",            "yes",  "CISO", date(2025, 12, 1)),
            _c("location_change_notification",  "yes",  "CISO", date(2025, 12, 1)),
            _c("data_processing_location",      "yes",  "CISO", date(2025, 12, 1)),
        ],
        "risk": _risk("high", "medium", "medium",
                      date(2025, 12, 1), date(2026, 6, 1), "CISO"),
    },

    # ── DESK_01 — AMBER (score 80) ────────────────────────────────────────────
    {
        "ref": "DESK_01",
        "clauses": [
            _c("service_description",          "yes",     "IT", date(2025, 9, 1)),
            _c("sla",                           "yes",     "IT", date(2025, 9, 1)),
            _c("incident_support",              "yes",     "IT", date(2025, 9, 1)),
            _c("authority_cooperation",         "partial", "IT", date(2025, 9, 1)),
            _c("audit_rights",                  "no",      "IT", date(2025, 9, 1)),
            _c("subcontracting_controls",       "partial", "IT", date(2025, 9, 1)),
            _c("data_return",                   "yes",     "IT", date(2025, 9, 1)),
            _c("business_continuity",           "no",      "IT", date(2025, 9, 1)),
            _c("exit_support",                  "no",      "IT", date(2025, 9, 1)),
            _c("termination_rights",            "yes",     "IT", date(2025, 9, 1)),
            _c("location_change_notification",  "yes",     "IT", date(2025, 9, 1)),
            _c("data_processing_location",      "yes",     "IT", date(2025, 9, 1)),
        ],
        "risk": _risk("low", "high", "low",
                      date(2025, 9, 1), date(2026, 3, 1), "IT"),
    },

    # ── TELCO_01 — AMBER (score 70) ───────────────────────────────────────────
    {
        "ref": "TELCO_01",
        "clauses": [
            _c("service_description",          "yes",           "IT", date(2025, 8, 1)),
            _c("sla",                           "yes",           "IT", date(2025, 8, 1)),
            _c("incident_support",              "yes",           "IT", date(2025, 8, 1)),
            _c("authority_cooperation",         "no",            "IT", date(2025, 8, 1)),
            _c("audit_rights",                  "no",            "IT", date(2025, 8, 1)),
            _c("subcontracting_controls",       "no",            "IT", date(2025, 8, 1),
               "Standard ISP terms; no subcontracting visibility"),
            _c("data_return",                   "not_applicable","IT", date(2025, 8, 1)),
            _c("business_continuity",           "partial",       "IT", date(2025, 8, 1)),
            _c("exit_support",                  "no",            "IT", date(2025, 8, 1),
               "Standard 30-day termination; no transition support"),
            _c("termination_rights",            "yes",           "IT", date(2025, 8, 1)),
            _c("location_change_notification",  "partial",       "IT", date(2025, 8, 1)),
            _c("data_processing_location",      "yes",           "IT", date(2025, 8, 1)),
        ],
        "risk": _risk("medium", "medium", "low",
                      date(2025, 8, 1), date(2026, 2, 1), "IT"),
    },

    # ── PFS_02 — AMBER (score 80) ─────────────────────────────────────────────
    {
        "ref": "PFS_02",
        "clauses": [
            _c("service_description",          "yes",     "Legal", date(2025, 7, 1)),
            _c("sla",                           "yes",     "Legal", date(2025, 7, 1)),
            _c("incident_support",              "yes",     "Legal", date(2025, 7, 1)),
            _c("authority_cooperation",         "no",      "Legal", date(2025, 7, 1)),
            _c("audit_rights",                  "partial", "Legal", date(2025, 7, 1)),
            _c("subcontracting_controls",       "yes",     "Legal", date(2025, 7, 1)),
            _c("data_return",                   "yes",     "Legal", date(2025, 7, 1)),
            _c("business_continuity",           "no",      "Legal", date(2025, 7, 1)),
            _c("exit_support",                  "partial", "Legal", date(2025, 7, 1)),
            _c("termination_rights",            "yes",     "Legal", date(2025, 7, 1)),
            _c("location_change_notification",  "yes",     "Legal", date(2025, 7, 1)),
            _c("data_processing_location",      "yes",     "Legal", date(2025, 7, 1)),
        ],
        "risk": _risk("high", "low", "high",
                      date(2025, 7, 1), date(2026, 1, 1), "Third-Party Risk"),
    },

    # ── PFS_01 — RED (score 35) ───────────────────────────────────────────────
    {
        "ref": "PFS_01",
        "clauses": [
            _c("service_description",          "yes",     "Compliance", date(2024, 9, 1)),
            _c("sla",                           "partial", "Compliance", date(2024, 9, 1)),
            _c("incident_support",              "no",      "Compliance", date(2024, 9, 1),
               "No incident support obligation — REMEDIATION REQUIRED"),
            _c("authority_cooperation",         "no",      "Compliance", date(2024, 9, 1),
               "No regulatory cooperation clause — REMEDIATION REQUIRED"),
            _c("audit_rights",                  "no",      "Compliance", date(2024, 9, 1),
               "Standard SaaS EULA only — REMEDIATION REQUIRED"),
            _c("subcontracting_controls",       "no",      "Compliance", date(2024, 9, 1),
               "No subcontracting transparency — REMEDIATION REQUIRED"),
            _c("data_return",                   "partial", "Compliance", date(2024, 9, 1)),
            _c("business_continuity",           "no",      "Compliance", date(2024, 9, 1)),
            _c("exit_support",                  "no",      "Compliance", date(2024, 9, 1),
               "Auto-renewal; no exit support — REMEDIATION REQUIRED"),
            _c("termination_rights",            "yes",     "Compliance", date(2024, 9, 1)),
            _c("location_change_notification",  "no",      "Compliance", date(2024, 9, 1)),
            _c("data_processing_location",      "partial", "Compliance", date(2024, 9, 1)),
        ],
        "risk": _risk(
            "critical", "low", "high",
            date(2024, 9, 1), date(2025, 3, 1), "Third-Party Risk",
            notes="Contract pre-dates DORA. Full renegotiation required at next renewal (2025-06-30).",
        ),
    },

    # ── DocSys_02 — GREY (no clauses) ────────────────────────────────────────
    {"ref": "DocSys_02", "clauses": [], "risk": None},

    # ── TELCO_02 — GREY (no clauses) ─────────────────────────────────────────
    {"ref": "TELCO_02", "clauses": [], "risk": None},
]


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    enriched = 0
    with Session(engine) as db:
        for entry in CONTRACT_DATA:
            ref = entry["ref"]

            contract = db.query(Contract).filter(Contract.contract_ref == ref).first()
            if not contract:
                print(f"  WARNING: Contract {ref!r} not found — upload the Excel first")
                continue

            # Skip if clauses already exist (idempotent)
            existing = db.query(ContractClause).filter(
                ContractClause.contract_id == contract.id
            ).first()
            if existing:
                print(f"  SKIP: {ref} already has clause data")
                continue

            # Insert clause records
            for cl in entry["clauses"]:
                db.add(ContractClause(contract_id=contract.id, **cl))

            # Insert risk assessment if provided
            if entry["risk"]:
                existing_ra = db.query(RiskAssessment).filter(
                    RiskAssessment.contract_id == contract.id
                ).first()
                if not existing_ra:
                    db.add(RiskAssessment(contract_id=contract.id, **entry["risk"]))

            db.commit()
            clause_count = len(entry["clauses"])
            print(f"  OK: {ref} — {clause_count} clauses" +
                  (" + risk assessment" if entry["risk"] else " (GREY — no clauses)"))
            enriched += 1

    print(f"\nEnriched {enriched} contracts with DORA compliance data")


if __name__ == "__main__":
    main()
