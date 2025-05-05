import subprocess

from taikoi2t import TAIKOI2T_VERSION

subprocess.run(["poetry", "version", TAIKOI2T_VERSION], check=True)
