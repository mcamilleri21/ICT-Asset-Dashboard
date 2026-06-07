@echo off
echo Starting DORA Platform...
cd dora-mvp\backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt -q
start "DORA Backend" cmd /k "call venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
cd ..\frontend
start "DORA Frontend" cmd /k "npm install -s && npm run dev"
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
