from typing import TYPE_CHECKING

from hadalized import utils

if TYPE_CHECKING:
    from hadalized.config import Config


def test_neovim_mapping(config: Config):
    theme = config.theme
    mapped = utils.neovim.mapping(theme)
    assert mapped


def test_neovim_transform(config: Config):
    theme = config.theme
    for _, dump in utils.neovim.transform(theme):
        assert dump.startswith("{")
