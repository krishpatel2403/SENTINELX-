# SentinelX Installation

## Prerequisites

| Requirement | Minimum | Recommended | Notes |
|-------------|---------|-------------|-------|
| Python | 3.10+ | 3.13 | Backend runtime |
| pip | 23+ | latest | Python package manager |
| Node.js | 18+ | 20+ | Frontend runtime |
| npm | 9+ | latest | Frontend package manager |
| Git | 2.30+ | latest | Version control |
| RAM | 4 GB | 8 GB | Development machine |
| Disk | 2 GB free | 5 GB free | Logs + sample data |
| Docker | optional | optional | Containerized deployment (not tested in this environment) |

No paid APIs or commercial security services are required. All detection and intelligence work offline by default; optional public threat-intel feeds require explicit configuration.

## Supported operating systems

- Windows 10/11 (PowerShell / CMD)
- Linux (Ubuntu, Debian, RHEL derivatives)
- macOS (Intel / Apple Silicon) — untested but expected to work

## Quick start (native)

### 1. Clone / create the repository

```powershell
# Windows PowerShell
cd C:\Users\krish\Downloads
# repository contents should already be present in this folder
```

### 2. Backend setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp ../.env.example .env
# edit .env as needed (SECRET_KEY, etc.)
python -m app.core.init_db   # initialize SQLite database + seed default rules
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Frontend setup

```powershell
cd frontend
npm install
npm run dev   # Vite dev server on http://localhost:5173
```

### 4. Access the application

- Frontend: http://localhost:5173
- Backend API: http://127.0.0.1:8000
- Interactive API docs: http://127.0.0.1:8000/docs
- Alternative docs: http://127.0.0.1:8000/redoc

## Environment variables

Copy `.env.example` to `.env` and adjust. Never commit real secrets.

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (required) | JWT signing secret — generate a strong random value |
| `ALGORITHM` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Access token lifetime |
| `DATABASE_URL` | `sqlite:///./sentinelx.db` | SQLAlchemy database URL |
| `POSTGRES_SERVER` | — | Optional production PostgreSQL host |
| `POSTGRES_USER` | — | Optional production PostgreSQL user |
| `POSTGRES_PASSWORD` | — | Optional production PostgreSQL password |
| `POSTGRES_DB` | sentinelx | Optional production database name |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed frontend origins |
| `MAX_UPLOAD_SIZE_MB` | 50 | Max log upload size |
| `RATE_LIMIT_AUTH` | 10/min | Auth endpoint rate limit |
| `THREAT_FEED_ENABLED` | false | Enable optional public threat-intel feeds |
| `THREAT_FEED_URL` | — | Optional public threat-intel feed URL |

## Sample dataset

A sample synthetic security-event dataset is provided under `data/sample/`. Import it via the Log Ingestion page to exercise detection rules, alerts, and dashboards. The dataset contains both normal and suspicious activity.

## Docker deployment (documented, not tested here)

```powershell
docker-compose up --build
```

Services: backend, frontend, (optional) postgres. See `docker-compose.yml`.

## Verifying the install

1. Backend health: `GET http://127.0.0.1:8000/health` → `{"status":"ok"}`
2. Open API docs at `/docs`.
3. Log in with the seeded admin account (see seeds in `backend/app/core/init_db.py`).
4. Import `data/sample/auth_logs_sample.json` through Log Ingestion.
5. Confirm events, alerts, and dashboard statistics appear.
