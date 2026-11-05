# SentinelX Sample Dataset

This directory contains synthetic security event datasets for demonstration and testing.
All data is synthetic — no real credentials, production secrets, or unauthorized scan data.

## auth_logs_sample.json

Synthetic Linux authentication log events (JSON lines format, one JSON object per line).
Contains both normal activity and suspicious activity (brute-force attempts, privilege escalation).

Import via the Log Ingestion page with source type "json" or "linux_auth".

## syslog_sample.txt

Synthetic syslog / auth log lines in traditional syslog format.

Import via the Log Ingestion page with source type "linux_auth" or "syslog".

## events_sample.csv

Synthetic security events in CSV format.

Import via the Log Ingestion page with source type "csv".

## Usage

1. Start the backend (`uvicorn app.main:app --reload`).
2. Start the frontend (`npm run dev`).
3. Log in as admin (admin / ChangeMeAdmin123!).
4. Go to Log Ingestion and upload one of the sample files.
5. Observe the ingestion report (accepted / rejected / skipped counts).
6. Run detection evaluation (Detection Rules → Evaluate Rules) to generate alerts.
7. View alerts, incidents, and the dashboard.
