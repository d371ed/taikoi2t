import re
import subprocess
import sys
from pathlib import Path


def main() -> int:
    SPEC_PATH = Path("./specification.md")
    with SPEC_PATH.open(mode="r", encoding="utf-8") as spec_file:
        content: str = spec_file.read()

    MARKER = "<!-- MARK for update_usage.py -->"
    match = re.search(MARKER, content)
    if match is None:
        print("Marker not found", file=sys.stderr)
        return 1

    usage = subprocess.run(
        ["poetry", "run", "taikoi2t", "--help"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    header = (
        "# 仕様\n\n```\n"
        + re.sub(r"^usage\: [A-Z]\:([\w\.]*\\)+", "usage: ", usage)
        + "```\n\n"
    )

    updated_content: str = header + content[match.start() :]

    with SPEC_PATH.open(mode="w", encoding="utf-8") as spec_file:
        spec_file.write(updated_content)

    try:
        subprocess.run(["git", "add", SPEC_PATH.as_posix()], check=True)
    except subprocess.CalledProcessError:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
