# KNOWN ISSUES — DORA Contract Metadata MVP

## Intentional MVP scope limitations (not bugs)

- **No user authentication** — the API and UI are open; add an auth layer (OAuth2/JWT) before production deployment.
- **No file upload for evidence documents** — the `EvidenceFile` model stores a URL reference only; actual document storage (S3, SharePoint) is out of scope for Phase 1.
- **No RoI XML export** — CSV export is available at `GET /api/export/contracts-csv`; the official EBA RoI XML/CSV template is a Phase 2 deliverable.
- **No workflow/approval engine** — clause checklists can be filled in via the API but there is no task assignment, approval routing, or audit trail for changes.
- **Provider LEIs in Sample_Data.xlsx are placeholder values** — identifiers are in the form `PROVIDER-LEI-00X`; real LEI validation via the GLEIF API is a Phase 2 item.
- **TELCO services (connectivity, mobile) have no software asset link in the dependency map** — the Dependency Map sheet does not reference TELCO_01/TELCO_02, so `supported_function` is blank for those services.

---

## Phase 2 roadmap

- **Real LEI validation** — integrate GLEIF `/api/v1/lei-records/{lei}` to validate and enrich provider LEI data at import time.
- **DORA RoI XML/CSV export** — generate the official EBA Register of Information template (both XML and CSV variants) from the stored contract and service data.
- **Evidence document upload** — attach SLA certificates, audit reports, and BCDR plans to contracts with file storage (SharePoint/S3) and a document viewer in the UI.
- **Remediation task assignment and tracking** — create remediation tasks from RED/AMBER clause gaps, assign to owners, track completion, and close with evidence.
- **Notification engine** — automated alerts for expiring contracts (configurable lead time), overdue clause reviews, and outstanding remediation tasks (email / MS Teams webhook).
- **Multi-entity group-level consolidated view** — support multiple `LegalEntity` records with a group dashboard aggregating DORA coverage across all entities in scope.
- **Integration with Asset Relationship Dashboard** — bi-directional sync between the ICT Asset Dashboard D3 graph and the DORA platform so that provider risk ratings are reflected in the force-directed graph overlay without requiring a separate backend call.
