"""Test various utility functions"""

from pathlib import Path

import pytest

from hadalized.config import split_template


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (Path("shrc"), ("shrc", "")),
        (Path("shrc.j2"), ("shrc", "")),
        (Path("shrc.toml"), ("shrc.toml", ".toml")),
        (Path("shrc.toml.j2"), ("shrc.toml", ".toml")),
    ],
)
def test_template_parts(path: Path, expected: tuple[str, str]):
    assert split_template(path) == expected
