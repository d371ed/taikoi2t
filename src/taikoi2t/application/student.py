from typing import Dict, Iterable, List, Tuple

import cv2
import easyocr  # type: ignore
import rapidfuzz
from rapidfuzz import process

from taikoi2t.implements.image import crop, level_contrast, resize_to, show_image, skew
from taikoi2t.implements.ocr import join_chars
from taikoi2t.implements.student import (
    new_empty_student,
    normalize_student_name,
    remove_diacritics,
)
from taikoi2t.models.args import VERBOSE_IMAGE, VERBOSE_PRINT, VERBOSE_SILENT
from taikoi2t.models.image import BoundingBox, Image
from taikoi2t.models.ocr import Character
from taikoi2t.models.student import Student


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


def extract_student_names(
    reader: easyocr.Reader,
    grayscale: Image,
    modal: BoundingBox,
    char_allow_list: str,
    verbose: int = 0,
) -> List[str]:
    student_name_images = __preprocess_students(grayscale, modal)

    results: List[str] = list()
    for image in student_name_images:
        chars: List[Character] = reader.readtext(  # type: ignore
            image, allowlist=char_allow_list, mag_ratio=2
        )  # type: ignore

        if verbose >= VERBOSE_PRINT:
            print([char[1] for char in chars])
        if verbose >= VERBOSE_IMAGE:
            for char in chars:
                top_left, _, bottom_right, _ = char[0]
                cv2.rectangle(image, top_left, bottom_right, (0, 0, 0))
            show_image(image)

        name = normalize_student_name(join_chars(chars))
        results.append(name)
    return results


def __preprocess_students(grayscale: Image, modal: BoundingBox) -> List[Image]:
    WIDTH: int = 4000

    FOOTER_RATIO: float = 0.085
    footer_height = int(FOOTER_RATIO * modal.height)
    footer_top = int(modal.bottom - footer_height)
    footer_region = BoundingBox(
        left=modal.left, top=footer_top, right=modal.right, bottom=modal.bottom
    )

    footer = crop(grayscale, footer_region)
    resized = resize_to(footer, WIDTH)
    skewed = skew(resized, 14.0)
    leveled = level_contrast(skewed, 112, 192)

    # cut out 12 sections
    PITCH_RATIO: float = 113 / 1844
    PITCH: int = int(WIDTH * PITCH_RATIO)
    TEAM_WIDTH: int = PITCH * 6
    PLAYER_TEAM_LEFT: int = 216
    OPPONENT_TEAM_LEFT: int = WIDTH // 2 + 292
    height: int = leveled.shape[1]

    results: List[Image] = list()
    for x in range(PLAYER_TEAM_LEFT, PLAYER_TEAM_LEFT + TEAM_WIDTH, PITCH):
        results.append(crop(leveled, BoundingBox(x, 0, (x + PITCH), height)))
    for x in range(OPPONENT_TEAM_LEFT, OPPONENT_TEAM_LEFT + TEAM_WIDTH, PITCH):
        results.append(crop(leveled, BoundingBox(x, 0, (x + PITCH), height)))

    return results
