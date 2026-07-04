"""Style types."""

from typing import Annotated, Literal

from pydantic import AfterValidator, Field, PrivateAttr

from hadalized.base import BaseNode
from hadalized.palette import Hue

# class Control(StrEnum):
#     """Special control references.
#
#     Stubbed at present for future use.
#     """
#
#     ignore = auto()
#     unset = auto()


type NullStr = Annotated[
    Literal["nil", "null", "none", "None"],
    AfterValidator(lambda _: None),
]
"""NullStr represent strings that should be transformed to None.
Used primarily in toml configurations where a user needs to explicitly
set a value to None, e.g., to specify some style fg or bg should be
transparent."""


type OptionalColorString = Annotated[
    Hue | NullStr | str | None,
    Field(union_mode="left_to_right"),
]
"""A resolved Color passed to template context."""


type ColorString = Annotated[Hue | str, Field(union_mode="left_to_right")]
"""A resolved Color passed to template context."""


class Style(BaseNode):
    """Style to apply to some element.

    Includes standard text styling such as italic, bold as well as
    foreground and background colors.

    Structurally, this node is similar to neovim's highlight groups. The
    distinction between GUI and non-gui elements is omitted.

    Subclasses define to which type of grouping the node belongs to.
    """

    bold: bool | None = None
    reverse: bool | None = None
    italic: bool | None = None
    standout: bool | None = None
    strikethrough: bool | None = None
    undercurl: bool | None = None
    underdashed: bool | None = None
    underdotted: bool | None = None
    underdouble: bool | None = None
    underline: bool | None = None

    fg: OptionalColorString = None
    """Foreground color. Defined as a palette reference and replaced with
    a concrete color field from a palette after resolution."""
    bg: OptionalColorString = None
    """Background color. Defined as a palette reference and replaced with
    a concrete color field from a palette after resolution."""
    sp: OptionalColorString = None
    """Color of special styling such as underlines."""
    border: OptionalColorString = None
    """For UI elements that contain an obvious border."""
    shadow: OptionalColorString = None
    """For UI elements that can style shadows."""
    font: str | None = None
    """Font to use for GUI components that allow it."""
    link: str | None = None
    """Specifies that the instance's values should be merged into the
    linked theme field."""
    exclude: bool = False
    """Set when a user wants to purposefully exlude a style from usage."""
    _is_empty: bool | None = PrivateAttr(default=None)
    _field: str = PrivateAttr(default="")

    @property
    def name(self) -> str:
        """The underlying field to which the style belongs."""
        return self._field

    @name.setter
    def name(self, val: str):
        self._field = val

    def __bool__(self) -> bool:
        """Is the instance excluded or an empty default.

        Returns:
            An bool indicating if the `exclude` flag is set or it every value
            is a default.

        """
        if self._is_empty is None:
            self._is_empty = self.exclude or bool(self.model_fields_set)
        return self._is_empty


class Syntax(Style):
    """Indicates code syntax highlight group."""


class UI(Style):
    """UI elements with additional fields.

    Invludes widgets, windows, menus, etc.
    """


class Diagnostic(Style):
    """Highlight blocks related to diagnostics.

    All highlights defined for diagnostics begin with `diagnostic` followed by
    the type of highlight (e.g., `sign`, `underline`, etc.) and the severity (e.g.
    `Error`, `Warn`, etc.)

    By default, highlights for signs, floating windows, and virtual text are
    linked to the corresponding default highlight. Underline highlights are
    linked to their corresponding severity highlight but
    by default specify that the text underline styling.

    cf. in neovim `h: diagnostic-highlights`
    """


class Lsp(Style):
    """Node belongs to LSP components.

    cf. https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
    cf. https://microsoft.github.io/language-server-protocol/specification#textDocument_documentHighlight
    cf. in neovim `h: lsp-highlight`
    """


class Terminal(UI):
    """Node belongs to UI Terminal elements.

    For example, terminal emulators embedded in an application (e.g., neovim)
    where some styling should be different than the main application.
    """


class Minimap(UI):
    """Minimap elements."""


class Treesitter(Style):
    """Syntax blocks defined by treesitter.

    cf: https://tree-sitter.github.io/tree-sitter/3-syntax-highlighting.html
    and neovim `:h treesitter-highlight-groups`
    The treesitter names are the field names prefixed with `@` and with
    "_" -> "."
    """
