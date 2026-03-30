import pytest

from hadalized.color import ColorInfo, ColorRep, ColorSpace
from hadalized.palette import Palette


def test_palette_parse_is_idempotent(raw_palette: Palette):
    parsed_once = raw_palette.parse(gamut=ColorSpace.srgb)
    parsed_twice = parsed_once.parse(gamut=ColorSpace.srgb)
    assert hash(parsed_once) == hash(parsed_twice)
    assert parsed_once == parsed_twice
    assert parsed_once.model_dump(mode="json") == parsed_twice.model_dump(mode="json")


@pytest.mark.skip("Logic changed so palette is reparsed after transform.")
def test_palette_to_chained_error(palette: Palette):
    with pytest.raises(TypeError):
        palette.transform(ColorSpace.srgb, ColorRep.hex).transform(
            ColorSpace.srgb, ColorRep.hex
        )


def test_palette_to_info(raw_palette: Palette):
    parsed = raw_palette.transform(ColorSpace.srgb, ColorRep.info)
    assert isinstance(parsed.red, ColorInfo)


def test_palette_to_hex(palette: Palette):
    val = palette.transform(ColorSpace.srgb, ColorRep.hex)
    leaf = val.red
    assert isinstance(val, Palette)
    assert isinstance(leaf, str)
    assert leaf.startswith("#")


def test_palette_to_css(palette: Palette):
    val = palette.transform(ColorSpace.srgb, ColorRep.css)
    leaf = val.red
    assert isinstance(val, Palette)
    assert isinstance(leaf, str)


def test_palette_to_oklch(palette: Palette):
    val = palette.transform(ColorSpace.srgb, ColorRep.oklch)
    leaf = val.red
    assert isinstance(val, Palette)
    assert isinstance(leaf, str)
    assert leaf.startswith("oklch")


def test_default_palette():
    assert Palette.default()
