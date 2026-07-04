import pytest

from hadalized.palette import Hue, Palette
from hadalized.style import Style
from hadalized.theme import (
    Theme,
    ThemeMetadata,
    resolve,
)


def test_palette_field_enum_contains_all_palette_fields():
    assert len(Hue) == len(Palette.model_fields) - 1


def test_link_resolution():
    def dump(inst: Style):
        return inst.model_dump(exclude={"link"})

    theme = Theme(
        meta=ThemeMetadata(),
        comment=Style(link="main"),
    )
    comment = theme.resolve_links("comment")
    assert dump(comment) == dump(theme.main)


def test_link_resolution_circular():
    theme = Theme(
        meta=ThemeMetadata(),
        main=Style(link="comment"),
        comment=Style(link="main"),
    )

    with pytest.raises(ValueError):
        _ = theme.resolve_links("comment")


def test_resolve(palette: Palette):
    theme = resolve(
        Theme(
            meta=ThemeMetadata(),
            comment=Style(link="main"),
        ),
        palette,
    )
    assert theme.comment.fg is not None
    assert theme.comment.fg.startswith("#")
