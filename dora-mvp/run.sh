#!/bin/bash
echo "Starting DORA Platform..."
cd dora-mvp/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt -q
uvicorn app.main:app --reload --port 8000 &
cd ../frontend
npm install -s && npm run dev &
echo "Backend: http://localhost:8000 | Docs: http://localhost:8000/docs"
echo "Frontend: http://localhost:5173"
wait
