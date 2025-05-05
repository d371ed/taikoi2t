from typing import Dict, Iterable, List, Tuple

import rapidfuzz
from rapidfuzz import process

from taikoi2t.models.args import VERBOSE_PRINT, VERBOSE_SILENT
from taikoi2t.models.student import (
    DEFAULT_STUDENT_INDEX,
    ERROR_STUDENT_NAME,
    Student,
)


def new_empty_student() -> Student:
    return Student(DEFAULT_STUDENT_INDEX, "", None)


def new_error_student() -> Student:
    return Student(DEFAULT_STUDENT_INDEX, ERROR_STUDENT_NAME, None)


class StudentDictionary:
    def __init__(self, raw: Iterable[Tuple[str, str]]) -> None:
        normalized = [(normalize_student_name(r[0]), r[1]) for r in raw]

        self.ordered_names: List[str] = [pair[0] for pair in normalized]
        self.no_diacritics_names: List[str] = [
            remove_diacritics(n) for n in self.ordered_names
        ]
        self.allow_char_list: str = "".join(set("".join(self.ordered_names))) + "()"
        self.alias_mapping: Dict[str, str] = dict(
            filter(lambda p: p[1] != "", normalized)
        )

    def match(self, detected_text: str, verbose: int = VERBOSE_SILENT) -> Student:
        if detected_text == "":
            return new_empty_student()

        normal_matched, normal_score, normal_index = process.extractOne(
            detected_text,
            self.ordered_names,
            scorer=rapidfuzz.distance.Levenshtein.normalized_similarity,
        )
        if verbose >= VERBOSE_PRINT:
            print(
                f"(normal) input: {detected_text}, matched: {normal_matched}, score: {normal_score}"
            )
        if normal_score > 0.95:  # exact matched
            return Student(
                normal_index, normal_matched, self.alias_mapping.get(normal_matched)
            )

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
        if normal_score > no_diacritics_score:
            return Student(
                normal_index, normal_matched, self.alias_mapping.get(normal_matched)
            )
        else:
            original_name = self.ordered_names[no_diacritics_index]
            return Student(
                no_diacritics_index,
                original_name,
                self.alias_mapping.get(original_name),
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
