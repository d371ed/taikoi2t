import subprocess

from taikoi2t import TAIKOI2T_VERSION


def main() -> int:
    try:
        subprocess.run(["poetry", "version", TAIKOI2T_VERSION], check=True)
        subprocess.run(["git", "add", "./pyproject.toml"], check=True)
    except subprocess.CalledProcessError:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
