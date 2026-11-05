# SentinelX — Advanced SOC Platform

An open-source security monitoring and threat detection platform that collects, normalizes, analyzes, correlates, and visualizes security events to help security analysts identify suspicious activity and investigate incidents.

## Status

Milestones 1–7 complete: project scaffolding, architecture docs, backend configuration, database models, authentication, log ingestion & normalization, detection engine, alert management, incident response, threat intelligence, MITRE ATT&CK integration, and a full React frontend.

## Features

- **Security Dashboard** — real-time statistics and charts from actual application data
- **Log Collection** — upload and parse Linux auth/syslog, Windows event exports, JSON and CSV security events
- **Event Normalization** — common security event schema with original raw event preserved
- **Threat Detection Engine** — configurable rules (brute force, failed logins, privilege escalation, IOC matches, etc.)
- **MITRE ATT&CK Integration** — tactic/technique mapping for detection rules
- **Alert Management** — create, filter, search, assign, resolve alerts (New → Investigating → Escalated → Resolved / False Positive)
- **Incident Response** — incident lifecycle (Detection → Triage → Investigation → Containment → Recovery → Closure)
- **Threat Intelligence** — IOC enrichment (IP, domain, hash, URL) with classification, reputation, confidence
- **User Management** — JWT auth, RBAC (admin/analyst), bcrypt password hashing, audit logging
- **Report Generation** — PDF, JSON, CSV reports
- **REST API** — versioned, OpenAPI documented (`/docs`), pagination, filtering, rate limiting

## Technology Stack

**Frontend:** React, TypeScript, Vite, Tailwind CSS, Recharts, Lucide icons  
**Backend:** Python, FastAPI, SQLAlchemy, Pydantic, Uvicorn  
**Database:** SQLite (default), PostgreSQL (optional production)  
**Security:** JWT authentication, RBAC, bcrypt password hashing, rate limiting, audit logs  
**Testing:** Pytest, Vitest, React Testing Library  
**DevOps:** Git, GitHub Actions, Docker, Docker Compose

## Architecture

```text
+---------------------+      HTTP/JSON      +---------------------------+
|   Frontend (React)  | <-----------------> |   Backend (FastAPI)       |
|   Vite + TypeScript |      (port 5173)    |   Uvicorn (port 8000)     |
|   Tailwind CSS      |                     |   SQLAlchemy + SQLite     |
|   Recharts          |                     |   JWT + RBAC auth         |
+---------------------+                     +---------------------------+
        |                                           |
        |                                           v
        |                                 +------------------+
        |                                 |  Detection Engine|
        |                                 |  (modular rules) |
        |                                 +------------------+
        |                                           |
        |                                 +------------------+
        |                                 |   Ingestion      |
        |                                 |  (log parsing)   |
        |                                 +------------------+
        |                                           |
        |                                 +------------------+
        +---------------------------------|  SQLite DB       |
                                          +------------------+
```

## Prerequisites

- Python 3.10+ (3.13 recommended)
- Node.js 18+ / npm
- Git
- 4–8 GB RAM

No paid APIs or commercial security services required.

## Quick Start

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy ..\.env.example .env
# edit .env (set SECRET_KEY)
python -m app.core.init_db
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173
- API docs: http://127.0.0.1:8000/docs

## Sample Dataset

Synthetic sample datasets are provided under `data/sample/` (`auth_logs_sample.json`,
`syslog_sample.txt`, `events_sample.csv`). Import them via the Log Ingestion page to
exercise detection rules, alerts, and dashboards. All data is synthetic.

## Documentation

- `docs/architecture.md` — System architecture
- `docs/installation.md` — Installation guide
- `docs/security.md` — Security assessment & threat model
- `docs/api.md` — API reference
- `docs/detection-rules.md` — Detection rule reference

## Testing

```powershell
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Screenshots

Screenshots are captured from the actual running application and added to the
repository as the UI is finalized.

## CI

GitHub Actions workflow (`.github/workflows/ci.yml`) runs backend tests, frontend
tests, TypeScript checks, Python/Node dependency auditing, and build verification
on every push and pull request.

## License

MIT License — see `LICENSE`.

## Roadmap

See Milestones 8–10 in the project master prompt: authentication hardening,
testing/debugging/performance optimization, documentation, Docker, and release.
