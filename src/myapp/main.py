#!/usr/bin/env python3
"""Main module"""
from __future__ import annotations

import sys

from myapp.__version__ import __commit__, __version__

APP_NAME = __name__.split(".", maxsplit=1)[0]

import click
import config_reader
import corpus_processor
import layout_generator


@click.command()
@click.option(
    "-k",
    "--keyboard",
    default="3-4h-2t",
    help="keyboard layout. See available layouts in data/config/keyboards",
)
def main(keyboard: str) -> None:
    """Main function"""
    print(f"{APP_NAME} {__version__} ({__commit__})")
    config = config_reader.read(keyboard)
    print(config)
    corpus = corpus_processor.generate_data(config["preferences"]["corpus"])
    layout_generator.generate(corpus, config)


if __name__ == "__main__":
    main()
