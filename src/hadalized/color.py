"""Color string parsing and information extraction."""

from enum import StrEnum, auto

from coloraide import Color as BaseColor
from pydantic import Field, PrivateAttr

from hadalized.base import BaseNode


class ColorSpace(StrEnum):
    """Colorspace constants."""

    srgb = auto()
    display_p3 = "display-p3"
    oklch = auto()


class ColorRep(StrEnum):
    """Constants representing fields in a ColorInfo object.

    Use in build directives to declaratively apply transformations to
    Palette ColorMap fields.
    """

    hex = auto()
    """Indicates a color value should be a RGB hex code in a specified gamut."""
    oklch = auto()
    """Indicates a color value should be a oklch css code in a specified gamut."""
    css = auto()
    """Indicates a color value should be a css code in a specified gamut."""


class ColorInfo(BaseNode):
    """Detailed information about a specific color.

    Use the `parse` function to instantiate an instance rather than doing so
    directly to ensure the raw value is parseable.
    """

    raw: str = Field(examples=["oklch(0.6 0.2 25)", "#010203"])
    """Parseable color definition, e.g., a css value."""
    oklch: str
    """OKLCH css value fit to the specified gamut defined by `css`."""
    css: str
    """CSS value in the gamut. Encodes the underlying gamut."""
    hex: str
    """24 or 32-bit hex representation for RGB gamuts."""
    gamut: ColorSpace
    is_in_gamut: bool
    """Indicates whether the raw value is within the color gamut."""
    max_oklch_chroma: float
    """The maximum oklch chroma value determined from the fit method."""
    _color: BaseColor | None = PrivateAttr(None)
    """Parsed instance."""

    def set_color(self, val: BaseColor):
        """Set the base color attribute."""
        self._color = val

    def color(self) -> BaseColor:
        """Coloraide.Color object parsed from the definition.

        Returns:
            A coloraide.Color instance.

        """
        if self._color is None:
            self._color = BaseColor(self.raw)
        return self._color


class ColorParser:
    """Parse raw color strings."""

    def __init__(
        self, gamut: ColorSpace = ColorSpace.srgb, fit_method: str = "raytrace"
    ):
        """Set gamut and fit method."""
        self.gamut: ColorSpace = gamut
        self.fit_method: str = fit_method

    @staticmethod
    def _to_hex(val: BaseColor) -> str:
        """Convert RGB to their corresponding 24-bit or 32-bit hex color code.

        Used primarily to extract a hex code for use
        in programs--such as neovim--that only allow specifying colors
        via RGB channels.

        Returns:
            A hex color code.

        """
        if val.space() != ColorSpace.srgb:
            val = BaseColor(ColorSpace.srgb, val.coords(), alpha=val.alpha())
        return val.to_string(hex=True)

    def _fit(self, val: BaseColor) -> BaseColor:
        return val.clone().fit(self.gamut, method=self.fit_method)

    def max_oklch_chroma(self, val: BaseColor) -> float:
        """Determine maximum OKLCH chroma in the gamut for fixed lightness and hue.

        Returns:
            OKLCH chroma value.

        """
        if val.space() != ColorSpace.oklch:
            val = val.convert("oklch")
        lightness, _, hue = val.coords()
        cmax = BaseColor("oklch", (lightness, 0.4, hue))
        return self._fit(cmax).get("chroma")

    def __call__(self, val: str) -> ColorInfo:
        """Parse a string representation of a color.

        Returns:
            A ColorInfo instance parsed from the input string. Raises a
            ValueError if the input is not parseable.

        """
        raw_color = BaseColor(val)
        if raw_color.space() != ColorSpace.oklch:
            raw_oklch = raw_color.convert(ColorSpace.oklch)
        else:
            raw_oklch = raw_color

        oklch_fit = self._fit(raw_oklch)
        color = oklch_fit.convert(self.gamut)

        inst = ColorInfo(
            raw=val,
            oklch=oklch_fit.to_string(),
            css=color.to_string(),
            hex=self._to_hex(color),
            gamut=self.gamut,
            is_in_gamut=raw_oklch.convert(self.gamut).in_gamut(),
            max_oklch_chroma=self.max_oklch_chroma(raw_oklch),
        )
        inst.set_color(raw_color)
        return inst


def parse(
    val: str,
    gamut: ColorSpace = ColorSpace.srgb,
    fit_method: str = "raytrace",
) -> ColorInfo:
    """Parse a string representation of a color.

    Generate a ``Parser`` instance and call it on the input.

    Returns:
        A ColorInfo instance parsed from the input string. Raises a
        ValueError if the input is not parseable.

    """
    return ColorParser(gamut=gamut, fit_method=fit_method)(val)
