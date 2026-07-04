import pytest
from coloraide import Color

from hadalized.color import ColorInfo, ColorSpace


def test_color_info_color_method():
    raw = "rgb(0.5 0.5 0.5)"
    color = Color(raw)
    val = ColorInfo(
        raw=raw,
        oklch="",
        hex="",
        css="",
        gamut=ColorSpace.srgb,
        is_in_gamut=True,
        max_oklch_chroma=0.5,
    )
    assert color == val.color()


def test_color_info_color_method_raises_error():
    val = ColorInfo(
        raw="bad color",
        oklch="",
        hex="",
        css="",
        gamut=ColorSpace.srgb,
        is_in_gamut=True,
        max_oklch_chroma=0.5,
    )
    with pytest.raises(ValueError):
        _ = val.color()
