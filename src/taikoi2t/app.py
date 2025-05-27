import json
import sys
from dataclasses import asdict
from datetime import datetime
from typing import Sequence

import cv2
import easyocr  # type: ignore

from taikoi2t.application.args import (
    parse_args,
    validate_args,
)
from taikoi2t.application.file import read_student_dictionary_source_file
from taikoi2t.application.match import extract_match_result
from taikoi2t.application.student import (
    StudentDictionary,
)
from taikoi2t.implements.match import (
    new_errored_match_result,
    render_match,
)
from taikoi2t.implements.settings import new_settings_from
from taikoi2t.models.args import VERBOSE_ERROR, VERBOSE_PRINT
from taikoi2t.models.image import Image, ImageMeta
from taikoi2t.models.match import MatchResult
from taikoi2t.models.run import RunResult


def run(argv: Sequence[str] | None = None) -> None:
    run_starts_at = datetime.now()
    run_result = RunResult(
        arguments=list(argv or sys.argv),
        starts_at=run_starts_at.isoformat(),
        ends_at="",
        matches=[],
    )

    args = parse_args(run_result.arguments)
    if args.verbose >= VERBOSE_PRINT:
        print(args)
    validate_args(args)

    settings = new_settings_from(args)
    if settings.verbose >= VERBOSE_PRINT:
        print(settings)

    student_alias_pairs = read_student_dictionary_source_file(args.dictionary)
    if student_alias_pairs is None:
        print(
            f"FATAL: {args.dictionary.as_posix()} is invalid as student's dictionary",
            file=sys.stderr,
        )
        sys.exit(1)

    student_dictionary = StudentDictionary(student_alias_pairs)
    student_dictionary.validate(settings.verbose)

    if settings.verbose >= VERBOSE_PRINT:
        print("allow_char_list: " + student_dictionary.allow_char_list)

    reader = easyocr.Reader(["ja", "en"], verbose=settings.verbose >= VERBOSE_PRINT)

    def append_match_result(match_result: MatchResult) -> None:
        run_result.matches.append(match_result)
        if settings.output_format != "json":
            print(render_match(match_result, settings))

    for path in args.files:
        image_process_starts_at = datetime.now()
        if settings.verbose >= VERBOSE_PRINT:
            print(f"=== START: {path.as_posix()} ===")

        image_meta = ImageMeta(path.as_posix(), path.name)
        if not path.exists():
            if settings.verbose >= VERBOSE_ERROR:
                print(f"ERROR: {path.as_posix()} is not found", file=sys.stderr)
            append_match_result(new_errored_match_result(image_meta))
            continue

        # imread returns None when error occurred
        source: Image | None = cv2.imread(path.as_posix())
        if source is None:  # type: ignore
            if settings.verbose >= VERBOSE_ERROR:
                print(
                    f"ERROR: {path.as_posix()} cannot read as an image", file=sys.stderr
                )
            append_match_result(new_errored_match_result(image_meta))
            continue

        # overwrite dimensions
        image_meta.height, image_meta.width, _ = source.shape
        if settings.verbose >= VERBOSE_PRINT:
            print(image_meta)

        match_result = extract_match_result(
            source, image_meta, student_dictionary, reader, settings
        ) or new_errored_match_result(image_meta)
        if args.verbose >= VERBOSE_PRINT:
            print(match_result)
        append_match_result(match_result)

        if settings.verbose >= VERBOSE_PRINT:
            image_process_ends_at = datetime.now()
            print(f"=== END: {path.as_posix()} ===")
            print(
                f"    start: {image_process_starts_at}, end: {image_process_ends_at}, elapsed: {image_process_ends_at - image_process_starts_at}"
            )

    run_ends_at = datetime.now()
    run_result.ends_at = run_ends_at.isoformat()
    if settings.verbose >= VERBOSE_PRINT:
        print("=== RUN FINISHED ===")
        print(
            f"    start: {run_result.starts_at}, end: {run_result.ends_at}, elapsed: {run_ends_at - run_starts_at}"
        )

    if settings.output_format == "json":
        print(json.dumps(asdict(run_result), ensure_ascii=False))
