# DORA Contract Metadata Platform — Local MVP

Local-first DORA Platform for ICT third-party contract metadata.
Implements the DORA Register of Information model (DORA Article 30, ITS on RoI).

## Quick start

**Mac/Linux:** `bash run.sh`  
**Windows:** `run.bat`

## First-time demo setup

1. Start both services
2. Open http://localhost:5173
3. Upload Sample_Data.xlsx via the dashboard upload button
4. In a new terminal: `cd dora-mvp/backend && python seed_demo_compliance.py`
5. Refresh the dashboard

## URLs
- Dashboard: http://localhost:5173
- API docs:   http://localhost:8000/docs
