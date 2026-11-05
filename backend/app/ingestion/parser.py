'''Log record parsers.

Each parser takes a raw record (a dict or a string line) and returns a
normalized event dict plus an optional rejection reason. Malformed records are
rejected with a reason -- never silently discarded.
'''

from __future__ import annotations

import csv
import io
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

# Month abbreviation -> number for syslog-style timestamps.
_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

_SYSLOG_RE = re.compile(
    r"^(?P<month>[A-Za-z]{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<host>\S+)\s+(?P<rest>.*)$"
)


def _now_year() -> int:
    return datetime.now(timezone.utc).year


def _parse_syslog_timestamp(month, day, time_str, year):
    try:
        month_num = _MONTHS[month.lower()]
        dt = datetime(year, month_num, int(day),
                      *map(int, time_str.split(":")),
                      tzinfo=timezone.utc)
        return dt
    except (ValueError, KeyError):
        return None


def _extract_ip(text):
    match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text or "")
    return match.group(0) if match else None


def _empty_event():
    return {
        "event_id": None,
        "timestamp": None,
        "source": "unknown",
        "hostname": None,
        "username": None,
        "source_ip": None,
        "destination_ip": None,
        "event_type": "unknown",
        "severity": "low",
        "description": "",
        "raw_event": {},
        "event_metadata": {},
    }


def _make_event_id(source, raw):
    for key in ("event_id", "id", "record_id", "uuid"):
        val = raw.get(key)
        if val:
            return f"{source}:{val}"
    import hashlib
    payload = json.dumps(raw, sort_keys=True).encode()
    return f"{source}:sha256:{hashlib.sha256(payload).hexdigest()[:16]}"


# ---------------------------------------------------------------------------
# Format parsers
# ---------------------------------------------------------------------------

def parse_json_record(line, source):
    try:
        raw = json.loads(line)
    except json.JSONDecodeError as exc:
        return _empty_event(), f"invalid JSON: {exc}"
    if not isinstance(raw, dict):
        return _empty_event(), "JSON record is not an object"
    return _normalize_dict(raw, source), None


def parse_csv_record(row, source):
    try:
        raw = {k: (v if v is not None else "") for k, v in row.items()}
        return _normalize_dict(raw, source), None
    except Exception as exc:
        return _empty_event(), f"csv parse error: {exc}"


def parse_syslog_line(line, source):
    match = _SYSLOG_RE.match(line.strip())
    if not match:
        return _empty_event(), "line does not match syslog format"
    month, day, time_str, host, rest = match.groups()
    timestamp = _parse_syslog_timestamp(month, day, time_str, _now_year())
    event = _empty_event()
    event["timestamp"] = timestamp
    event["source"] = source
    event["hostname"] = host
    event["description"] = rest.strip()
    event["raw_event"] = {"line": line.strip()}
    event["event_metadata"] = {"parser": "syslog", "raw_line": line.strip()}
    lower = rest.lower()
    if "failed password" in lower or "authentication failure" in lower:
        event["event_type"] = "login_failure"
        event["severity"] = "medium"
    elif "accepted password" in lower or "publickey" in lower:
        event["event_type"] = "login_success"
        event["severity"] = "low"
    elif "sudo" in lower:
        event["event_type"] = "privilege_escalation"
        event["severity"] = "high"
    ip = _extract_ip(rest)
    if ip:
        event["source_ip"] = ip
    user_match = re.search(r"\bfor\s+(\S+)\s", rest)
    if user_match:
        event["username"] = user_match.group(1)
    return event, None


def parse_windows_event(raw, source):
    return _normalize_dict(raw, source), None


# ---------------------------------------------------------------------------
# Normalization to the common schema
# ---------------------------------------------------------------------------

def _normalize_dict(raw, source):
    event = _empty_event()
    event["source"] = source
    event["event_id"] = _make_event_id(source, raw)

    aliases = {
        "timestamp": ("timestamp", "time", "event_time", "@timestamp", "generated_at"),
        "hostname": ("hostname", "host", "computer_name", "source_host"),
        "username": ("username", "user", "user_name", "account_name", "target_user"),
        "source_ip": ("source_ip", "src_ip", "source_address", "client_ip"),
        "destination_ip": ("destination_ip", "dest_ip", "dst_ip", "target_ip"),
        "event_type": ("event_type", "type", "event_id", "action", "operation"),
        "severity": ("severity", "level", "priority"),
        "description": ("description", "message", "msg", "details"),
    }

    def pick(field):
        for alias in aliases.get(field, ()):
            if alias in raw and raw[alias] is not None:
                return raw[alias]
        return None

    event["timestamp"] = _parse_timestamp(pick("timestamp"))
    event["hostname"] = pick("hostname") or raw.get("hostname")
    event["username"] = pick("username")
    event["source_ip"] = pick("source_ip")
    event["destination_ip"] = pick("destination_ip")
    event["event_type"] = pick("event_type") or "unknown"
    event["severity"] = str(pick("severity") or "low").lower()
    event["description"] = str(pick("description") or "")
    event["raw_event"] = raw
    event["event_metadata"] = {
        k: v for k, v in raw.items()
        if k not in {a for aliases_list in aliases.values() for a in aliases_list}
    }
    return event


def _parse_timestamp(value):
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    text = str(value).strip()
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        pass
    match = re.match(r"([A-Za-z]{3})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})", text)
    if match:
        return _parse_syslog_timestamp(match.group(1), match.group(2),
                                       match.group(3), _now_year())
    return None


# ---------------------------------------------------------------------------
# File-level parsing helpers
# ---------------------------------------------------------------------------

def iter_json_lines(content):
    return [line for line in content.splitlines() if line.strip()]


def iter_csv_rows(content):
    reader = csv.DictReader(io.StringIO(content))
    return [row for row in reader]
