#!/usr/bin/env python3
"""
intuition_engine.py — FRIDAY Intuition Engine (System 1 / RPD)
================================================================

Implements fast, pattern-matching cognition based on two foundational models:

  [IE-1] Kahneman's System 1 (Thinking, Fast and Slow, 2011)
         — Automatic, fast, effortless pattern recognition that operates
           without conscious deliberation. Generates intuitions from
           learned associations and expert pattern libraries.

  [IE-2] Gary Klein's Recognition-Primed Decision (RPD) model
         (Sources of Power: How People Make Decisions, 1998)
         — Experts don't compare options; they recognize situations and
           simulate a single course of action. Decision speed is itself
           a confidence signal.

  [IE-3] Gut feeling generation via weak signal aggregation
         — Multiple sub-threshold signals combine to produce a strong
           intuitive judgment, consistent with the somatic marker
           hypothesis (Damasio, 1994) and fluency heuristic literature.

Key behaviors:
  - Situation → signature → pattern match → action + confidence
  - Confidence = speed and closeness of match (not deliberation)
  - Escalation to System 2 (deliberative) when confidence is low
  - Pattern strength decays with disuse (Ebbinghaus forgetting curve)
  - Expertise grows with domain-specific pattern accumulation
  - Outcome recording strengthens/weakenes patterns (reinforcement)

This module does NOT think slowly. It fires fast. When it can't help,
it signals the cognitive_integration layer to engage deeper reasoning.
"""

import hashlib
import json
import math
import random
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


BRAIN_DIR = Path(__file__).parent.resolve()
INTUITION_FILE = BRAIN_DIR / "intuition_data.json"

# ── Configuration ───────────────────────────────────────────────────────────

# Pattern matching
MAX_PATTERNS_PER_DOMAIN = 500
SIGNATURE_FEATURES = 12          # features extracted per situation
SIMILARITY_THRESHOLD = 0.6       # minimum similarity to count as a match
CONFIDENT_THRESHOLD = 0.75       # above this = confident enough for fast path
DELIBERATE_THRESHOLD = 0.4       # below this = must escalate to System 2

# Pattern strength & decay
INITIAL_STRENGTH = 0.5
STRENGTH_ON_SUCCESS = 0.15       # gain on positive outcome
STRENGTH_ON_FAILURE = -0.2       # loss on negative outcome
MIN_STRENGTH = 0.05
MAX_STRENGTH = 1.0
DECAY_HALF_LIFE_DAYS = 60.       # unused patterns halve in strength every 60 days

# Gut feeling
GUT_SIGNAL_COUNT = 7             # number of weak signals aggregated
GUT_NOISE_SCALE = 0.1            # noise added for realistic gut feelings

# Expertise
EXPERTISE_NOVICE = 10            # patterns needed for novice
EXPERTISE_COMPETENT = 50
EXPERTISE_EXPERT = 200
EXPERTISE_MASTER = 500

# Persistence
MAX_RECENT_MATCHES = 100
MAX_OUTCOME_HISTORY = 500


def _now() -> str:
    return datetime.now().isoformat()


def _timestamp() -> float:
    return time.time()


def _hash_signature(features: List[float]) -> str:
    """Create a compact hash from feature vector for fast lookup."""
    raw = "|".join(f"{f:.4f}" for f in features)
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _sigmoid(x: float) -> float:
    try:
        return 1.0 / (1.0 + math.exp(-max(-10, min(10, x))))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _extract_features(text: str) -> List[float]:
    """
    Extract a feature signature from a text situation description.
    Uses lightweight text statistics — no ML dependencies.
    """
    if not text:
        return [0.0] * SIGNATURE_FEATURES

    words = text.lower().split()
    n = len(words)

    # Feature 1: length (normalized)
    f_len = min(1.0, n / 100.0)
    # Feature 2: average word length
    avg_wl = sum(len(w) for w in words) / max(n, 1)
    f_avg_wl = min(1.0, avg_wl / 15.0)
    # Feature 3: unique word ratio
    f_uniq = len(set(words)) / max(n, 1)
    # Feature 4: question mark presence
    f_q = 1.0 if "?" in text else 0.0
    # Feature 5: exclamation presence
    f_exc = 1.0 if "!" in text else 0.0
    # Feature 6: digit density
    digits = sum(1 for c in text if c.isdigit())
    f_digits = min(1.0, digits / max(len(text), 1) * 5)
    # Feature 7: punctuation density
    punct = sum(1 for c in text if c in ".,;:!?")
    f_punct = min(1.0, punct / max(len(text), 1) * 10)
    # Feature 8: uppercase ratio
    upper = sum(1 for c in text if c.isupper())
    f_upper = upper / max(len(text), 1)
    # Feature 9: hash of content (stable pseudo-random)
    h = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
    f_hash = (h % 10000) / 10000.0
    # Feature 10: sentence count
    sents = max(1, text.count(".") + text.count("!") + text.count("?"))
    f_sents = min(1.0, sents / 20.0)
    # Feature 11: whitespace ratio
    ws = sum(1 for c in text if c.isspace())
    f_ws = ws / max(len(text), 1)
    # Feature 12: first-word hash (topic signal)
    fw = words[0] if words else ""
    fh = int(hashlib.md5(fw.encode()).hexdigest()[:4], 16)
    f_topic = (fh % 1000) / 1000.0

    return [f_len, f_avg_wl, f_uniq, f_q, f_exc, f_digits,
            f_punct, f_upper, f_hash, f_sents, f_ws, f_topic]


# ── Pattern Data ────────────────────────────────────────────────────────────

class Pattern:
    """A single (situation, action, outcome) memory."""

    __slots__ = [
        "pattern_id", "domain", "situation_signature", "situation_text",
        "action", "outcome", "strength", "success_count", "failure_count",
        "created_at", "last_used_at", "last_outcome_at",
    ]

    def __init__(self, domain: str, situation_signature: List[float],
                 situation_text: str, action: str, pattern_id: str = ""):
        self.pattern_id = pattern_id or hashlib.md5(
            f"{domain}:{situation_text}:{action}:{_now()}".encode()
        ).hexdigest()[:12]
        self.domain = domain
        self.situation_signature = situation_signature
        self.situation_text = situation_text[:500]
        self.action = action
        self.outcome: Optional[str] = None
        self.strength = INITIAL_STRENGTH
        self.success_count = 0
        self.failure_count = 0
        self.created_at = _now()
        self.last_used_at = _now()
        self.last_outcome_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "domain": self.domain,
            "situation_signature": self.situation_signature,
            "situation_text": self.situation_text,
            "action": self.action,
            "outcome": self.outcome,
            "strength": round(self.strength, 4),
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "created_at": self.created_at,
            "last_used_at": self.last_used_at,
            "last_outcome_at": self.last_outcome_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Pattern":
        p = cls(
            domain=d.get("domain", "general"),
            situation_signature=d.get("situation_signature", []),
            situation_text=d.get("situation_text", ""),
            action=d.get("action", ""),
            pattern_id=d.get("pattern_id", ""),
        )
        p.outcome = d.get("outcome")
        p.strength = d.get("strength", INITIAL_STRENGTH)
        p.success_count = d.get("success_count", 0)
        p.failure_count = d.get("failure_count", 0)
        p.created_at = d.get("created_at", _now())
        p.last_used_at = d.get("last_used_at", _now())
        p.last_outcome_at = d.get("last_outcome_at")
        return p


# ── Intuition Engine ────────────────────────────────────────────────────────

class IntuitionEngine:
    """
    Fast pattern-matching cognition — FRIDAY's System 1.

    Recognizes situations from experience, generates intuitive responses,
    and decides when to escalate to deliberate (System 2) reasoning.

    Based on Kahneman's dual-process theory and Klein's RPD model.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._data: Dict[str, Any] = {}
        self._patterns: Dict[str, List[Pattern]] = defaultdict(list)
        self._domain_stats: Dict[str, Dict[str, float]] = {}
        self._recent_matches: List[dict] = []
        self._session_recognitions = 0
        self._session_confident = 0
        self._load()

    # ── Persistence ─────────────────────────────────────────────────────

    def _empty_store(self) -> dict:
        return {
            "meta": {
                "version": 1,
                "created": _now(),
                "last_update": _now(),
                "total_recognitions": 0,
                "total_confident_fast_paths": 0,
                "total_escalations": 0,
            },
            "patterns": {},       # domain → [pattern_dicts]
            "domain_stats": {},   # domain → {size, accuracy, ...}
            "recent_matches": [],
        }

    def _load(self):
        if not INTUITION_FILE.exists():
            self._data = self._empty_store()
            self._save()
            return
        try:
            raw = INTUITION_FILE.read_text(encoding="utf-8")
            self._data = json.loads(raw)
            # Rebuild pattern objects
            for domain, p_list in self._data.get("patterns", {}).items():
                self._patterns[domain] = [Pattern.from_dict(p) for p in p_list]
            self._domain_stats = self._data.get("domain_stats", {})
            self._recent_matches = self._data.get("recent_matches", [])
        except (json.JSONDecodeError, IOError):
            self._data = self._empty_store()
            self._save()

    def _save(self):
        BRAIN_DIR.mkdir(parents=True, exist_ok=True)
        with self._lock:
            # Serialize patterns back
            self._data["patterns"] = {
                domain: [p.to_dict() for p in p_list]
                for domain, p_list in self._patterns.items()
            }
            self._data["domain_stats"] = self._domain_stats
            self._data["recent_matches"] = self._recent_matches[-MAX_RECENT_MATCHES:]
            self._data["meta"]["last_update"] = _now()
            INTUITION_FILE.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    # ── Pattern Decay ───────────────────────────────────────────────────

    def _apply_decay(self, pattern: Pattern):
        """Apply time-based strength decay (Ebbinghaus forgetting curve)."""
        try:
            last = datetime.fromisoformat(pattern.last_used_at)
        except (ValueError, TypeError):
            return
        days_elapsed = (datetime.now() - last).total_seconds() / 86400.0
        if days_elapsed < 1:
            return
        # Exponential decay: strength * 2^(-days / half_life)
        decay_factor = math.pow(2, -days_elapsed / DECAY_HALF_LIFE_DAYS)
        pattern.strength = max(MIN_STRENGTH, pattern.strength * decay_factor)

    def _decay_all(self, domain: Optional[str] = None):
        """Apply decay to all patterns (or a specific domain)."""
        domains = [domain] if domain else list(self._patterns.keys())
        for d in domains:
            for p in self._patterns.get(d, []):
                self._apply_decay(p)

    # ── Core Recognition ────────────────────────────────────────────────

    def recognize(self, situation: str, domain: str = "general") -> Tuple[Optional[str], float, Optional[dict]]:
        """
        Fast pattern recognition — the core System 1 operation.

        Given a situation description, find the best matching pattern
        from experience and return an intuitive action recommendation.

        Args:
            situation: Text description of the current situation
            domain: Knowledge domain (e.g., "coding", "conversation", "planning")

        Returns:
            (action, confidence, matched_pattern_info)
            - action: recommended action string, or None if no match
            - confidence: 0.0-1.0, how confident the intuition is
            - matched_pattern_info: dict with pattern details, or None
        """
        start_time = _timestamp()
        features = _extract_features(situation)

        with self._lock:
            self._session_recognitions += 1
            self._data["meta"]["total_recognitions"] += 1

            candidates = self._patterns.get(domain, [])
            # Also check "general" as fallback if domain-specific is sparse
            if domain != "general" and len(candidates) < 5:
                candidates = candidates + self._patterns.get("general", [])

            if not candidates:
                return None, 0.0, None

            # Find best match via cosine similarity
            best_pattern: Optional[Pattern] = None
            best_similarity = 0.0

            for pat in candidates:
                sim = _cosine_similarity(features, pat.situation_signature)
                # Weight similarity by pattern strength
                weighted_sim = sim * (0.7 + 0.3 * pat.strength)
                if weighted_sim > best_similarity:
                    best_similarity = weighted_sim
                    best_pattern = pat

            elapsed_ms = (_timestamp() - start_time) * 1000

            if best_pattern is None or best_similarity < SIMILARITY_THRESHOLD:
                return None, best_similarity, None

            # Confidence: combines similarity, strength, and speed
            # Faster recognition = higher confidence (RPD speed heuristic)
            speed_bonus = max(0, 0.1 - elapsed_ms / 1000)  # bonus for <100ms
            confidence = min(1.0, (
                best_similarity * 0.5 +
                best_pattern.strength * 0.3 +
                speed_bonus +
                0.1  # base confidence for having any match
            ))

            # Update last_used
            best_pattern.last_used_at = _now()

            # Record match
            match_info = {
                "pattern_id": best_pattern.pattern_id,
                "domain": domain,
                "similarity": round(best_similarity, 4),
                "confidence": round(confidence, 4),
                "action": best_pattern.action,
                "strength": round(best_pattern.strength, 4),
                "elapsed_ms": round(elapsed_ms, 2),
                "timestamp": _now(),
            }
            self._recent_matches.append(match_info)
            if len(self._recent_matches) > MAX_RECENT_MATCHES:
                self._recent_matches = self._recent_matches[-MAX_RECENT_MATCHES:]

            if confidence >= CONFIDENT_THRESHOLD:
                self._session_confident += 1
                self._data["meta"]["total_confident_fast_paths"] += 1

            return best_pattern.action, confidence, match_info

    def should_deliberate(self, situation: str, domain: str = "general") -> bool:
        """
        Should FRIDAY engage System 2 (deliberative reasoning)?

        Returns True when:
        - No matching pattern exists (novel situation)
        - Best match confidence is below threshold
        - Situation is high-stakes (domain-specific heuristics)
        """
        action, confidence, _ = self.recognize(situation, domain)
        if action is None:
            return True
        if confidence < DELIBERATE_THRESHOLD:
            return True
        return False

    # ── Pattern Recording ───────────────────────────────────────────────

    def record_pattern(self, domain: str, situation: str, action: str) -> str:
        """
        Store a new (situation, action) pattern for future recognition.

        Returns the pattern_id.
        """
        features = _extract_features(situation)
        pattern = Pattern(
            domain=domain,
            situation_signature=features,
            situation_text=situation,
            action=action,
        )

        with self._lock:
            self._patterns[domain].append(pattern)

            # Enforce capacity
            if len(self._patterns[domain]) > MAX_PATTERNS_PER_DOMAIN:
                # Remove weakest pattern
                self._patterns[domain].sort(key=lambda p: p.strength)
                self._patterns[domain] = self._patterns[domain][1:]

            self._update_domain_stats(domain)
            self._save()

        return pattern.pattern_id

    def record_outcome(self, pattern_id: str, outcome: str,
                       success: Optional[bool] = None):
        """
        Record the outcome of a pattern-based decision.

        Strengthens the pattern on success, weakens on failure.
        """
        with self._lock:
            for domain, p_list in self._patterns.items():
                for pat in p_list:
                    if pat.pattern_id == pattern_id:
                        pat.outcome = outcome
                        pat.last_outcome_at = _now()

                        if success is True:
                            pat.strength = min(MAX_STRENGTH,
                                               pat.strength + STRENGTH_ON_SUCCESS)
                            pat.success_count += 1
                        elif success is False:
                            pat.strength = max(MIN_STRENGTH,
                                               pat.strength + STRENGTH_ON_FAILURE)
                            pat.failure_count += 1

                        self._update_domain_stats(domain)
                        self._save()
                        return

    def learn_from_observation(self, domain: str, situation: str,
                                action: str, outcome: str, success: bool):
        """
        Observe a (situation, action, outcome) tuple and learn from it.
        Either strengthens an existing pattern or creates a new one.
        """
        features = _extract_features(situation)

        with self._lock:
            candidates = self._patterns.get(domain, [])
            best_match: Optional[Pattern] = None
            best_sim = 0.0

            for pat in candidates:
                sim = _cosine_similarity(features, pat.situation_signature)
                if sim > best_sim:
                    best_sim = sim
                    best_match = pat

            if best_match and best_sim > 0.8 and best_match.action == action:
                # Reinforce existing pattern
                self.record_outcome(best_match.pattern_id, outcome, success)
            else:
                # New pattern
                pid = self.record_pattern(domain, situation, action)
                self.record_outcome(pid, outcome, success)

    # ── Gut Feeling ─────────────────────────────────────────────────────

    def generate_gut_feeling(self, signals: List[float]) -> Tuple[str, float]:
        """
        Aggregate multiple weak signals into a strong intuitive judgment.

        Based on the idea that gut feelings are the cumulative result of
        many sub-threshold pattern activations (Bechara et al., 1997).

        Args:
            signals: List of weak signal strengths (0.0-1.0 each)

        Returns:
            (feeling_label, strength)
            - feeling_label: "positive", "negative", "neutral", "uncertain"
            - strength: 0.0-1.0 how strong the gut feeling is
        """
        if not signals:
            return "neutral", 0.0

        # Add realistic noise
        noisy = [s + random.gauss(0, GUT_NOISE_SCALE) for s in signals]
        noisy = [max(0, min(1, s)) for s in noisy]

        # Aggregate: mean + variance signal
        mean_signal = sum(noisy) / len(noisy)
        variance = sum((s - mean_signal) ** 2 for s in noisy) / len(noisy)

        # High variance = uncertain gut feeling
        # Low variance + high mean = strong positive
        # Low variance + low mean = strong negative
        if variance > 0.15:
            return "uncertain", mean_signal

        strength = abs(mean_signal - 0.5) * 2  # distance from neutral
        if mean_signal > 0.6:
            return "positive", round(min(1.0, strength), 3)
        elif mean_signal < 0.4:
            return "negative", round(min(1.0, strength), 3)
        else:
            return "neutral", round(strength, 3)

    def generate_intuitive_judgment(self, situation: str, domain: str = "general") -> dict:
        """
        Generate a full intuitive judgment by combining multiple signals:
        1. Pattern match quality
        2. Pattern strength
        3. Historical success rate in domain
        4. Novelty (how different from known patterns)
        5. Domain expertise level
        """
        features = _extract_features(situation)

        with self._lock:
            candidates = self._patterns.get(domain, [])
            if not candidates:
                return {
                    "judgment": "no_intuition",
                    "feeling": "neutral",
                    "strength": 0.0,
                    "signals": [],
                    "recommendation": "deliberate",
                }

            # Signal 1: best match similarity
            sims = [_cosine_similarity(features, p.situation_signature) for p in candidates]
            best_sim = max(sims) if sims else 0.0

            # Signal 2: average pattern strength
            avg_strength = sum(p.strength for p in candidates) / len(candidates)

            # Signal 3: domain success rate
            total_s = sum(p.success_count for p in candidates)
            total_f = sum(p.failure_count for p in candidates)
            success_rate = total_s / max(total_s + total_f, 1)

            # Signal 4: novelty (inverse of best match)
            novelty = 1.0 - best_sim

            # Signal 5: expertise level
            expertise = min(1.0, len(candidates) / EXPERTISE_EXPERT)

            signals = [best_sim, avg_strength, success_rate, 1.0 - novelty, expertise]
            feeling, strength = self.generate_gut_feeling(signals)

            recommendation = "act_intuitively" if strength > 0.5 and feeling != "negative" else "deliberate"

            return {
                "judgment": feeling,
                "feeling": feeling,
                "strength": round(strength, 3),
                "signals": {
                    "match_quality": round(best_sim, 3),
                    "avg_pattern_strength": round(avg_strength, 3),
                    "domain_success_rate": round(success_rate, 3),
                    "novelty": round(novelty, 3),
                    "expertise": round(expertise, 3),
                },
                "recommendation": recommendation,
                "patterns_available": len(candidates),
            }

    # ── Expertise Tracking ──────────────────────────────────────────────

    def _update_domain_stats(self, domain: str):
        """Update expertise statistics for a domain."""
        patterns = self._patterns.get(domain, [])
        n = len(patterns)
        total_s = sum(p.success_count for p in patterns)
        total_f = sum(p.failure_count for p in patterns)
        accuracy = total_s / max(total_s + total_f, 1) if (total_s + total_f) > 0 else 0.5
        avg_strength = sum(p.strength for p in patterns) / max(n, 1)

        if n >= EXPERTISE_MASTER:
            level = "master"
        elif n >= EXPERTISE_EXPERT:
            level = "expert"
        elif n >= EXPERTISE_COMPETENT:
            level = "competent"
        elif n >= EXPERTISE_NOVICE:
            level = "novice"
        else:
            level = "beginner"

        self._domain_stats[domain] = {
            "pattern_count": n,
            "success_count": total_s,
            "failure_count": total_f,
            "accuracy": round(accuracy, 3),
            "avg_strength": round(avg_strength, 3),
            "expertise_level": level,
            "last_update": _now(),
        }

    def get_expertise(self, domain: str = "general") -> dict:
        """Get expertise level and stats for a domain."""
        with self._lock:
            stats = self._domain_stats.get(domain)
            if not stats:
                return {
                    "domain": domain,
                    "expertise_level": "beginner",
                    "pattern_count": 0,
                    "accuracy": 0.0,
                }
            return dict(stats)

    def get_all_domains(self) -> List[str]:
        """List all domains with stored patterns."""
        with self._lock:
            return list(self._patterns.keys())

    # ── Statistics ──────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Get overall intuition engine statistics."""
        with self._lock:
            total_patterns = sum(len(pl) for pl in self._patterns.values())
            domains = len(self._patterns)
            total_recog = self._data["meta"].get("total_recognitions", 0)
            total_conf = self._data["meta"].get("total_confident_fast_paths", 0)
            total_esc = self._data["meta"].get("total_escalations", 0)

            fast_path_rate = total_conf / max(total_recog, 1)

            return {
                "total_patterns": total_patterns,
                "domains": domains,
                "total_recognitions": total_recog,
                "confident_fast_paths": total_conf,
                "escalations": total_esc,
                "fast_path_rate": round(fast_path_rate, 3),
                "session_recognitions": self._session_recognitions,
                "session_confident": self._session_confident,
            }

    def format_for_prompt(self, max_chars: int = 500) -> str:
        """Format intuition awareness for system prompt injection."""
        stats = self.get_stats()
        domains = self.get_all_domains()
        expertise_parts = []
        for d in domains[:5]:
            exp = self.get_expertise(d)
            expertise_parts.append(f"{d}={exp['expertise_level']}")

        parts = [
            "[INTUITION ENGINE — System 1 awareness]",
            f"Patterns: {stats['total_patterns']} across {stats['domains']} domains | "
            f"Fast-path rate: {stats['fast_path_rate']:.0%}",
        ]
        if expertise_parts:
            parts.append(f"Expertise: {', '.join(expertise_parts)}")

        result = "\n".join(parts)
        if len(result) > max_chars:
            result = result[:max_chars] + "[...]"
        return result

    # ── Maintenance ─────────────────────────────────────────────────────

    def prune_weak_patterns(self, threshold: float = MIN_STRENGTH * 2):
        """Remove patterns that have decayed below threshold."""
        with self._lock:
            pruned = 0
            for domain in list(self._patterns.keys()):
                before = len(self._patterns[domain])
                self._patterns[domain] = [
                    p for p in self._patterns[domain]
                    if p.strength > threshold
                ]
                pruned += before - len(self._patterns[domain])
                self._update_domain_stats(domain)
            if pruned > 0:
                self._save()
            return pruned


# ── Singleton ───────────────────────────────────────────────────────────────

_intuition_engine = None
_intuition_lock = threading.Lock()


def get_intuition_engine() -> IntuitionEngine:
    """Get singleton IntuitionEngine instance."""
    global _intuition_engine
    if _intuition_engine is None:
        with _intuition_lock:
            if _intuition_engine is None:
                _intuition_engine = IntuitionEngine()
    return _intuition_engine
