import unittest


def test_type_check(project_path, run):
    cmd = [project_path.joinpath("tools", "qa", "type_check.sh")]
    run(cmd)


if __name__ == "__main__":
    unittest.main()
