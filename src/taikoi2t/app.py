import logging
import sys
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
    StudentDictionaryImpl,
)
from taikoi2t.implements.json import to_json_str
from taikoi2t.implements.match import (
    new_errored_match_result,
    render_match,
)
from taikoi2t.implements.settings import new_settings_from
from taikoi2t.models.args import VERBOSE_ERROR, VERBOSE_PRINT, Args
from taikoi2t.models.image import Image, ImageMeta
from taikoi2t.models.match import MatchResult
from taikoi2t.models.run import RunResult
from taikoi2t.models.student import StudentDictionary

logger: logging.Logger = logging.getLogger("taikoi2t")


def run(argv: Sequence[str] | None = None) -> None:
    run_starts_at = datetime.now()
    run_result = RunResult(
        arguments=list(argv or sys.argv),
        starts_at=run_starts_at.isoformat(),
        ends_at="",
        matches=[],
    )

    args = parse_args(run_result.arguments)
    __set_logging(args)
    logger.info(f"=> {args}")
    if not validate_args(args):
        sys.exit(1)

    settings = new_settings_from(args)
    logger.debug(f"=> {settings}")

    student_alias_pairs = read_student_dictionary_source_file(args.dictionary)
    if student_alias_pairs is None:
        logger.critical(
            f"{args.dictionary.as_posix()} is invalid as student's dictionary"
        )
        sys.exit(1)

    student_dictionary: StudentDictionary = StudentDictionaryImpl(student_alias_pairs)
    if not student_dictionary.validate():
        sys.exit(1)

    reader = easyocr.Reader(["ja", "en"], verbose=settings.verbose >= VERBOSE_PRINT)

    def append_match_result(match_result: MatchResult) -> None:
        run_result.matches.append(match_result)
        if settings.output_format != "json":
            print(render_match(match_result, settings))

    for path in args.files:
        image_process_starts_at = datetime.now()
        logger.info(f"=== START: {path.as_posix()} ===")

        image_meta = ImageMeta(path.as_posix(), path.name)
        if not path.exists():
            logger.error(f"{path.as_posix()} is not found")
            append_match_result(new_errored_match_result(image_meta))
            continue

        # imread returns None when error occurred
        source: Image | None = cv2.imread(path.as_posix())
        if source is None:  # type: ignore
            logger.error(f"{path.as_posix()} cannot read as an image")
            append_match_result(new_errored_match_result(image_meta))
            continue

        # overwrite dimensions
        image_meta.height, image_meta.width, _ = source.shape

        match_result = extract_match_result(
            source, image_meta, student_dictionary, reader, settings
        ) or new_errored_match_result(image_meta)

        logger.info(f"{path.as_posix()} => {match_result}")
        append_match_result(match_result)

        logger.info(
            f"=== END: {path.as_posix()}; elapsed: {datetime.now() - image_process_starts_at} ==="
        )

    run_ends_at = datetime.now()
    run_result.ends_at = run_ends_at.isoformat()
    logger.info(f"=== RUN FINISHED; elapsed: {run_ends_at - run_starts_at} ===")

    if settings.output_format == "json":
        json_str = to_json_str(run_result)
        if json_str is None:
            logger.critical(f"Failed to serialize the result as JSON: {run_result}")
            sys.exit(1)
        else:
            print(json_str)


def __set_logging(args: Args) -> None:
    if args.verbose >= VERBOSE_PRINT:
        console_log_level = logging.DEBUG
    elif args.verbose == VERBOSE_ERROR:
        console_log_level = logging.WARN
    else:
        console_log_level = logging.CRITICAL

    CONSOLE_FORMAT = "%(levelname)-8s | %(message)s"

    if args.logfile is None:
        logging.basicConfig(
            level=console_log_level,
            encoding="utf-8",
            format=CONSOLE_FORMAT,
        )
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            filename=args.logfile,
            filemode="w",
            encoding="utf-8",
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        console = logging.StreamHandler()
        console.setLevel(console_log_level)
        console.setFormatter(logging.Formatter(CONSOLE_FORMAT))
        logging.getLogger("").addHandler(console)
