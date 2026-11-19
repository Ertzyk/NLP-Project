VOWELS = set("aeiou")
SILENT_H_PREFIXES = ("honest", "hour", "honor", "heir")

IRREGULAR_VERBS: dict[str, tuple[str, str]] = {
    # lemma: (past_simple, past_participle)
    "read": ("read", "read"),
    "write": ("wrote", "written"),
    "buy": ("bought", "bought"),
    "sell": ("sold", "sold"),
    "build": ("built", "built"),
    "break": ("broke", "broken"),
    "draw": ("drew", "drawn"),
    "hold": ("held", "held"),
    "find": ("found", "found"),
    "lose": ("lost", "lost"),
    "keep": ("kept", "kept"),
    "take": ("took", "taken"),
    "bring": ("brought", "brought"),
    "send": ("sent", "sent"),
    "catch": ("caught", "caught"),
    "throw": ("threw", "thrown"),
    "hide": ("hid", "hidden"),
    "show": ("showed", "shown"),
    "lend": ("lent", "lent"),
    "cut": ("cut", "cut"),
    "choose": ("chose", "chosen"),
    "sleep": ("slept", "slept"),
    "run": ("ran", "run"),
    "sit": ("sat", "sat"),
    "stand": ("stood", "stood"),
    "swim": ("swam", "swum"),
    "fall": ("fell", "fallen"),
    "rise": ("rose", "risen"),
    "sing": ("sang", "sung"),
    "grow": ("grew", "grown"),
    "teach": ("taught", "taught"),
    "hurt": ("hurt", "hurt"),
    "forgive": ("forgave", "forgiven"),
}

DOUBLING_VERBS = {"drop", "wrap", "cut", "run", "sit", "swim"}

IRREGULAR_PLURALS: dict[str, str] = {
    "knife": "knives",
}


def pluralize_noun(noun: str) -> str:
    if noun in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[noun]
    if noun.endswith(("s", "sh", "ch", "x", "z")):
        return noun + "es"
    if len(noun) >= 2 and noun.endswith("y") and noun[-2].lower() not in VOWELS:
        return noun[:-1] + "ies"
    return noun + "s"


def choose_indefinite_article(next_word: str) -> str:
    lower = next_word.lower()
    if lower.startswith(SILENT_H_PREFIXES):
        return "an"
    if lower.startswith(("eu", "uni", "use", "one")):
        return "a"
    if lower[0] in VOWELS:
        return "an"
    return "a"


def third_person_singular(verb: str) -> str:
    if verb == "have":
        return "has"
    if verb == "do":
        return "does"
    if verb.endswith(("s", "sh", "ch", "x", "z", "o")):
        return verb + "es"
    if len(verb) >= 2 and verb.endswith("y") and verb[-2] not in VOWELS:
        return verb[:-1] + "ies"
    return verb + "s"


def past_simple(verb: str) -> str:
    if verb in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[verb][0]
    if verb in DOUBLING_VERBS:
        return verb + verb[-1] + "ed"
    if verb.endswith("e"):
        return verb + "d"
    if len(verb) >= 2 and verb.endswith("y") and verb[-2] not in VOWELS:
        return verb[:-1] + "ied"
    return verb + "ed"


def past_participle(verb: str) -> str:
    if verb in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[verb][1]
    return past_simple(verb)


def present_participle(verb: str) -> str:
    if verb in DOUBLING_VERBS:
        return verb + verb[-1] + "ing"
    if verb.endswith("ie"):
        return verb[:-2] + "ying"
    if verb.endswith("e") and not verb.endswith(("ee", "ye", "oe")):
        return verb[:-1] + "ing"
    return verb + "ing"


def conjugate_be(time: str, person: int, number: str) -> str:
    if time == "present":
        if number == "sg" and person == 1:
            return "am"
        if number == "sg" and person == 3:
            return "is"
        return "are"
    if time == "past":
        if number == "sg" and person in (1, 3):
            return "was"
        return "were"
    raise ValueError(f"Cannot finitely conjugate 'be' for time={time}")


def conjugate_have(time: str, person: int, number: str) -> str:
    if time == "present":
        return "has" if (number == "sg" and person == 3) else "have"
    if time == "past":
        return "had"
    raise ValueError(f"Cannot finitely conjugate 'have' for time={time}")


def conjugate_do(time: str, person: int, number: str) -> str:
    if time == "present":
        return "does" if (number == "sg" and person == 3) else "do"
    if time == "past":
        return "did"
    raise ValueError(f"Cannot finitely conjugate 'do' for time={time}")