import unittest


def test_lint_python(project_path, run):
    cmds = [
        [project_path.joinpath("tools", "qa", "lint.sh"), "--pylint"],
        [
            project_path.joinpath("tools", "qa", "dictionary", "update.sh"),
            "--check",
        ],
    ]
    for cmd in cmds:
        run(cmd)


def test_lint_shell(project_path, run):
    cmd = [project_path.joinpath("tools", "qa", "lint.sh"), "--shellcheck"]
    run(cmd)


if __name__ == "__main__":
    unittest.main()
