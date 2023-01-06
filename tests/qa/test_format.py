import unittest


def test_run(project_path, run):
    cmd = [project_path.joinpath("tools", "qa", "format.sh"), "--check"]
    run(cmd)


if __name__ == "__main__":
    unittest.main()
