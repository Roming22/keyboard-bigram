from pathlib import Path
from subprocess import CalledProcessError
from subprocess import run as sp_run

from pytest import fail, fixture


@fixture
def project_path():
    return Path(__file__).parent.parent.parent


@fixture
def run():
    def func(cmd):
        cmd = [f"{x}" for x in cmd]
        try:
            sp_run(cmd, capture_output=True, check=True, text=True)
        except CalledProcessError as ex:
            fail(
                f"""\nCMD: {" ".join(cmd)}\nSTDOUT: {ex.stdout}\nSTDERR: {ex.stderr}""",
                False,
            )
        except Exception as ex:
            fail(f"""CMD: {" ".join(cmd)}\nEXCEPTION: {ex}""")

    return func
