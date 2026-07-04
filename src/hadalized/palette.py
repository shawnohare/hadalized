"""Schema for a color palette.

A palette is the primary context used to render a color theme.
"""

from enum import StrEnum, auto
from functools import cache
from typing import TYPE_CHECKING, Literal, Self, override

from hadalized.base import BaseNode
from hadalized.color import (
    ColorInfo,
    ColorParser,
    ColorRep,
    ColorSpace,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


class Hue(StrEnum):
    """Palette field references."""

    base00 = auto()
    base01 = auto()
    base02 = auto()
    base03 = auto()
    base04 = auto()
    base05 = auto()
    base06 = auto()
    base07 = auto()
    base08 = auto()
    base09 = auto()
    base10 = auto()
    base11 = auto()
    base12 = auto()
    base13 = auto()
    base14 = auto()
    base15 = auto()
    red = auto()
    orange = auto()
    yellow = auto()
    lime = auto()
    green = auto()
    mint = auto()
    cyan = auto()
    azure = auto()
    blue = auto()
    violet = auto()
    magenta = auto()
    rose = auto()
    alt_red = auto()
    alt_orange = auto()
    alt_yellow = auto()
    alt_lime = auto()
    alt_green = auto()
    alt_mint = auto()
    alt_cyan = auto()
    alt_azure = auto()
    alt_blue = auto()
    alt_violet = auto()
    alt_magenta = auto()
    alt_rose = auto()
    hl_red = auto()
    hl_orange = auto()
    hl_yellow = auto()
    hl_lime = auto()
    hl_green = auto()
    hl_mint = auto()
    hl_cyan = auto()
    hl_azure = auto()
    hl_blue = auto()
    hl_violet = auto()
    hl_magenta = auto()
    hl_rose = auto()
    black = auto()
    jet = auto()
    abyss = auto()
    onyx = auto()
    charcoal = auto()
    dimgray = auto()
    smoke = auto()
    darkgray = auto()
    silver = auto()
    lightgray = auto()
    platinum = auto()
    white = auto()


class PaletteMetadata(BaseNode):
    """Information describing the palette."""

    name: str
    """Palette."""
    desc: str = "A hadalized palette."
    """Palette description."""
    version: str = "0.1"
    """Palette version."""
    mode: Literal["dark", "light"] = "dark"
    """Whether the palette is dark or light mode."""

    @override
    def __hash__(self) -> int:
        return super().__hash__()


class Palette(BaseNode):
    """A mapping of color name to value (e.g., hex code, css, etc).

    The main groups of colors are

    - 16 bases used in foregrounds, backgrounds, overlays, etc. prefixed with `base`.
    - 12 common grayscale colors
    - 12 standard hues
    - 12 alternate / bright hues prefixed with `alt_`
    - 12 highlight hues prefixed with `hl_`
    """

    meta: PaletteMetadata
    """Name, version, etc."""

    # Bases (16)
    base00: str = "oklch(0.130 0.030 220)"
    """Primary background color."""
    base01: str = "oklch(0.140 0.030 220)"
    """Secondary background color / overlay 1."""
    base02: str = "oklch(0.1625 0.030 220)"
    """Tertiary background color / overlay 2."""
    base03: str = "oklch(0.200 .030 220)"
    """Overlay 3."""
    base04: str = "oklch(0.250 .030 220)"
    """Overlay 4."""
    base05: str = "oklch(0.300 .035 220)"
    """Overlay 5."""
    base06: str = "oklch(0.350 .035 220)"
    """Overlay 6."""
    base07: str = "oklch(0.4750 .020 220)"
    """Base Midpoint."""
    base08: str = "oklch(0.500 .010 220)"
    """Strongly de-emphasized foreground text."""
    base09: str = "oklch(0.600 .010 220)"
    base10: str = "oklch(0.700 .010 220)"
    """De-emphasized foreground text."""
    base11: str = "oklch(0.800 .005 220)"
    """Primary foreground text."""
    base12: str = "oklch(0.850 .005 100)"
    """Emphasized foreground text."""
    base13: str = "oklch(0.900 .020 100)"
    """Tertiary opposite background color."""
    base14: str = "oklch(0.925 .020 100)"
    """Secondary opposite background color ."""
    base15: str = "oklch(0.950 .020 100)"
    """Primary opposite background color."""

    # neutral
    # dark_red: str = "oklch(0.575 0.185 25)"
    # dark_orange: str = "oklch(0.650 0.150 60)"
    # yellow: str = "oklch(0.675 0.120 100)"
    # lime: str = "oklch(0.650 0.130 115)"
    # green: str = "oklch(0.575 0.165 130)"
    # mint: str = "oklch(0.675 0.130 155)"
    # cyan: str = "oklch(0.625 0.100 180)"
    # azure: str = "oklch(0.675 0.110 225)"
    # blue: str = "oklch(0.575 0.140 250)"
    # violet: str = "oklch(0.575 0.185 290)"
    # magenta: str = "oklch(0.575 0.185 330)"
    # rose: str = "oklch(0.675 0.100 360)"

    # Main hues (12).
    # dark hue defaults
    red: str = "oklch(0.60 0.185 25)"
    orange: str = "oklch(0.650 0.150 60)"
    yellow: str = "oklch(0.700 0.120 100)"
    lime: str = "oklch(0.675 0.120 115)"
    green: str = "oklch(0.650 0.165 130)"
    mint: str = "oklch(0.715 0.130 155)"
    cyan: str = "oklch(0.650 0.100 180)"
    azure: str = "oklch(0.725 0.110 225)"
    blue: str = "oklch(0.625 0.150 250)"
    violet: str = "oklch(0.625 0.185 290)"
    magenta: str = "oklch(0.625 0.185 330)"
    rose: str = "oklch(0.700 0.100 360)"

    # Brights or alternate hues (12)
    alt_red: str = "oklch(0.675 0.200 25)"
    alt_orange: str = "oklch(0.75 0.175 60)"
    alt_yellow: str = "oklch(0.80 0.165 100)"
    alt_lime: str = "oklch(0.800 0.185 120)"
    alt_green: str = "oklch(0.800 0.200 135)"
    alt_mint: str = "oklch(0.800 0.195 155)"
    alt_cyan: str = "oklch(0.800 0.145 180)"
    alt_azure: str = "oklch(0.800 0.135 225)"
    alt_blue: str = "oklch(0.800 0.100 250)"
    alt_violet: str = "oklch(0.800 0.100 290)"
    alt_magenta: str = "oklch(0.800 0.185 330)"
    alt_rose: str = "oklch(0.800 0.120 360)"

    # Highlight hues (12)
    hl_red: str = "oklch(0.800 0.100 25)"
    hl_orange: str = "oklch(0.850 0.100 60)"
    hl_yellow: str = "oklch(0.950 0.200 100)"
    hl_lime: str = "oklch(0.855 0.100 115)"
    hl_green: str = "oklch(0.85 0.100 130)"
    hl_mint: str = "oklch(0.875 0.100 155)"
    hl_cyan: str = "oklch(0.900 0.100 180)"
    hl_azure: str = "oklch(0.875 0.100 225)"
    hl_blue: str = "oklch(0.825 0.100 250)"
    hl_violet: str = "oklch(0.825 0.200 290)"
    hl_magenta: str = "oklch(0.825 0.200 330)"
    hl_rose: str = "oklch(0.825 0.200 360)"

    # Achromatic grayscale (12).
    black: str = "oklch(0.10 0.01 220)"
    jet: str = "oklch(0.15 0.01 220)"
    abyss: str = "oklch(0.20 0.01 220)"
    onyx: str = "oklch(0.30 0.01 220)"
    charcoal: str = "oklch(0.40 0.01 220)"
    dimgray: str = "oklch(0.50 0.01 220)"
    smoke: str = "oklch(0.60 0.01 220)"
    darkgray: str = "oklch(0.70 0.01 220)"
    silver: str = "oklch(0.80 0.01 220)"
    lightgray: str = "oklch(0.850 0.005 220)"
    platinum: str = "oklch(0.90 0.01 220)"
    white: str = "oklch(0.975 0.005 220)"

    @property
    def name(self) -> str:
        """Palette name."""
        return self.meta.name

    @property
    def desc(self) -> str:
        """Palette description."""
        return self.meta.desc

    @property
    def version(self) -> str:
        """Palette version."""
        return self.meta.version

    @property
    def mode(self) -> str:
        """Palette mode."""
        return self.meta.mode

    # def hue(self, name: Hue) -> str:
    #     """Get a palette color by name.
    #
    #     Returns:
    #         The hue value.
    #
    #     Raises:
    #         ValueError:
    #             When the hue name is an unexpected field.
    #
    #     """
    #     out = getattr(self, name)
    #     if not isinstance(out, str):
    #         raise ValueError(f"Invalid field {name}")
    #     return out

    def colors(self) -> Iterator[tuple[str, str]]:
        """Palette colors.

        Yields:
            A field name and color representation.

        """
        for key, val in self:
            if key == "meta":
                continue
            yield key, val

    @staticmethod
    def default() -> Palette:
        """Create a a generic default palette.

        Returns:
            A ready to use dummy instance.

        """
        return Palette(
            meta=PaletteMetadata(
                name="dark", desc="default", mode="dark", version="0.1"
            ),
        )

    @override
    def __hash__(self) -> int:
        return super().__hash__()

    def parse(self, gamut: ColorSpace) -> dict[str, ColorInfo]:
        """Produce a map of color name to ColorInfo.

        Returns:
            A map of color name -> ColorInfo.

        """
        return _parse(self, gamut)

    def transform(self, gamut: ColorSpace, rep: ColorRep) -> Self:
        """Parse the palette's color definitions and extract a color representation.

        Returns:
            A new instance with the colors transformed.

        """
        colors = {k: v[rep] for k, v in self.parse(gamut).items()}
        return self.__class__(meta=self.meta, **colors)


@cache
def _parse(palette: Palette, gamut: ColorSpace) -> dict[str, ColorInfo]:
    parser = ColorParser(gamut=gamut)
    return {k: parser(v) for k, v in palette.colors()}


@cache
def transform(palette: Palette, gamut: ColorSpace, rep: ColorRep) -> Palette:
    """Transform a palette to be used in template rendering.

    Returns:
        A palette parsed against the input gamut with the specified node selected.

    """
    colors = {k: v[rep] for k, v in _parse(palette, gamut).items()}
    return Palette(meta=palette.meta, **colors)
