from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

import myapp


@pytest.fixture
def echo_mock(monkeypatch: MonkeyPatch) -> Mock:
    mock = Mock()
    monkeypatch.setattr(myapp.main, "echo", mock)
    return mock
