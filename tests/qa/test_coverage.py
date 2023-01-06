import unittest


def test_run(project_path, run):
    coverage_path = project_path.joinpath("tools", "qa", "coverage")
    # Only compare coverage if the python versions are the same
    output = coverage_path.joinpath("report.txt")
    output_ver = output.read_text().split()[1]

    reference = coverage_path.joinpath("report.ref.txt")
    reference_ver = reference.read_text().split()[1]

    if output_ver == reference_ver:
        cmd = [
            "diff",
            reference,
            output,
        ]
        run(cmd)


if __name__ == "__main__":
    unittest.main()
