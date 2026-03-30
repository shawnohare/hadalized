"""Abstract and universal theme models.

An abstract theme serves as a collection of references to palette colors.
When the references are resolved against a specific palette, a universal
application agnostic theme results.
"""

from enum import StrEnum, auto
from functools import cache
from typing import TYPE_CHECKING, Annotated, Literal, Self

from pydantic import AfterValidator, Field, PrivateAttr

from hadalized.base import BaseNode
from hadalized.color import ColorField
from hadalized.palette import Palette  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Iterator


class R(StrEnum):
    """Palette field references."""

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


type PaletteField = R
"""More descriptive alias."""


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


# def _ref_validator(val: R | ColorField | None) -> R | ColorField | None:
#     if val is None or isinstance(val, (ColorInfo, R)):
#         return val
#     try:
#         out = R(val)
#     except ValueError:
#         out = val if val not in {"nil", "null", "none", "None"} else None
#     return out


type ColorValue = Annotated[
    PaletteField | NullStr | ColorField | None,
    Field(union_mode="left_to_right"),
    # AfterValidator(_ref_validator),
]
"""A resolved Color passed to template context."""
type ColorRef = NullStr | PaletteField | None


class Refs(BaseNode):
    """Container for palette field references."""

    fg: ColorRef
    bg: ColorRef
    color: ColorRef


class BaseStyle(BaseNode):
    """Base linkable object for style elements."""

    link: Link | None = None
    """Specifies that the instance's values should be merged into the
    linked style."""
    exclude: bool = False
    """Set when a user wants to purposefully exlude a style from usage."""
    _is_empty: bool | None = PrivateAttr(default=None)
    _field: str = PrivateAttr(default="")

    @property
    def name(self) -> str:
        """The underlying field to which the style belongs."""
        return self._field

    def __bool__(self) -> bool:
        """Is the instance excluded or an empty default.

        Returns:
            An bool indicating if the `exclude` flag is set or it every value
            is default.

        """
        if self._is_empty is None:
            self._is_empty = self.exclude or bool(
                self.model_dump(exclude_defaults=True)
            )
        return self._is_empty


class Color(BaseStyle):
    """Style blocks that represent a single color, typically without styling.

    In templates, these nodes are rendered as the value of `fg`.
    """

    color: ColorValue = None
    """Color. Defined as a palette reference and replaced with a concrete color
    field from a palette after resolution."""

    def __str__(self) -> str:
        """Representation of node in a template.

        Returns:
            The `color` attribute as a string if defined, else the standard
            representation.

        """
        return str(self.color)


class Style(BaseStyle):
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

    # Concrete values.
    fg: ColorValue = None
    """Foreground color. Defined as a palette reference and replaced with
    a concrete color field from a palette after resolution."""
    bg: ColorValue = None
    """Background color. Defined as a palette reference and replaced with
    a concrete color field from a palette after resolution."""


class UI(Style):
    """UI elements with additional fields.

    Invludes widgets, windows, menus, etc.
    """

    border: ColorValue = None
    """For elements that contain an obvious border."""
    shadw: ColorValue = None
    """For elements that can style shadows."""


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


def color(val: PaletteField | None) -> Color:
    """Create a new Color instance.

    Returns:
        New Color instance with `fg` attribute defined.

    """
    return Color(color=val)


class ThemeMetadata(BaseNode):
    """Theme metadata fields that are not style blocks."""

    name: str = Field(
        default="hadalized",
        examples=["hadalized"],
    )
    """Prefixed to a palette name to generate full theme name.
    This name is typically used for generated application theme files."""
    desc: str = "Theme built using hadalized."
    version: str = "0.1"
    url: str = "https://www.github.com/hadalized/hadalized"

    @classmethod
    def builtin(cls) -> Self:
        """Builtin hadalized abstract theme.

        Returns:
            An abstract theme whose styles are those defined in the package.

        """
        return cls(
            name="hadalized",
            desc="Builtin hadalized theme.",
        )

    def __hash__(self) -> int:  # noqa: D105
        return super().__hash__()


class Link(StrEnum):
    """Theme field names that can be linked to."""

    # visual_nos = auto()
    # pmenu = auto()
    # pmenu_extra = auto()
    # pmenu_extra_sel = auto()
    # pmenu_kind = auto()
    # pmenu_kind_sel = auto()
    # pmenu_match = auto()
    # pmenu_match_sel = auto()
    # pmenu_sbar = auto()
    # pmenu_sel = auto()
    # pmenu_thumb = auto()
    ansi00 = auto()
    ansi01 = auto()
    ansi02 = auto()
    ansi03 = auto()
    ansi04 = auto()
    ansi05 = auto()
    ansi06 = auto()
    ansi07 = auto()
    ansi08 = auto()
    ansi09 = auto()
    ansi10 = auto()
    ansi11 = auto()
    ansi12 = auto()
    ansi13 = auto()
    ansi14 = auto()
    ansi15 = auto()
    attribute = auto()
    attribute_builtin = auto()
    boolean = auto()
    character = auto()
    character_special = auto()
    color_column = auto()
    comment = auto()
    comment_documentation = auto()
    comment_error = auto()
    comment_note = auto()
    comment_todo = auto()
    comment_warning = auto()
    completion_match_insert = auto()
    conceal = auto()
    constant = auto()
    constant_builtin = auto()
    constant_macro = auto()
    constructor = auto()
    cursor = auto()
    cursor_column = auto()
    cursor_line = auto()
    cursor_line_fold = auto()
    cursor_line_gutter = auto()
    cursor_line_number = auto()
    diagnostic_deprecated = auto()
    diagnostic_error = auto()
    diagnostic_hint = auto()
    diagnostic_info = auto()
    diagnostic_ok = auto()
    diagnostic_unnecessary = auto()
    diagnostic_warn = auto()
    dianostic_floating_error = auto()
    dianostic_floating_hint = auto()
    dianostic_floating_info = auto()
    dianostic_floating_ok = auto()
    dianostic_floating_warn = auto()
    dianostic_sign_error = auto()
    dianostic_sign_hint = auto()
    dianostic_sign_info = auto()
    dianostic_sign_ok = auto()
    dianostic_sign_warn = auto()
    dianostic_underline_error = auto()
    dianostic_underline_hint = auto()
    dianostic_underline_info = auto()
    dianostic_underline_ok = auto()
    dianostic_underline_warn = auto()
    dianostic_virtual_lines_error = auto()
    dianostic_virtual_lines_hint = auto()
    dianostic_virtual_lines_info = auto()
    dianostic_virtual_lines_ok = auto()
    dianostic_virtual_lines_warn = auto()
    dianostic_virtual_text_error = auto()
    dianostic_virtual_text_hint = auto()
    dianostic_virtual_text_info = auto()
    dianostic_virtual_text_ok = auto()
    dianostic_virtual_text_warn = auto()
    diff_delta = auto()
    diff_minus = auto()
    diff_plus = auto()
    end_of_buffer = auto()
    floating_window = auto()
    floating_window_border = auto()
    floating_window_footer = auto()
    floating_window_title = auto()
    fold_column = auto()
    folded_line = auto()
    function = auto()
    function_builtin = auto()
    function_call = auto()
    function_macro = auto()
    function_method = auto()
    function_method_call = auto()
    gutter = auto()
    keyword = auto()
    keyword_conditional = auto()
    keyword_conditional_ternary = auto()
    keyword_coroutine = auto()
    keyword_debug = auto()
    keyword_directive = auto()
    keyword_directive_define = auto()
    keyword_exception = auto()
    keyword_function = auto()
    keyword_import = auto()
    keyword_modifier = auto()
    keyword_operator = auto()
    keyword_repeat = auto()
    keyword_return = auto()
    keyword_type = auto()
    label = auto()
    line_number = auto()
    line_number_above = auto()
    line_number_below = auto()
    lsp_code_lens_separator = auto()
    lsp_inlay_hint = auto()
    lsp_mod_abstract = auto()
    lsp_mod_async = auto()
    lsp_mod_declaration = auto()
    lsp_mod_default_library = auto()
    lsp_mod_definition = auto()
    lsp_mod_deprecated = auto()
    lsp_mod_documentation = auto()
    lsp_mod_modification = auto()
    lsp_mod_readonly = auto()
    lsp_mod_static = auto()
    lsp_reference_read = auto()
    lsp_reference_target = auto()
    lsp_reference_text = auto()
    lsp_reference_write = auto()
    lsp_signature_active_parameter = auto()
    lsp_type_class = auto()
    lsp_type_comment = auto()
    lsp_type_decorator = auto()
    lsp_type_enum = auto()
    lsp_type_enum_member = auto()
    lsp_type_event = auto()
    lsp_type_function = auto()
    lsp_type_interface = auto()
    lsp_type_keyword = auto()
    lsp_type_macro = auto()
    lsp_type_method = auto()
    lsp_type_modifier = auto()
    lsp_type_namespace = auto()
    lsp_type_number = auto()
    lsp_type_operator = auto()
    lsp_type_parameter = auto()
    lsp_type_property = auto()
    lsp_type_regexp = auto()
    lsp_type_string = auto()
    lsp_type_struct = auto()
    lsp_type_type = auto()
    lsp_type_type_parameter = auto()
    lsp_type_variable = auto()
    main = auto()
    main_unfocused = auto()
    markup_heading = auto()
    markup_heading_1 = auto()
    markup_heading_2 = auto()
    markup_heading_3 = auto()
    markup_heading_4 = auto()
    markup_heading_5 = auto()
    markup_heading_6 = auto()
    markup_italic = auto()
    markup_link = auto()
    markup_link_label = auto()
    markup_link_url = auto()
    markup_list = auto()
    markup_list_checked = auto()
    markup_list_unchecked = auto()
    markup_math = auto()
    markup_quote = auto()
    markup_raw = auto()
    markup_raw_block = auto()
    markup_strikethrough = auto()
    markup_strong = auto()
    markup_underline = auto()
    matched_bracket = auto()
    menu = auto()
    message = auto()
    message_error = auto()
    message_mode = auto()
    message_more = auto()
    message_question = auto()
    message_separator = auto()
    message_warn = auto()
    module = auto()
    module_builtin = auto()
    non_text = auto()
    number = auto()
    number_float = auto()
    operator = auto()
    property = auto()
    punctuation_bracket = auto()
    punctuation_delimiter = auto()
    punctuation_special = auto()
    quick_fix_line = auto()
    scrollbar = auto()
    search = auto()
    search_current_match = auto()
    search_incremental = auto()
    selection = auto()
    snippet_tabstop = auto()
    special_key = auto()
    spell_bad = auto()
    spell_cap = auto()
    spell_local = auto()
    spell_rare = auto()
    status_line = auto()
    status_line_unfocused = auto()
    string = auto()
    string_documentation = auto()
    string_escape = auto()
    string_regexp = auto()
    string_special = auto()
    string_special_path = auto()
    string_special_symbol = auto()
    string_special_url = auto()
    substitute = auto()
    tab_line = auto()
    tab_line_fill = auto()
    tab_line_sel = auto()
    tag = auto()
    tag_attribute = auto()
    tag_builtin = auto()
    tag_delimiter = auto()
    terminal_cursor = auto()
    terminal_status_line = auto()
    terminal_status_line_unfocused = auto()
    type = auto()
    type_builtin = auto()
    type_definition = auto()
    variable = auto()
    variable_builtin = auto()
    variable_member = auto()
    variable_parameter = auto()
    variable_parameter_builtin = auto()
    whitespace = auto()
    wild_menu = auto()
    window_bar = auto()
    window_bar_unfocused = auto()
    window_separator = auto()


class ThemeBlocks(BaseNode):
    """Theme style blocks and highlight groups.

    Each Style field defines a style or color to apply to a particular element.
    For example, UI interfaces, code syntax blocks, etc.

    vscode reference

    - https://code.visualstudio.com/api/references/theme-color
    - https://gist.github.com/AndreasBackx/ab5c7df0ef214a798cfa8fdeaf59197f
    - https://gist.github.com/dcts/5b2af4c8b6918e7d35c4121f11d49fb1
    """

    ansi00: Color = color(R.black)
    ansi01: Color = color(R.red)
    ansi02: Color = color(R.green)
    ansi03: Color = color(R.yellow)
    ansi04: Color = color(R.blue)
    ansi05: Color = color(R.magenta)
    ansi06: Color = color(R.cyan)
    ansi07: Color = color(R.silver)
    ansi08: Color = color(R.smoke)
    ansi09: Color = color(R.rose)
    ansi10: Color = color(R.lime)
    ansi11: Color = color(R.orange)
    ansi12: Color = color(R.azure)
    ansi13: Color = color(R.violet)
    ansi14: Color = color(R.mint)
    ansi15: Color = color(R.white)

    # Elements corresponding to fundamental foregrounds and backgrounds.
    main: Style = Style(fg=R.base11, bg=R.base00)
    """Main background and foreground. Similar to vim's Normal group."""
    main_unfocused: Style = Style(fg=R.base11, bg=R.base00)
    """Normal text in inactive / non-current / unfocused windows."""

    cursor: UI = UI(fg=R.base10, bg=R.base05, border=R.blue)
    """Cursor style (e.g., in terminal emulators).

    Note that in neovim in wezterm, it appears this value is inherited
    from the wezterm settings
    """
    selection: Style = Style(bg=R.base03)
    """Selected areas, e.g., vim's Visual selection."""

    # begin: treesitter
    attribute: Treesitter = Treesitter(fg=R.orange)
    """Attribute annotations (e.g., Python decorators and Rust lifetimes)."""
    attribute_builtin: Treesitter = Treesitter(fg=R.orange, italic=True)
    """Builtin annotations (e.g., `@property` in Python)."""
    diff_delta: Treesitter = Treesitter(fg=R.yellow)
    """Changed text for diff files,"""
    diff_minus: Treesitter = Treesitter(fg=R.red)
    """Deleted text for diff files,"""
    diff_plus: Treesitter = Treesitter(fg=R.green)
    """Added text for diff files,"""
    comment: Treesitter = Treesitter(fg=R.base09)
    """Line and block comments."""
    comment_documentation: Treesitter = Treesitter(link=Link.string_documentation)
    """Comments that document code."""
    comment_error: Treesitter = Treesitter(fg=R.red)
    """Error type comments (e.g., `ERROR`, `FIXME`)."""
    comment_warning: Treesitter = Treesitter(fg=R.orange)
    """Warning type comments (e.g., `WARNING`, `FIX`, `HACK`)."""
    comment_todo: Treesitter = Treesitter(fg=R.yellow)
    """Todo type comments (e.g., `TODO`, `WIP`)."""
    comment_note: Treesitter = Treesitter(fg=R.blue)
    """Note type comments (e.g., `NOTE`, `INFO`, `xxx`)."""

    constant: Treesitter = Treesitter(fg=R.magenta)
    """Constant identifiers."""
    constant_builtin: Treesitter = Treesitter(fg=R.magenta, italic=True)
    """Builtin constant identifiers."""
    constant_macro: Treesitter = Treesitter(fg=R.magenta, bold=True)
    """Constants defined by a preprocessor."""

    label: Treesitter = Treesitter(fg=R.orange)
    """GOTO and other labels, including heredoc labels."""
    module: Treesitter = Treesitter(fg=R.lime, bold=True)
    """Modules or namespace."""
    module_builtin: Treesitter = Treesitter(fg=R.magenta, italic=True, bold=True)
    """Builtin or stdlib modules and namespaces."""

    # Basic types.
    character: Treesitter = Treesitter(fg=R.cyan)
    """Character literals."""
    character_special: Treesitter = Treesitter(fg=R.red)
    """Special characters, (e.g., wildcards)."""
    boolean: Treesitter = Treesitter(fg=R.lime, italic=True)
    """Boolean literals."""
    number: Treesitter = Treesitter(fg=R.rose)
    """Numeric literals."""
    number_float: Treesitter = Treesitter(fg=R.magenta)
    """Floating point literals."""
    type: Treesitter = Treesitter(fg=R.violet)
    """Type or class definitions and annotations."""
    type_builtin: Treesitter = Treesitter(fg=R.magenta)
    """Builtin types."""
    type_definition: Treesitter = Treesitter(fg=R.violet)
    """Identifiers in type definitions (e.g., typedef <type> <identifier>)."""
    operator: Treesitter = Treesitter(fg=R.azure)
    """Symbolic operators, (e.g., `+` and `*`)."""
    property: Treesitter = Treesitter(fg=R.yellow)
    """The key in key, value pairs."""

    # functions
    function: Treesitter = Treesitter(fg=R.blue)
    """Function definitions."""
    function_builtin: Treesitter = Treesitter(fg=R.magenta)
    """Functions provided by the stdlib."""
    function_call: Treesitter = Treesitter(link=Link.function)
    """Function calls (e.g., `myfunc(x)`)."""
    function_macro: Treesitter = Treesitter(fg=R.orange)
    """Preprocessor macros."""
    function_method: Treesitter = Treesitter(fg=R.blue)
    """Method definitions."""
    function_method_call: Treesitter = Treesitter(link=Link.function_method)
    """Method calls."""
    constructor: Treesitter = Treesitter(fg=R.azure)
    """Constructor calls and definitions."""

    keyword: Treesitter = Treesitter(fg=R.violet)
    """Keywords not fitting into specific categories."""
    keyword_coroutine: Treesitter = Treesitter(fg=R.magenta)
    """Keywords related to async (e.g., `go` in Go, `async/await` in Python)."""
    keyword_function: Treesitter = Treesitter(fg=R.violet, italic=True)
    """Keywords that define a function (e.g. `func` in Go, `def` in Python)."""
    keyword_operator: Treesitter = Treesitter(fg=R.azure)
    """Operators that are english words (e.g., `and`, `or`)."""
    keyword_import: Treesitter = Treesitter(fg=R.rose)
    """Keywords for including or exporting modules (e.g., `import` in Python)."""
    keyword_type: Treesitter = Treesitter(fg=R.rose, italic=True)
    """Keywords describing namespaces and composite types (e.g. `struct`, `enum`)."""
    keyword_modifier: Treesitter = Treesitter(fg=R.mint)
    """Keywords modifying other constructs (e.g. `const`, `static`, `public`)."""
    keyword_repeat: Treesitter = Treesitter(fg=R.lime)
    """Keywords related to loops (e.g., `for`, `while`)."""
    keyword_return: Treesitter = Treesitter(fg=R.red)
    """Keywords like `return` and `yield`."""
    keyword_debug: Treesitter = Treesitter(fg=R.red)
    """Keywords related to debugging."""
    keyword_exception: Treesitter = Treesitter(fg=R.violet)
    """Keywords related to exception handling (e.g., `throw`, `catch`)."""
    keyword_conditional: Treesitter = Treesitter(fg=R.mint)
    """Keywords related to conditional logic (e.g., `if`, `else`)."""
    keyword_conditional_ternary: Treesitter = Treesitter(fg=R.mint)
    """Ternary operator (e.g., `?`, `;`)."""
    keyword_directive: Treesitter = Treesitter(fg=R.yellow)
    """Various preprocessor directives and shebangs."""
    keyword_directive_define: Treesitter = Treesitter(fg=R.orange)
    """Preprocessor definition directives."""

    markup_strong: Treesitter = Treesitter(bold=True)
    """Bold text in markup."""
    markup_italic: Treesitter = Treesitter(italic=True)
    """Italic text in markup."""
    markup_strikethrough: Treesitter = Treesitter(strikethrough=True)
    """Struckthrough text in markup."""
    markup_underline: Treesitter = Treesitter(underline=True)
    """Underlined text in markup."""
    markup_heading: Treesitter = Treesitter(underdouble=True)
    """Headings and titles, including markers (e.g, `#` in markdown)."""
    markup_heading_1: Treesitter = Treesitter(fg=R.red, bold=True)
    """Top-level heading."""
    markup_heading_2: Treesitter = Treesitter(fg=R.orange, bold=True)
    """Second-level heading."""
    markup_heading_3: Treesitter = Treesitter(fg=R.yellow, bold=True)
    """Third-level heading."""
    markup_heading_4: Treesitter = Treesitter(fg=R.lime, bold=True)
    """Fourth-level heading."""
    markup_heading_5: Treesitter = Treesitter(fg=R.green, bold=True)
    """Fifth-level heading."""
    markup_heading_6: Treesitter = Treesitter(fg=R.mint, bold=True)
    """Sixth-level heading."""
    markup_quote: Treesitter = Treesitter(fg=R.azure, italic=True)
    """Block quotes."""
    markup_math: Treesitter = Treesitter(fg=R.green)
    """Math environments (e.g., `$` in LaTeX)."""
    markup_link: Treesitter = Treesitter(fg=R.blue, underdashed=True)
    """Text references, footnotes, citations, etc."""
    markup_link_label: Treesitter = Treesitter(fg=R.yellow)
    """Link, reference descriptions."""
    markup_link_url: Treesitter = Treesitter(fg=R.blue, underline=True)
    """URL-style links."""
    markup_raw: Treesitter = Treesitter(fg=R.yellow)
    """Literal or verbatim text (e.g., inline code)."""
    markup_raw_block: Treesitter = Treesitter(fg=R.yellow)
    """Literal or verbatim text as a standalone block."""
    markup_list: Treesitter = Treesitter(fg=R.violet)
    """List markers (e.g., `-`)."""
    markup_list_checked: Treesitter = Treesitter(fg=R.green)
    """Checked todo-style list markers (e.g., `[x]`)."""
    markup_list_unchecked: Treesitter = Treesitter(fg=R.yellow)
    """Unchecked todo-style list markers (e.g., `[ ]`)."""

    punctuation_delimiter: Treesitter = Treesitter(fg=R.magenta)
    """Delimiters such as `;`, `.` and `,`."""
    punctuation_bracket: Treesitter = Treesitter(fg=R.red)
    """Brackets (e.g., `()`, `{}`, `[]`)."""
    punctuation_special: Treesitter = Treesitter(fg=R.rose)
    """Special symbols (e.g., `{}` in string interpolation.)"""

    # strings
    string: Treesitter = Treesitter(fg=R.cyan)
    """String literals."""
    string_escape: Treesitter = Treesitter(fg=R.red)
    """Escape characters in a string."""
    string_documentation: Treesitter = Treesitter(fg=R.base10)
    """Strings representing documentation such as Python docstrings."""
    string_regexp: Treesitter = Treesitter(fg=R.orange)
    """Regular expressions."""
    string_special: Treesitter = Treesitter(fg=R.violet)
    """Special strings such as dates."""
    string_special_symbol: Treesitter = Treesitter(fg=R.violet)
    """Symbols or atoms."""
    string_special_path: Treesitter = Treesitter(fg=R.blue)
    """Filename strings."""
    string_special_url: Treesitter = Treesitter(fg=R.blue, underline=True)
    """String URIs (e.g., hyperlinks.)"""

    # tags
    tag: Treesitter = Treesitter(fg=R.violet)
    """XML-style tag names."""
    tag_builtin: Treesitter = Treesitter(fg=R.magenta)
    """Builtin tag names (e.g., HTML tags)."""
    tag_attribute: Treesitter = Treesitter(fg=R.yellow)
    """XML-style tag attributes."""
    tag_delimiter: Treesitter = Treesitter(fg=R.red)
    """XML-style tag delimiters."""

    # variables
    variable: Treesitter = Treesitter(fg=R.azure)
    """Variable Names."""
    variable_builtin: Treesitter = Treesitter(fg=R.rose, italic=True)
    """Builtin ariable Names, e.g., `this` or `self`."""
    variable_parameter: Treesitter = Treesitter(fg=R.orange)
    """Parameters of a function."""
    variable_parameter_builtin: Treesitter = Treesitter(fg=R.magenta)
    """Special parameters of a function, e.g., `_` and `it`."""
    variable_member: Treesitter = Treesitter(fg=R.yellow)
    """Object and struct fields."""
    # end: treesitter

    # begin: diagnostic
    diagnostic_deprecated: Diagnostic = Diagnostic(fg=R.rose)
    """Deprecated or obsolete code in diagnostics."""
    diagnostic_unnecessary: Diagnostic = Diagnostic(fg=R.base05)
    """Unreachable code in diagnostics."""

    diagnostic_error: Diagnostic = Diagnostic(fg=R.red)
    """Used as the base highlight group. Other groups link to this by default."""
    diagnostic_warn: Diagnostic = Diagnostic(fg=R.orange)
    """Used as the base highlight group. Other groups link to this by default."""
    diagnostic_info: Diagnostic = Diagnostic(fg=R.yellow)
    """Used as the base highlight group. Other groups link to this by default."""
    diagnostic_hint: Diagnostic = Diagnostic(fg=R.green)
    """Used as the base highlight group. Other groups link to this by default."""
    diagnostic_ok: Diagnostic = Diagnostic(fg=R.mint)
    """Used as the base highlight group. Other groups link to this by default."""

    dianostic_floating_error: Diagnostic = Diagnostic(link=Link.diagnostic_error)
    dianostic_floating_warn: Diagnostic = Diagnostic(link=Link.diagnostic_warn)
    dianostic_floating_info: Diagnostic = Diagnostic(link=Link.diagnostic_info)
    dianostic_floating_hint: Diagnostic = Diagnostic(link=Link.diagnostic_hint)
    dianostic_floating_ok: Diagnostic = Diagnostic(link=Link.diagnostic_ok)

    dianostic_sign_error: Diagnostic = Diagnostic(link=Link.diagnostic_error)
    dianostic_sign_warn: Diagnostic = Diagnostic(link=Link.diagnostic_warn)
    dianostic_sign_info: Diagnostic = Diagnostic(link=Link.diagnostic_info)
    dianostic_sign_hint: Diagnostic = Diagnostic(link=Link.diagnostic_hint)
    dianostic_sign_ok: Diagnostic = Diagnostic(link=Link.diagnostic_ok)

    dianostic_underline_error: Diagnostic = Diagnostic(
        link=Link.diagnostic_error, underline=True
    )
    dianostic_underline_warn: Diagnostic = Diagnostic(
        link=Link.diagnostic_warn, underline=True
    )
    dianostic_underline_info: Diagnostic = Diagnostic(
        link=Link.diagnostic_info, underline=True
    )
    dianostic_underline_hint: Diagnostic = Diagnostic(
        link=Link.diagnostic_hint, underline=True
    )
    dianostic_underline_ok: Diagnostic = Diagnostic(
        link=Link.diagnostic_ok, underline=True
    )

    dianostic_virtual_text_error: Diagnostic = Diagnostic(link=Link.diagnostic_error)
    dianostic_virtual_text_warn: Diagnostic = Diagnostic(link=Link.diagnostic_warn)
    dianostic_virtual_text_info: Diagnostic = Diagnostic(link=Link.diagnostic_info)
    dianostic_virtual_text_hint: Diagnostic = Diagnostic(link=Link.diagnostic_hint)
    dianostic_virtual_text_ok: Diagnostic = Diagnostic(link=Link.diagnostic_ok)

    dianostic_virtual_lines_error: Diagnostic = Diagnostic(link=Link.diagnostic_error)
    dianostic_virtual_lines_warn: Diagnostic = Diagnostic(link=Link.diagnostic_warn)
    dianostic_virtual_lines_info: Diagnostic = Diagnostic(link=Link.diagnostic_info)
    dianostic_virtual_lines_hint: Diagnostic = Diagnostic(link=Link.diagnostic_hint)
    dianostic_virtual_lines_ok: Diagnostic = Diagnostic(link=Link.diagnostic_ok)
    # end: diagnostic

    # begin: lsp
    lsp_reference_text: Lsp = Lsp()
    """Used for highlighting "text" references"""
    lsp_reference_read: Lsp = Lsp()
    """Used for highlighting "read" references"""
    lsp_reference_write: Lsp = Lsp()
    """Used for highlighting "write" references"""
    lsp_reference_target: Lsp = Lsp()
    """Used for highlighting reference targets (e.g., in a however range)."""
    lsp_inlay_hint: Lsp = Lsp()
    lsp_code_lens_separator: Lsp = Lsp()
    lsp_signature_active_parameter: Lsp = Lsp()

    # Semantic highlight provided by lsps. neovim `:h lsp-highlight`
    lsp_type_class: Lsp = Lsp()
    """Reference a class type."""
    lsp_type_comment: Lsp = Lsp()
    """Tokens that represent a comment."""
    lsp_type_decorator: Lsp = Lsp()
    """Reference an annotation or decorator."""
    lsp_type_enum: Lsp = Lsp()
    """Reference to an enumeration type."""
    lsp_type_enum_member: Lsp = Lsp()
    """Reference to an enumeration property, constant, or member."""
    lsp_type_event: Lsp = Lsp()
    """Reference to an event property."""
    lsp_type_function: Lsp = Lsp(link=Link.function)
    lsp_type_interface: Lsp = Lsp()
    lsp_type_keyword: Lsp = Lsp()
    lsp_type_macro: Lsp = Lsp()
    lsp_type_method: Lsp = Lsp()
    lsp_type_modifier: Lsp = Lsp()
    lsp_type_namespace: Lsp = Lsp()
    lsp_type_number: Lsp = Lsp()
    lsp_type_operator: Lsp = Lsp()
    lsp_type_parameter: Lsp = Lsp()
    lsp_type_property: Lsp = Lsp()
    lsp_type_regexp: Lsp = Lsp(link=Link.string_regexp)
    lsp_type_string: Lsp = Lsp()
    lsp_type_struct: Lsp = Lsp()
    lsp_type_type: Lsp = Lsp()
    lsp_type_type_parameter: Lsp = Lsp()
    lsp_type_variable: Lsp = Lsp()
    lsp_mod_abstract: Lsp = Lsp()
    """Types and methods that are abstract."""
    lsp_mod_async: Lsp = Lsp()
    """Functions that are marked async."""
    lsp_mod_declaration: Lsp = Lsp()
    """Declaration of symbols."""
    lsp_mod_default_library: Lsp = Lsp()
    """Symbols that are part of the standard library."""
    lsp_mod_definition: Lsp = Lsp()
    """Definitions of files, (e.g., in header files)."""
    lsp_mod_deprecated: Lsp = Lsp()
    """Symbols that should no longer be used."""
    lsp_mod_documentation: Lsp = Lsp()
    """Occurrences of symbols in documentation."""
    lsp_mod_modification: Lsp = Lsp()
    """Variable references where the variable is assigned to."""
    lsp_mod_readonly: Lsp = Lsp()
    """Readonly variables and fields (constants)."""
    lsp_mod_static: Lsp = Lsp()
    """Static class members."""

    # begin: neovim groups.
    # Some might have had their names changed slightly, as many of these groups
    # are more general purpose and would apply to any particular application.
    # From neovim `h: highlight-groups`
    # syntax groups

    conceal: UI = UI(fg=R.base08)
    """Placeholder characters substituted for concealed text."""

    color_column: UI = UI(bg=R.base02)
    """Used for the columns such as max line length guide.."""
    completion_match_insert: UI = UI(fg=R.green)
    """Matched text of the currently inserted completion."""
    # l_cursor: UI = UI()
    # """Character under cursor when |language-mapping| is used (see 'guicursor')."""
    cursor_column: UI = UI(bg=R.base02)
    """Screen column at the cursor."""
    cursor_line: UI = UI(bg=R.base02)
    """Screen line (row) at the cursor."""
    cursor_line_number: UI = UI(fg=R.base10, bg=R.base02)
    """The line number gutter item on the current cursor line."""
    cursor_line_fold: UI = UI()
    """Like `fold_column` when 'cursorline' is set for the cursor line."""
    cursor_line_gutter: UI = UI()
    """Like `sign_column` when 'cursorline' is set for the cursor line."""
    # directory: UI = UI()
    # """Directory names (and other special names in listings)."""
    # diff_add: UI = UI()
    # """Diff mode: Added line. |diff.txt|"""
    # diff_change: UI = UI()
    # """Diff mode: Changed line. |diff.txt|"""
    # diff_delete: UI = UI()
    # """Diff mode: Deleted line. |diff.txt|"""
    # diff_text: UI = UI()
    # """Diff mode: Changed text within a changed line. |diff.txt|"""
    end_of_buffer: UI = UI(link=Link.non_text)
    """Filler lines (~) after the end of the buffer."""
    window_separator: UI = UI(bg=R.base15)
    """Separators between window splits."""
    folded_line: UI = UI()
    """Line used for closed folds."""
    fold_column: UI = UI()
    """'foldcolumn'"""
    gutter: UI = UI(bg=R.base02)
    """Column where signs (e.g., git, error checks)  are displayed."""
    substitute: UI = UI(bg=R.hl_green, fg=R.black)
    """Substituted text in find / replace."""
    line_number: UI = UI(bg=R.base02, fg=R.base10)
    """Line numbers in sidebar. Applies to all numbers."""
    line_number_above: UI = UI(bg=R.base02, fg=R.base09)
    """Line number above the cursor line. In vim, only relevant with
    with relative numbering."""
    line_number_below: UI = UI(bg=R.base02, fg=R.base09)
    """Line number below the cursor line. In vim, only relevant with
    relative line numbering."""
    matched_bracket: UI = UI(fg=R.yellow)
    """Character under the cursor or just before it, if it is a paired bracket"""

    message: UI = UI(bg=R.base03)
    """Area for messages and command-line. Vim's MsgArea."""
    message_error: Style = Style(link=Link.diagnostic_error)
    """Error messages / notifications (e.g., on the command line)."""
    message_warn: Style = Style(link=Link.diagnostic_warn)
    """Warning messages / notifications (e.g., on the command line)."""
    message_mode: Style = Style(fg=R.orange)
    """For modal editors, the mode display (e.g., vim `-- INSERT --`)."""
    message_more: UI = UI(fg=R.yellow)
    """More prompt. Vim's MoreMsg."""
    message_question: UI = UI(fg=R.green)
    """|hit-enter| prompt and yes/no questions."""
    message_separator: UI = UI()
    """Separator for scrolled messages |msgsep|."""
    non_text: UI = UI(fg=R.base08)
    """'@' at the end of the window, characters from 'showbreak' and other
    characters that do not really exist in the text
    (e.g., ">" displayed when a double-wide character doesn't fit."""
    # normal: UI = UI(fg=R.b11, bg=R.b0)
    # """Normal text. Primary foreground and background."""
    floating_window: UI = UI(link=Link.main, bg=R.base02)
    """Normal text in floating windows."""
    floating_window_border: UI = UI()
    """Border of floating windows."""
    floating_window_title: UI = UI()
    """Title of floating windows."""
    floating_window_footer: UI = UI()
    """Footer of floating windows."""
    # pmenu: UI = UI()
    # """Popup menu: Normal item."""
    # pmenu_sel: UI = UI()
    # """Popup menu: Selected item. Combined with |hl-Pmenu|."""
    # pmenu_kind: UI = UI()
    # """Popup menu: Normal item "kind"."""
    # pmenu_kind_sel: UI = UI()
    # """Popup menu: Selected item "kind"."""
    # pmenu_extra: UI = UI()
    # """Popup menu: Normal item "extra text"."""
    # pmenu_extra_sel: UI = UI()
    # """Popup menu: Selected item "extra text"."""
    # pmenu_sbar: UI = UI()
    # """Popup menu: Scrollbar."""
    # pmenu_thumb: UI = UI()
    # """Popup menu: Thumb of the scrollbar."""
    # pmenu_match: UI = UI()
    # """Popup menu: Matched text in normal item. Combined with |hl-Pmenu|."""
    # pmenu_match_sel: UI = UI()
    # """Popup menu: Matched text in selected item."""
    # quick_fix_line: UI = UI()
    # """Current |quickfix| item in the quickfix window."""
    snippet_tabstop: UI = UI()
    """Tabstops in snippets. |vim.snippet|"""
    special_key: UI = UI()
    """Unprintable characters: Text displayed differently from what it really is."""
    status_line: UI = UI(bg=R.base03, fg=R.base10)
    """Status line of current window."""
    status_line_unfocused: UI = UI(fg=R.base09, bg=R.base03)
    """Status lines of not-current windows."""
    tab_line: UI = UI()
    """Tab pages line, not active tab page label."""
    tab_line_fill: UI = UI()
    """Tab pages line, where there are no labels."""
    tab_line_sel: UI = UI()
    """Tab pages line, active tab page label."""
    # visual_nos: UI = UI()
    # """Visual mode selection when vim is "Not Owning the Selection"."""
    whitespace: UI = UI(fg=R.base08)
    """"Tokens like non-breaking space, trailing whitespace, etc."""
    wild_menu: UI = UI()
    """Current match in 'wildmenu' completion."""
    window_bar: UI = UI()
    """Window bar of current window."""
    window_bar_unfocused: UI = UI()
    """Window bar of not-current windows."""
    menu: UI = UI(bg=R.base03, fg=R.base11)
    """Current menus and toolbars."""
    scrollbar: UI = UI(bg=R.base04)
    """Current main window's scrollbars."""
    search: UI = UI(bg=R.hl_yellow, fg=R.black)
    """Last search pattern highlighting"""
    search_current_match: UI = UI(bg=R.hl_blue)
    """Current match for the last search pattern."""
    # TODO: Do we want this?
    search_incremental: UI = UI(bg=R.hl_blue, fg=R.black)
    """Incremental search in find / replace.."""
    spell_bad: Style = Style(fg=R.red, undercurl=True)
    """Word that is not recognized by the spellchecker."""
    spell_cap: Style = Style(fg=R.orange, undercurl=True)
    """Word that should start with a capital."""
    spell_local: Style = Style(fg=R.yellow, underdotted=True)
    """Word that is recognized one that used in another region."""
    spell_rare: Style = Style(fg=R.lime, underdotted=True)
    """Word that is recognized is hardly ever used."""

    # terminal for e.g., embedded terminal emulators in neovim
    terminal_cursor: Terminal = Terminal(link=Link.cursor)
    """Cursor in a focused terminal."""
    terminal_status_line: Terminal = Terminal(link=Link.status_line)
    """Status line of |terminal| window."""
    terminal_status_line_unfocused: UI = UI(link=Link.status_line_unfocused)
    """Status line of non-current terminal windows."""

    def __hash__(self) -> int:  # noqa: D105
        return super().__hash__()


class AbstractTheme(ThemeBlocks, ThemeMetadata):
    """Theme style blocks and highlight groups.

    Each Style field defines a style or color to apply to a particular element.
    For example, UI interfaces, code syntax blocks, etc.
    """

    def model_post_init(self, context, /) -> None:
        """Set field names to each node."""
        for key, val in self:
            if isinstance(val, BaseStyle):
                val._field = key
        return super().model_post_init(context)

    def make(self, palette: Palette) -> Theme:
        """Resolve an abstract theme with refs into a concrete universal theme.

        Args:
            palette: A palette containing color definitions.

        Returns:
            A universal, concrete Theme referencing the .

        """
        return make(self, palette)

    def __hash__(self) -> int:  # noqa: D105
        return super().__hash__()

    @staticmethod
    def _get(palette: Palette, path: R | None) -> ColorField | None:
        return palette[path] if path else None

    def _resolve_links(self, node: BaseStyle) -> BaseStyle:
        """Resolve and merge a chain of linked Style instances.

        The merge order is root-most -> ... -> input instance.

        Args:
            node: A Style node to resolve its links against.

        Returns:
            A merged Style instance.

        Raises:
            ValueError: If a circular link chain is detected.

        """
        # Early escape
        if node.link is None:
            return node

        # Walk the link chain from the provided instance towards the root
        # Use the fact dicts are order preserving or use a set and list.
        key = node._field
        seen: dict[str, BaseStyle] = {}
        while True:
            if key in seen:
                # produce cycle trace for easier debugging
                cycle_trace = " -> ".join([*seen.keys(), key])
                raise ValueError(f"Circular links detected: {cycle_trace}")
            seen[key] = node

            if (link := node.link) is None:
                break
            node = self[link]
            key = link

        # Merge from root-most to leaf (earlier -> later).
        merged: BaseStyle = BaseStyle()
        for part in reversed(seen.values()):
            merged |= part

        return merged

    def _resolve_node(self, palette: Palette, node: BaseStyle) -> BaseStyle:
        """Resolve a style reference against the instance.

        Links are resolved, where the input instance is merged into the linked
        reference.

        Returns:
            A concrete style element.

        """
        node = self._resolve_links(node)
        resolved_fields = {
            k: palette[v] if v in R else v
            for k, v in node
            if k in node.model_fields_set
        }
        out = node.model_validate(resolved_fields)
        out._field = node._field
        return out


class Theme(ThemeBlocks, ThemeMetadata):
    """A universal cross-application intermediate theme representation.

    Each field contains color values derived from the underlying palette.

    Passed in to any application theme template whose context specifies
    a single palette.
    """

    palette: Palette

    def __hash__(self) -> int:  # noqa: D105
        return super().__hash__()

    def meta(self) -> Iterator[tuple[str, str]]:
        """Theme and palette metadata.

        Yields:
            Metadata field, value pairs in the theme and palette.

        """
        for key in ThemeMetadata.model_fields:
            yield key, self[key]
        for key, val in self.palette.meta():
            yield f"palette.{key}", val

    @property
    def fullname(self) -> str:
        """Name of the theme and underlying palette."""
        return f"{self.name}-{self.palette.name}"

    def styles(self) -> Iterator[tuple[str, BaseStyle]]:
        """Yield Style items.

        Yields:
            Field name and Style instance.

        """
        for key, val in self:
            if isinstance(val, BaseStyle) and not isinstance(val, Color) and val:
                yield key, val

    def colors(self) -> Iterator[tuple[str, Color | ColorField]]:
        """Yield simple color reference items.

        Also yields the underlying palette colors.

        Yields:
            Field name and Ref instance.

        """
        for key, val in self:
            if isinstance(val, Color) and val:
                yield key, val
        for key, val in self.palette.colors():
            yield f"palette.{key}", val


class ThemeCollection(BaseNode):
    """A collection of themes."""

    themes: tuple[Theme, ...]

    def __hash__(self) -> int:  # noqa: D105
        return super().__hash__()


@cache
def make(theme: AbstractTheme, palette: Palette) -> Theme:
    """Resolve an abstract theme with refs into a concrete universal theme.

    Args:
        palette: A palette containing color definitions.
        theme: An abstract theme instance.

    Returns:
        A universal, concrete Theme referencing the .

    """
    data: dict = {
        k: theme._resolve_node(palette, v) if k in ThemeBlocks.model_fields else v
        for k, v in theme
    }
    return Theme(
        palette=palette,
        **data,
    )


# def _to_camel(key: str) -> str:
#     return "".join(x.title() for x in key.split("_"))
#
#
# def stub_to_neovim(theme: Theme):
#     # Experiments with some "neovim" mapping logic.
#     # casing doesn't matter for :
#     mapping: dict[str, str] = {
#         "our field": "neovim field",
#     }
#
#     out: dict[str, Style] = {}
#     for key, val in theme.diagnostic:
#         out["Diagnostic" + _to_camel(key)] = val
#     for key, val in theme.lsp:
#         # some keys camel, some not
#         if key.startswith(("refer", "inlay", "code")):
#             out["Lsp" + _to_camel(key)] = val
#         else:
#             out["@" + key[4:].replace('_', ',')]
#     for key, val in theme.ts:
#         out["@" + key[3:].replace('_', '.')]
#
#     # vs a flat implicit ns approach, with treesitter not prefixed but
#     # namespace models
#     # defined. Has advantage that link refs are of the form key instead of having
#     # to parse a "."
#     for key, val in theme:
#         if not isinstance(val, Style):
#             continue
#         if key.startswith(
#             ("diagnostic", "lsp_refer", "lsp_inlay", "lsp_code", "lsp_sig")):
#             out[_to_camel(key)] = val
#         elif key.startswith("lsp") or key in TreeSitter.model_fields:
#             out["@" + key.replace("_", ".")] = val
#         elif key.startswith("ts"):
#             # optional case if instead of TreeSitter ns defined, just use `ts_`
#             # having ts_comment seems awkard though, so maybe keep ts ns.
#             out["@" + key.strip("ts_").replace("_", ".")] = val
#         elif key in mapping:
#             out[mapping[key]] = val
#
#     # [x] Probably the most ergonomic
#     # A third approach is to use subclasses of Style such as DiagnosticStyle,
#     # TreeSitter, etc that that each Theme node's type tells you what group it
#     # is in.
#     # - Avoids having to explicitly namespace things like `ts_comment`
#     # - Avoids having to define separate classes of group elements.
#     # - Each node has explicit group in its type
#     # Would need to define BaseNode.__ror__(self, left) (left | self)
#     # so that right type is used.
#     for key, val in theme:
#         if not isinstance(val, Style):
#             continue
#         if isinstance(val, Treesitter):
#             ...
#     return out
#
