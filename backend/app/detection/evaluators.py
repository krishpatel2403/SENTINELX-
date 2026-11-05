'''Rule evaluators.

Each evaluator is a pure function:
    evaluator(rule, events, db) -> list[dict]

where each dict describes a detected match:
    {
        "key": str,              # grouping key used for dedup
        "matched_event_ids": [int],
        "count": int,
        "description": str,      # human-readable detection summary
    }

No suspicious commands or payloads are ever executed.
'''

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta, timezone
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.detection_rule import DetectionRule
from app.models.security_event import SecurityEvent


def _events_within_window(events, window_seconds):
    if not events:
        return []
    latest = max((e.timestamp for e in events if e.timestamp), default=None)
    if latest is None:
        return []
    cutoff = latest - timedelta(seconds=window_seconds)
    return [e for e in events if e.timestamp and e.timestamp >= cutoff]


def _group_by(events, attr):
    groups = defaultdict(list)
    for e in events:
        groups[getattr(e, attr, None)].append(e)
    return groups


# ---------------------------------------------------------------------------
# Individual rule evaluators
# ---------------------------------------------------------------------------

def brute_force_evaluator(rule, events, db):
    '''Repeated authentication failures from a single source IP (T1110).'''
    matches = []
    window = rule.time_window or 300
    candidates = _events_within_window(events, window)
    failures = [e for e in candidates
                if (e.event_type or "").endswith("_failure")
                or (e.severity or "") in ("high", "critical")
                or "failure" in (e.description or "").lower()
                or "failed" in (e.description or "").lower()]
    groups = _group_by(failures, "source_ip")
    for source_ip, group in groups.items():
        if not source_ip:
            continue
        if len(group) >= rule.threshold:
            matches.append({
                "key": "brute_force:" + source_ip,
                "matched_event_ids": [e.id for e in group],
                "count": len(group),
                "description": (
                    "Brute-force authentication attempts: " + str(len(group)) +
                    " failed authentication events from source IP " + source_ip +
                    " within " + str(window) + "s."
                ),
            })
    return matches


def failed_login_evaluator(rule, events, db):
    '''Repeated failed logins for a single user account (T1110).'''
    matches = []
    window = rule.time_window or 300
    candidates = _events_within_window(events, window)
    failures = [e for e in candidates
                if (e.event_type or "").endswith("_failure")
                or "failed" in (e.description or "").lower()
                or "failure" in (e.description or "").lower()]
    groups = _group_by(failures, "username")
    for username, group in groups.items():
        if not username:
            continue
        if len(group) >= rule.threshold:
            matches.append({
                "key": "failed_login:" + username,
                "matched_event_ids": [e.id for e in group],
                "count": len(group),
                "description": (
                    "Repeated failed logins: " + str(len(group)) +
                    " failed login events for user " + username +
                    " within " + str(window) + "s."
                ),
            })
    return matches


def privilege_escalation_evaluator(rule, events, db):
    '''Privilege escalation indicators such as sudo/su events (T1548).'''
    matches = []
    window = rule.time_window or 300
    candidates = _events_within_window(events, window)
    esc = [e for e in candidates
           if (e.event_type or "").endswith("_escalation")
           or "sudo" in (e.description or "").lower()
           or "privilege" in (e.description or "").lower()]
    groups = _group_by(esc, "username") or _group_by(esc, "source_ip")
    for key, group in groups.items():
        if not key:
            continue
        if len(group) >= rule.threshold:
            matches.append({
                "key": "privilege_escalation:" + key,
                "matched_event_ids": [e.id for e in group],
                "count": len(group),
                "description": (
                    "Privilege escalation indicators: " + str(len(group)) +
                    " events for " + key + " within " + str(window) + "s."
                ),
            })
    return matches


def admin_activity_evaluator(rule, events, db):
    '''Unusual administrative activity (T1078).'''
    matches = []
    window = rule.time_window or 300
    candidates = _events_within_window(events, window)
    admin = [e for e in candidates
             if (e.event_type or "").endswith("_admin")
             or "admin" in (e.description or "").lower()
             or "administrator" in (e.description or "").lower()]
    groups = _group_by(admin, "source_ip")
    for source_ip, group in groups.items():
        if not source_ip:
            continue
        if len(group) >= rule.threshold:
            matches.append({
                "key": "admin_activity:" + source_ip,
                "matched_event_ids": [e.id for e in group],
                "count": len(group),
                "description": (
                    "Unusual administrative activity: " + str(len(group)) +
                    " admin events from " + source_ip + " within " + str(window) + "s."
                ),
            })
    return matches


def access_denied_evaluator(rule, events, db):
    '''Repeated access-denied events from a single source (T1210).'''
    matches = []
    window = rule.time_window or 300
    candidates = _events_within_window(events, window)
    denied = [e for e in candidates
              if "denied" in (e.description or "").lower()
              or "access-denied" in (e.description or "").lower()
              or (e.event_type or "").endswith("_denied")]
    groups = _group_by(denied, "source_ip")
    for source_ip, group in groups.items():
        if not source_ip:
            continue
        if len(group) >= rule.threshold:
            matches.append({
                "key": "access_denied:" + source_ip,
                "matched_event_ids": [e.id for e in group],
                "count": len(group),
                "description": (
                    "Repeated access-denied events: " + str(len(group)) +
                    " events from source IP " + source_ip + " within " + str(window) + "s."
                ),
            })
    return matches


def suspicious_process_evaluator(rule, events, db):
    '''Suspicious process execution indicators (T1059).'''
    matches = []
    window = rule.time_window or 300
    candidates = _events_within_window(events, window)
    procs = [e for e in candidates
             if (e.event_type or "").endswith("_process")
             or "process" in (e.description or "").lower()
             or "execution" in (e.description or "").lower()]
    groups = _group_by(procs, "source_ip")
    for source_ip, group in groups.items():
        if not source_ip:
            continue
        if len(group) >= rule.threshold:
            matches.append({
                "key": "suspicious_process:" + source_ip,
                "matched_event_ids": [e.id for e in group],
                "count": len(group),
                "description": (
                    "Suspicious process execution: " + str(len(group)) +
                    " events from " + source_ip + " within " + str(window) + "s."
                ),
            })
    return matches


def ioc_match_evaluator(rule, events, db):
    '''Known malicious IOC matches (T1071).'''
    from app.models.threat_indicator import ThreatIndicator
    matches = []
    malicious = db.query(ThreatIndicator).filter(
        ThreatIndicator.classification == "malicious").all()
    indicators = {i.indicator_value for i in malicious}
    if not indicators:
        return []
    window = rule.time_window or 300
    candidates = _events_within_window(events, window)
    hits = []
    for e in candidates:
        haystack = " ".join(filter(None, [
            e.source_ip or "", e.destination_ip or "", e.hostname or "",
            e.description or "", str(e.raw_event or {})]))
        for ind in indicators:
            if ind in haystack:
                hits.append(e)
                break
    if hits:
        matches.append({
            "key": "ioc_match",
            "matched_event_ids": [e.id for e in hits],
            "count": len(hits),
            "description": (
                "Known malicious IOC match: " + str(len(hits)) +
                " event(s) reference a known malicious indicator of compromise."
            ),
        })
    return matches


def frequency_evaluator(rule, events, db):
    '''Unusual event frequency from a single source (T1499).'''
    matches = []
    window = rule.time_window or 300
    candidates = _events_within_window(events, window)
    groups = _group_by(candidates, "source_ip")
    for source_ip, group in groups.items():
        if not source_ip:
            continue
        if len(group) >= rule.threshold:
            matches.append({
                "key": "frequency:" + source_ip,
                "matched_event_ids": [e.id for e in group],
                "count": len(group),
                "description": (
                    "Unusual event frequency: " + str(len(group)) +
                    " events from source IP " + source_ip + " within " + str(window) + "s."
                ),
            })
    return matches


def multi_failure_evaluator(rule, events, db):
    '''Multiple security failure types from one source (T1110).'''
    matches = []
    window = rule.time_window or 300
    candidates = _events_within_window(events, window)
    failures = [e for e in candidates
                if (e.severity or "") in ("high", "critical")
                or "failure" in (e.description or "").lower()
                or "failed" in (e.description or "").lower()
                or "denied" in (e.description or "").lower()]
    groups = _group_by(failures, "source_ip")
    for source_ip, group in groups.items():
        if not source_ip:
            continue
        types = {e.event_type for e in group if e.event_type}
        if len(group) >= rule.threshold and len(types) >= 2:
            matches.append({
                "key": "multi_failure:" + source_ip,
                "matched_event_ids": [e.id for e in group],
                "count": len(group),
                "description": (
                    "Multiple security failures from one source: " + str(len(group)) +
                    " events across " + str(len(types)) + " types from " +
                    source_ip + " within " + str(window) + "s."
                ),
            })
    return matches


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

RULE_EVALUATORS = {
    "brute_force": brute_force_evaluator,
    "failed_login": failed_login_evaluator,
    "privilege_escalation": privilege_escalation_evaluator,
    "admin_activity": admin_activity_evaluator,
    "access_denied": access_denied_evaluator,
    "suspicious_process": suspicious_process_evaluator,
    "ioc_match": ioc_match_evaluator,
    "frequency": frequency_evaluator,
    "multi_failure": multi_failure_evaluator,
}
