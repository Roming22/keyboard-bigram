# Some examples of fixtures, mocking, parametrized tests

from __future__ import annotations

from unittest.mock import Mock, call

import pytest

from myapp import __commit__, __version__
from myapp.main import main


@pytest.fixture(name="default_args")
def fixture_default_args() -> list(str):
    return ["arg1", "arg2"]


@pytest.mark.parametrize(
    "more_args",
    [[""], ["arg3", "arg4"]],
)
def test_main(echo_mock: Mock, default_args: list[str], more_args: list[str]) -> None:
    args = default_args + more_args
    main(args)
    assert echo_mock.call_count == 2
    assert echo_mock.call_args_list == [
        call("myapp 0.0.dev0 (localdev)"),
        call(f"Args: {args}"),
    ]
