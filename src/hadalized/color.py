"""Color string parsing and information extraction."""

from collections import UserString
from collections.abc import Callable
from enum import StrEnum, auto

from coloraide import Color as ColorBase
from pydantic import Field, PrivateAttr

from hadalized.base import BaseNode


class ColorStr(UserString):
    """String subclass indicating a ColorInfo leaf."""


type ColorField = ColorInfo | str
"""A field value containing either full ColorInfo for a specific space / gamut
parseable string representation of a color."""

type ColorFieldStr = str

type ColorFieldHandler = Callable[[ColorField], ColorField]
"""A function that can be mapped across"""


class ColorSpace(StrEnum):
    """Colorspace constants."""

    srgb = auto()
    display_p3 = "display-p3"
    oklch = auto()


class ColorRep(StrEnum):
    """Constants representing nodes in a ColorInfo object.

    Use in build directives to declaratively apply transformations to
    Palette ColorMap fields.
    """

    info = auto()
    """Indicates a ColorField is a ``ColorInfo`` instance."""
    hex = auto()
    """Indicates a ColorField should be a RGB hex code in a specified gamut."""
    oklch = auto()
    """Indicates a ColorField should be a oklch css code in a specified gamut."""
    css = auto()
    """Indicates a ColorField should be a css code in a specified gamut."""


class ColorInfo(BaseNode):
    """Detailed information about a specific color.

    Use the `parse` function to instantiate an instance rather than doing so
    directly to ensure the raw value is parseable.
    """

    raw: str = Field(examples=["oklch(0.6 0.2 25)", "#010203"])
    """Parseable color definition, e.g., a css value."""
    oklch: ColorFieldStr
    """OKLCH css value fit to the specified gamut defined by `css`."""
    css: ColorFieldStr
    """CSS value in the gamut. Encodes the underlying gamut."""
    hex: ColorFieldStr
    """24 or 32-bit hex representation for RGB gamuts."""
    gamut: ColorSpace
    is_in_gamut: bool
    """Indicates whether the raw value is within the color gamut."""
    max_oklch_chroma: float
    """The maximum oklch chroma value determined from the fit method."""
    _color: ColorBase | None = PrivateAttr(None)
    """Parsed instance."""

    def color(self) -> ColorBase:
        """Coloraide.Color object parsed from the definition.

        Returns:
            A coloraide.Color instance.

        """
        if self._color is None:
            self._color = ColorBase(self.raw)
        return self._color


class Parser:
    """Parse raw color strings."""

    def __init__(
        self, gamut: ColorSpace = ColorSpace.srgb, fit_method: str = "raytrace"
    ):
        """Set gamut and fit method."""
        self.gamut = gamut
        self.fit_method = fit_method

    @staticmethod
    def _to_hex(val: ColorBase) -> str:
        """Convert RGB to their corresponding 24-bit or 34-bit hex color code.

        Used primarily to extract a hex code for use
        in programs--such as neovim--that only allow specifying colors
        via RGB channels.

        Returns:
            A hex color code.

        """
        if val.space() != ColorSpace.srgb:
            val = ColorBase(ColorSpace.srgb, val.coords(), alpha=val.alpha())
        return val.to_string(hex=True)

    def _fit(self, val: ColorBase) -> ColorBase:
        return val.clone().fit(self.gamut, method=self.fit_method)

    def _max_oklch_chroma(self, val: ColorBase) -> float:
        """Determine maximum OKLCH chroma in the gamut for fixed lightness and hue.

        Returns:
            OKLCH chroma value.

        """
        if val.space() != ColorSpace.oklch:
            val = val.convert("oklch")
        lightness, _, hue = val.coords()
        cmax = ColorBase("oklch", (lightness, 0.4, hue))
        return self._fit(cmax).get("chroma")

    def __call__(self, val: ColorField) -> ColorInfo:
        """Parse a string representation of a color.

        Returns:
            A ColorInfo instance parsed from the input string. Raises a
            ValueError if the input is not parseable.

        """
        if isinstance(val, ColorInfo):
            if val.gamut == self.gamut:
                return val
            color_def = val.raw
        else:
            color_def = val

        raw_color = ColorBase(color_def)
        if raw_color.space() != ColorSpace.oklch:
            raw_oklch = raw_color.convert(ColorSpace.oklch)
        else:
            raw_oklch = raw_color

        oklch_fit = self._fit(raw_oklch)
        color = oklch_fit.convert(self.gamut)

        inst = ColorInfo(
            raw=color_def,
            oklch=oklch_fit.to_string(),
            css=color.to_string(),
            hex=self._to_hex(color),
            gamut=self.gamut,
            is_in_gamut=raw_oklch.convert(self.gamut).in_gamut(),
            max_oklch_chroma=self._max_oklch_chroma(raw_oklch),
        )
        inst._color = raw_color
        return inst


class Extractor:
    """A ColorFieldHandler that extracts ``ColorInfo`` field values.

    Attrs:
        field (ColorFieldType): Which field will be extracted.
        is_identity: Indicates whether the extractor is the identity function.

    """

    def __init__(self, field: str | ColorRep):
        """Validate input as a ColorFieldType."""
        self.field = ColorRep(field)
        self.is_identity = self.field == ColorRep.info

    def __call__(self, val: ColorField) -> ColorField:
        """Extract field value from the input.

        Calling twice results in a TypeError, to avoid uncaught errors
        when chaining extractors. An expection is when the extractor
        represents the identity function.

        Returns:
            A ``ColorInfo`` field value defined by the ``field`` attr
            or the ColorInfo instance itself in case when the extractor is
            the identity function.

        Raises:
            TypeError: When the input is not a ``ColorInfo`` instance.

        """
        if not isinstance(val, ColorInfo):
            clsname = ColorInfo.__name__
            raise TypeError(f"Input type {type(val)} is not a {clsname} instance.")
        return val if self.is_identity else val[self.field]


def parse(
    val: ColorField,
    gamut: ColorSpace = ColorSpace.srgb,
    fit_method: str = "raytrace",
) -> ColorInfo:
    """Parse a string representation of a color.

    Generate a ``Parser`` instance and call it on the input.

    Returns:
        A ColorInfo instance parsed from the input string. Raises a
        ValueError if the input is not parseable.

    """
    return Parser(gamut=gamut, fit_method=fit_method)(val)
