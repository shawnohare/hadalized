"""Schema for a color palette.

A palette is the primary context used to render a color theme.
"""

from functools import cache
from typing import TYPE_CHECKING, Literal, Self

from hadalized.base import BaseNode
from hadalized.color import (
    ColorField,
    ColorFieldHandler,
    ColorRep,
    ColorSpace,
    Extractor,
    Parser,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


class Colors:
    """Builtin color definitions."""

    # blues, high chroma
    blue12: ColorField = "oklch(0.125 0.0225 220)"
    blue13: ColorField = "oklch(0.130 0.030 220)"
    blue14: ColorField = "oklch(0.140 0.030 220)"
    blue16: ColorField = "oklch(0.1625 0.030 220)"
    blue20: ColorField = "oklch(0.200 .030 220)"
    blue25: ColorField = "oklch(0.250 .030 220)"
    blue30: ColorField = "oklch(0.300 .035 220)"
    blue35: ColorField = "oklch(0.350 .035 220)"
    # grays, mid / low chroma
    gray10: ColorField = "oklch(0.100 .010 220)"
    gray12: ColorField = "oklch(0.125 .010 220)"
    gray13: ColorField = "oklch(0.130 .010 220)"
    gray14: ColorField = "oklch(0.140 .010 220)"
    gray16: ColorField = "oklch(0.160 .010 220)"
    gray20: ColorField = "oklch(0.200 .010 220)"
    gray25: ColorField = "oklch(0.250 .010 220)"
    gray30: ColorField = "oklch(0.300 .010 220)"
    gray35: ColorField = "oklch(0.350 .010 220)"
    gray40: ColorField = "oklch(0.40 .010 220)"
    gray45: ColorField = "oklch(0.450 .010 220)"
    gray50: ColorField = "oklch(0.500 .010 220)"
    gray55: ColorField = "oklch(0.550 .010 220)"
    gray60: ColorField = "oklch(0.600 .010 220)"
    gray65: ColorField = "oklch(0.650 .010 220)"
    gray70: ColorField = "oklch(0.700 .010 220)"
    gray75: ColorField = "oklch(0.750 .010 220)"
    gray80: ColorField = "oklch(0.800 .005 220)"
    gray85: ColorField = "oklch(0.850 .005 100)"
    gray90: ColorField = "oklch(0.900 .005 220)"
    gray91: ColorField = "oklch(0.910 .005 100)"
    gray92: ColorField = "oklch(0.925 .005 100)"
    gray95: ColorField = "oklch(0.950 .005 100)"
    gray97: ColorField = "oklch(0.975 .005 100)"
    gray99: ColorField = "oklch(0.990 .005 100)"
    gray100: ColorField = "oklch(0.995 .005 100)"
    # Sun / Day high chroma
    sun12: ColorField = "oklch(0.125 .020 100)"
    sun14: ColorField = "oklch(0.14 .020 100)"
    sun16: ColorField = "oklch(0.16 .020 100)"
    sun20: ColorField = "oklch(0.200 .020 100)"
    sun30: ColorField = "oklch(0.300 .020 100)"
    sun40: ColorField = "oklch(0.400 .020 100)"
    sun50: ColorField = "oklch(0.500 .020 100)"
    sun60: ColorField = "oklch(0.600 .020 100)"
    sun70: ColorField = "oklch(0.700 .020 100)"
    sun80: ColorField = "oklch(0.800 .020 100)"
    sun85: ColorField = "oklch(0.850 .020 100)"
    sun90: ColorField = "oklch(0.900 .020 100)"
    sun91: ColorField = "oklch(0.910 .020 100)"
    sun92: ColorField = "oklch(0.925 .020 100)"
    sun95: ColorField = "oklch(0.950 .020 100)"
    sun97: ColorField = "oklch(0.975 .015 100)"
    sun99: ColorField = "oklch(0.990 .010 100)"
    sun100: ColorField = "oklch(0.995 .010 100)"


class PaletteMetadata(BaseNode):
    """Color definitions accessible to a theme."""

    name: str
    """Palette."""
    desc: str = "A hadalized palette."
    """Palette description."""
    version: str = "0.1"
    """Palette version."""
    mode: Literal["dark", "light"] = "dark"
    """Whether the palette is dark or light mode."""

    def __hash__(self) -> int:  # noqa: D105
        return super().__hash__()


class Palette(PaletteMetadata):
    """Palette Colors.

    A flat mapping of color name to ColorField.

    The main groups of colors are as follows.
    - Bases (16) prefixed with `b` for regular foreground and background.
      This includes overlays,
    - Named grayscale colors (12)
    - Standard hues (12)
    - Alternate / bright (12) prefixed with `alt_`
    - highlights (12) prefixed with `hl_`
    """

    # Bases (16)
    base00: ColorField = "oklch(0.130 0.030 220)"
    """Primary background color."""
    base01: ColorField = "oklch(0.140 0.030 220)"
    """Secondary background color / overlay 1."""
    base02: ColorField = "oklch(0.1625 0.030 220)"
    """Tertiary background color / overlay 2."""
    base03: ColorField = "oklch(0.200 .030 220)"
    """Overlay 3."""
    base04: ColorField = "oklch(0.250 .030 220)"
    """Overlay 4."""
    base05: ColorField = "oklch(0.300 .035 220)"
    """Overlay 5."""
    base06: ColorField = "oklch(0.350 .035 220)"
    """Overlay 6."""
    base07: ColorField = "oklch(0.4250 .020 220)"
    """Base Midpoint."""
    base08: ColorField = "oklch(0.500 .010 220)"
    """Strongly de-mphasized foreground text."""
    base09: ColorField = "oklch(0.600 .010 220)"
    base10: ColorField = "oklch(0.700 .010 220)"
    """De-emphasized foreground text."""
    base11: ColorField = "oklch(0.800 .005 220)"
    """Primary foreground text."""
    base12: ColorField = "oklch(0.850 .005 100)"
    """Emphasized foreground text."""
    base13: ColorField = "oklch(0.900 .020 100)"
    """Tertiary opposite background color."""
    base14: ColorField = "oklch(0.925 .020 100)"
    """Secondary opposite background color ."""
    base15: ColorField = "oklch(0.950 .020 100)"
    """Primary opposite background color."""

    # neutral
    # dark_red: ColorField = "oklch(0.575 0.185 25)"
    # dark_orange: ColorField = "oklch(0.650 0.150 60)"
    # yellow: ColorField = "oklch(0.675 0.120 100)"
    # lime: ColorField = "oklch(0.650 0.130 115)"
    # green: ColorField = "oklch(0.575 0.165 130)"
    # mint: ColorField = "oklch(0.675 0.130 155)"
    # cyan: ColorField = "oklch(0.625 0.100 180)"
    # azure: ColorField = "oklch(0.675 0.110 225)"
    # blue: ColorField = "oklch(0.575 0.140 250)"
    # violet: ColorField = "oklch(0.575 0.185 290)"
    # magenta: ColorField = "oklch(0.575 0.185 330)"
    # rose: ColorField = "oklch(0.675 0.100 360)"

    # Main hues (12).
    # dark hue defaults
    red: ColorField = "oklch(0.60 0.185 25)"
    orange: ColorField = "oklch(0.650 0.150 60)"
    yellow: ColorField = "oklch(0.700 0.120 100)"
    lime: ColorField = "oklch(0.675 0.120 115)"
    green: ColorField = "oklch(0.650 0.165 130)"
    mint: ColorField = "oklch(0.715 0.130 155)"
    cyan: ColorField = "oklch(0.650 0.100 180)"
    azure: ColorField = "oklch(0.725 0.110 225)"
    blue: ColorField = "oklch(0.625 0.150 250)"
    violet: ColorField = "oklch(0.625 0.185 290)"
    magenta: ColorField = "oklch(0.625 0.185 330)"
    rose: ColorField = "oklch(0.700 0.100 360)"

    # Brights or alternate hues (12)
    alt_red: ColorField = "oklch(0.675 0.200 25)"
    alt_orange: ColorField = "oklch(0.75 0.175 60)"
    alt_yellow: ColorField = "oklch(0.80 0.165 100)"
    alt_lime: ColorField = "oklch(0.800 0.185 120)"
    alt_green: ColorField = "oklch(0.800 0.200 135)"
    alt_mint: ColorField = "oklch(0.800 0.195 155)"
    alt_cyan: ColorField = "oklch(0.800 0.145 180)"
    alt_azure: ColorField = "oklch(0.800 0.135 225)"
    alt_blue: ColorField = "oklch(0.800 0.100 250)"
    alt_violet: ColorField = "oklch(0.800 0.100 290)"
    alt_magenta: ColorField = "oklch(0.800 0.185 330)"
    alt_rose: ColorField = "oklch(0.800 0.120 360)"

    # Highlight hues (12)
    hl_red: ColorField = "oklch(0.800 0.100 25)"
    hl_orange: ColorField = "oklch(0.850 0.100 60)"
    hl_yellow: ColorField = "oklch(0.950 0.200 100)"
    hl_lime: ColorField = "oklch(0.855 0.100 115)"
    hl_green: ColorField = "oklch(0.85 0.100 130)"
    hl_mint: ColorField = "oklch(0.875 0.100 155)"
    hl_cyan: ColorField = "oklch(0.900 0.100 180)"
    hl_azure: ColorField = "oklch(0.875 0.100 225)"
    hl_blue: ColorField = "oklch(0.825 0.100 250)"
    hl_violet: ColorField = "oklch(0.825 0.200 290)"
    hl_magenta: ColorField = "oklch(0.825 0.200 330)"
    hl_rose: ColorField = "oklch(0.825 0.200 360)"

    # Achromatic grayscale (12).
    black: ColorField = "oklch(0.10 0.01 220)"
    jet: ColorField = "oklch(0.15 0.01 220)"
    abyss: ColorField = "oklch(0.20 0.01 220)"
    onyx: ColorField = "oklch(0.30 0.01 220)"
    charcoal: ColorField = "oklch(0.40 0.01 220)"
    dimgray: ColorField = "oklch(0.50 0.01 220)"
    smoke: ColorField = "oklch(0.60 0.01 220)"
    darkgray: ColorField = "oklch(0.70 0.01 220)"
    silver: ColorField = "oklch(0.80 0.01 220)"
    lightgray: ColorField = "oklch(0.850 0.005 220)"
    platinum: ColorField = "oklch(0.90 0.01 220)"
    white: ColorField = "oklch(0.975 0.005 220)"

    def meta(self) -> Iterator[tuple[str, str]]:
        """Palette colors.

        Yields:
            A field name and color representation.

        """
        for key in PaletteMetadata.model_fields:
            yield key, self[key]

    def colors(self) -> Iterator[tuple[str, ColorField]]:
        """Palette colors.

        Yields:
            A field name and color representation.

        """
        for key, val in self:
            if key in PaletteMetadata.model_fields:
                continue
            yield key, val

    def map(self, handler: ColorFieldHandler) -> Self:
        """Map a handler accross color fields.

        Returns:
            A new Palette instance with the handler applied to each
            field that contains a ColorMap instance.

        """
        data = {
            k: handler(v) if k not in PaletteMetadata.model_fields else v
            for k, v in self
        }
        return self.model_validate(data)

    @staticmethod
    def default() -> Palette:
        """Create a a generic default palette.

        Returns:
            A ready to use dummy instance.

        """
        return Palette(name="dark", desc="default", mode="dark", version="0.1")

    @staticmethod
    def builtin() -> dict[str, Palette]:
        """Lazily compute default palette colors.

        Returns:
            A map of palette.name -> palette.

        """
        # Palette definitions
        dark: Palette = Palette(
            name="dark",
            desc="Main dark palette with darker solarized inspired bases.",
            version="2.1",
            mode="dark",
        )
        gray: Palette = Palette(
            name="gray",
            desc="Dark theme variant with more grayish backgrounds.",
            version="2.1",
            mode="dark",
            base00=Colors.gray13,
            base01=Colors.gray14,
            base02=Colors.gray16,
            base03=Colors.gray20,
            base04=Colors.gray25,
            base05=Colors.gray30,
            base06=Colors.gray35,
        )

        day: Palette = Palette(
            name="day",
            desc="Light theme variant with sunny backgrounds.",
            version="2.1",
            mode="light",
            red="oklch(0.550 0.185 25)",
            orange="oklch(0.650 0.150 60)",
            yellow="oklch(0.650 0.120 100)",
            lime="oklch(0.650 0.130 115)",
            green="oklch(0.575 0.165 130)",
            mint="oklch(0.650 0.130 155)",
            cyan="oklch(0.550 0.100 180)",
            azure="oklch(0.650 0.110 225)",
            blue="oklch(0.575 0.140 250)",
            violet="oklch(0.550 0.185 290)",
            magenta="oklch(0.550 0.185 330)",
            rose="oklch(0.625 0.100 360)",
            base00=Colors.sun100,
            base01=Colors.sun99,
            base02=Colors.sun95,
            base03=Colors.sun92,
            base04=Colors.sun99,
            base05=Colors.sun85,
            base06=Colors.sun80,
            base07=Colors.gray75,
            base09=Colors.gray60,
            base10=Colors.gray50,
            base11=Colors.gray40,
            base12=Colors.gray30,
            base13=Colors.blue20,
            base14=Colors.blue16,
            base15=Colors.blue12,
        )

        white: Palette = day | Palette(
            name="white",
            desc="Light theme variant with whiter backgrounds.",
            version="2.1",
            mode="light",
            base00=Colors.gray100,
            base01=Colors.gray99,
            base02=Colors.gray95,
            base03=Colors.gray92,
            base04=Colors.gray99,
            base05=Colors.gray85,
            base06=Colors.gray80,
        )

        palettes = [
            dark,
            gray,
            day,
            white,
        ]
        return {x.name: x for x in palettes}

    def __hash__(self) -> int:  # noqa: D105
        return super().__hash__()

    def transform(self, gamut: ColorSpace, rep: ColorRep) -> Palette:
        """Transform the palette via `transform_palette`.

        Returns:
            Same as `transform_palette`

        """
        return transform_palette(self, gamut, rep)

    def parse(self, gamut: ColorSpace) -> Palette:
        """Transform the palette via `transform_palette`.

        Returns:
            Same as `transform_palette`

        """
        return _parse(self, gamut)


@cache
def _parse(palette: Palette, gamut: ColorSpace) -> Palette:
    parser = Parser(gamut=gamut)
    return palette.map(parser)


@cache
def transform_palette(palette: Palette, gamut: ColorSpace, rep: ColorRep) -> Palette:
    """Transform a palette to be used in template rendering.

    Returns:
        A palette parsed against the input gamut with the specified node selected.

    """
    parsed = _parse(palette, gamut)
    return parsed if rep == ColorRep.info else parsed.map(Extractor(rep))
