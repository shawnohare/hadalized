from hadalized.color import ColorRep, ColorSpace
from hadalized.palette import Palette


def test_palette_to_hex(raw_palette: Palette):
    val = raw_palette.transform(ColorSpace.srgb, ColorRep.hex)
    leaf = val.red
    assert isinstance(val, Palette)
    assert isinstance(leaf, str)
    assert leaf.startswith("#")


def test_palette_to_css(raw_palette: Palette):
    val = raw_palette.transform(ColorSpace.srgb, ColorRep.css)
    leaf = val.red
    assert isinstance(val, Palette)
    assert isinstance(leaf, str)


def test_palette_to_oklch(raw_palette: Palette):
    val = raw_palette.transform(ColorSpace.srgb, ColorRep.oklch)
    leaf = val.red
    assert isinstance(val, Palette)
    assert isinstance(leaf, str)
    assert leaf.startswith("oklch")


def test_default_palette():
    assert Palette.default()
