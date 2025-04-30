from itertools import chain
from typing import Dict, Iterable, List, Sequence, Tuple

import rapidfuzz
from rapidfuzz import process

from taikoi2t.args import VERBOSE_PRINT, VERBOSE_SILENT

type Strikers = Tuple[str, str, str, str]
type Specials = Tuple[str, str]

ERROR_STUDENT: str = "Error"


class StudentDictionary:
    def __init__(self, raw: Iterable[Tuple[str, str]]) -> None:
        normalized = [(normalize_student_name(r[0]), r[1]) for r in raw]

        self.ordered_names: List[str] = [pair[0] for pair in normalized]
        self.no_diacritics_names: List[str] = [
            remove_diacritics(n) for n in self.ordered_names
        ]
        self.allow_char_list: str = "".join(set("".join(self.ordered_names))) + "()"
        self.output_mapping: Dict[str, str] = dict(normalized)

    def match(self, detected_text: str, verbose: int = VERBOSE_SILENT) -> str:
        if detected_text == "":
            return ""

        normal_matched, normal_score, _ = process.extractOne(
            detected_text,
            self.ordered_names,
            scorer=rapidfuzz.distance.Levenshtein.normalized_similarity,
        )
        if verbose >= VERBOSE_PRINT:
            print(
                f"(normal) input: {detected_text}, matched: {normal_matched}, score: {normal_score}"
            )
        if normal_score > 0.95:
            return normal_matched  # exact matched

        # taking care of missing diacritics in OCR
        # re-matching without diacritics
        no_diacritics_text = remove_diacritics(detected_text)
        no_diacritics_matched, no_diacritics_score, no_diacritics_index = (
            process.extractOne(
                no_diacritics_text,
                self.no_diacritics_names,
                scorer=rapidfuzz.distance.Levenshtein.normalized_similarity,
            )
        )
        if verbose >= VERBOSE_PRINT:
            print(
                f"(no diacritics) input: {no_diacritics_text}, matched: {no_diacritics_matched}, score: {no_diacritics_score}"
            )
        return (
            normal_matched
            if normal_score > no_diacritics_score
            else self.ordered_names[no_diacritics_index]  # returns the original name
        )

    def arrange_team(self, team: Sequence[str]) -> List[str]:
        strikers, specials = split_team(team)
        return [
            self.apply_alias(name)
            for name in chain(strikers, self.sort_specials(specials))
        ]

    def apply_alias(self, name: str) -> str:
        if name == "" or name == ERROR_STUDENT:
            return name
        else:
            try:
                mapped: str = self.output_mapping[name]
                return mapped or name
            except KeyError:
                return ERROR_STUDENT

    def sort_specials(self, specials: Specials) -> Specials:
        sp1_index, sp1_name = self.__index_name_pair(specials[0])
        sp2_index, sp2_name = self.__index_name_pair(specials[1])
        return (sp1_name, sp2_name) if sp1_index <= sp2_index else (sp2_name, sp1_name)

    def __index_name_pair(self, name: str) -> Tuple[int, str]:
        if name == "":
            # more to the right of Error
            return (len(self.ordered_names) + 1, "")
        elif name in self.ordered_names:
            return (self.ordered_names.index(name), name)
        else:
            # more to the right of a valid name
            return (len(self.ordered_names), ERROR_STUDENT)


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
