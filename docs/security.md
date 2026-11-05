# SentinelX Security Assessment & Threat Model

## 1. Threat Model

### Assets
- User accounts and credentials
- Security events, alerts, incidents
- Detection rules and configuration
- Audit logs
- Uploaded log files and evidence

### Threat actors
- Unauthenticated external attacker
- Authenticated low-privilege analyst (insider)
- Compromised analyst workstation

### Threats and mitigations

| Threat | Impact | Mitigation |
|--------|--------|------------|
| Credential theft / brute force on login | Account takeover | bcrypt password hashing, rate limiting on `/auth/login`, short-lived JWT, account lockout guidance |
| JWT theft / replay | Unauthorized API access | Short access-token lifetime, HTTPS-only cookies in production, `HttpOnly`/`SameSite` guidance |
| Privilege escalation (analyst → admin) | Unauthorized rule/config changes | RBAC enforced on every mutating endpoint; `admin`-only registration |
| SQL injection | Data exposure / modification | SQLAlchemy ORM with parameterized queries; no raw string interpolation |
| Cross-site scripting (XSS) | Session theft / UI manipulation | React auto-escapes; Content-Security-Policy header; input validation |
| Cross-site request forgery (CSRF) | State-changing actions | SameSite cookies; token-based auth (Bearer) not cookie-based by default |
| Insecure file upload | Arbitrary file execution / path traversal | Extension allowlist, size limit, safe filename handling, uploads outside web root |
| Sensitive information exposure | Credentials/leakage in logs/API | Password hashes and tokens never returned; structured logging excludes secrets; audit logs redact sensitive fields |
| API abuse / denial of service | Service unavailability | Rate limiting on auth and ingestion; pagination on list endpoints |
| Malicious log content | Detection evasion / parser crash | Malformed records are captured, not silently discarded; ingestion report surfaces rejections |
| Secret leakage in repository | Credential compromise | `.env.example` only; `.gitignore` excludes `.env`, `.venv`, `*.db`; no real secrets committed |
| Destructive containment | Service disruption / data loss | No automatic destructive actions; containment is analyst-initiated and logged |

## 2. Security headers

Applied by FastAPI middleware:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy` (restrictive default)
- `Strict-Transport-Security` when behind HTTPS

## 3. CORS

Restricted to `CORS_ORIGINS` (default `http://localhost:5173`). Credentials allowed only for same-origin/frontend.

## 4. Authentication & authorization

- JWT Bearer auth, HS256, `SECRET_KEY` from environment.
- Roles: `admin` (full access, user registration), `analyst` (read/write events, alerts, incidents; cannot manage users).
- Dependency-based permission checks (`get_current_user`, `require_admin`, `require_analyst`).
- Password reset/registration is admin-restricted.

## 5. Audit logging

Every authenticated action is recorded in `AuditLog`:
`user_id, action, resource_type, resource_id, details, ip_address, created_at`.

Audit logs are append-only in practice and viewable only by admins.

## 6. Evidence integrity

Report records include a SHA-256 checksum of generated report files for integrity verification.

## 7. Limitations

- Single-instance SQLite by default (not suitable for high-concurrency production without PostgreSQL).
- Threat intelligence is offline by default; optional public feeds may be incomplete or delayed.
- No automated response/containment; all response actions are manual.
- This platform is for authorized security environments only. Do not run against systems you do not own or have permission to assess.
