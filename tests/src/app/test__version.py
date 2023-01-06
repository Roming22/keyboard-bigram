"""KEEP THIS FILE

It guarantees that versions are not committed by accident"""

from myapp import __commit__, __version__


def test_version():
    assert __version__ == "0.0.dev0"
    assert __commit__ == "localdev"
