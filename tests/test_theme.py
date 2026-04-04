from typing import TYPE_CHECKING

import pytest

from hadalized.palette import Palette, PaletteMetadata
from hadalized.theme import (
    AbstractTheme,
    Color,
    Diagnostic,
    Hue,
    T,
    ThemeBlocks,
    Treesitter,
)

if TYPE_CHECKING:
    from hadalized.theme import BaseStyle


def test_link_enum_contains_all_theme_fields():
    assert len(T) == len(ThemeBlocks.model_fields)


def test_palette_field_enum_contains_all_palette_fields():
    assert len(Hue) == len(Palette.model_fields) - len(PaletteMetadata.model_fields)


def test_link_resolution(palette: Palette):
    def dump(inst: BaseStyle):
        return inst.model_dump(exclude={"link"})

    abstheme = AbstractTheme(
        name="test",
        comment=Treesitter(link=T.main),
        ansi01=Color(link=T.ansi00),
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
        ansi00=Color(link=T.ansi01),
        ansi01=Color(link=T.ansi02),
        ansi02=Color(link=T.ansi00),
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
