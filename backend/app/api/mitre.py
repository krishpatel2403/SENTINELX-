'''MITRE ATT&CK mapping API.'''

from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_analyst
from app.models.detection_rule import DetectionRule
from app.models.user import User

# Accurate MITRE ATT&CK technique data (official identifiers).
MITRE_TECHNIQUES = [
    {
        "technique_id": "T1110",
        "technique_name": "Brute Force",
        "tactic": "Credential Access",
        "description": (
            "Adversaries may use brute force techniques to gain access to "
            "accounts when passwords are unknown or when password hashes are "
            "obtained."
        ),
        "detection_rule_types": ["brute_force", "failed_login", "multi_failure"],
    },
    {
        "technique_id": "T1548",
        "technique_name": "Abuse Elevation Control Mechanism",
        "tactic": "Privilege Escalation",
        "description": (
            "Adversaries may leverage mechanisms that run with elevated "
            "privileges to execute code or bypass access controls."
        ),
        "detection_rule_types": ["privilege_escalation", "admin_activity"],
    },
    {
        "technique_id": "T1078",
        "technique_name": "Valid Accounts",
        "tactic": "Persistence, Privilege Escalation, Defense Evasion",
        "description": (
            "Adversaries may obtain and abuse credentials of existing accounts "
            "as a means of gaining Initial Access, Persistence, Privilege "
            "Escalation, or Defense Evasion."
        ),
        "detection_rule_types": ["admin_activity", "suspicious_login"],
    },
    {
        "technique_id": "T1059",
        "technique_name": "Command and Scripting Interpreter",
        "tactic": "Execution",
        "description": (
            "Adversaries may abuse command and script interpreters to execute "
            "commands, scripts, or binaries."
        ),
        "detection_rule_types": ["suspicious_process"],
    },
    {
        "technique_id": "T1071",
        "technique_name": "Application Layer Protocol",
        "tactic": "Command and Control",
        "description": (
            "Adversaries may communicate using application layer protocols to "
            "avoid detection or network filtering."
        ),
        "detection_rule_types": ["ioc_match"],
    },
    {
        "technique_id": "T1499",
        "technique_name": "Endpoint Denial of Service",
        "tactic": "Impact",
        "description": (
            "Adversaries may perform endpoint Denial of Service (DoS) attacks "
            "to degrade or disrupt the availability of services."
        ),
        "detection_rule_types": ["frequency"],
    },
    {
        "technique_id": "T1087",
        "technique_name": "Account Discovery",
        "tactic": "Discovery",
        "description": (
            "Adversaries may attempt to gather information about accounts on a "
            "system."
        ),
        "detection_rule_types": ["access_denied"],
    },
]

RULE_TYPE_TO_TECHNIQUE = {}
for tech in MITRE_TECHNIQUES:
    for rule_type in tech["detection_rule_types"]:
        RULE_TYPE_TO_TECHNIQUE[rule_type] = tech


router = APIRouter()


@router.get("/techniques", tags=["mitre"])
def list_techniques(
    current_user: User = Depends(require_analyst),
):
    return MITRE_TECHNIQUES


@router.get("/mapping", tags=["mitre"])
def get_mapping(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    rules = db.query(DetectionRule).all()
    mapping = []
    for rule in rules:
        tech = RULE_TYPE_TO_TECHNIQUE.get(rule.rule_type)
        mapping.append({
            "rule_id": rule.id,
            "rule_name": rule.name,
            "rule_type": rule.rule_type,
            "technique": tech if tech else None,
        })
    return {
        "techniques": MITRE_TECHNIQUES,
        "rule_mapping": mapping,
    }
