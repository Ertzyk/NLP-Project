from pathlib import Path

from src.syntax.generator import (
    ASPECTS,
    PERSONAL_PRONOUNS,
    TIMES,
    SVOGenerator,
    build_noun_phrase,
    generate_sentence,
)

PARADIGM_PATH = "results/svo_paradigm.txt"
SAMPLES_PATH = "results/svo_samples.txt"


def run_syntax() -> None:
    gen = SVOGenerator("data/lexicon_en.json", seed=42)
    counts = gen.lexicon_counts()
    print(
        f"Loaded English lexicon: {counts['nouns']} nouns | "
        f"{counts['verbs']} verbs | {counts['adjectives']} adjectives\n"
    )

    # 1. Complete Tense x Aspect x Voice x Mood Paradigm
    subj = build_noun_phrase("writer", number = "sg", adjective = "young", determiner = "the", reflexive = "himself")
    obj = build_noun_phrase("book", number = "sg", adjective = "new", determiner = "his")

    paradigm_lines: list[str] = [
        "=== FULL ENGLISH TENSE / MOOD / VOICE PARADIGM ===",
        "Base SVO: (the young writer) + [write] + (his new book)\n",
    ]

    for voice in ("active", "passive"):
        paradigm_lines.append(f"--- {voice.upper()} VOICE ---")
        for time in TIMES:
            for aspect in ASPECTS:
                label = f"{time.capitalize()} {aspect.replace('_', ' ').title()}"
                paradigm_lines.append(f"[{label}]")
                for mood in ("declarative", "negative", "interrogative"):
                    sent = generate_sentence(
                        subj, "write", "transitive", obj,
                        time=time, aspect=aspect, mood=mood, voice=voice,
                    )
                    paradigm_lines.append(f"  {mood:<14}: {sent}")
        for imp_mood in ("imperative", "imperative_negative"):
            sent = generate_sentence(
                subj, "write", "transitive", obj, mood=imp_mood, voice=voice
            )
            paradigm_lines.append(f"  {imp_mood:<20}: {sent}")
        paradigm_lines.append("")

    Path(PARADIGM_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(PARADIGM_PATH).write_text("\n".join(paradigm_lines), encoding="utf-8")

    # 2. Feature Coverage Showcase & Random Samples
    sample_lines: list[str] = ["=== DETERMINER & PRONOUN FEATURE SHOWCASE ==="]

    showcase = [
        ("Definite + Adj", build_noun_phrase("chef", "sg", "famous", "the"), "prepare", "transitive", build_noun_phrase("meal", "sg", "warm", "a/an"), "present", "simple", "declarative", "active"),
        ("Indefinite (an/a)", build_noun_phrase("teacher", "sg", "honest", "a/an"), "carry", "transitive", build_noun_phrase("umbrella", "sg", "useful", "a/an"), "past", "simple", "declarative", "active"),
        ("Possessive", build_noun_phrase("neighbor", "sg", "kind", "our"), "repair", "transitive", build_noun_phrase("bicycle", "pl", "old", "their"), "future", "simple", "declarative", "active"),
        ("Demonstrative (pl)", build_noun_phrase("builder", "pl", "strong", "these"), "build", "transitive", build_noun_phrase("bridge", "pl", "wooden", "those"), "present", "continuous", "declarative", "active"),
        ("Quantifier + Irreg", build_noun_phrase("cook" if False else "baker", "sg", None, "every"), "polish", "transitive", build_noun_phrase("knife", "pl", "sharp", "many"), "present", "simple", "declarative", "active"),
        ("Pronoun Subj + Obj", PERSONAL_PRONOUNS[2], "take", "transitive", PERSONAL_PRONOUNS[4], "past", "perfect", "declarative", "active"),
        ("Pronoun Passive", PERSONAL_PRONOUNS[2], "take", "transitive", PERSONAL_PRONOUNS[4], "past", "perfect", "declarative", "passive"),
        ("Intransitive", build_noun_phrase("traveler", "pl", "tired", "the"), "arrive", "intransitive", None, "present", "perfect", "declarative", "active"),
        ("Reflexive (NP)", build_noun_phrase("soldier", "pl", "brave", "the", reflexive="themselves"), "defend", "reflexive", None, "conditional", "simple", "declarative", "active"),
        ("Reflexive (Pronoun)", PERSONAL_PRONOUNS[3], "blame", "reflexive", None, "past", "simple", "negative", "active"),
        ("Reflexive Imperative", PERSONAL_PRONOUNS[1], "introduce", "reflexive", None, "present", "simple", "imperative", "active"),
    ]

    for label, s, v, vt, o, t, a, m, vo in showcase:
        sent = generate_sentence(s, v, vt, o, time = t, aspect = a, mood = m, voice = vo)
        sample_lines.append(f"  {label:<20}: {sent}")

    sample_lines.append("\n=== RANDOM GENERATED SAMPLES (20) ===")
    for i in range(1, 21):
        tag, sent = gen.random_sentence()
        sample_lines.append(f"  {i:02d}. [{tag}] {sent}")

    Path(SAMPLES_PATH).write_text("\n".join(sample_lines), encoding = "utf-8")

    print("\n".join(sample_lines))
    print("-" * 60)
    print(f"Saved 100-form paradigm to : {PARADIGM_PATH}")
    print(f"Saved feature showcase & samples: {SAMPLES_PATH}")