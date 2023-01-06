#!/usr/bin/env python3
"""Generate """

from datetime import datetime
from pathlib import Path
from subprocess import run


def generate_version() -> None:
    """Generate a unique version number and commit id in version.py

    Version numbers are in the form `X.Y.Z` where:
      - X is the major version number.
      - Y is the minor version number, odd for development releases,
        even for production releases. Some usecases allow for an alpha character
        after the number.
      - Z is a revision number.

    For work in progress (a.k.a feature) branches:
      - X is 0, to prevent accidental installation from the test pypi instance.
      - Y is the year, month and day the release was generated.
      - Z is the hour, minute and second the release was generated, prefixed by
        dev to prevent accidental installation from the test pypi instance.

    c.f:
      - https://www.python.org/dev/peps/pep-0440/
    """
    origin = "origin"
    branches = run(
        ["git", "branch"], capture_output=True, check=True, text=True
    ).stdout.split("\n")

    # Get current branch
    for branch in branches:
        if branch.startswith("* "):
            branch = branch[2:]
            break

    x = y = None
    if branch.startswith("release/"):
        x, y = branch.split("/")[1].split(".")
    elif branch == "dev":
        # Get releases
        releases = (
            run(
                ["git", "ls-remote", "--heads", origin, "release/*"],
                capture_output=True,
                check=True,
                text=True,
            )
            .stdout.strip()
            .split("\n")
        )
        releases = [r.split("/")[-1] for r in releases]
        releases = [r.split(".") for r in releases]

        # Handle releases that use an alpha character by removing any non-numeric characters
        releases = [
            (int(x), int("".join(c for c in y if c.isdigit()))) for x, y in releases
        ]

        # Get latest release version
        x, y = sorted(releases)[-1]
        y += 1

    if x is not None:
        # Retrieve only the tags
        run(["git", "fetch", origin, "refs/tags/*:refs/tags/*"], check=True)
        z = len(
            run(
                ["git", "tag", "--list", f"{x}.{y}.*"],
                capture_output=True,
                check=True,
                text=True,
            ).stdout.split("\n")
        )
    else:
        now = datetime.utcnow()
        x = "0"
        y = now.strftime("%y%m%d")
        z = "dev" + now.strftime("%H%M%S")
    version = f"{x}.{y}.{z}"

    commit_id = run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.split("\n")[0]

    repo_path = Path(__file__).parent.parent.parent
    version_path = repo_path.joinpath("src", "myapp", "__version__.py")
    version_path.write_text(
        "\n".join(
            [
                '"""Changes on this file should not be tracked."""',
                f'__version__ = "{version}"',
                f'__commit__ = "{commit_id[:6]}"',
                "",
                """if __name__ == "__main__":""",
                """    print(f"{__version__}")""",
                "",
            ]
        )
    )

    # Update pyproject.toml
    run(
        [
            "sed",
            "-i",
            "-e",
            f"s:0.0.dev0:{version}:",
            repo_path.joinpath("pyproject.toml"),
        ]
    )


if __name__ == "__main__":
    generate_version()
