import dataclasses
import itertools
import logging
from dataclasses import dataclass
from typing import Callable, Counter, Dict, Iterable, List, Sequence, Tuple

import easyocr  # type: ignore
import rapidfuzz
from rapidfuzz import process

from taikoi2t.implements.image import (
    binarize,
    crop,
    level_contrast,
    resize_to,
    sharpen,
    show_bboxes,
    skew,
    smooth,
)
from taikoi2t.implements.ocr import join_chars
from taikoi2t.implements.student import (
    new_empty_student,
    new_error_student,
    normalize_student_name,
    remove_diacritics,
)
from taikoi2t.models.args import (
    VERBOSE_IMAGE,
)
from taikoi2t.models.image import BoundingBox, Image
from taikoi2t.models.ocr import Character
from taikoi2t.models.student import Student, StudentDictionary

logger: logging.Logger = logging.getLogger("taikoi2t.student")

STUDENT_EXACT_MATCH_SCORE: float = 0.95
# reject 0.5 or less
STUDENT_PRIMARY_CUTOFF_SCORE: float = 0.51
# reject if 1 letter in 3 letter name is different
STUDENT_SECONDARY_CUTOFF_SCORE: float = 0.67


class StudentDictionaryImpl(StudentDictionary):
    def __init__(self, raw: Iterable[Tuple[str, str]]) -> None:
        normalized = [(normalize_student_name(r[0]), r[1]) for r in raw]

        self.ordered_names: List[str] = [pair[0] for pair in normalized]
        self.no_diacritics_names: List[str] = [
            remove_diacritics(n) for n in self.ordered_names
        ]
        self.allow_char_list: str = (
            "".join(
                set("".join(self.ordered_names + self.no_diacritics_names))
                - set("（）")
            )
            + "()"
        )
        self.alias_mapping: Dict[str, str] = dict(
            filter(lambda p: p[1] != "", normalized)
        )

        self.logger: logging.Logger = logging.getLogger(
            "taikoi2t.student.StudentDictionary"
        )
        self.logger.debug(f"<Init> allow_char_list: {self.allow_char_list}")

    # Returns False if there are critical errors
    def validate(self) -> bool:
        duplicated_names: Sequence[str] = [
            name for name, count in Counter(self.ordered_names).items() if count > 1
        ]
        if len(duplicated_names) > 0:
            self.logger.warning(
                f"Duplicated names in student's dictionary {duplicated_names}"
            )
        return True  # currently always returns True

    def get_allow_char_list(self) -> str:
        return self.allow_char_list

    def match(self, recognized_text: str) -> Student:
        if recognized_text == "":
            return new_empty_student()  # empty

        raw_results: Sequence[_ExtractResult] = [
            _ExtractResult(name, score, index)
            for name, score, index in process.extract(
                recognized_text,
                self.ordered_names,
                scorer=rapidfuzz.distance.Levenshtein.normalized_similarity,
                score_cutoff=STUDENT_PRIMARY_CUTOFF_SCORE,
            )
        ]
        self.logger.debug(f"<Raw> {recognized_text} => {raw_results}")

        raw_first: _ExtractResult | None = (
            raw_results[0] if len(raw_results) > 0 else None
        )
        if raw_first is not None and raw_first.score > STUDENT_EXACT_MATCH_SCORE:
            return self.__new_student_by(raw_first.index)  # exact matched

        # taking care of missing diacritics in OCR
        # re-matching without diacritics
        no_diacritics_text = remove_diacritics(recognized_text)
        no_diacritics_results: Sequence[_ExtractResult] = [
            _ExtractResult(name, score, index)
            for name, score, index in process.extract(
                no_diacritics_text,
                self.no_diacritics_names,
                scorer=rapidfuzz.distance.Levenshtein.normalized_similarity,
                score_cutoff=STUDENT_PRIMARY_CUTOFF_SCORE,
            )
        ]
        self.logger.debug(
            f"<No-diacritics> {no_diacritics_text} => {no_diacritics_results}"
        )

        no_diacritics_first: _ExtractResult | None
        match no_diacritics_results:
            # diacritics-removed names may be duplicates
            case [first, second, *_] if first.name == second.name:
                no_diacritics_first = None  # ignore results
            case [first, *_]:
                no_diacritics_first = first
            case _:
                no_diacritics_first = None

        if (
            no_diacritics_first is not None
            and no_diacritics_first.score > STUDENT_EXACT_MATCH_SCORE
        ):
            return self.__new_student_by(no_diacritics_first.index)  # exact matched

        first_matched: _ExtractResult
        results: Sequence[_ExtractResult]
        match (raw_first, no_diacritics_first):
            case (None, None):
                return new_error_student()  # no students to match
            case (None, _):
                first_matched, results = no_diacritics_first, no_diacritics_results
            case (_, None):
                first_matched, results = raw_first, raw_results
            case (_, _) if raw_first.score >= no_diacritics_first.score:
                first_matched, results = raw_first, raw_results
            case (_, _):
                first_matched, results = no_diacritics_first, no_diacritics_results

        if len(results) == 1 or first_matched.score >= STUDENT_SECONDARY_CUTOFF_SCORE:
            return self.__new_student_by(first_matched.index)  # matched
        else:
            return new_error_student()  # ambiguous results

    def __new_student_by(self, index: int) -> Student:
        if index < 0 or index >= len(self.ordered_names):
            return new_error_student()
        else:
            name = self.ordered_names[index]
            return Student(index, name, self.alias_mapping.get(name))


@dataclass(frozen=True)
class _ExtractResult:
    name: str
    score: float
    index: int

    def __repr__(self) -> str:
        fields = [f"{f.name}={getattr(self, f.name)}" for f in dataclasses.fields(self)]
        return f"({', '.join(fields)})"


OCR_MODAL_WIDTH: int = 4000
FOOTER_HEIGHT_RATIO: float = 0.085
# based on OCR_MODAL_WIDTH
STUDENTS_HORIZONTAL_PITCH: int = 245
TEAM_WIDTH: int = STUDENTS_HORIZONTAL_PITCH * 6
PLAYER_TEAM_LEFT_X: int = 216
OPPONENT_TEAM_LEFT_X: int = OCR_MODAL_WIDTH // 2 + 292
STUDENTS_LEFT_XS: Iterable[int] = list(
    itertools.chain(
        range(
            PLAYER_TEAM_LEFT_X,
            PLAYER_TEAM_LEFT_X + TEAM_WIDTH,
            STUDENTS_HORIZONTAL_PITCH,
        ),
        range(
            OPPONENT_TEAM_LEFT_X,
            OPPONENT_TEAM_LEFT_X + TEAM_WIDTH,
            STUDENTS_HORIZONTAL_PITCH,
        ),
    )
)

OCR_PREPROCESS: Iterable[Callable[[Image], Image | None]] = [
    lambda src: resize_to(src, OCR_MODAL_WIDTH),
    lambda src: skew(src, 14.0),
    lambda src: smooth(src, 9),
    lambda src: sharpen(src, 2),
    lambda src: level_contrast(src, 144, 192),
    lambda src: binarize(src),
]


def preprocess_students_for_ocr(grayscale: Image, modal: BoundingBox) -> List[Image]:
    preprocessed: Image = crop(
        grayscale,
        BoundingBox(
            left=modal.left,
            top=int(modal.bottom - int(FOOTER_HEIGHT_RATIO * modal.height)),
            right=modal.right,
            bottom=modal.bottom,
        ),
    )
    for index, pred in enumerate(OCR_PREPROCESS):
        temp = pred(preprocessed)
        if temp is None:
            logger.error(f"<OCR pre> Image preprocess error at {index}")
            return []
        preprocessed = temp

    # cut out 12 sections
    height: int = preprocessed.shape[1]
    results: List[Image] = [
        crop(preprocessed, BoundingBox(x, 0, (x + STUDENTS_HORIZONTAL_PITCH), height))
        for x in STUDENTS_LEFT_XS
    ]

    return results


def recognize_student(
    reader: easyocr.Reader,
    dictionary: StudentDictionary,
    preprocessed_image: Image,
    verbose: int = 0,
) -> Student:
    chars: Sequence[Character] = []
    height, width = preprocessed_image.shape[:2]
    if width > 0 and height > 0:
        try:
            chars = reader.readtext(  # type: ignore
                preprocessed_image,
                allowlist=dictionary.get_allow_char_list(),
                mag_ratio=2,
            )
        except Exception as e:
            logger.error(e)
    if len(chars) == 0:
        return new_error_student()

    logger.debug(f"<OCR read> {[(char[1], float(char[2])) for char in chars]}")
    if verbose >= VERBOSE_IMAGE:
        bboxes = [
            BoundingBox(char[0][0][0], char[0][0][1], char[0][2][0], char[0][2][1])
            for char in chars
        ]
        show_bboxes(preprocessed_image, bboxes, to_bgr=True)

    name = normalize_student_name(join_chars(chars))
    return dictionary.match(name)


CHAR_VERTICAL_PADDING: float = 0.2
CHAR_HEIGHT_RATIO: float = 1 - CHAR_VERTICAL_PADDING


def recognize_student_by_character(
    reader: easyocr.Reader,
    dictionary: StudentDictionary,
    preprocessed_image: Image,
    verbose: int = 0,
) -> Student:
    # in order to solve the type in Pylance
    horizontal_list: List[List[__OCRTextBox]] = []
    try:
        horizontal_list, _ = reader.detect(  # type: ignore
            preprocessed_image, mag_ratio=2
        )
    except Exception as e:
        logger.error(e)
    if len(horizontal_list) == 0:
        return new_error_student()

    detected_text_boxes: Iterable[__OCRTextBox] = horizontal_list[0]
    logger.debug(
        f"<OCR detect> {[tuple(int(i) for i in b) for b in detected_text_boxes]}"
    )

    single_char_boxes: List[BoundingBox] = []
    for left, right, top, bottom in detected_text_boxes:
        width = right - left
        height = bottom - top
        char_count: int = round(width / (height * CHAR_HEIGHT_RATIO))

        if char_count >= 2:
            single_char_width: int = width // char_count
            single_char_boxes += [
                BoundingBox(
                    left=left + single_char_width * i,
                    top=top,
                    right=left + single_char_width * (i + 1),
                    bottom=bottom,
                )
                for i in range(char_count)
            ]
        else:
            single_char_boxes.append(
                BoundingBox(left=left, top=top, right=right, bottom=bottom)
            )
    logger.debug(
        f"<OCR detect> single_char_boxes: {[b.as_python_int() for b in single_char_boxes]}"
    )

    chars: List[Character] = []
    for box in single_char_boxes:
        if box.is_empty():
            continue
        try:
            chars += reader.recognize(  # type: ignore
                crop(preprocessed_image, box),
                allowlist=dictionary.get_allow_char_list(),
            )
        except Exception as e:
            logger.error(e)
            continue

    logger.debug(f"<OCR recognize> {[(char[1], float(char[2])) for char in chars]}")
    if verbose >= VERBOSE_IMAGE:
        show_bboxes(preprocessed_image, single_char_boxes, to_bgr=True)

    name = normalize_student_name(join_chars(chars))
    return dictionary.match(name)


type __OCRTextBox = Tuple[int, int, int, int]
