from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from hadalized.color import ColorRep, ColorSpace
from hadalized.config import Config
from hadalized.palette import Palette

if TYPE_CHECKING:
    from hadalized.config import AppConfig


@pytest.fixture
def config(tmp_path: Path) -> Config:
    return Config(
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        template_dir=Path(__file__).parent,
        output_dir=tmp_path / "output",
        verbose=True,
    )


@pytest.fixture
def dry_config(tmp_path: Path) -> Config:
    return Config(
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        template_dir=Path(__file__).parent,
        output_dir=tmp_path / "output",
        verbose=True,
        dry_run=True,
    )


@pytest.fixture
def palette() -> Palette:
    return Palette.default().transform(ColorSpace.srgb, ColorRep.hex)


@pytest.fixture
def raw_palette() -> Palette:
    return Palette.default()


@pytest.fixture
def build_config() -> AppConfig:
    return Config.builtin_apps["neovim"]
