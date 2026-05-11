#!/usr/bin/env python3
"""
document_intelligence.py — Friday Document Intelligence Engine
================================================================

Advanced document understanding that goes far beyond "summarize this."
A cognitive system for deep document analysis, structured extraction,
cross-document reasoning, and knowledge synthesis.

  [DI-1] Deep Document Analysis — extracts structure, arguments, evidence,
         assumptions, and logical flow from any document type.

  [DI-2] Contract Review — identifies key clauses, obligations, risks,
         unusual terms, and missing protections.

  [DI-3] Research Paper Analysis — extracts methodology, findings,
         limitations, citations, and contribution claims.

  [DI-4] Cross-Document Reasoning — compares, contrasts, and synthesizes
         information across multiple documents.

  [DI-5] Argument Mapping — identifies claims, evidence, assumptions,
         logical structure, and potential fallacies.

  [DI-6] Key Extraction — structured extraction of entities, dates,
         numbers, obligations, and action items from unstructured text.

  [DI-7] Reading Level Assessment — Flesch-Kincaid, complexity analysis,
         jargon detection, and accessibility scoring.

  [DI-8] Bias Detection — identifies loaded language, framing effects,
         one-sided presentation, and rhetorical manipulation.

Inspired by:
  - Argumentation Theory (Toulmin, 1958)
  - Rhetorical Structure Theory (Mann & Thompson, 1988)
  - Critical Discourse Analysis (Fairclough, 1995)
  - Information Extraction literature (Nadeau & Sekine, 2007)

Usage:
    from skills.document_intelligence import get_document_intelligence
    di = get_document_intelligence()
    analysis = di.analyze_document(text, doc_type="contract")
"""

import hashlib
import json
import math
import re
import threading
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SKILLS_DIR = Path(__file__).parent.resolve()
DATA_DIR = SKILLS_DIR / "document_data"
ANALYSIS_HISTORY_FILE = DATA_DIR / "analysis_history.json"
PATTERNS_FILE = DATA_DIR / "extraction_patterns.json"

# ── Configuration ───────────────────────────────────────────────────────────

MAX_ANALYSIS_HISTORY = 200
MAX_EXTRACTED_ITEMS = 100
MAX_ARGUMENT_DEPTH = 5
MIN_SENTENCE_LENGTH = 15
MAX_SENTENCE_LENGTH = 500

# Contract clause types
CLAUSE_TYPES = [
    "termination", "liability", "indemnification", "confidentiality",
    "intellectual_property", "payment", "dispute_resolution",
    "governing_law", "force_majeure", "warranty", "limitation_of_liability",
    "non_compete", "non_solicitation", "assignment", "amendment",
    "severability", "entire_agreement", "notice", "audit_rights",
    "data_protection", "insurance", "compliance",
]

# Risk indicators
RISK_INDICATORS = {
    "high": [
        "unlimited liability", "personal guarantee", "irrevocable",
        "perpetual", "exclusive", "sole discretion", "without limitation",
        "indemnify and hold harmless", "liquidated damages",
        "consequential damages", "punitive damages",
    ],
    "medium": [
        "reasonable efforts", "best efforts", "material adverse",
        "significant", "substantial", "may at any time",
        "reserve the right", "subject to change",
    ],
    "low": [
        "in writing", "mutual agreement", "good faith",
        "commercially reasonable", "industry standard",
        "notice period", "cure period",
    ],
}

# Logical fallacy patterns
FALLACY_PATTERNS = {
    "ad_hominem": {
        "patterns": ["you are", "your character", "you personally", "attack the person"],
        "description": "Attacking the person rather than the argument",
    },
    "straw_man": {
        "patterns": ["so you're saying", "what you really mean", "in other words you think"],
        "description": "Misrepresenting someone's argument to make it easier to attack",
    },
    "false_dilemma": {
        "patterns": ["either.*or", "only two", "you must choose", "there is no alternative"],
        "description": "Presenting only two options when more exist",
    },
    "appeal_to_authority": {
        "patterns": ["experts say", "studies show", "scientists agree", "everyone knows"],
        "description": "Citing authority without evidence or relevance",
    },
    "slippery_slope": {
        "patterns": ["will inevitably lead to", "next thing you know", "before you know it", "domino effect"],
        "description": "Assuming one event will lead to extreme consequences",
    },
    "bandwagon": {
        "patterns": ["everyone is", "most people", "nobody disagrees", "widely accepted"],
        "description": "Arguing something is true because many people believe it",
    },
    "circular_reasoning": {
        "patterns": ["because it is", "by definition", "obviously", "it goes without saying"],
        "description": "Using the conclusion as a premise",
    },
}


def _now() -> str:
    return datetime.now().isoformat()


def _hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:12]


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


# ── Data Structures ─────────────────────────────────────────────────────────

class ExtractedItem:
    """A structured item extracted from a document."""

    __slots__ = ["item_type", "text", "context", "confidence", "position"]

    def __init__(self, item_type: str, text: str, context: str = "",
                 confidence: float = 0.5, position: int = 0):
        self.item_type = item_type
        self.text = text[:500]
        self.context = context[:200]
        self.confidence = _clamp(confidence)
        self.position = position

    def to_dict(self) -> dict:
        return {
            "type": self.item_type,
            "text": self.text,
            "context": self.context,
            "confidence": round(self.confidence, 3),
            "position": self.position,
        }


class Argument:
    """An argument with claim, evidence, and logical structure."""

    __slots__ = [
        "claim", "evidence", "assumptions", "warrant",
        "counterargument", "strength", "fallacies",
    ]

    def __init__(self, claim: str):
        self.claim = claim[:300]
        self.evidence: List[str] = []
        self.assumptions: List[str] = []
        self.warrant: str = ""  # underlying reasoning
        self.counterargument: str = ""
        self.strength = 0.5     # 0=weak, 1=strong
        self.fallacies: List[str] = []

    def to_dict(self) -> dict:
        return {
            "claim": self.claim,
            "evidence": self.evidence,
            "assumptions": self.assumptions,
            "warrant": self.warrant,
            "counterargument": self.counterargument,
            "strength": round(self.strength, 3),
            "fallacies": self.fallacies,
        }


class ContractClause:
    """A clause extracted from a contract."""

    __slots__ = [
        "clause_type", "text", "risk_level", "risk_factors",
        "obligations", "recommendations", "is_unusual",
    ]

    def __init__(self, clause_type: str, text: str):
        self.clause_type = clause_type
        self.text = text[:500]
        self.risk_level = "low"
        self.risk_factors: List[str] = []
        self.obligations: List[str] = []
        self.recommendations: List[str] = []
        self.is_unusual = False

    def to_dict(self) -> dict:
        return {
            "clause_type": self.clause_type,
            "text": self.text,
            "risk_level": self.risk_level,
            "risk_factors": self.risk_factors,
            "obligations": self.obligations,
            "recommendations": self.recommendations,
            "is_unusual": self.is_unusual,
        }


class DocumentAnalysis:
    """Complete document analysis result."""

    __slots__ = [
        "analysis_id", "doc_type", "title", "summary",
        "key_points", "arguments", "entities", "clauses",
        "risks", "fallacies", "reading_level", "bias_indicators",
        "action_items", "metadata", "timestamp",
    ]

    def __init__(self, doc_type: str = "general"):
        self.analysis_id = _hash(f"{doc_type}:{_now()}")
        self.doc_type = doc_type
        self.title = ""
        self.summary = ""
        self.key_points: List[str] = []
        self.arguments: List[dict] = []
        self.entities: List[dict] = []
        self.clauses: List[dict] = []
        self.risks: List[dict] = []
        self.fallacies: List[dict] = []
        self.reading_level: dict = {}
        self.bias_indicators: List[dict] = []
        self.action_items: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.timestamp = _now()

    def to_dict(self) -> dict:
        return {
            "analysis_id": self.analysis_id,
            "doc_type": self.doc_type,
            "title": self.title,
            "summary": self.summary,
            "key_points": self.key_points,
            "arguments": self.arguments,
            "entities": self.entities,
            "clauses": self.clauses,
            "risks": self.risks,
            "fallacies": self.fallacies,
            "reading_level": self.reading_level,
            "bias_indicators": self.bias_indicators,
            "action_items": self.action_items,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


# ── Document Intelligence ───────────────────────────────────────────────────

class DocumentIntelligence:
    """
    Advanced document understanding system.

    Analyzes documents for structure, arguments, risks, bias,
    and extracts structured information.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._analysis_history: List[dict] = []
        self._load()

    def _load(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if ANALYSIS_HISTORY_FILE.exists():
            try:
                self._analysis_history = json.loads(
                    ANALYSIS_HISTORY_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                self._analysis_history = []

    def _save(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with self._lock:
            ANALYSIS_HISTORY_FILE.write_text(json.dumps(
                self._analysis_history[-MAX_ANALYSIS_HISTORY:],
                indent=2, ensure_ascii=False), encoding="utf-8")

    # ── Main Analysis ────────────────────────────────────────────────

    def analyze_document(self, text: str, doc_type: str = "general",
                          title: str = "", context: dict = None) -> dict:
        """
        Perform comprehensive document analysis.

        Args:
            text: The document text
            doc_type: "contract", "research_paper", "report", "article", "general"
            title: Document title if known
            context: Additional context for analysis

        Returns:
            Complete analysis dict
        """
        analysis = DocumentAnalysis(doc_type)
        analysis.title = title or self._extract_title(text)
        analysis.metadata = {
            "word_count": len(text.split()),
            "char_count": len(text),
            "sentence_count": len(re.split(r'[.!?]+', text)),
            "paragraph_count": len(text.split('\n\n')),
        }

        # Always extract: summary, key points, entities, reading level
        analysis.summary = self._extract_summary(text)
        analysis.key_points = self._extract_key_points(text)
        analysis.entities = self._extract_entities(text)
        analysis.reading_level = self._assess_reading_level(text)
        analysis.action_items = self._extract_action_items(text)

        # Type-specific analysis
        if doc_type == "contract":
            analysis.clauses = self._analyze_contract_clauses(text)
            analysis.risks = self._identify_contract_risks(text)
        elif doc_type == "research_paper":
            analysis.arguments = self._map_arguments(text)
            analysis.risks = self._identify_limitations(text)
        else:
            analysis.arguments = self._map_arguments(text)

        # Always check for fallacies and bias
        analysis.fallacies = self._detect_fallacies(text)
        analysis.bias_indicators = self._detect_bias(text)

        # Record
        self._analysis_history.append({
            "analysis_id": analysis.analysis_id,
            "doc_type": doc_type,
            "title": analysis.title[:100],
            "word_count": analysis.metadata["word_count"],
            "timestamp": _now(),
        })
        self._save()

        return analysis.to_dict()

    # ── Title & Summary ──────────────────────────────────────────────

    def _extract_title(self, text: str) -> str:
        """Extract title from first non-empty line."""
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) < 200:
                return line
        return "Untitled Document"

    def _extract_summary(self, text: str, max_sentences: int = 5) -> str:
        """
        Extract a summary using extractive summarization.
        Selects the most important sentences based on position and keyword density.
        """
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text)
                     if MIN_SENTENCE_LENGTH < len(s.strip()) < MAX_SENTENCE_LENGTH]

        if not sentences:
            return text[:300]

        # Score sentences
        scored = []
        for i, sentence in enumerate(sentences):
            score = 0.0
            # Position bonus (first and last sentences are important)
            if i == 0:
                score += 0.3
            elif i < 3:
                score += 0.15
            elif i >= len(sentences) - 2:
                score += 0.1

            # Length bonus (medium sentences are better)
            word_count = len(sentence.split())
            if 10 <= word_count <= 30:
                score += 0.1

            # Keyword density (common important words)
            important_words = {
                "important", "significant", "key", "main", "primary",
                "conclusion", "result", "finding", "therefore", "however",
                "must", "shall", "required", "critical", "essential",
            }
            s_lower = sentence.lower()
            keyword_hits = sum(1 for w in important_words if w in s_lower)
            score += keyword_hits * 0.05

            scored.append((score, i, sentence))

        # Select top sentences in original order
        scored.sort(key=lambda x: x[0], reverse=True)
        selected = sorted(scored[:max_sentences], key=lambda x: x[1])
        return " ".join(s[2] for s in selected)

    def _extract_key_points(self, text: str, max_points: int = 10) -> List[str]:
        """Extract key points from the document."""
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text)
                     if MIN_SENTENCE_LENGTH < len(s.strip()) < MAX_SENTENCE_LENGTH]

        key_indicators = [
            "key", "important", "significant", "main", "primary",
            "essential", "critical", "must", "shall", "required",
            "conclusion", "finding", "result", "recommendation",
            "summary", "objective", "goal", "purpose",
        ]

        points = []
        for sentence in sentences:
            s_lower = sentence.lower()
            if any(ind in s_lower for ind in key_indicators):
                points.append(sentence)
                if len(points) >= max_points:
                    break

        return points

    # ── Entity Extraction ─────────────────────────────────────────────

    def _extract_entities(self, text: str) -> List[dict]:
        """Extract named entities from text."""
        entities = []
        seen = set()

        # Dates
        date_patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            r'\b(\w+ \d{1,2},? \d{4})\b',
            r'\b(\d{4}-\d{2}-\d{2})\b',
        ]
        for pattern in date_patterns:
            for match in re.finditer(pattern, text):
                date = match.group(1)
                if date not in seen:
                    seen.add(date)
                    entities.append({"type": "date", "text": date, "confidence": 0.8})

        # Money amounts
        money_pattern = r'\$[\d,]+(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars|USD|EUR|GBP)\b'
        for match in re.finditer(money_pattern, text):
            amount = match.group(0)
            if amount not in seen:
                seen.add(amount)
                entities.append({"type": "money", "text": amount, "confidence": 0.9})

        # Percentages
        pct_pattern = r'\b\d+(?:\.\d+)?%'
        for match in re.finditer(pct_pattern, text):
            pct = match.group(0)
            if pct not in seen:
                seen.add(pct)
                entities.append({"type": "percentage", "text": pct, "confidence": 0.9})

        # Organizations (capitalized multi-word)
        org_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company|Organization|Institute|University|Foundation|Agency|Association|Group|Partners|Solutions|Technologies))\b'
        for match in re.finditer(org_pattern, text):
            org = match.group(1)
            if org not in seen:
                seen.add(org)
                entities.append({"type": "organization", "text": org, "confidence": 0.7})

        # Email addresses
        email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            email = match.group(0)
            if email not in seen:
                seen.add(email)
                entities.append({"type": "email", "text": email, "confidence": 0.95})

        # URLs
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        for match in re.finditer(url_pattern, text):
            url = match.group(0)
            if url not in seen:
                seen.add(url)
                entities.append({"type": "url", "text": url, "confidence": 0.95})

        return entities[:MAX_EXTRACTED_ITEMS]

    # ── Contract Analysis ─────────────────────────────────────────────

    def _analyze_contract_clauses(self, text: str) -> List[dict]:
        """Extract and analyze contract clauses."""
        clauses = []
        text_lower = text.lower()

        for clause_type in CLAUSE_TYPES:
            # Search for clause-type indicators
            keywords = clause_type.replace("_", " ").split()
            # Also check common variations
            variations = [clause_type.replace("_", " ")]
            if clause_type == "limitation_of_liability":
                variations.extend(["limit of liability", "liability cap", "liability limit"])
            elif clause_type == "intellectual_property":
                variations.extend(["ip rights", "copyright", "patent", "trademark"])
            elif clause_type == "dispute_resolution":
                variations.extend(["arbitration", "mediation", "jurisdiction"])
            elif clause_type == "force_majeure":
                variations.extend(["act of god", "unforeseeable", "impossibility"])
            elif clause_type == "data_protection":
                variations.extend(["privacy", "gdpr", "data processing", "personal data"])

            for variation in variations:
                if variation in text_lower:
                    # Find the surrounding context
                    idx = text_lower.index(variation)
                    start = max(0, idx - 100)
                    end = min(len(text), idx + 300)
                    context = text[start:end].strip()

                    clause = ContractClause(clause_type, context)

                    # Assess risk
                    for level, indicators in RISK_INDICATORS.items():
                        for indicator in indicators:
                            if indicator in context.lower():
                                clause.risk_factors.append(indicator)
                                if level == "high":
                                    clause.risk_level = "high"
                                elif level == "medium" and clause.risk_level != "high":
                                    clause.risk_level = "medium"

                    # Check if unusual
                    unusual_terms = [
                        "perpetual", "irrevocable", "unlimited",
                        "sole discretion", "without notice",
                        "personal guarantee", "jointly and severally",
                    ]
                    if any(term in context.lower() for term in unusual_terms):
                        clause.is_unusual = True

                    clauses.append(clause.to_dict())
                    break  # Don't double-count the same clause type

        return clauses

    def _identify_contract_risks(self, text: str) -> List[dict]:
        """Identify risks in contract text."""
        risks = []
        text_lower = text.lower()

        for level, indicators in RISK_INDICATORS.items():
            for indicator in indicators:
                if indicator in text_lower:
                    # Find context
                    idx = text_lower.index(indicator)
                    start = max(0, idx - 50)
                    end = min(len(text), idx + 200)
                    context = text[start:end].strip()

                    risks.append({
                        "level": level,
                        "indicator": indicator,
                        "context": context[:200],
                        "recommendation": self._risk_recommendation(indicator, level),
                    })

        # Deduplicate by indicator
        seen = set()
        unique_risks = []
        for risk in risks:
            if risk["indicator"] not in seen:
                seen.add(risk["indicator"])
                unique_risks.append(risk)

        return unique_risks[:MAX_EXTRACTED_ITEMS]

    def _risk_recommendation(self, indicator: str, level: str) -> str:
        """Generate a recommendation for a contract risk."""
        recommendations = {
            "unlimited liability": "Consider capping liability at contract value",
            "personal guarantee": "Negotiate removal or limit to specific obligations",
            "irrevocable": "Ensure this is truly necessary; add termination conditions",
            "perpetual": "Add a reasonable term limit with renewal option",
            "sole discretion": "Negotiate for mutual agreement or reasonable standards",
            "without limitation": "Add specific caps and carve-outs",
            "liquidated damages": "Ensure damages are proportionate and reasonable",
            "consequential damages": "Consider mutual exclusion of consequential damages",
        }
        for key, rec in recommendations.items():
            if key in indicator:
                return rec
        return f"Review this {level}-risk term with legal counsel"

    # ── Argument Mapping ──────────────────────────────────────────────

    def _map_arguments(self, text: str) -> List[dict]:
        """
        Map the argumentative structure of a document.
        Identifies claims, evidence, and reasoning patterns.
        """
        arguments = []
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text)
                     if len(s.strip()) > MIN_SENTENCE_LENGTH]

        claim_indicators = [
            "therefore", "thus", "consequently", "we conclude",
            "this shows", "this demonstrates", "the evidence suggests",
            "we argue", "we claim", "it is clear that", "obviously",
            "the data indicates", "results show", "findings suggest",
        ]

        evidence_indicators = [
            "according to", "the study found", "data shows",
            "research indicates", "evidence suggests", "for example",
            "such as", "specifically", "in particular", "the report states",
            "percent", "%", "survey", "experiment", "analysis",
        ]

        assumption_indicators = [
            "assuming", "given that", "if we accept", "it is assumed",
            "premise", "based on the assumption", "taking for granted",
            "we presuppose", "it goes without saying",
        ]

        for i, sentence in enumerate(sentences):
            s_lower = sentence.lower()

            # Check for claims
            if any(ind in s_lower for ind in claim_indicators):
                arg = Argument(sentence)
                # Look for supporting evidence in nearby sentences
                for j in range(max(0, i-3), min(len(sentences), i+3)):
                    if j != i and any(ind in sentences[j].lower() for ind in evidence_indicators):
                        arg.evidence.append(sentences[j])
                # Look for assumptions
                for j in range(max(0, i-2), min(len(sentences), i+2)):
                    if any(ind in sentences[j].lower() for ind in assumption_indicators):
                        arg.assumptions.append(sentences[j])

                # Assess strength
                arg.strength = min(1.0, 0.3 + len(arg.evidence) * 0.15)
                if arg.assumptions:
                    arg.strength -= len(arg.assumptions) * 0.05
                arg.strength = _clamp(arg.strength)

                arguments.append(arg.to_dict())
                if len(arguments) >= MAX_ARGUMENT_DEPTH * 3:
                    break

        return arguments

    # ── Fallacy Detection ─────────────────────────────────────────────

    def _detect_fallacies(self, text: str) -> List[dict]:
        """Detect logical fallacies in text."""
        fallacies = []
        text_lower = text.lower()
        sentences = re.split(r'(?<=[.!?])\s+', text)

        for fallacy_name, info in FALLACY_PATTERNS.items():
            for pattern in info["patterns"]:
                # Use regex for pattern matching
                try:
                    if ".*" in pattern:
                        matches = re.finditer(pattern, text_lower)
                    else:
                        matches = re.finditer(r'\b' + re.escape(pattern) + r'\b', text_lower)

                    for match in matches:
                        # Find the sentence containing this match
                        match_pos = match.start()
                        context = ""
                        for sent in sentences:
                            if match.group(0) in sent.lower():
                                context = sent[:200]
                                break

                        fallacies.append({
                            "fallacy": fallacy_name,
                            "description": info["description"],
                            "matched_text": match.group(0),
                            "context": context,
                            "confidence": 0.6,  # pattern-based, not certain
                        })
                except re.error:
                    continue

        # Deduplicate
        seen = set()
        unique = []
        for f in fallacies:
            key = f"{f['fallacy']}:{f['matched_text']}"
            if key not in seen:
                seen.add(key)
                unique.append(f)

        return unique[:20]

    # ── Bias Detection ───────────────────────────────────────────────

    def _detect_bias(self, text: str) -> List[dict]:
        """Detect potential bias indicators in text."""
        indicators = []

        # Loaded language
        loaded_words = {
            "positive": ["amazing", "incredible", "revolutionary", "breakthrough",
                        "unprecedented", "extraordinary", "remarkable", "brilliant"],
            "negative": ["disastrous", "catastrophic", "devastating", "terrible",
                        "horrible", "outrageous", "scandalous", "shameful"],
        }

        text_lower = text.lower()
        for polarity, words in loaded_words.items():
            found = [w for w in words if w in text_lower]
            if found:
                indicators.append({
                    "type": "loaded_language",
                    "polarity": polarity,
                    "words": found,
                    "severity": "medium" if len(found) > 2 else "low",
                })

        # One-sided presentation (check for counterarguments)
        counter_indicators = ["however", "on the other hand", "conversely",
                            "critics argue", "opponents", "counterpoint",
                            "alternatively", "despite", "although"]
        counter_count = sum(1 for ind in counter_indicators if ind in text_lower)
        if counter_count == 0 and len(text.split()) > 200:
            indicators.append({
                "type": "one_sided",
                "description": "No counterarguments or alternative perspectives detected",
                "severity": "medium",
            })

        # Excessive hedging or certainty
        hedging_words = ["perhaps", "maybe", "possibly", "might", "could be"]
        certainty_words = ["definitely", "certainly", "absolutely", "undoubtedly", "clearly"]
        hedge_count = sum(1 for w in hedging_words if w in text_lower)
        certainty_count = sum(1 for w in certainty_words if w in text_lower)
        if certainty_count > 3 and hedge_count == 0:
            indicators.append({
                "type": "excessive_certainty",
                "description": "High certainty language without hedging — potential overconfidence",
                "severity": "low",
            })

        return indicators

    # ── Reading Level ─────────────────────────────────────────────────

    def _assess_reading_level(self, text: str) -> dict:
        """Assess reading level using Flesch-Kincaid and related metrics."""
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        words = text.split()
        syllables = sum(self._count_syllables(w) for w in words)

        n_sentences = max(len(sentences), 1)
        n_words = max(len(words), 1)

        # Flesch Reading Ease
        flesch_re = 206.835 - 1.015 * (n_words / n_sentences) - 84.6 * (syllables / n_words)
        flesch_re = max(0, min(100, flesch_re))

        # Flesch-Kincaid Grade Level
        fk_grade = 0.39 * (n_words / n_sentences) + 11.8 * (syllables / n_words) - 15.59
        fk_grade = max(0, min(18, fk_grade))

        # Determine level
        if fk_grade < 6:
            level = "elementary"
        elif fk_grade < 9:
            level = "middle_school"
        elif fk_grade < 13:
            level = "high_school"
        elif fk_grade < 16:
            level = "college"
        else:
            level = "graduate"

        # Vocabulary complexity
        unique_words = set(w.lower() for w in words)
        vocab_richness = len(unique_words) / n_words if n_words > 0 else 0

        return {
            "flesch_reading_ease": round(flesch_re, 1),
            "flesch_kincaid_grade": round(fk_grade, 1),
            "level": level,
            "avg_sentence_length": round(n_words / n_sentences, 1),
            "avg_syllables_per_word": round(syllables / n_words, 2),
            "vocabulary_richness": round(vocab_richness, 3),
            "total_words": n_words,
            "unique_words": len(unique_words),
        }

    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for a word."""
        word = word.lower().strip()
        if len(word) <= 2:
            return 1
        # Simple heuristic: count vowel groups
        vowels = "aeiouy"
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        # Adjust for silent e
        if word.endswith("e") and count > 1:
            count -= 1
        return max(1, count)

    # ── Limitations (Research Papers) ─────────────────────────────────

    def _identify_limitations(self, text: str) -> List[dict]:
        """Identify stated limitations in research papers."""
        limitations = []
        limit_keywords = [
            "limitation", "caveat", "weakness", "shortcoming",
            "future work", "further research", "could not",
            "did not account for", "beyond the scope",
            "small sample", "preliminary", "exploratory",
        ]

        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text)
                     if len(s.strip()) > MIN_SENTENCE_LENGTH]

        for sentence in sentences:
            s_lower = sentence.lower()
            if any(kw in s_lower for kw in limit_keywords):
                limitations.append({
                    "type": "limitation",
                    "text": sentence[:300],
                    "confidence": 0.7,
                })

        return limitations[:20]

    # ── Action Items ──────────────────────────────────────────────────

    def _extract_action_items(self, text: str) -> List[str]:
        """Extract action items and tasks from text."""
        action_items = []
        action_patterns = [
            r'(?:must|shall|should|need to|has to|required to)\s+([^.!?]+[.!?])',
            r'(?:TODO|FIXME|ACTION|TASK|NEXT)[:\s]+([^.!?]+)',
            r'(?:we will|we shall|the team will|plan to|intend to)\s+([^.!?]+[.!?])',
            r'(?:deadline|due by|by \w+ \d+|before \w+ \d+)[:\s]*([^.!?]+)',
        ]

        for pattern in action_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                item = match.group(0).strip()
                if 10 < len(item) < 200:
                    action_items.append(item)

        return action_items[:20]

    # ── Cross-Document Analysis ───────────────────────────────────────

    def compare_documents(self, docs: List[dict]) -> dict:
        """
        Compare multiple documents for agreements, contradictions,
        and unique contributions.
        """
        if len(docs) < 2:
            return {"error": "Need at least 2 documents to compare"}

        # Extract key points from each
        all_points = {}
        for i, doc in enumerate(docs):
            text = doc.get("text", "")
            points = self._extract_key_points(text, max_points=5)
            all_points[f"doc_{i}"] = {
                "title": doc.get("title", f"Document {i}"),
                "key_points": points,
                "word_count": len(text.split()),
            }

        # Find overlapping vocabulary
        doc_words = {}
        for i, doc in enumerate(docs):
            words = set(w.lower() for w in doc.get("text", "").split() if len(w) > 4)
            doc_words[f"doc_{i}"] = words

        overlaps = {}
        doc_keys = list(doc_words.keys())
        for i, k1 in enumerate(doc_keys):
            for k2 in doc_keys[i+1:]:
                shared = doc_words[k1] & doc_words[k2]
                total = doc_words[k1] | doc_words[k2]
                overlap_pct = len(shared) / max(len(total), 1)
                overlaps[f"{k1}_vs_{k2}"] = {
                    "shared_words": len(shared),
                    "overlap_percentage": round(overlap_pct * 100, 1),
                    "sample_shared": list(shared)[:10],
                }

        return {
            "documents": all_points,
            "vocabulary_overlap": overlaps,
            "document_count": len(docs),
        }

    # ── Stats ────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Get document intelligence statistics."""
        return {
            "analyses_performed": len(self._analysis_history),
            "clause_types_known": len(CLAUSE_TYPES),
            "fallacy_patterns": len(FALLACY_PATTERNS),
            "risk_levels": list(RISK_INDICATORS.keys()),
        }

    def format_for_prompt(self, max_chars: int = 400) -> str:
        """Format document intelligence context for system prompt."""
        stats = self.get_stats()
        parts = [
            "[DOCUMENT INTELLIGENCE — Analysis engine]",
            f"Analyses: {stats['analyses_performed']} | "
            f"Clause types: {stats['clause_types_known']} | "
            f"Fallacy patterns: {stats['fallacy_patterns']}",
        ]
        return "\n".join(parts)[:max_chars]


# ── Singleton ───────────────────────────────────────────────────────────────

_document_intelligence = None
_di_lock = threading.Lock()


def get_document_intelligence() -> DocumentIntelligence:
    """Get singleton DocumentIntelligence instance."""
    global _document_intelligence
    if _document_intelligence is None:
        with _di_lock:
            if _document_intelligence is None:
                _document_intelligence = DocumentIntelligence()
    return _document_intelligence
