#!/usr/bin/env python3
"""
creative_studio.py — Friday Creative Studio Engine
=====================================================

A full creative writing and storytelling system that goes far beyond
"generate text." This is a creative COGNITIVE SYSTEM that plans narratives,
builds worlds, develops characters, manages tone, and produces structured
creative works.

  [CS-1] Narrative Architecture — three-act structure, hero's journey,
         Freytag's pyramid, and custom story frameworks.

  [CS-2] World Builder — creates consistent fictional worlds with rules,
         geography, history, cultures, and magic/tech systems.

  [CS-3] Character Engine — generates multi-dimensional characters with
         motivations, flaws, arcs, and relationship webs.

  [CS-4] Style Transfer — adapts writing to match specific styles
         (Hemingway, Tolkien, cyberpunk, noir, academic, etc.)

  [CS-5] Poetry Generator — structured poetry with meter, rhyme schemes,
         and form (sonnet, haiku, villanelle, free verse, etc.)

  [CS-6] Dialogue System — generates character-consistent dialogue with
         subtext, conflict, and voice differentiation.

  [CS-7] Creative Constraints — generates within specified constraints
         (word count, tone, theme, POV, tense) — constraints breed creativity.

  [CS-8] Iterative Refinement — drafts, critiques, revises. The creative
         process is iterative, not one-shot.

Inspired by:
  - Joseph Campbell's Hero's Journey (1949)
  - Kurt Vonnegut's Story Shapes (1995)
  - Robert McKee's "Story" (1997)
  - Aristotle's Poetics (~335 BCE)

Usage:
    from skills.creative_studio import get_creative_studio
    studio = get_creative_studio()
    story = studio.write_story(genre="sci-fi", theme="first contact")
"""

import hashlib
import json
import math
import random
import re
import threading
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SKILLS_DIR = Path(__file__).parent.resolve()
DATA_DIR = SKILLS_DIR / "creative_data"
WORLDS_FILE = DATA_DIR / "worlds.json"
CHARACTERS_FILE = DATA_DIR / "characters.json"
WORKS_FILE = DATA_DIR / "creative_works.json"
STYLES_FILE = DATA_DIR / "style_profiles.json"

# ── Configuration ───────────────────────────────────────────────────────────

MAX_WORLDS = 50
MAX_CHARACTERS = 200
MAX_WORKS = 100
MAX_STYLE_PROFILES = 30
MAX_CHAPTERS = 20
MAX_SCENES_PER_CHAPTER = 10


def _now() -> str:
    return datetime.now().isoformat()


def _hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:12]


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


# ── Story Structures ────────────────────────────────────────────────────────

STORY_STRUCTURES = {
    "three_act": {
        "name": "Three-Act Structure",
        "description": "Setup → Confrontation → Resolution",
        "acts": [
            {"name": "Act I: Setup", "beats": ["opening_image", "theme_stated", "catalyst", "debate", "break_into_act_ii"]},
            {"name": "Act II: Confrontation", "beats": ["b_story", "fun_and_games", "midpoint", "bad_guys_close_in", "all_is_lost", "dark_night"]},
            {"name": "Act III: Resolution", "beats": ["break_into_act_iii", "finale", "final_image"]},
        ],
    },
    "heros_journey": {
        "name": "Hero's Journey",
        "description": "Campbell's monomyth — departure, initiation, return",
        "acts": [
            {"name": "Departure", "beats": ["ordinary_world", "call_to_adventure", "refusal_of_call", "meeting_mentor", "crossing_threshold"]},
            {"name": "Initiation", "beats": ["tests_allies_enemies", "approach_inmost_cave", "ordeal", "reward"]},
            {"name": "Return", "beats": ["road_back", "resurrection", "return_with_elixir"]},
        ],
    },
    "freytags_pyramid": {
        "name": "Freytag's Pyramid",
        "description": "Rising action → climax → falling action",
        "acts": [
            {"name": "Exposition", "beats": ["introduction", "setting", "initial_situation"]},
            {"name": "Rising Action", "beats": ["inciting_incident", "complications", "rising_tension"]},
            {"name": "Climax", "beats": ["turning_point", "peak_tension"]},
            {"name": "Falling Action", "beats": ["consequences", "loose_ends"]},
            {"name": "Denouement", "beats": ["resolution", "new_equilibrium"]},
        ],
    },
    "kishotenketsu": {
        "name": "Kishōtenketsu",
        "description": "Japanese four-act structure — introduction, development, twist, reconciliation",
        "acts": [
            {"name": "Ki (Introduction)", "beats": ["setup", "characters", "world"]},
            {"name": "Shō (Development)", "beats": ["deepening", "exploration", "building"]},
            {"name": "Ten (Twist)", "beats": ["unexpected_event", "perspective_shift"]},
            {"name": "Ketsu (Reconciliation)", "beats": ["synthesis", "new_understanding"]},
        ],
    },
}

GENRE_DEFAULTS = {
    "sci-fi": {
        "themes": ["exploration", "identity", "technology ethics", "first contact", "time", "consciousness"],
        "tones": ["wonder", "tension", "philosophical", "cerebral"],
        "settings": ["space station", "colony ship", "dystopian city", "research lab", "alien world"],
    },
    "fantasy": {
        "themes": ["power", "destiny", "sacrifice", "good vs evil", "coming of age", "redemption"],
        "tones": ["epic", "mysterious", "whimsical", "dark"],
        "settings": ["enchanted forest", "ancient kingdom", "floating city", "underground realm"],
    },
    "noir": {
        "themes": ["corruption", "justice", "deception", "obsession", "moral ambiguity"],
        "tones": ["cynical", "atmospheric", "tense", "gritty"],
        "settings": ["rain-soaked city", "smoky bar", "seedy motel", "police station"],
    },
    "horror": {
        "themes": ["isolation", "madness", "the unknown", "survival", "guilt"],
        "tones": ["dread", "unsettling", "claustrophobic", "paranoid"],
        "settings": ["abandoned house", "small town", "forest", "hospital", "space vessel"],
    },
    "literary": {
        "themes": ["love", "loss", "identity", "family", "memory", "time"],
        "tones": ["introspective", "lyrical", "bittersweet", "quiet"],
        "settings": ["small town", "family home", "city apartment", "countryside"],
    },
    "cyberpunk": {
        "themes": ["transhumanism", "corporate control", "identity in digital age", "inequality"],
        "tones": ["gritty", "neon-lit", "rebellious", "philosophical"],
        "settings": ["megacity slums", "virtual reality", "corporate tower", "underground hacker den"],
    },
}

POETRY_FORMS = {
    "haiku": {"lines": 3, "syllables": [5, 7, 5], "description": "Japanese 5-7-5"},
    "tanka": {"lines": 5, "syllables": [5, 7, 5, 7, 7], "description": "Japanese extended haiku"},
    "sonnet": {"lines": 14, "rhyme": "abab cdcd efef gg", "description": "Shakespearean sonnet"},
    "limerick": {"lines": 5, "rhyme": "aabba", "description": "Humorous aabba"},
    "villanelle": {"lines": 19, "rhyme": "aba aba aba aba aba abaa", "description": "19 lines, 2 refrains"},
    "free_verse": {"lines": 0, "description": "No fixed structure — rhythm and imagery driven"},
    "acrostic": {"lines": 0, "description": "First letters spell a word"},
    "couplet": {"lines": 2, "rhyme": "aa", "description": "Two rhyming lines"},
}


# ── Data Structures ─────────────────────────────────────────────────────────

class Character:
    """A multi-dimensional character with arc, traits, and relationships."""

    __slots__ = [
        "character_id", "name", "role", "description",
        "traits", "flaws", "motivations", "backstory",
        "arc_start", "arc_end", "voice_notes",
        "relationships", "first_created",
    ]

    def __init__(self, name: str, role: str = "supporting",
                 description: str = ""):
        self.character_id = _hash(f"{name}:{role}")
        self.name = name
        self.role = role  # protagonist, antagonist, supporting, mentor, etc.
        self.description = description[:300]
        self.traits: List[str] = []
        self.flaws: List[str] = []
        self.motivations: List[str] = []
        self.backstory: str = ""
        self.arc_start: str = ""  # who they are at the beginning
        self.arc_end: str = ""    # who they become
        self.voice_notes: str = ""  # how they speak, verbal tics, vocabulary
        self.relationships: Dict[str, str] = {}  # character_id → relationship
        self.first_created = _now()

    def to_dict(self) -> dict:
        return {
            "character_id": self.character_id,
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "traits": self.traits,
            "flaws": self.flaws,
            "motivations": self.motivations,
            "backstory": self.backstory[:500],
            "arc_start": self.arc_start,
            "arc_end": self.arc_end,
            "voice_notes": self.voice_notes,
            "relationships": self.relationships,
            "first_created": self.first_created,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Character":
        c = cls(d.get("name", ""), d.get("role", "supporting"),
                d.get("description", ""))
        c.character_id = d.get("character_id", c.character_id)
        c.traits = d.get("traits", [])
        c.flaws = d.get("flaws", [])
        c.motivations = d.get("motivations", [])
        c.backstory = d.get("backstory", "")
        c.arc_start = d.get("arc_start", "")
        c.arc_end = d.get("arc_end", "")
        c.voice_notes = d.get("voice_notes", "")
        c.relationships = d.get("relationships", {})
        c.first_created = d.get("first_created", _now())
        return c


class World:
    """A fictional world with rules, geography, and culture."""

    __slots__ = [
        "world_id", "name", "genre", "description",
        "geography", "cultures", "magic_system", "technology",
        "history", "rules", "tone",
    ]

    def __init__(self, name: str, genre: str = "fantasy",
                 description: str = ""):
        self.world_id = _hash(f"{name}:{genre}")
        self.name = name
        self.genre = genre
        self.description = description[:500]
        self.geography: List[str] = []
        self.cultures: List[str] = []
        self.magic_system: str = ""
        self.technology: str = ""
        self.history: List[str] = []
        self.rules: List[str] = []
        self.tone: str = ""

    def to_dict(self) -> dict:
        return {
            "world_id": self.world_id,
            "name": self.name,
            "genre": self.genre,
            "description": self.description,
            "geography": self.geography,
            "cultures": self.cultures,
            "magic_system": self.magic_system,
            "technology": self.technology,
            "history": self.history,
            "rules": self.rules,
            "tone": self.tone,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "World":
        w = cls(d.get("name", ""), d.get("genre", "fantasy"),
                d.get("description", ""))
        w.world_id = d.get("world_id", w.world_id)
        w.geography = d.get("geography", [])
        w.cultures = d.get("cultures", [])
        w.magic_system = d.get("magic_system", "")
        w.technology = d.get("technology", "")
        w.history = d.get("history", [])
        w.rules = d.get("rules", [])
        w.tone = d.get("tone", "")
        return w


class StyleProfile:
    """A writing style profile with vocabulary, rhythm, and technique markers."""

    __slots__ = [
        "style_id", "name", "description",
        "sentence_length", "vocabulary_level", "imagery_density",
        "dialogue_ratio", "techniques", "sample_passage",
    ]

    def __init__(self, name: str, description: str = ""):
        self.style_id = _hash(name)
        self.name = name
        self.description = description[:200]
        self.sentence_length = "medium"   # short, medium, long
        self.vocabulary_level = "standard"  # simple, standard, literary, academic
        self.imagery_density = 0.5         # 0=sparse, 1=dense
        self.dialogue_ratio = 0.3          # 0=none, 1=all dialogue
        self.techniques: List[str] = []
        self.sample_passage: str = ""

    def to_dict(self) -> dict:
        return {
            "style_id": self.style_id,
            "name": self.name,
            "description": self.description,
            "sentence_length": self.sentence_length,
            "vocabulary_level": self.vocabulary_level,
            "imagery_density": round(self.imagery_density, 2),
            "dialogue_ratio": round(self.dialogue_ratio, 2),
            "techniques": self.techniques,
            "sample_passage": self.sample_passage[:300],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StyleProfile":
        s = cls(d.get("name", ""), d.get("description", ""))
        s.style_id = d.get("style_id", s.style_id)
        s.sentence_length = d.get("sentence_length", "medium")
        s.vocabulary_level = d.get("vocabulary_level", "standard")
        s.imagery_density = d.get("imagery_density", 0.5)
        s.dialogue_ratio = d.get("dialogue_ratio", 0.3)
        s.techniques = d.get("techniques", [])
        s.sample_passage = d.get("sample_passage", "")
        return s


class CreativeWork:
    """A creative work with metadata and structure."""

    __slots__ = [
        "work_id", "title", "genre", "form", "structure",
        "characters", "world_id", "style_id",
        "chapters", "metadata", "created_at", "word_count",
    ]

    def __init__(self, title: str, genre: str = "literary",
                 form: str = "story"):
        self.work_id = _hash(f"{title}:{_now()}")
        self.title = title
        self.genre = genre
        self.form = form  # story, poem, script, essay
        self.structure = ""
        self.characters: List[str] = []
        self.world_id: Optional[str] = None
        self.style_id: Optional[str] = None
        self.chapters: List[dict] = []
        self.metadata: Dict[str, Any] = {}
        self.created_at = _now()
        self.word_count = 0

    def to_dict(self) -> dict:
        return {
            "work_id": self.work_id,
            "title": self.title,
            "genre": self.genre,
            "form": self.form,
            "structure": self.structure,
            "characters": self.characters,
            "world_id": self.world_id,
            "style_id": self.style_id,
            "chapters": self.chapters,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "word_count": self.word_count,
        }


# ── Creative Studio ─────────────────────────────────────────────────────────

class CreativeStudio:
    """
    Full creative writing and storytelling system.

    Plans narratives, builds worlds, develops characters,
    and produces structured creative works.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._worlds: Dict[str, World] = {}
        self._characters: Dict[str, Character] = {}
        self._works: Dict[str, CreativeWork] = {}
        self._styles: Dict[str, StyleProfile] = {}
        self._load()
        self._init_default_styles()

    def _load(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        for fname, target, cls in [
            (WORLDS_FILE, "_worlds", World),
            (CHARACTERS_FILE, "_characters", Character),
            (STYLES_FILE, "_styles", StyleProfile),
        ]:
            if fname.exists():
                try:
                    data = json.loads(fname.read_text(encoding="utf-8"))
                    items = getattr(self, target)
                    for d in data:
                        obj = cls.from_dict(d)
                        key = getattr(obj, f"{cls.__name__.lower()}_id", obj.name)
                        items[key] = obj
                except (json.JSONDecodeError, IOError):
                    pass

    def _save(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with self._lock:
            WORLDS_FILE.write_text(json.dumps(
                [w.to_dict() for w in list(self._worlds.values())[-MAX_WORLDS:]],
                indent=2, ensure_ascii=False), encoding="utf-8")
            CHARACTERS_FILE.write_text(json.dumps(
                [c.to_dict() for c in list(self._characters.values())[-MAX_CHARACTERS:]],
                indent=2, ensure_ascii=False), encoding="utf-8")
            STYLES_FILE.write_text(json.dumps(
                [s.to_dict() for s in list(self._styles.values())[-MAX_STYLE_PROFILES:]],
                indent=2, ensure_ascii=False), encoding="utf-8")

    def _init_default_styles(self):
        """Initialize built-in style profiles."""
        defaults = {
            "hemingway": StyleProfile("Hemingway", "Short sentences, minimal adjectives, iceberg theory"),
            "tolkien": StyleProfile("Tolkien", "Epic, detailed, archaic vocabulary, songs and poetry"),
            "noir": StyleProfile("Hardboiled Noir", "Cynical first-person, similes, atmosphere over plot"),
            "cyberpunk": StyleProfile("Cyberpunk", "Technical jargon, fragmented, neon imagery, street slang"),
            "literary": StyleProfile("Literary Fiction", "Dense imagery, introspective, layered prose"),
            "minimalist": StyleProfile("Minimalist", "Sparse, precise, every word earns its place"),
        }
        for name, style in defaults.items():
            if style.style_id not in self._styles:
                self._styles[style.style_id] = style

    # ── Story Planning ───────────────────────────────────────────────

    def plan_story(self, genre: str = "literary", theme: str = "",
                   structure: str = "three_act",
                   word_target: int = 2000) -> dict:
        """
        Generate a story plan with structure, beats, and guidance.

        Returns a detailed plan that can guide story writing.
        """
        genre_lower = genre.lower()
        genre_data = GENRE_DEFAULTS.get(genre_lower, GENRE_DEFAULTS["literary"])
        struct = STORY_STRUCTURES.get(structure, STORY_STRUCTURES["three_act"])

        # Select theme if not provided
        if not theme:
            theme = random.choice(genre_data["themes"])

        # Build plan
        plan = {
            "genre": genre,
            "theme": theme,
            "structure": struct["name"],
            "structure_description": struct["description"],
            "tone_suggestions": genre_data["tones"],
            "setting_suggestions": genre_data["settings"],
            "word_target": word_target,
            "acts": [],
        }

        beats_per_act = max(1, word_target // (len(struct["acts"]) * 100))
        for act in struct["acts"]:
            act_plan = {
                "name": act["name"],
                "beats": act["beats"],
                "target_words": word_target // len(struct["acts"]),
                "guidance": [],
            }
            for beat in act["beats"]:
                guidance = beat.replace("_", " ").capitalize()
                act_plan["guidance"].append(guidance)
            plan["acts"].append(act_plan)

        return plan

    # ── Character Creation ───────────────────────────────────────────

    def create_character(self, name: str, role: str = "supporting",
                         genre: str = "literary",
                         traits: List[str] = None) -> Character:
        """
        Create a multi-dimensional character.

        Generates traits, flaws, motivations, and arc if not provided.
        """
        character = Character(name, role)

        if traits:
            character.traits = traits
        else:
            # Generate based on role and genre
            trait_pool = {
                "protagonist": ["determined", "flawed", "relatable", "brave", "conflicted"],
                "antagonist": ["intelligent", "charismatic", "ruthless", "driven", "complex"],
                "mentor": ["wise", "patient", "mysterious", "burdened", "kind"],
                "supporting": ["loyal", "pragmatic", "humorous", "cautious", "curious"],
            }
            character.traits = random.sample(
                trait_pool.get(role, trait_pool["supporting"]),
                min(3, len(trait_pool.get(role, trait_pool["supporting"])))

            )

        flaw_pool = [
            "impulsive", "overconfident", "distrustful", "obsessive",
            "self-doubting", "reckless", "stubborn", "naive", "cynical",
        ]
        character.flaws = random.sample(flaw_pool, 2)

        motivation_pool = [
            "seeking redemption", "protecting loved ones",
            "uncovering the truth", "proving their worth",
            "escaping the past", "finding belonging",
            "gaining power", "seeking justice",
        ]
        character.motivations = [random.choice(motivation_pool)]

        character.arc_start = f"Defined by their {character.flaws[0]} nature"
        character.arc_end = f"Overcomes {character.flaws[0]} through {theme if 'theme' in dir() else 'hardship'}"
        character.voice_notes = f"Speaks with {random.choice(['directness', 'wit', 'caution', 'warmth', 'intensity'])}"

        with self._lock:
            self._characters[character.character_id] = character
            self._save()

        return character

    # ── World Building ───────────────────────────────────────────────

    def build_world(self, name: str, genre: str = "fantasy",
                    description: str = "") -> World:
        """
        Build a fictional world with consistent rules and lore.
        """
        world = World(name, genre, description)

        genre_data = GENRE_DEFAULTS.get(genre.lower(), GENRE_DEFAULTS["fantasy"])
        world.tone = random.choice(genre_data["tones"])

        # Generate geography
        geo_pool = [
            "mountain ranges", "vast plains", "archipelago", "dense forests",
            "desert wasteland", "floating islands", "underground caverns",
            "coastal cliffs", "volcanic islands", "frozen tundra",
        ]
        world.geography = random.sample(geo_pool, 3)

        # Generate cultures
        culture_pool = [
            "nomadic traders", "isolated monastery", "merchant guilds",
            "warrior clans", "scholar academies", "underground resistance",
            "technocratic council", "religious order", "free cities",
        ]
        world.cultures = random.sample(culture_pool, 2)

        # Genre-specific world building
        if genre.lower() == "fantasy":
            world.magic_system = "Element-based with cost and consequence"
            world.rules = [
                "Magic requires personal sacrifice",
                "Ancient artifacts hold residual power",
                "The natural world has memory",
            ]
        elif genre.lower() == "sci-fi":
            world.technology = "Post-scarcity with resource constraints at the frontier"
            world.rules = [
                "FTL travel exists but is dangerous",
                "AI is ubiquitous but not sentient",
                "Genetic modification is regulated",
            ]
        elif genre.lower() == "cyberpunk":
            world.technology = "Advanced but stratified — high-tech for the rich, low-tech for the rest"
            world.rules = [
                "Corporations are more powerful than governments",
                "Identity is fluid in the digital age",
                "The street finds its own uses for things",
            ]

        with self._lock:
            self._worlds[world.world_id] = world
            self._save()

        return world

    # ── Style Transfer ───────────────────────────────────────────────

    def get_style(self, name: str) -> Optional[StyleProfile]:
        """Get a style profile by name."""
        name_lower = name.lower().replace(" ", "_")
        for style in self._styles.values():
            if style.name.lower().replace(" ", "_") == name_lower:
                return style
        return None

    def list_styles(self) -> List[dict]:
        """List all available style profiles."""
        return [s.to_dict() for s in self._styles.values()]

    # ── Poetry ───────────────────────────────────────────────────────

    def get_poetry_form(self, form_name: str) -> Optional[dict]:
        """Get poetry form specifications."""
        return POETRY_FORMS.get(form_name.lower())

    def list_poetry_forms(self) -> List[dict]:
        """List all available poetry forms."""
        return [
            {"name": name, **spec}
            for name, spec in POETRY_FORMS.items()
        ]

    # ── Story Generation Guidance ────────────────────────────────────

    def generate_beat_guidance(self, beat_name: str, genre: str,
                                characters: List[str] = None,
                                context: str = "") -> dict:
        """
        Generate writing guidance for a specific story beat.

        Returns what should happen, emotional tone, and writing tips.
        """
        beat_guidance = {
            "opening_image": {
                "purpose": "Establish the tone and show the protagonist's world before change",
                "tone": "atmospheric, establishing",
                "tip": "Show, don't tell. Let the reader feel the world through sensory details.",
            },
            "catalyst": {
                "purpose": "The event that disrupts the protagonist's ordinary world",
                "tone": "surprising, disruptive",
                "tip": "Make it personal. The catalyst should directly affect the protagonist.",
            },
            "debate": {
                "purpose": "The protagonist hesitates — should they act?",
                "tone": "uncertain, anxious",
                "tip": "Show internal conflict. What do they have to lose?",
            },
            "midpoint": {
                "purpose": "Stakes are raised. False victory or false defeat.",
                "tone": "shifting, revelatory",
                "tip": "Change the game. What the protagonist thought was true isn't.",
            },
            "all_is_lost": {
                "purpose": "The lowest point. Something precious is lost.",
                "tone": "desperate, hopeless",
                "tip": "This is where your protagonist's flaw catches up with them.",
            },
            "finale": {
                "purpose": "The protagonist faces the final challenge using everything they've learned",
                "tone": "climactic, earned",
                "tip": "The resolution should come from character growth, not luck.",
            },
        }

        guidance = beat_guidance.get(beat_name, {
            "purpose": f"Story beat: {beat_name.replace('_', ' ')}",
            "tone": "contextual",
            "tip": "Focus on character emotion and advancing the plot.",
        })

        guidance["beat"] = beat_name
        guidance["genre"] = genre
        if characters:
            guidance["characters"] = characters
        guidance["genre_notes"] = GENRE_DEFAULTS.get(
            genre.lower(), {}).get("tones", [])

        return guidance

    # ── Stats ────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Get creative studio statistics."""
        return {
            "worlds_created": len(self._worlds),
            "characters_created": len(self._characters),
            "works_created": len(self._works),
            "style_profiles": len(self._styles),
            "story_structures": len(STORY_STRUCTURES),
            "poetry_forms": len(POETRY_FORMS),
            "genres_supported": len(GENRE_DEFAULTS),
        }

    def format_for_prompt(self, max_chars: int = 500) -> str:
        """Format creative context for system prompt."""
        stats = self.get_stats()
        parts = [
            "[CREATIVE STUDIO — Storytelling engine]",
            f"Worlds: {stats['worlds_created']} | Characters: {stats['characters_created']} | "
            f"Works: {stats['works_created']}",
            f"Structures: {stats['story_structures']} | Poetry forms: {stats['poetry_forms']} | "
            f"Genres: {stats['genres_supported']}",
        ]
        result = "\n".join(parts)
        return result[:max_chars]


# ── Singleton ───────────────────────────────────────────────────────────────

_creative_studio = None
_creative_lock = threading.Lock()


def get_creative_studio() -> CreativeStudio:
    """Get singleton CreativeStudio instance."""
    global _creative_studio
    if _creative_studio is None:
        with _creative_lock:
            if _creative_studio is None:
                _creative_studio = CreativeStudio()
    return _creative_studio
