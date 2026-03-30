from typing import TYPE_CHECKING

import pytest

from hadalized.theme import AbstractTheme, Color, Diagnostic, Link, Treesitter

if TYPE_CHECKING:
    from hadalized.palette import Palette
    from hadalized.theme import BaseStyle


def test_link_resolution(palette: Palette):
    def dump(inst: BaseStyle):
        return inst.model_dump(exclude={"link"})

    abstheme = AbstractTheme(
        name="test",
        comment=Treesitter(link=Link.main),
        ansi01=Color(link=Link.ansi00),
    )
    comment = abstheme._resolve_node(palette, abstheme.comment)
    main = abstheme._resolve_node(palette, abstheme.main)
    ansi1 = abstheme._resolve_node(palette, abstheme.ansi01)
    ansi0 = abstheme._resolve_node(palette, abstheme.ansi00)
    assert dump(comment) == dump(main)
    assert dump(ansi1) == dump(ansi0)


def test_link_resolution_circular():

    abstheme = AbstractTheme(
        name="test",
        ansi00=Color(link=Link.ansi01),
        ansi01=Color(link=Link.ansi02),
        ansi02=Color(link=Link.ansi00),
    )
    with pytest.raises(ValueError):
        abstheme._resolve_links(abstheme.ansi02)


def test_theme_blocks(palette: Palette):
    theme = AbstractTheme(name="test").make(palette)
    assert list(theme.styles())


def test_theme_fields_not_stubbed():
    """Tests that certain collections of styles are not stubbed."""
    thm = AbstractTheme()

    for _, val in thm:
        if isinstance(val, (Treesitter, Diagnostic)):
            assert val
