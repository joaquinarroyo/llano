"""Deterministic checks of llano rules on a Spanish text, plus the INFLESZ readability index.

The checks are heuristics. They count what a regex can see reliably and skip the
rules that need parsing (for example, the impersonal "se"). The dictionary and the
banned filler come from the language pack, so the linter follows the pack.

Usage:
  uv run lint.py file.md        # report for one text
"""

from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent / "skills" / "llano" / "languages" / "es" / "reference"
MAX_PROSE = 25
MAX_STEP = 20
MAX_PARAGRAPH = 6
PRONOUN_ONLY = {"el mismo", "la misma"}  # the rule targets pronoun use, which a regex cannot tell apart
HEDGES = ["podría", "podrían", "quizás", "quizá", "posiblemente", "tal vez", "en principio", "probablemente", "puede que"]
WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+(?:[-'][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+)*")


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


@lru_cache(maxsize=1)
def pack_lists() -> tuple[list[str], list[str]]:
    """(avoid terms from the dictionary tables, banned filler phrases)."""
    text = (PACK / "dictionary.md").read_text()
    avoid: list[str] = []
    section = ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
        if section in {"verbs", "connectors", "calques"} and line.startswith("| ") and not line.startswith("| Avoid") and not line.startswith("|---"):
            cell = line.split("|")[1]
            cell = re.sub(r"\([^)]*\)", "", cell)  # drop "(= ...)" notes
            for term in cell.split(","):
                term = term.strip().strip('"').strip()
                term = term.split("+")[0].strip()  # "proceder a + infinitive" -> "proceder a"
                if term and "/" not in term and term.lower() not in PRONOUN_ONLY:
                    avoid.append(term.lower())
    banned: list[str] = []
    start = text.find("## Banned filler")
    end = text.find("## Technical terms")
    for phrase in re.findall(r'"([^"]+)"', text[start:end]):
        phrase = phrase.replace("…", "").strip(" .!?").lower()
        if phrase:
            banned.append(phrase)
    return avoid, banned


# Regular conjugation endings (with common clitics). A stem plus "\\w*" matched nouns like
# "correcto" (correr) or "alternativa" (alterar), so only real verb forms count.
AR_ENDINGS = ("o as a amos an é aste ó aron aba abas ábamos aban ar ará arán aré aría arían "
              "ando ado ada ados adas e es emos en ara aran arlo arla arlos arlas arse ándolo ándola")
ER_IR_ENDINGS = ("o es e emos imos en í iste ió ieron ía ías íamos ían er ir erá irá erán irán "
                 "ería iría erían irían iendo ido ida idos idas a as amos an iera ieran erlo irlo "
                 "erla irla erse irse iéndolo")
# Nouns and adjectives that share a form with a listed verb.
NOT_VERBS = {"acceso", "accesos", "soporte", "soportes", "preciso", "precisa", "precisos", "precisas",
             "alterno", "alterna", "levante", "arranque", "arranques", "saca"}


def verb_stem(word: str) -> str | None:
    """Regex for the conjugated forms of a regular verb, for example realizar -> realicé."""
    if len(word) < 6 or not re.search(r"(ar|er|ir)$", word):
        return None
    stem, cls = word[:-2], word[-2:]
    endings = (AR_ENDINGS if cls == "ar" else ER_IR_ENDINGS).split()
    soft = [e for e in endings if e[0] in "eé"]
    hard = [e for e in endings if e[0] not in "eé"]
    alt = {"z": "c", "c": "qu", "g": "gu"}.get(stem[-1]) if cls == "ar" else None
    alts = []
    if alt:  # spelling change before e: realice, verifique, agregue
        alts.append(re.escape(stem[:-1] + alt) + "(?:" + "|".join(soft) + ")")
        alts.append(re.escape(stem) + "(?:" + "|".join(hard) + ")")
    else:
        alts.append(re.escape(stem) + "(?:" + "|".join(endings) + ")")
    neg = "".join(rf"(?!{re.escape(n)}\b)" for n in NOT_VERBS)
    return neg + "(?:" + "|".join(alts) + ")"


def term_regex(term: str) -> re.Pattern:
    words = term.split()
    first = verb_stem(words[0])
    if first:  # the first word is a verb: "llevar a cabo" -> "llev\w* a cabo"
        rest = "".join(r"\s+" + re.escape(w) for w in words[1:])
        return re.compile(rf"\b{first}{rest}\b", re.IGNORECASE)
    return re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)


def prose(text: str) -> str:
    """Remove code blocks, inline code, tables, URLs and markdown syntax."""
    text = re.sub(r"```.*?```", "\n", text, flags=re.S)
    text = re.sub(r"`[^`]*`", "X", text)
    text = re.sub(r"https?://\S+", "X", text)
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("|"))
    text = re.sub(r"[*_#>]+", " ", text)
    return text


@dataclass
class Sentence:
    text: str
    step: bool  # numbered list item -> procedural limit
    words: int = 0


def sentences(text: str) -> list[list[Sentence]]:
    """Paragraphs -> sentences. List items count as their own paragraph."""
    paragraphs: list[list[Sentence]] = []
    for block in re.split(r"\n\s*\n", prose(text)):
        lines = [l for l in block.splitlines() if l.strip()]
        current: list[str] = []
        groups: list[tuple[str, bool]] = []
        for l in lines:
            m = re.match(r"\s*(\d+[.)]|[-•])\s+", l)
            if m:
                if current:
                    groups.append((" ".join(current), False))
                    current = []
                groups.append((l[m.end():], m.group(1)[0].isdigit()))
            else:
                current.append(l.strip())
        if current:
            groups.append((" ".join(current), False))
        for g, step in groups:
            parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡0-9])|:\s*$", g) if s.strip()]
            sents = [Sentence(s, step, len(WORD_RE.findall(s))) for s in parts]
            sents = [s for s in sents if s.words > 0]
            if sents:
                paragraphs.append(sents)
    return paragraphs


def syllables(word: str) -> int:
    """Spanish syllable count by vowel nuclei (diphthongs merge, hiatus splits)."""
    w = word.lower()
    strong = set("aeoáéóíú")  # accented i/u break a diphthong, like strong vowels
    vowels = strong | set("iuü")
    count, prev = 0, ""
    for c in w:
        if c in vowels:
            if not prev or (prev in strong and c in strong):
                count += 1
            prev = c
        else:
            prev = ""
    return max(count, 1)


@dataclass
class Report:
    words: int = 0
    sentences: int = 0
    violations: dict[str, int] = field(default_factory=dict)
    hits: dict[str, list[str]] = field(default_factory=dict)
    inflesz: float | None = None

    @property
    def total(self) -> int:
        return sum(self.violations.values())

    @property
    def per_100(self) -> float:
        return 100 * self.total / self.words if self.words else 0.0


def lint(text: str) -> Report:
    r = Report()
    v = {k: 0 for k in ["long_sentence", "semicolon", "long_paragraph", "banned_filler", "avoid_word", "stacked_hedges", "gerund_chain"]}
    hits: dict[str, list[str]] = {k: [] for k in v}
    paragraphs = sentences(text)
    flat = [s for p in paragraphs for s in p]
    r.sentences = len(flat)
    r.words = sum(s.words for s in flat)
    clean = prose(text)

    for s in flat:
        limit = MAX_STEP if s.step else MAX_PROSE
        if s.words > limit:
            v["long_sentence"] += 1
            hits["long_sentence"].append(f"{s.words}w: {s.text[:80]}")
        low = s.text.lower()
        if sum(1 for h in HEDGES if re.search(rf"\b{h}\b", low)) >= 2:
            v["stacked_hedges"] += 1
            hits["stacked_hedges"].append(s.text[:80])
        if len(re.findall(r"\b\w+(?:ando|iendo|yendo)\b", low)) >= 2:
            v["gerund_chain"] += 1
            hits["gerund_chain"].append(s.text[:80])
    for p in paragraphs:
        if len(p) > MAX_PARAGRAPH:
            v["long_paragraph"] += 1
    v["semicolon"] = clean.count(";")

    avoid, banned = pack_lists()
    low_clean = clean.lower()
    for phrase in banned:
        # Exclamations ("¡claro!") only count as exclamations, not as the plain word.
        n = len(re.findall(rf"(?<!\w){re.escape(phrase)}(?!\w)", low_clean))
        if n:
            v["banned_filler"] += n
            hits["banned_filler"].append(phrase)
    for term in avoid:
        n = len(term_regex(term).findall(clean))
        if n:
            v["avoid_word"] += n
            hits["avoid_word"].append(term)

    if r.words and r.sentences:
        syl = sum(syllables(w) for s in flat for w in WORD_RE.findall(s.text))
        r.inflesz = round(206.835 - 62.3 * syl / r.words - r.words / r.sentences, 1)
    r.violations, r.hits = v, {k: x for k, x in hits.items() if x}
    return r


if __name__ == "__main__":
    rep = lint(Path(sys.argv[1]).read_text())
    print(f"words={rep.words} sentences={rep.sentences} violations={rep.total} per100={rep.per_100:.2f} inflesz={rep.inflesz}")
    for k, n in rep.violations.items():
        if n:
            print(f"  {k}: {n}  {rep.hits.get(k, [])[:5]}")
