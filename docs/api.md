# SentinelX API Reference

The SentinelX backend exposes a versioned REST API under `/api/v1/*`. Interactive
documentation is available at `/docs` (Swagger UI) and `/redoc` once the server
is running.

## Base URL

- Development: `http://127.0.0.1:8000/api/v1`

All responses are JSON. Errors follow the structure:

```json
{
  "error": "<error_code>",
  "message": "<human readable message>",
  "details": {}
}
```

## Authentication

Authentication uses JWT Bearer tokens. Obtain a token via `POST /auth/login` and
include it in the `Authorization: Bearer <token>` header.

Passwords are hashed with bcrypt. Password hashes and tokens are never returned
by any endpoint.

### Endpoints

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/auth/login` | Authenticate and receive a JWT | No | — |
| POST | `/auth/register` | Create a user (admin only) | Yes | admin |
| GET | `/auth/me` | Current user profile | Yes | any |
| POST | `/auth/logout` | Acknowledge logout | Yes | any |

## Users

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/users/` | List users | Yes | admin |
| GET | `/users/{id}` | Get a user | Yes | admin |
| POST | `/users/` | Create a user | Yes | admin |
| PATCH | `/users/{id}` | Update a user | Yes | admin |
| DELETE | `/users/{id}` | Delete a user | Yes | admin |

## Security Events

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/events/` | List events (paginated, filterable) | Yes | any |
| GET | `/events/{id}` | Get a single event | Yes | any |
| GET | `/events/stats/summary` | Event counts by severity | Yes | any |

Query parameters for `GET /events/`: `source`, `severity`, `event_type`,
`username`, `source_ip`, `start_time`, `end_time`, `search`, `page`, `page_size`.

## Log Ingestion

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/ingestion/upload` | Upload and ingest a log file | Yes | any |
| GET | `/ingestion/sources` | List supported source types | Yes | any |

Supported files: Linux auth/syslog, Windows event exports, JSON (lines or
array), CSV. The response is an ingestion report with accepted / rejected /
skipped / duplicates counts. Malformed records are rejected with a reason and
are never silently discarded.

## Detection Rules

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/rules/` | List detection rules | Yes | any |
| GET | `/rules/{id}` | Get a rule | Yes | any |
| POST | `/rules/` | Create a rule | Yes | admin |
| PATCH | `/rules/{id}` | Update a rule | Yes | admin |
| DELETE | `/rules/{id}` | Delete a rule | Yes | admin |
| POST | `/rules/evaluate` | Run detection engine | Yes | any |

## Alerts

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/alerts/` | List alerts (paginated, filterable) | Yes | any |
| GET | `/alerts/{id}` | Get an alert | Yes | any |
| POST | `/alerts/` | Create an alert | Yes | any |
| PATCH | `/alerts/{id}` | Update an alert (status, assignee) | Yes | any |

Alert statuses: `new`, `investigating`, `escalated`, `resolved`, `false_positive`.

## Incidents

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/incidents/` | List incidents | Yes | any |
| GET | `/incidents/{id}` | Get an incident | Yes | any |
| POST | `/incidents/` | Create an incident | Yes | any |
| PATCH | `/incidents/{id}` | Update an incident | Yes | any |
| POST | `/incidents/{id}/notes` | Add an investigation note | Yes | any |

Incident lifecycle: `detection` → `triage` → `investigation` → `containment` →
`recovery` → `closure`. Invalid transitions are rejected.

## Threat Intelligence

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/intelligence/indicators` | List threat indicators | Yes | any |
| GET | `/intelligence/enrich/{type}/{value}` | Enrich an IOC | Yes | any |
| POST | `/intelligence/indicators` | Upsert an indicator | Yes | any |

Types: `ip`, `domain`, `hash`, `url`. Enrichment returns `available` (true/false),
`classification`, `reputation`, `source`, `confidence`, `first_seen`, `last_seen`.
`available=false` means no intelligence exists — explicitly not a clean result.

## MITRE ATT&CK

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/mitre/techniques` | List MITRE techniques | Yes | any |
| GET | `/mitre/mapping` | Rule → technique mapping | Yes | any |

## Reports

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/reports/generate` | Generate a report (pdf/json/csv) | Yes | any |
| GET | `/reports/` | List generated reports | Yes | any |

## Dashboard

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/dashboard/stats` | Dashboard statistics | Yes | any |
| GET | `/dashboard/events-over-time` | Events over time (days query) | Yes | any |

## Security

- CORS is restricted to configured origins (`CORS_ORIGINS` env var).
- Security headers applied: `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Content-Security-Policy`.
- Rate limiting on auth and ingestion endpoints.
- All authenticated actions are written to the audit log.
