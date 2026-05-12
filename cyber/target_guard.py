"""
cyber/target_guard.py — Target Validation & Access Control
===========================================================

Restricts where Friday's cyber tools can aim:
- Localhost / loopback / private IPs → always allowed (testing your own stuff)
- External targets → require explicit authorization with typed consent
- Blocked targets → never allowed (cloud metadata, internal infra)

This is the legal safety layer. It doesn't remove capabilities —
it ensures they're only used responsibly.
"""

import ipaddress
import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("friday.cyber.target_guard")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "target_guard.json"
AUDIT_LOG_PATH = BASE_DIR / "data" / "audit_log.json"

# ── Target Classification ────────────────────────────────────────────

# Always allowed — you're testing your own machine
LOCAL_PATTERNS = [
    "localhost",
    "127.0.0.1",
    "::1",
    "0.0.0.0",
    "10.",
    "172.16.", "172.17.", "172.18.", "172.19.",
    "172.20.", "172.21.", "172.22.", "172.23.",
    "172.24.", "172.25.", "172.26.", "172.27.",
    "172.28.", "172.29.", "172.30.", "172.31.",
    "192.168.",
]

# Always blocked — cloud metadata, internal infra
BLOCKED_PATTERNS = [
    "169.254.169.254",      # AWS/GCP/Azure metadata
    "metadata.google.internal",
    "instance-data",
    "100.100.100.200",      # Alibaba Cloud metadata
]

# Consent phrase for external target authorization
CONSENT_PHRASE = "I own this target or have written authorization to test it"

# How long authorization lasts (hours)
AUTH_EXPIRY_HOURS = 24


def is_local_target(target: str) -> bool:
    """Check if target is localhost / private network (your own stuff)."""
    if not target:
        return False

    # Extract hostname from URL
    hostname = target
    if "://" in target:
        hostname = target.split("://")[1].split("/")[0].split(":")[0]
    else:
        hostname = target.split("/")[0].split(":")[0]

    hostname = hostname.lower().strip()

    # Blocked targets are NEVER local (check first)
    if is_blocked_target(target):
        return False

    # .local domains (mDNS/Bonjour) are always local
    if hostname.endswith(".local"):
        return True

    # Check local patterns
    for pattern in LOCAL_PATTERNS:
        if hostname.startswith(pattern) or hostname == pattern.rstrip("."):
            return True

    # Check if it's a local file path (not a URL)
    if not target.startswith("http") and "." not in hostname:
        return True

    # Try parsing as IP
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        pass

    return False


def is_blocked_target(target: str) -> bool:
    """Check if target is explicitly blocked (cloud metadata, etc.)."""
    if not target:
        return False
    target_lower = target.lower()
    return any(bp in target_lower for bp in BLOCKED_PATTERNS)


class TargetGuard:
    """
    Validates targets before cyber operations.

    Classification:
    - LOCAL (localhost/private) → always allowed
    - OWNED (external, user confirmed ownership) → allowed with auth
    - BLOCKED (cloud metadata, etc.) → never allowed
    - UNKNOWN (external, no auth) → blocked, requires auth
    """

    def __init__(self):
        self._owned_targets: dict[str, float] = {}  # target -> expiry timestamp
        self._load_config()

    def _load_config(self):
        """Load owned targets from config."""
        try:
            if CONFIG_PATH.exists():
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                now = time.time()
                for entry in data.get("owned_targets", []):
                    expiry = entry.get("expires_at", 0)
                    if expiry > now:
                        self._owned_targets[entry["target"]] = expiry
        except Exception as e:
            logger.warning(f"Failed to load target guard config: {e}")

    def _save_config(self):
        """Persist owned targets."""
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            now = time.time()
            records = []
            for target, expiry in self._owned_targets.items():
                if expiry > now:
                    records.append({"target": target, "expires_at": expiry})
            data = {
                "version": 1,
                "description": "Targets the user has confirmed ownership of",
                "owned_targets": records,
            }
            CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to save target guard config: {e}")

    def classify(self, target: str) -> str:
        """
        Classify a target.

        Returns: "local", "owned", "blocked", or "unknown"
        """
        # Check blocked FIRST — cloud metadata is never "local"
        if is_blocked_target(target):
            return "blocked"
        if is_local_target(target):
            return "local"
        if self._is_owned(target):
            return "owned"
        return "unknown"

    def _is_owned(self, target: str) -> bool:
        """Check if user has confirmed ownership of this target."""
        expiry = self._owned_targets.get(target)
        if expiry and time.time() < expiry:
            return True
        if target in self._owned_targets:
            del self._owned_targets[target]
        return False

    def check(self, target: str, operation: str = "scan") -> Optional[str]:
        """
        Validate a target for a cyber operation.

        Returns None if allowed, or an error message explaining why blocked.
        """
        classification = self.classify(target)

        if classification == "local":
            self._audit_log(target, operation, "allowed", "local_target")
            return None  # Always allowed

        if classification == "blocked":
            msg = (
                f"⛔ Target '{target}' is blocked.\n"
                f"Cloud metadata endpoints and internal infrastructure cannot be scanned."
            )
            self._audit_log(target, operation, "blocked", "blocked_target")
            return msg

        if classification == "owned":
            self._audit_log(target, operation, "allowed", "owned_target")
            return None  # Previously authorized

        # Unknown external target — need authorization
        msg = (
            f"🔒 External target: '{target}'\n\n"
            f"Friday's cyber tools are designed for testing your own systems.\n"
            f"To proceed, you must confirm you own this target or have written authorization.\n\n"
            f"Type exactly:\n"
            f"  {CONSENT_PHRASE}\n\n"
            f"Or use: friday authorize '{target}'\n\n"
            f"⚠️  Unauthorized scanning is illegal in most jurisdictions."
        )
        self._audit_log(target, operation, "requires_auth", "external_target")
        return msg

    def grant_ownership(self, target: str, consent_phrase: str) -> tuple[bool, str]:
        """
        Grant ownership authorization for an external target.

        Returns (success, message).
        """
        if consent_phrase.strip() != CONSENT_PHRASE:
            return False, (
                f"Invalid consent phrase. You must type exactly:\n"
                f"  \"{CONSENT_PHRASE}\""
            )

        expiry = time.time() + (AUTH_EXPIRY_HOURS * 3600)
        self._owned_targets[target] = expiry
        self._save_config()

        self._audit_log(target, "authorize", "granted", "user_consent")

        return True, (
            f"✅ Authorization granted for '{target}'.\n"
            f"Valid for {AUTH_EXPIRY_HOURS} hours.\n"
            f"Logged to audit trail."
        )

    def revoke(self, target: str = None) -> int:
        """Revoke authorization. If target=None, revoke all."""
        if target:
            if target in self._owned_targets:
                del self._owned_targets[target]
                self._save_config()
                self._audit_log(target, "revoke", "revoked", "user_request")
                return 1
            return 0
        else:
            count = len(self._owned_targets)
            self._owned_targets.clear()
            self._save_config()
            self._audit_log("*", "revoke_all", "revoked", "user_request")
            return count

    def list_owned(self) -> list[dict]:
        """List all authorized external targets."""
        now = time.time()
        active = []
        for target, expiry in self._owned_targets.items():
            if expiry > now:
                hours_left = (expiry - now) / 3600
                active.append({
                    "target": target,
                    "expires_in_hours": round(hours_left, 1),
                })
        return active

    def _audit_log(self, target: str, operation: str, decision: str, reason: str):
        """Log all target validation decisions for audit trail."""
        try:
            AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

            # Load existing log
            records = []
            if AUDIT_LOG_PATH.exists():
                data = json.loads(AUDIT_LOG_PATH.read_text(encoding="utf-8"))
                records = data.get("records", [])

            records.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "target": target,
                "operation": operation,
                "decision": decision,
                "reason": reason,
            })

            # Keep last 1000 entries
            if len(records) > 1000:
                records = records[-1000:]

            data = {"version": 1, "records": records}
            AUDIT_LOG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")


# ── Singleton ─────────────────────────────────────────────────────────

_guard: Optional[TargetGuard] = None


def get_target_guard() -> TargetGuard:
    global _guard
    if _guard is None:
        _guard = TargetGuard()
    return _guard
