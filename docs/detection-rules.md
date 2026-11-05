# SentinelX Detection Rules

Detection rules are modular, independently testable, and mapped to MITRE ATT&CK
tactics and techniques. Each rule has a configurable threshold, time window,
severity, and enabled/disabled setting.

## Default Detection Rules

Seeded on database initialization:

| # | Rule Name | Type | Technique | Tactic | Severity | Threshold | Window (s) |
|---|-----------|------|-----------|--------|----------|-----------|------------|
| 1 | Brute-force authentication attempts | brute_force | T1110 | Credential Access | high | 5 | 300 |
| 2 | Repeated failed logins | failed_login | T1110 | Credential Access | medium | 5 | 300 |
| 3 | Privilege escalation indicators | privilege_escalation | T1548 | Privilege Escalation | high | 1 | 300 |
| 4 | Unusual administrative activity | admin_activity | T1078 | Persistence / PrivEsc / Defense Evasion | medium | 3 | 300 |
| 5 | Repeated access-denied events | access_denied | T1087 | Discovery | medium | 5 | 300 |
| 6 | Suspicious process execution indicators | suspicious_process | T1059 | Execution | high | 1 | 300 |
| 7 | Known malicious IOC matches | ioc_match | T1071 | Command and Control | critical | 1 | 300 |
| 8 | Unusual event frequency | frequency | T1499 | Impact | medium | 100 | 300 |
| 9 | Multiple security failures from one source | multi_failure | T1110 | Credential Access | high | 3 | 300 |

## Rule Fields

- `name` — unique rule name.
- `description` — human-readable description.
- `mitre_technique_id` — MITRE ATT&CK technique ID (e.g. T1110).
- `mitre_tactic` — MITRE ATT&CK tactic (e.g. Credential Access).
- `severity` — low | medium | high | critical.
- `threshold` — event count required to trigger.
- `time_window` — sliding window in seconds.
- `enabled` — whether the rule is active.
- `rule_type` — determines which evaluator is used.
- `config` — extra rule-specific configuration (JSON).

## How Detection Works

1. The detection engine loads all enabled `DetectionRule` records.
2. For each rule, the matching evaluator runs against recent normalized
   `SecurityEvent` records within the rule's time window.
3. When a rule matches, an `Alert` is created with the rule's severity.
4. Alerts are de-duplicated by rule + match key, so re-running detection does
   not create duplicate alerts for the same condition.

No suspicious commands or payloads are ever executed during analysis.

## Evaluators

Each `rule_type` maps to a pure function in `backend/app/detection/evaluators.py`:

- `brute_force` — repeated auth failures from one source IP.
- `failed_login` — repeated failed logins for one user.
- `privilege_escalation` — sudo/su/privilege events.
- `admin_activity` — repeated admin events from one source.
- `access_denied` — repeated access-denied events from one source.
- `suspicious_process` — suspicious process execution events.
- `ioc_match` — events matching known malicious indicators.
- `frequency` — unusually high event frequency from one source.
- `multi_failure` — multiple failure types from one source.

## Adding a Rule

Rules can be added via the API (`POST /api/v1/rules/`, admin only) or the
Detection Rules page. Provide `rule_type` matching one of the evaluators above.

MITRE ATT&CK identifiers used are accurate identifiers from the official MITRE
ATT&CK knowledge base.
