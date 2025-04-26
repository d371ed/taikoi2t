from itertools import chain
from typing import Dict, Iterable, List, Sequence, Tuple

import rapidfuzz
from rapidfuzz import process

type Strikers = Tuple[str, str, str, str]
type Specials = Tuple[str, str]


class StudentDictionary:
    def __init__(self, raw: Iterable[Tuple[str, str]]) -> None:
        normalized = [(normalize_student_name(r[0]), r[1]) for r in raw]

        self.ordered_names: List[str] = [pair[0] for pair in normalized]
        self.no_diacritics_names: List[str] = [
            remove_diacritics(n) for n in self.ordered_names
        ]
        self.allow_char_list: str = "".join(set("".join(self.ordered_names))) + "()"
        self.output_mapping: Dict[str, str] = dict(normalized)

    def match(self, detected_text: str) -> str:
        if detected_text == "":
            return ""

        normal_matched, normal_score, _ = process.extractOne(
            detected_text,
            self.ordered_names,
            scorer=rapidfuzz.distance.Levenshtein.normalized_similarity,
        )
        if normal_score > 0.95:
            return normal_matched  # exact matched

        # taking care of missing diacritics in OCR
        # re-matching without diacritics
        _, no_diacritics_score, no_diacritics_index = process.extractOne(
            remove_diacritics(detected_text),
            self.no_diacritics_names,
            scorer=rapidfuzz.distance.Levenshtein.normalized_similarity,
        )
        return (
            normal_matched
            if normal_score > no_diacritics_score
            else self.ordered_names[no_diacritics_index]  # returns the original name
        )

    def apply_alias(self, names: Iterable[str]) -> List[str]:
        return [
            (name if self.output_mapping[name] == "" else self.output_mapping[name])
            for name in names
        ]

    def sort_specials(self, specials: Specials) -> Specials:
        return (
            (specials[1], specials[0])
            if self.ordered_names.index(specials[0])
            > self.ordered_names.index(specials[1])
            else (specials[0], specials[1])
        )


def split_team(students: Sequence[str]) -> Tuple[Strikers, Specials]:
    ss: Sequence[str] = (
        list(chain(students, [""] * (6 - len(students))))
        if len(students) < 6
        else students
    )
    return (
        (ss[0], ss[1], ss[2], ss[3]),
        (ss[4], ss[5]),
    )


def normalize_student_name(name: str) -> str:
    return name.replace("(", "（").replace(")", "）")


def remove_diacritics(word: str) -> str:
    return word.translate(__DIACRITIC_MAP)


__DIACRITIC_MAP = str.maketrans(
    {
        "が": "か",
        "ぎ": "き",
        "ぐ": "く",
        "げ": "け",
        "ご": "こ",
        "ざ": "さ",
        "じ": "し",
        "ず": "す",
        "ぜ": "せ",
        "ぞ": "そ",
        "だ": "た",
        "ぢ": "ち",
        "づ": "つ",
        "で": "て",
        "ど": "と",
        "ば": "は",
        "び": "ひ",
        "ぶ": "ふ",
        "べ": "へ",
        "ぼ": "ほ",
        "ぱ": "は",
        "ぴ": "ひ",
        "ぷ": "ふ",
        "ぺ": "へ",
        "ぽ": "ほ",
        "ガ": "カ",
        "ギ": "キ",
        "グ": "ク",
        "ゲ": "ケ",
        "ゴ": "コ",
        "ザ": "サ",
        "ジ": "シ",
        "ズ": "ス",
        "ゼ": "セ",
        "ゾ": "ソ",
        "ダ": "タ",
        "ヂ": "チ",
        "ヅ": "ツ",
        "デ": "テ",
        "ド": "ト",
        "バ": "ハ",
        "ビ": "ヒ",
        "ブ": "フ",
        "ベ": "ヘ",
        "ボ": "ホ",
        "パ": "ハ",
        "ピ": "ヒ",
        "プ": "フ",
        "ペ": "ヘ",
        "ポ": "ホ",
    }
)
