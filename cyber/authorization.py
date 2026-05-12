"""
cyber/authorization.py — Authorization & Consent Gate
=======================================================

Requires explicit user authorization before running any live cyber operations
(network scanning, exploit validation, etc.). Static analysis of local code
does NOT require authorization since it's read-only file inspection.

Users must type a specific confirmation phrase to enable live operations.
Consent is logged with timestamp and expires after 24 hours.

Usage:
    from cyber.authorization import require_authorization, AuthorizationError

    # Before running any live operation:
    require_authorization(target, operation="port_scan")

    # Or check without raising:
    if is_authorized():
        ...
"""

import json
import hashlib
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("friday.cyber.authorization")

# ── Constants ─────────────────────────────────────────────────────────

CONSENT_PHRASE = "I have written authorization to test this target"
CONSENT_LOG_FILE = Path(__file__).parent.parent / "config" / "consent_log.json"
CONSENT_EXPIRY_HOURS = 24

# Operations that require authorization (anything involving network)
LIVE_OPERATIONS = {
    "port_scan", "nmap_scan", "nmap_script", "subdomain_enum", "subfinder",
    "httpx_probe", "dns_info", "dnsx", "ssl_info", "whois", "web_fuzz_ps",
    "ffuf", "gobuster", "nuclei", "sqlmap", "whatweb", "wpscan", "gospider",
    "http_archive", "katana", "naabu", "header_check", "cors_check",
    "recon_full", "cyber_scan", "mythos_scan",
    "exploit_validation", "business_logic", "full_pipeline",
}

# Operations that are always allowed (local file analysis only)
SAFE_OPERATIONS = {
    "static_analysis", "data_flow", "source_sink", "code_review",
    "check_tools", "debug_wsl", "health", "url_parse",
    "extract_domains", "extract_urls", "start_mcp", "stop_mcp", "reset_wsl",
}


class AuthorizationError(Exception):
    """Raised when user has not authorized live operations."""
    def __init__(self, target: str, operation: str):
        self.target = target
        self.operation = operation
        super().__init__(
            f"Authorization required for '{operation}' on '{target}'.\n"
            f"To authorize, type: {CONSENT_PHRASE}\n"
            f"Or run: friday authorize {target}"
        )


@dataclass
class ConsentRecord:
    """A single consent record."""
    target: str
    timestamp: float
    timestamp_human: str
    consent_phrase_hash: str
    ip_hash: Optional[str] = None


class AuthorizationManager:
    """
    Manages user consent for live cyber operations.

    Consent is:
    - Required for any operation that touches the network
    - Valid for 24 hours per target
    - Logged to config/consent_log.json for audit trail
    - Verified by requiring user to type an exact phrase
    """

    def __init__(self):
        self._consent_log: list[dict] = []
        self._active_consents: dict[str, float] = {}  # target -> expiry timestamp
        self._load_consent_log()

    def _load_consent_log(self):
        """Load existing consent records from disk."""
        try:
            if CONSENT_LOG_FILE.exists():
                data = json.loads(CONSENT_LOG_FILE.read_text(encoding="utf-8"))
                self._consent_log = data.get("records", [])
                # Rebuild active consents from log
                now = time.time()
                for record in self._consent_log:
                    expiry = record["timestamp"] + (CONSENT_EXPIRY_HOURS * 3600)
                    if expiry > now:
                        self._active_consents[record["target"]] = expiry
        except Exception as e:
            logger.warning(f"Failed to load consent log: {e}")
            self._consent_log = []

    def _save_consent_log(self):
        """Persist consent records to disk."""
        try:
            CONSENT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "version": 1,
                "description": "Audit log of user consent for live cyber operations",
                "records": self._consent_log,
            }
            CONSENT_LOG_FILE.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"Failed to save consent log: {e}")

    def is_authorized(self, target: str) -> bool:
        """
        Check if target has active (non-expired) authorization.

        Returns True if:
        - User previously consented for this target
        - Consent has not expired (within 24 hours)
        """
        expiry = self._active_consents.get(target)
        if expiry and time.time() < expiry:
            return True
        # Clean up expired
        if target in self._active_consents:
            del self._active_consents[target]
        return False

    def grant_consent(self, target: str, consent_phrase: str) -> tuple[bool, str]:
        """
        Attempt to grant consent for a target.

        Args:
            target: The target URL/IP/domain
            consent_phrase: Must match CONSENT_PHRASE exactly

        Returns:
            (success, message) tuple
        """
        # Validate consent phrase
        if consent_phrase.strip() != CONSENT_PHRASE:
            return False, (
                f"Incorrect consent phrase. You must type exactly:\n"
                f"  \"{CONSENT_PHRASE}\""
            )

        # Record consent
        now = time.time()
        record = ConsentRecord(
            target=target,
            timestamp=now,
            timestamp_human=datetime.now(timezone.utc).isoformat(),
            consent_phrase_hash=hashlib.sha256(
                CONSENT_PHRASE.encode()
            ).hexdigest()[:16],
        )

        self._consent_log.append(asdict(record))
        self._active_consents[target] = now + (CONSENT_EXPIRY_HOURS * 3600)
        self._save_consent_log()

        logger.info(f"Consent granted for target: {target}")
        return True, (
            f"Authorization granted for '{target}'.\n"
            f"Valid for {CONSENT_EXPIRY_HOURS} hours.\n"
            f"Logged to: {CONSENT_LOG_FILE}"
        )

    def revoke_consent(self, target: str) -> bool:
        """Revoke active consent for a target."""
        if target in self._active_consents:
            del self._active_consents[target]
            logger.info(f"Consent revoked for target: {target}")
            return True
        return False

    def revoke_all(self) -> int:
        """Revoke all active consents. Returns count of revoked."""
        count = len(self._active_consents)
        self._active_consents.clear()
        logger.info(f"All consents revoked ({count} targets)")
        return count

    def get_active_consents(self) -> list[dict]:
        """List all active (non-expired) consents."""
        now = time.time()
        active = []
        expired_targets = []
        for target, expiry in self._active_consents.items():
            if now < expiry:
                remaining_hours = (expiry - now) / 3600
                active.append({
                    "target": target,
                    "expires_in_hours": round(remaining_hours, 1),
                })
            else:
                expired_targets.append(target)
        # Clean up expired
        for t in expired_targets:
            del self._active_consents[t]
        return active

    def get_consent_log(self) -> list[dict]:
        """Return full consent audit log."""
        return list(self._consent_log)

    def require_authorization(self, target: str, operation: str):
        """
        Gate: raises AuthorizationError if not authorized.

        Call this before any live cyber operation.

        Args:
            target: Target URL/IP/domain
            operation: Operation name (must be in LIVE_OPERATIONS)

        Raises:
            AuthorizationError: If not authorized
        """
        if operation not in LIVE_OPERATIONS:
            # Unknown operation — treat as requiring auth to be safe
            logger.warning(f"Unknown operation '{operation}' — requiring authorization")

        if not self.is_authorized(target):
            raise AuthorizationError(target, operation)

        logger.debug(f"Authorization confirmed for {operation} on {target}")


# ── Singleton ─────────────────────────────────────────────────────────

_auth_manager: Optional[AuthorizationManager] = None


def get_auth_manager() -> AuthorizationManager:
    """Get or create the singleton authorization manager."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthorizationManager()
    return _auth_manager


def is_authorized(target: str) -> bool:
    """Quick check if target is authorized."""
    return get_auth_manager().is_authorized(target)


def require_authorization(target: str, operation: str = "unknown"):
    """
    Convenience function: raises AuthorizationError if not authorized.

    Usage:
        require_authorization("http://example.com", "port_scan")
    """
    get_auth_manager().require_authorization(target, operation)


def grant_consent(target: str, consent_phrase: str) -> tuple[bool, str]:
    """Convenience function: attempt to grant consent."""
    return get_auth_manager().grant_consent(target, consent_phrase)


def is_live_operation(operation: str) -> bool:
    """Check if an operation requires authorization."""
    return operation in LIVE_OPERATIONS
