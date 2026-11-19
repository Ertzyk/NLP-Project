from dataclasses import dataclass
import json
from pathlib import Path
import random

from src.syntax.morphology import (
    choose_indefinite_article,
    conjugate_be,
    conjugate_do,
    conjugate_have,
    past_participle,
    past_simple,
    pluralize_noun,
    present_participle,
    third_person_singular,
)

TIMES = ("past", "present", "future", "conditional")
ASPECTS = ("simple", "continuous", "perfect", "perfect_continuous")
MOODS = ("declarative", "negative", "interrogative", "imperative", "imperative_negative")
VOICES = ("active", "passive")


@dataclass(frozen = True)
class Entity:
    """Represents either a Noun Phrase or a Personal Pronoun."""
    subject_text: str
    object_text: str
    reflexive_text: str
    person: int
    number: str  # "sg" or "pl"


PERSONAL_PRONOUNS: list[Entity] = [
    Entity("I", "me", "myself", 1, "sg"),
    Entity("you", "you", "yourself", 2, "sg"),
    Entity("he", "him", "himself", 3, "sg"),
    Entity("she", "her", "herself", 3, "sg"),
    Entity("it", "it", "itself", 3, "sg"),
    Entity("we", "us", "ourselves", 1, "pl"),
    Entity("you", "you", "yourselves", 2, "pl"),
    Entity("they", "them", "themselves", 3, "pl"),
]

AGENT_PRONOUNS = [p for p in PERSONAL_PRONOUNS if p.subject_text != "it"]
OBJECT_PRONOUNS = [p for p in PERSONAL_PRONOUNS if p.subject_text in ("it", "they")]

DETERMINERS: dict[str, dict[str, list[str]]] = {
    "definite": {"sg": ["the"], "pl": ["the"]},
    "indefinite": {"sg": ["a/an"], "pl": []},
    "possessive": {
        "sg": ["my", "your", "his", "her", "its", "our", "their"],
        "pl": ["my", "your", "his", "her", "its", "our", "their"],
    },
    "demonstrative": {"sg": ["this", "that"], "pl": ["these", "those"]},
    "quantifier": {
        "sg": ["every", "each", "another", "some", "any", "no"],
        "pl": ["many", "few", "several", "all", "some", "any", "no"],
    },
}


def capitalize_first(text: str) -> str:
    return text[0].upper() + text[1:] if text else text


def build_noun_phrase(noun: str, number: str = "sg", adjective: str | None = None, determiner: str | None = "the",
    reflexive: str | None = None) -> Entity:
    """Builds a grammatical NP with optional determiner and adjective."""
    head = pluralize_noun(noun) if number == "pl" else noun
    tokens: list[str] = []

    if adjective:
        tokens.append(adjective)
    tokens.append(head)

    if determiner == "a/an":
        if number == "sg":
            tokens.insert(0, choose_indefinite_article(tokens[0]))
    elif determiner:
        tokens.insert(0, determiner)

    text = " ".join(tokens)
    refl = reflexive or ("themselves" if number == "pl" else "itself")
    return Entity(text, text, refl, person=3, number=number)


def _build_auxiliary_chain(verb: str, time: str, aspect: str, voice: str, mood: str, person: int, number: str) -> list[str]:
    """
    Constructs the English VP token list via the auxiliary stack:
    [will/would] -> [have + V3] -> [be + V-ing] -> [be + V3] -> Main Verb
    """
    slots: list[str] = []
    if time == "future":
        slots.append("will")
    elif time == "conditional":
        slots.append("would")

    if aspect in ("perfect", "perfect_continuous"):
        slots.append("have")
    if aspect in ("continuous", "perfect_continuous"):
        slots.append("be_cont")
    if voice == "passive":
        slots.append("be_pass")
    slots.append(verb)

    if len(slots) == 1:
        if mood == "declarative":
            if time == "present":
                return [third_person_singular(verb) if (number == "sg" and person == 3) else verb]
            return [past_simple(verb)]
        return [conjugate_do(time, person, number), verb]

    tokens: list[str] = []
    first = slots[0]
    if first in ("will", "would"):
        tokens.append(first)
    elif first == "have":
        tokens.append(conjugate_have(time, person, number))
    elif first in ("be_cont", "be_pass"):
        tokens.append(conjugate_be(time, person, number))

    for prev, curr in zip(slots, slots[1:]):
        is_be = curr in ("be_cont", "be_pass")
        if prev in ("will", "would"):
            tokens.append("be" if is_be else curr)
        elif prev == "have":
            tokens.append("been" if is_be else past_participle(curr))
        elif prev == "be_cont":
            tokens.append("being" if is_be else present_participle(curr))
        elif prev == "be_pass":
            tokens.append(past_participle(curr))

    return tokens


def generate_sentence(subject: Entity, verb: str, verb_type: str, obj: Entity | None = None, time: str = "present", 
                      aspect: str = "simple", mood: str = "declarative", voice: str = "active") -> str:
    """Generates a single grammatical English SVO/SV/SV-refl sentence."""
    if voice == "passive" and verb_type != "transitive":
        raise ValueError(f"Passive voice is only valid for transitive verbs, got {verb_type!r}.")
    if verb_type == "transitive" and obj is None:
        raise ValueError("Transitive verbs require a direct object.")

    if voice == "passive":
        assert obj is not None
        gram_subj = obj
        tail_parts = [f"by {subject.object_text}"]
    else:
        gram_subj = subject
        if verb_type == "transitive":
            assert obj is not None
            tail_parts = [obj.object_text]
        elif verb_type == "reflexive":
            if mood in ("imperative", "imperative_negative"):
                tail_parts = ["yourselves" if subject.number == "pl" else "yourself"]
            else:
                tail_parts = [subject.reflexive_text]
        else:
            tail_parts = []

    tail = " " + " ".join(tail_parts) if tail_parts else ""

    if mood in ("imperative", "imperative_negative"):
        prefix = "do not " if mood == "imperative_negative" else ""
        vp = f"be {past_participle(verb)}" if voice == "passive" else verb
        return capitalize_first(f"{prefix}{vp}{tail}!")

    vp_tokens = _build_auxiliary_chain(verb = verb, time = time, aspect = aspect, voice = voice, mood = mood,
                                       person = gram_subj.person, number = gram_subj.number)

    if mood == "declarative":
        sentence = f"{gram_subj.subject_text} {' '.join(vp_tokens)}{tail}."
    elif mood == "negative":
        neg_vp = " ".join([vp_tokens[0], "not", *vp_tokens[1:]])
        sentence = f"{gram_subj.subject_text} {neg_vp}{tail}."
    elif mood == "interrogative":
        rest = " ".join(vp_tokens[1:])
        sentence = f"{vp_tokens[0]} {gram_subj.subject_text} {rest}{tail}?"
    else:
        raise ValueError(f"Unsupported mood: {mood!r}")

    return capitalize_first(sentence)


class SVOGenerator:
    """Lexicon-backed generator for structured paradigms and random SVO samples."""

    def __init__(self, lexicon_path: str = "data/lexicon_en.json", seed: int = 42) -> None:
        with open(Path(lexicon_path), "r", encoding="utf-8") as f:
            data = json.load(f)

        self.agent_nouns: list[str] = data["nouns"]["agents"]
        self.object_nouns: list[str] = data["nouns"]["objects"]
        self.all_nouns: list[str] = self.agent_nouns + self.object_nouns

        self.verbs_by_type: dict[str, list[str]] = data["verbs"]
        self.adjectives: list[str] = data["adjectives"]
        self.rng = random.Random(seed)

    def lexicon_counts(self) -> dict[str, int]:
        return {
            "nouns": len(self.all_nouns),
            "verbs": sum(len(v) for v in self.verbs_by_type.values()),
            "adjectives": len(self.adjectives),
        }

    def random_entity(self, role: str = "agent", allow_pronoun: bool = True, determiner_category: str | None = None) -> Entity:
        if allow_pronoun and determiner_category is None and self.rng.random() < 0.25:
            pronoun_pool = AGENT_PRONOUNS if role == "agent" else OBJECT_PRONOUNS
            return self.rng.choice(pronoun_pool)

        pool = self.agent_nouns if role == "agent" else self.object_nouns
        noun = self.rng.choice(pool)
        number = self.rng.choice(["sg", "pl"])

        if determiner_category is None:
            valid_cats = [c for c, opts in DETERMINERS.items() if opts[number]]
            determiner_category = self.rng.choice(valid_cats)

        det_options = DETERMINERS[determiner_category][number]
        if not det_options:
            number = "sg"
            det_options = DETERMINERS[determiner_category][number]

        determiner = self.rng.choice(det_options)
        adjective = self.rng.choice(self.adjectives) if self.rng.random() < 0.65 else None

        reflexive = None
        if role == "agent":
            reflexive = "themselves" if number == "pl" else self.rng.choice(["himself", "herself"])

        return build_noun_phrase(noun, number = number, adjective = adjective, determiner = determiner, reflexive = reflexive)

    def random_sentence(self, verb_type: str | None = None) -> tuple[str, str]:
        vtype = verb_type or self.rng.choice(["transitive", "intransitive", "reflexive"])
        verb = self.rng.choice(self.verbs_by_type[vtype])

        mood = self.rng.choice(MOODS)
        voice = "passive" if (vtype == "transitive" and self.rng.random() < 0.35) else "active"
        time = self.rng.choice(TIMES)
        aspect = self.rng.choice(ASPECTS)

        subject = self.random_entity(role = "agent")
        obj = self.random_entity(role = "object") if vtype == "transitive" else None

        sentence = generate_sentence(subject = subject, verb = verb, verb_type = vtype, obj = obj, time = time, 
                                     aspect = aspect, mood = mood, voice = voice)
        tag = f"{vtype} | {voice} | {mood}" if mood.startswith("imperative") else f"{vtype} | {voice} | {time} {aspect} | {mood}"
        return tag, sentence