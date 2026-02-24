# Data Manager Fullstack

Fullstack data manager with:
- `data_manager` Python package (multi-format DataFrame I/O)
- FastAPI backend (`backend/`)
- React + TypeScript + Vite + Tailwind frontend (`frontend/`)

## Project Layout

- `data_manager/`: core Python package
- `backend/`: FastAPI API server
- `frontend/`: React UI
- `docker-compose.yml`: full stack containers

## Backend (local)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: `http://localhost:8000/docs`

## Frontend (local)

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

## Docker (full stack)

```bash
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

## Existing Package Tests

```bash
python3 -m pytest tests/ -v
```
