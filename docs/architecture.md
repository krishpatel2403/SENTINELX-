# SentinelX System Architecture

## 1. Overview

SentinelX is a modular, lightweight, self-hosted Security Operations Center (SOC) and Security Information and Event Management (SIEM) platform. It collects, normalizes, analyzes, correlates, and visualizes security events so analysts can identify suspicious activity and investigate incidents.

The application runs locally with **no paid APIs or commercial security services required**. SQLite is the default database; PostgreSQL is supported as an optional production configuration.

## 2. High-Level Architecture

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

Deployed via Docker Compose (optional) or run natively.
```

### Component responsibilities

| Component | Responsibility |
|-----------|----------------|
| **Frontend** | SOC dashboard, event browsing, log ingestion UI, detection rule management, alert/incident workflows, threat intelligence, MITRE ATT&CK mapping, report generation, user management, settings |
| **Backend API** | Versioned REST API (`/api/v1/*`), authentication, authorization, input validation, rate limiting, audit logging, centralized exception handling |
| **Database** | Persistent store for users, events, rules, alerts, incidents, indicators, audit logs, report records |
| **Detection Engine** | Evaluates configurable detection rules against normalized events, emits alerts |
| **Ingestion Pipeline** | Parses uploaded log files, normalizes to common schema, deduplicates, produces ingestion report |
| **Intelligence Module** | IOC enrichment (IP, domain, hash, URL) using optional public feeds |
| **Reports Module** | Generates PDF/JSON/CSV security reports |

## 3. Module-to-Folder Mapping

| Module | Backend location | Frontend location |
|--------|------------------|-------------------|
| A. Security Dashboard | `backend/app/api/dashboard.py`, `services/dashboard.py` | `frontend/src/pages/Dashboard.tsx` |
| B. Log Collection | `backend/app/ingestion/`, `api/ingestion.py` | `frontend/src/pages/LogIngestion.tsx` |
| C. Event Normalization | `backend/app/ingestion/normalization.py`, `models/security_event.py` | `frontend/src/pages/SecurityEvents.tsx` |
| D. Threat Detection | `backend/app/detection/`, `api/rules.py` | `frontend/src/pages/DetectionRules.tsx` |
| E. MITRE ATT&CK | `backend/app/api/mitre.py`, `services/mitre.py` | `frontend/src/pages/MitreAttck.tsx` |
| F. Alert Management | `backend/app/api/alerts.py`, `services/alerts.py` | `frontend/src/pages/AlertManagement.tsx` |
| G. Incident Response | `backend/app/api/incidents.py`, `services/incidents.py` | `frontend/src/pages/IncidentManagement.tsx` |
| H. Threat Intelligence | `backend/app/intelligence/`, `api/intelligence.py` | `frontend/src/pages/ThreatIntelligence.tsx` |
| I. User Management | `backend/app/api/auth.py`, `api/users.py`, `core/security.py` | `frontend/src/pages/UserManagement.tsx`, `Login.tsx` |
| J. Report Generation | `backend/app/reports/`, `api/reports.py` | `frontend/src/pages/Reports.tsx` |

## 4. Data Flow

1. **Ingestion** — Analyst uploads a log file (Linux auth, syslog, Windows event export, JSON, CSV). The ingestion service parses, validates, normalizes timestamps, identifies the source, deduplicates, and writes `SecurityEvent` records. An ingestion report (accepted/rejected/skipped counts) is returned. Malformed records are never silently discarded.
2. **Normalization** — Every event is stored in the common `SecurityEvent` schema with the original raw event preserved in `raw_event` / `event_metadata` for investigation.
3. **Detection** — The detection engine loads enabled `DetectionRule` entries and evaluates them against recent events. Matches create `Alert` records with severity and MITRE mapping.
4. **Alerting** — Analysts view, filter, search, assign, and annotate alerts. Status lifecycle: New → Investigating → Escalated → Resolved / False Positive.
5. **Incidents** — Related alerts are grouped into `Incident`s following the lifecycle Detection → Triage → Investigation → Containment → Recovery → Closure. No automatic destructive containment.
6. **Intelligence** — IOCs (IP, domain, hash, URL) are enriched with optional public feeds; results carry classification, reputation, source, confidence, first/last seen. Absence of intelligence is explicitly distinguished from a clean result.
7. **Reporting** — Analysts generate PDF/JSON/CSV reports over a time range, including events, detection stats, alerts, incidents, indicators, and recommendations.
8. **Audit** — All authenticated actions are written to `AuditLog` (user, action, resource, IP, timestamp).

## 5. Security Boundaries

- Passwords are hashed with bcrypt; hashes/tokens are never returned by APIs.
- JWT access tokens are short-lived; refresh via re-login.
- Role-Based Access Control (RBAC): `admin` and `analyst` roles; user registration is admin-only.
- File uploads are validated (extension, size, content-type) and stored outside the web root where practical.
- CORS is restricted to configured origins.
- Security headers are applied (X-Content-Type-Options, X-Frame-Options, CSP, HSTS where HTTPS).
- Rate limiting on auth and ingestion endpoints.
- No credentials or secrets committed to the repository (`.env.example` only).
- No destructive containment actions are performed automatically.
- Suspicious commands/payloads are never executed during analysis.

## 6. Deployment Options

| Option | Description |
|--------|-------------|
| Native (Windows/Linux) | Python venv + uvicorn; Node + vite dev server; SQLite default |
| Docker Compose | Backend, frontend, optional PostgreSQL (documented; Docker not available in this build environment) |
| Production | PostgreSQL, HTTPS reverse proxy, environment-based secrets, restricted CORS |
