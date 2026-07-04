"""Abstract and universal theme models.

An abstract theme serves as a collection of references to palette colors.
When the references are resolved against a specific palette, a universal
application agnostic theme results.
"""

from functools import cache
from typing import TYPE_CHECKING, override

from pydantic import Field

from hadalized.base import BaseNode
from hadalized.palette import Hue, Palette
from hadalized.style import ColorString, Style

if TYPE_CHECKING:
    from collections.abc import Iterator


class ThemeMetadata(BaseNode):
    """Theme metadata fields that are not style blocks."""

    name: str = Field(
        default="default",
        examples=["default", "alt1"],
    )
    """Prefixed to a palette name to generate full theme name.
    This name is typically used for generated application theme files."""
    desc: str = "Hadalized default theme."
    version: str = "0.1"
    url: str = "https://www.github.com/hadalized/hadalized"


class ThemeColors(BaseNode):
    """Map of name to palette field reference or value.

    When defining a theme in a configuration, the field values should be
    a Hue enum.

    """

    ansi00: ColorString = Hue.black
    ansi01: ColorString = Hue.red
    ansi02: ColorString = Hue.green
    ansi03: ColorString = Hue.yellow
    ansi04: ColorString = Hue.blue
    ansi05: ColorString = Hue.magenta
    ansi06: ColorString = Hue.cyan
    ansi07: ColorString = Hue.silver
    ansi08: ColorString = Hue.smoke
    ansi09: ColorString = Hue.rose
    ansi10: ColorString = Hue.lime
    ansi11: ColorString = Hue.orange
    ansi12: ColorString = Hue.azure
    ansi13: ColorString = Hue.violet
    ansi14: ColorString = Hue.mint
    ansi15: ColorString = Hue.white


class Theme(BaseNode):
    """Generic style blocks and highlight groups.

    Each Style field defines a styling to apply to a particular block or
    element in an application theme. For example, UI interfaces, code syntax
    blocks, etc.

    An instance can be either abstract or concrete. The color leaves
    of an abstract instance contain references to palette fields. The leaves
    of a concrete theme contain the actual palette fields (e.g., hex codes).

    vscode reference

    - https://code.visualstudio.com/api/references/theme-color
    - https://gist.github.com/AndreasBackx/ab5c7df0ef214a798cfa8fdeaf59197f
    - https://gist.github.com/dcts/5b2af4c8b6918e7d35c4121f11d49fb1
    """

    meta: ThemeMetadata = ThemeMetadata()
    """Theme metadata such as name and version."""
    colors: ThemeColors = ThemeColors()
    """Map of name to palette field reference or value."""

    # Elements corresponding to fundamental foregrounds and backgrounds.
    main: Style = Style(fg=Hue.base11, bg=Hue.base00)
    """Main background and foreground. Similar to vim's Normal group."""
    unfocused: Style = Style(fg=Hue.base11, bg=Hue.base00)
    """Normal text in inactive / non-current / unfocused windows."""

    cursor: Style = Style(fg=Hue.base10, bg=Hue.base05, border=Hue.blue)
    """Cursor style (e.g., in terminal emulators).

    Note that in neovim in wezterm, it appears this value is inherited
    from the wezterm settings
    """
    selection: Style = Style(bg=Hue.base03)
    """Selected areas, e.g., vim's Visual selection."""

    # begin: treesitter
    attribute: Style = Style(fg=Hue.orange)
    """Attribute annotations (e.g., Python decorators and Rust lifetimes)."""
    attribute_builtin: Style = Style(fg=Hue.orange, italic=True)
    """Builtin annotations (e.g., `@property` in Python)."""
    diff_delta: Style = Style(fg=Hue.yellow)
    """Changed text for diff files,"""
    diff_minus: Style = Style(fg=Hue.red)
    """Deleted text for diff files,"""
    diff_plus: Style = Style(fg=Hue.green)
    """Added text for diff files,"""
    comment: Style = Style(fg=Hue.base10)
    """Line and block comments."""
    comment_special: Style = Style(fg=Hue.magenta)
    """Special elements inside of comments."""
    comment_documentation: Style = Style(link="string_documentation")
    """Comments that document code."""
    comment_error: Style = Style(fg=Hue.red)
    """Error type comments (e.g., `ERROR`, `FIXME`)."""
    comment_warning: Style = Style(fg=Hue.orange)
    """Warning type comments (e.g., `WARNING`, `FIX`, `HACK`)."""
    comment_todo: Style = Style(fg=Hue.yellow)
    """Todo type comments (e.g., `TODO`, `WIP`)."""
    comment_note: Style = Style(fg=Hue.blue)
    """Note type comments (e.g., `NOTE`, `INFO`, `xxx`)."""

    constant: Style = Style(fg=Hue.magenta)
    """Constant identifiers."""
    constant_builtin: Style = Style(fg=Hue.magenta, bold=True)
    """Builtin constant identifiers."""
    constant_macro: Style = Style(fg=Hue.magenta, bold=True)
    """Constants defined by a preprocessor."""

    label: Style = Style(fg=Hue.orange)
    """GOTO and other labels, including heredoc labels."""
    module: Style = Style(fg=Hue.yellow)
    """Modules or namespace."""
    module_builtin: Style = Style(fg=Hue.orange, italic=True)
    """Builtin or stdlib modules and namespaces."""

    # Basic types.
    character: Style = Style(fg=Hue.azure)
    """Character literals."""
    character_special: Style = Style(fg=Hue.red)
    """Special characters, (e.g., wildcards)."""
    boolean: Style = Style(fg=Hue.magenta)
    """Boolean literals."""
    number: Style = Style(fg=Hue.magenta)
    """Numeric literals."""
    number_float: Style = Style(fg=Hue.rose)
    """Floating point literals."""
    type: Style = Style(fg=Hue.violet)
    """Type or class definitions and annotations."""
    type_builtin: Style = Style(fg=Hue.violet, italic=True)
    """Builtin types."""
    type_definition: Style = Style(fg=Hue.violet)
    """Identifiers in type definitions (e.g., typedef <type> <identifier>)."""
    operator: Style = Style(fg=Hue.green)
    """Symbolic operators, (e.g., `+` and `*`)."""
    prop: Style = Style(fg=Hue.yellow)
    """The key in key, value pairs."""

    # functions
    function: Style = Style(fg=Hue.blue)
    """Function definitions."""
    function_builtin: Style = Style(fg=Hue.blue, italic=True)
    """Functions provided by the stdlib."""
    function_call: Style = Style(fg=Hue.blue)
    """Function calls (e.g., `myfunc(x)`)."""
    function_macro: Style = Style(fg=Hue.orange)
    """Preprocessor macros."""
    function_method: Style = Style(fg=Hue.blue)
    """Method definitions."""
    function_method_call: Style = Style(fg=Hue.blue)
    """Method calls."""
    constructor: Style = Style(fg=Hue.blue)
    """Constructor calls and definitions."""

    keyword: Style = Style(fg=Hue.violet)
    """Keywords not fitting into specific categories."""
    keyword_coroutine: Style = Style(fg=Hue.magenta)
    """Keywords related to async (e.g., `go` in Go, `async/await` in Python)."""
    keyword_function: Style = Style(fg=Hue.violet, italic=True)
    """Keywords that define a function (e.g. `func` in Go, `def` in Python)."""
    keyword_operator: Style = Style(fg=Hue.azure)
    """Operators that are english words (e.g., `and`, `or`)."""
    keyword_import: Style = Style(fg=Hue.orange, italic=True)
    """Keywords for including or exporting modules (e.g., `import` in Python)."""
    keyword_type: Style = Style(fg=Hue.magenta, italic=True)
    """Keywords describing namespaces and composite types (e.g. `struct`, `enum`)."""
    keyword_modifier: Style = Style(fg=Hue.mint, italic=True)
    """Keywords modifying other constructs (e.g. `const`, `static`, `public`)."""
    keyword_repeat: Style = Style(fg=Hue.lime, italic=True)
    """Keywords related to loops (e.g., `for`, `while`)."""
    keyword_return: Style = Style(fg=Hue.red, italic=True)
    """Keywords like `return` and `yield`."""
    keyword_debug: Style = Style(fg=Hue.red)
    """Keywords related to debugging."""
    keyword_exception: Style = Style(fg=Hue.magenta, italic=True)
    """Keywords related to exception handling (e.g., `throw`, `catch`)."""
    keyword_conditional: Style = Style(fg=Hue.orange, italic=True)
    """Keywords related to conditional logic (e.g., `if`, `else`)."""
    keyword_conditional_ternary: Style = Style(fg=Hue.red, italic=True)
    """Ternary operator (e.g., `?`, `;`)."""
    keyword_directive: Style = Style(fg=Hue.yellow)
    """Various preprocessor directives and shebangs."""
    keyword_directive_define: Style = Style(fg=Hue.orange)
    """Preprocessor definition directives."""

    markup_strong: Style = Style(bold=True)
    """Bold text in markup."""
    markup_italic: Style = Style(italic=True)
    """Italic text in markup."""
    markup_strikethrough: Style = Style(strikethrough=True)
    """Struckthrough text in markup."""
    markup_underline: Style = Style(underline=True)
    """Underlined text in markup."""
    markup_heading: Style = Style(bg=Hue.base15, fg=Hue.base00)
    """Headings and titles, including markers (e.g, `#` in markdown)."""
    markup_heading_1: Style = Style(bg=Hue.base15, fg=Hue.base00)
    """Top-level heading."""
    markup_heading_2: Style = Style(bg=Hue.base15, fg=Hue.base00)
    """Second-level heading."""
    markup_heading_3: Style = Style(bg=Hue.base15, fg=Hue.base00)
    """Third-level heading."""
    markup_heading_4: Style = Style(bg=Hue.base15, fg=Hue.base00)
    """Fourth-level heading."""
    markup_heading_5: Style = Style(bg=Hue.base15, fg=Hue.base00)
    """Fifth-level heading."""
    markup_heading_6: Style = Style(bg=Hue.base15, fg=Hue.base00)
    """Sixth-level heading."""
    markup_quote: Style = Style(fg=Hue.azure, italic=True)
    """Block quotes."""
    markup_math: Style = Style(fg=Hue.green)
    """Math environments (e.g., `$` in LaTeX)."""
    markup_link: Style = Style(fg=Hue.blue, underdashed=True)
    """Text references, footnotes, citations, etc."""
    markup_link_label: Style = Style(fg=Hue.yellow)
    """Link, reference descriptions."""
    markup_link_url: Style = Style(fg=Hue.blue, underline=True)
    """URL-style links."""
    markup_raw: Style = Style(fg=Hue.yellow)
    """Literal or verbatim text (e.g., inline code)."""
    markup_raw_block: Style = Style(fg=Hue.yellow)
    """Literal or verbatim text as a standalone block."""
    markup_list: Style = Style(fg=Hue.violet)
    """List markers (e.g., `-`)."""
    markup_list_checked: Style = Style(fg=Hue.green)
    """Checked todo-style list markers (e.g., `[x]`)."""
    markup_list_unchecked: Style = Style(fg=Hue.yellow)
    """Unchecked todo-style list markers (e.g., `[ ]`)."""

    punctuation_delimiter: Style = Style(fg=Hue.magenta)
    """Delimiters such as `;`, `.` and `,`."""
    punctuation_bracket: Style = Style(fg=Hue.red)
    """Brackets (e.g., `()`, `{}`, `[]`)."""
    punctuation_special: Style = Style(fg=Hue.rose)
    """Special symbols (e.g., `{}` in string interpolation.)"""

    # strings
    string: Style = Style(fg=Hue.cyan)
    """String literals."""
    string_escape: Style = Style(fg=Hue.red)
    """Escape characters in a string."""
    string_documentation: Style = Style(fg=Hue.base11)
    """Strings representing documentation such as Python docstrings."""
    string_regexp: Style = Style(fg=Hue.orange)
    """Regular expressions."""
    string_special: Style = Style(fg=Hue.violet)
    """Special strings such as dates."""
    string_special_symbol: Style = Style(fg=Hue.violet)
    """Symbols or atoms."""
    string_special_path: Style = Style(fg=Hue.blue)
    """Filename strings."""
    string_special_url: Style = Style(fg=Hue.blue, underline=True)
    """String URIs (e.g., hyperlinks.)"""

    # tags
    tag: Style = Style(fg=Hue.violet)
    """XML-style tag names."""
    tag_builtin: Style = Style(fg=Hue.magenta)
    """Builtin tag names (e.g., HTML tags)."""
    tag_attribute: Style = Style(fg=Hue.yellow)
    """XML-style tag attributes."""
    tag_delimiter: Style = Style(fg=Hue.red)
    """XML-style tag delimiters."""

    # variables
    variable: Style = Style(fg=Hue.base11)
    """Variable Names."""
    variable_builtin: Style = Style(fg=Hue.rose, italic=True)
    """Builtin variable names, e.g., `this` or `self`."""
    variable_parameter: Style = Style(fg=Hue.orange)
    """Parameters of a function."""
    variable_parameter_builtin: Style = Style(fg=Hue.magenta)
    """Special parameters of a function, e.g., `_` and `it`."""
    variable_member: Style = Style(fg=Hue.yellow)
    """Object and struct fields."""
    # end: treesitter

    # begin: diagnostic
    diagnostic_deprecated: Style = Style(sp=Hue.magenta, undercurl=True)
    """Deprecated or obsolete code in diagnostics."""
    diagnostic_unnecessary: Style = Style(sp=Hue.base15, undercurl=True)
    """Unreachable code in diagnostics."""
    diagnostic_error: Style = Style(fg=Hue.red)
    """Diagnostic errors."""
    diagnostic_warn: Style = Style(fg=Hue.orange)
    """Diagnostic warnings and similar."""
    diagnostic_info: Style = Style(fg=Hue.yellow)
    """Diagnostic info and similar."""
    diagnostic_hint: Style = Style(fg=Hue.green)
    """Diagnostic hints and similar."""
    diagnostic_ok: Style = Style(fg=Hue.mint)
    """Style `ok`."""
    diagnostic_underline_error: Style = Style(sp=Hue.red, undercurl=True)
    """Errors that should be underlined."""
    diagnostic_underline_warn: Style = Style(sp=Hue.orange, undercurl=True)
    """Warnings that should be underlined."""
    diagnostic_underline_info: Style = Style(sp=Hue.yellow, underline=True)
    """Style info that should be underlined."""
    diagnostic_underline_hint: Style = Style(sp=Hue.green, underline=True)
    """Style hints that should be underlined."""
    diagnostic_underline_ok: Style = Style(sp=Hue.mint, underline=True)
    """Style ok that should be underlined."""
    diagnostic_floating_error: Style = Style(link="diagnostic_error")
    diagnostic_floating_warn: Style = Style(link="diagnostic_warn")
    diagnostic_floating_info: Style = Style(link="diagnostic_info")
    diagnostic_floating_hint: Style = Style(link="diagnostic_hint")
    diagnostic_floating_ok: Style = Style(link="diagnostic_ok")
    diagnostic_gutter_error: Style = Style(link="diagnostic_error")
    diagnostic_gutter_warn: Style = Style(link="diagnostic_warn")
    diagnostic_gutter_info: Style = Style(link="diagnostic_info")
    diagnostic_gutter_hint: Style = Style(link="diagnostic_hint")
    diagnostic_gutter_ok: Style = Style(link="diagnostic_ok")
    diagnostic_virtual_text_error: Style = Style(link="diagnostic_error")
    diagnostic_virtual_text_warn: Style = Style(link="diagnostic_warn")
    diagnostic_virtual_text_info: Style = Style(link="diagnostic_info")
    diagnostic_virtual_text_hint: Style = Style(link="diagnostic_hint")
    diagnostic_virtual_text_ok: Style = Style(link="diagnostic_ok")
    diagnostic_virtual_lines_error: Style = Style(link="diagnostic_error")
    diagnostic_virtual_lines_warn: Style = Style(link="diagnostic_warn")
    diagnostic_virtual_lines_info: Style = Style(link="diagnostic_info")
    diagnostic_virtual_lines_hint: Style = Style(link="diagnostic_hint")
    diagnostic_virtual_lines_ok: Style = Style(link="diagnostic_ok")
    spellcheck_error: Style = Style(sp=Hue.red, undercurl=True)
    """Word that is not recognized by the spellchecker."""
    spellcheck_warn: Style = Style(sp=Hue.orange, undercurl=True)
    """Word that should start with a capital."""
    spellcheck_info: Style = Style(sp=Hue.lime, underdotted=True)
    """Word that is recognized is hardly ever used."""
    spellcheck_hint: Style = Style(sp=Hue.yellow, underdotted=True)
    """Word that is recognized one that used in another region."""
    # end: diagnostic

    # TODO: Maybe remove elements linked to TS and add new ones that provide more
    # nuance. This means that lsp logic is handled in mapping layer.
    # begin: lsp
    lsp_reference_text: Style = Style()
    """Used for highlighting "text" references."""
    lsp_reference_read: Style = Style()
    """Used for highlighting "read" references."""
    lsp_reference_write: Style = Style()
    """Used for highlighting "write" references."""
    lsp_reference_target: Style = Style()
    """Used for highlighting reference targets (e.g., in a however range)."""
    lsp_inlay_hint: Style = Style()
    lsp_code_lens: Style = Style()
    lsp_code_lens_separator: Style = Style()
    lsp_signature_active_parameter: Style = Style()

    # Semantic highlight provided by lsps. neovim `:h lsp-highlight`
    # lsp_type_class: Style = Style()
    # """Reference a class type."""
    # lsp_type_comment: Style = Style()
    # """Tokens that represent a comment."""
    # lsp_type_decorator: Style = Style(link=Link.attribute)
    # """Reference an annotation or decorator."""
    # lsp_type_enum: Style = Style()
    # """Reference to an enumeration type."""
    # lsp_type_enum_member: Style = Style()
    # """Reference to an enumeration property, constant, or member."""
    # lsp_type_event: Style = Style()
    # """Reference to an event property."""
    # lsp_type_function: Style = Style(link=Link.function)
    # lsp_type_interface: Style = Style()
    # lsp_type_keyword: Style = Style(link=Link.keyword)
    # """Tokens that represent a language keyword."""
    # lsp_type_macro: Style = Style()
    # lsp_type_method: Style = Style(link=Link.function_method)
    # lsp_type_modifier: Style = Style(link=Link.keyword_modifier)
    # lsp_type_namespace: Style = Style(link=Link.module)
    # lsp_type_number: Style = Style(link=Link.number)
    # lsp_type_operator: Style = Style(link=Link.operator)
    # lsp_type_parameter: Style = Style(link=Link.variable_parameter)
    # lsp_type_property: Style = Style(link=Link.property)
    # lsp_type_regexp: Style = Style(link=Link.string_regexp)
    # lsp_type_string: Style = Style(link=Link.string)
    # lsp_type_struct: Style = Style()
    # """Identifiers that declare or reference a struct."""
    # lsp_type_type: Style = Style(link=Link.keyword_type)
    # lsp_type_type_parameter: Style = Style()
    # lsp_type_variable: Style = Style(link=Link.variable)
    # lsp_mod_abstract: Style = Style(fg=R.orange)
    # """Types and methods that are abstract."""
    # lsp_mod_async: Style = Style(link=Link.keyword_coroutine)
    # """Functions that are marked async."""
    # lsp_mod_declaration: Style = Style(fg=R.magenta)
    # """Declaration of symbols."""
    # lsp_mod_default_library: Style = Style(link=Link.module_builtin)
    # """Symbols that are part of the standard library."""
    # lsp_mod_definition: Style = Style(fg=R.blue)
    # """Definitions of files, (e.g., in header files)."""
    # lsp_mod_deprecated: Style = Style(link=Link.diagnostic_deprecated)
    # """Symbols that should no longer be used."""
    # lsp_mod_documentation: Style = Style(fg=R.yellow)
    # """Occurrences of symbols in documentation."""
    # lsp_mod_modification: Style = Style(fg=R.green)
    # """Variable references where the variable is assigned to."""
    # lsp_mod_readonly: Style = Style(fg=R.red)
    # """Readonly variables and fields (constants)."""
    # lsp_mod_static: Style = Style()
    # """Static class members."""

    # new "lsp" nodes?
    # @lsp.type.typeParameter
    # @lsp.type.enumMember
    # @lsp.type.event (what even is this?)
    # @lsp.type.interface
    # @lsp.mod.abstract
    # @lsp.mod.declaration (maybe)
    # @lsp.mod.static
    # @lsp.mod.modification
    # @lsp.mod.deprecated

    # Semantic tokens
    # Finer grained types from lsp semantic tokens.
    # deprecated: Style = Style(link=Link.diagnostic_deprecated)
    # """Tokens marked as deprecated."""
    abstract: Style = Style()
    """Types and methods that are abstract."""
    declaration: Style = Style()
    """Declaration of symbols."""
    classes: Style = Style()
    """Identifiers that declare or reference a class."""
    event_property: Style = Style(fg=Hue.yellow)
    """Identifiers that declare or reference an event property."""
    enum: Style = Style(fg=Hue.yellow)
    """Identifiers that declare or reference an enumeration type."""
    enum_member: Style = Style(fg=Hue.magenta)
    """Identifiers that declare or reference an enumeration property."""
    function_async: Style = Style(fg=Hue.azure)
    """Functions that are marked async."""
    interface: Style = Style(fg=Hue.azure)
    """Identifiers that declare or reference an interface."""
    struct: Style = Style(fg=Hue.lime)
    """Identifiers that declare or reference a struct type."""
    type_parameter: Style = Style(fg=Hue.rose)
    """Identifiers that declare or reference a type parameter."""
    variable_modification: Style = Style(fg=Hue.green)
    """Variable reference where the variable is assigned to."""
    static_member: Style = Style(fg=Hue.orange)

    # begin: neovim groups.
    # Some might have had their names changed slightly, as many of these groups
    # are more general purpose and would apply to any particular application.
    # From neovim `h: highlight-groups`
    # syntax groups

    concealed: Style = Style(fg=Hue.base08)
    """Placeholder characters substituted for concealed text."""

    color_column: Style = Style(bg=Hue.base02)
    """Used for the columns such as max line length guide.."""
    completion_match_insert: Style = Style(fg=Hue.green)
    """Matched text of the currently inserted completion."""
    # l_cursor: Style = Style()
    # """Character under cursor when |language-mapping| is used (see 'guicursor')."""
    cursor_column: Style = Style(bg=Hue.base02)
    """Screen column at the cursor."""
    cursor_line: Style = Style(bg=Hue.base02)
    """Screen line (row) at the cursor."""
    cursor_line_number: Style = Style(fg=Hue.base10, bg=Hue.base02)
    """The line number gutter item on the current cursor line."""
    cursor_line_fold: Style = Style()
    """Like `fold_column` when 'cursorline' is set for the cursor line."""
    cursor_line_gutter: Style = Style()
    """Like `sign_column` when 'cursorline' is set for the cursor line."""
    # directory: Style = Style()
    # """Directory names (and other special names in listings)."""
    # diff_add: Style = Style()
    # """Diff mode: Added line. |diff.txt|"""
    # diff_change: Style = Style()
    # """Diff mode: Changed line. |diff.txt|"""
    # diff_delete: Style = Style()
    # """Diff mode: Deleted line. |diff.txt|"""
    # diff_text: Style = Style()
    # """Diff mode: Changed text within a changed line. |diff.txt|"""
    end_of_buffer: Style = Style(fg=Hue.base08)
    """Filler lines (~) after the end of the buffer."""
    window_separator: Style = Style(bg=Hue.base15)
    """Separators between window splits."""
    folded_line: Style = Style()
    """Line used for closed folds."""
    fold_column: Style = Style()
    """'foldcolumn'"""
    gutter: Style = Style(bg=Hue.base02)
    """Column where signs (e.g., git, error checks)  are displayed."""
    line_number: Style = Style(bg=Hue.base02, fg=Hue.base10)
    """Line numbers in sidebar. Applies to all numbers."""
    line_number_above: Style = Style(bg=Hue.base02, fg=Hue.base09)
    """Line number above the cursor line. In vim, only relevant with
    with relative numbering."""
    line_number_below: Style = Style(bg=Hue.base02, fg=Hue.base09)
    """Line number below the cursor line. In vim, only relevant with
    relative line numbering."""
    matched_bracket: Style = Style(fg=Hue.black, bg=Hue.hl_yellow)
    """Character under the cursor or just before it, if it is a paired bracket"""

    message: Style = Style(bg=Hue.base03)
    """Area for messages and command-line. Vim's MsgArea."""
    message_error: Style = Style(fg=Hue.red)
    """Error messages / notifications (e.g., on the command line)."""
    message_warn: Style = Style(fg=Hue.orange)
    """Warning messages / notifications (e.g., on the command line)."""
    message_mode: Style = Style(fg=Hue.blue)
    """For modal editors, the mode display (e.g., vim `-- INSERT --`)."""
    message_more: Style = Style(fg=Hue.green)
    """More prompt. Vim's MoreMsg."""
    message_question: Style = Style(fg=Hue.yellow)
    """|hit-enter| prompt and yes/no questions."""
    message_separator: Style = Style()
    """Separator for scrolled messages |msgsep|."""
    non_text: Style = Style(fg=Hue.base08)
    """'@' at the end of the window, characters from 'showbreak' and other
    characters that do not really exist in the text
    (e.g., ">" displayed when a double-wide character doesn't fit."""
    # normal: Style = Style(fg=R.b11, bg=R.b0)
    # """Normal text. Primary foreground and background."""
    floating_window: Style = Style(fg=Hue.base11, bg=Hue.base02)
    """Normal text in floating windows."""
    floating_window_border: Style = Style()
    """Border of floating windows."""
    floating_window_title: Style = Style()
    """Title of floating windows."""
    floating_window_footer: Style = Style()
    """Footer of floating windows."""
    # pmenu: Style = Style()
    # """Popup menu: Normal item."""
    # pmenu_sel: Style = Style()
    # """Popup menu: Selected item. Combined with |hl-Pmenu|."""
    # pmenu_kind: Style = Style()
    # """Popup menu: Normal item "kind"."""
    # pmenu_kind_sel: Style = Style()
    # """Popup menu: Selected item "kind"."""
    # pmenu_extra: Style = Style()
    # """Popup menu: Normal item "extra text"."""
    # pmenu_extra_sel: Style = Style()
    # """Popup menu: Selected item "extra text"."""
    # pmenu_sbar: Style = Style()
    # """Popup menu: Scrollbar."""
    # pmenu_thumb: Style = Style()
    # """Popup menu: Thumb of the scrollbar."""
    # pmenu_match: Style = Style()
    # """Popup menu: Matched text in normal item. Combined with |hl-Pmenu|."""
    # pmenu_match_sel: Style = Style()
    # """Popup menu: Matched text in selected item."""
    # quick_fix_line: Style = Style()
    # """Current |quickfix| item in the quickfix window."""
    snippet_tabstop: Style = Style()
    """Tabstops in snippets. |vim.snippet|"""
    special_key: Style = Style(fg=Hue.red)
    """Unprintable characters: Text displayed differently from what it really is."""
    status_line: Style = Style(bg=Hue.base03, fg=Hue.base10)
    """Status line of current window."""
    status_line_unfocused: Style = Style(fg=Hue.base09, bg=Hue.base03)
    """Status lines of not-current windows."""
    tab_line: Style = Style()
    """Tab pages line, not active tab page label."""
    tab_line_fill: Style = Style()
    """Tab pages line, where there are no labels."""
    tab_line_sel: Style = Style()
    """Tab pages line, active tab page label."""
    # visual_nos: Style = Style()
    # """Visual mode selection when vim is "Not Owning the Selection"."""
    tooltip: Style = Style()
    """Current font, bg and fg of the tooltips when using a GUI."""
    whitespace: Style = Style(fg=Hue.base08)
    """"Tokens like non-breaking space, trailing whitespace, etc."""
    wild_menu: Style = Style()
    """Current match in 'wildmenu' completion."""
    window_bar: Style = Style()
    """Window bar of current window."""
    window_bar_unfocused: Style = Style()
    """Window bar of not-current windows."""
    menu: Style = Style(bg=Hue.base03, fg=Hue.base11)
    """Current menus and toolbars."""
    scrollbar: Style = Style(bg=Hue.base04)
    """Current main window's scrollbars."""
    search: Style = Style(bg=Hue.hl_yellow, fg=Hue.black)
    """Last search pattern highlighting"""
    search_current_match: Style = Style(bg=Hue.hl_blue, fg=Hue.black)
    """Current match for the last search pattern."""
    # TODO: Do we want this?
    search_incremental: Style = Style(bg=Hue.hl_blue, fg=Hue.black)
    """Incremental search in find / replace.."""
    search_replace: Style = Style(bg=Hue.hl_green, fg=Hue.black)
    """Substituted text in find / replace."""

    # terminal for e.g., embedded terminal emulators in neovim
    terminal_cursor: Style = Style(link="cursor")
    """Cursor in a focused terminal."""
    terminal_status_line: Style = Style(link="status_line")
    """Status line of |terminal| window."""
    terminal_status_line_unfocused: Style = Style(link="status_line_unfocused")
    """Status line of non-current terminal windows."""

    @override
    def __hash__(self) -> int:
        return super().__hash__()

    # def resolve(self, palette: Palette) -> Theme:
    #     """Resolve an abstract theme with refs into a concrete universal theme.
    #
    #     Args:
    #         palette: A palette containing color definitions.
    #
    #     Returns:
    #         A universal, concrete Theme referencing the .
    #
    #     """
    #     return resolve(self, palette)

    @property
    def desc(self) -> str:
        """Theme description from metadata."""
        return self.meta.desc

    @property
    def name(self) -> str:
        """Theme name from metadata."""
        return self.meta.name

    @property
    def version(self) -> str:
        """Theme version from metadata."""
        return self.meta.version

    @property
    def url(self) -> str:
        """Theme url from metadata."""
        return self.meta.url

    def styles(self) -> Iterator[tuple[str, Style]]:
        """Yield Style items.

        Yields:
            Field name and Style instance.

        """
        for key, val in self:
            if isinstance(val, Style):
                yield key, val

    def resolve_links(self, field: str) -> Style:
        """Merge linked styles.

        Args:
            field: The name of the theme field to resolve, e.g., "comment".

        Returns:
            A new Style instance merged with its links.

        Raises:
            ValueError: When circular links are detected.

        """
        node: Style = self[field]
        if node.link is None:
            return node

        # Walk the link chain from the provided instance towards the root
        # Use the fact dicts are order preserving or use a set and list.
        key = field
        seen: dict[str, Style] = {}
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
        merged: Style = Style()
        for part in reversed(seen.values()):
            merged |= part

        return merged

    def resolve(self, palette: Palette) -> Theme:
        """Resolve an abstract theme against a specific palette.

        Args:
            palette: A palette containing color definitions.

        Returns:
            A universal, concrete Theme resolved against the input palette.

        """
        return resolve(self, palette)


@cache
def resolve(theme: Theme, palette: Palette) -> Theme:
    """Resolve an abstract theme against a specific palette.

    Args:
        theme: An abstract theme instance.
        palette: A palette containing color definitions.

    Returns:
        A universal, concrete Theme resolved against the input palette.

    """

    def get_colors(node: Style) -> Style:
        resolved_fields = {
            k: palette[v] if v in Hue else v
            for k, v in node
            if k in node.model_fields_set
        }
        return node.model_validate(resolved_fields)

    return Theme(
        meta=theme.meta,
        colors=ThemeColors(**{k: palette[v] for k, v in theme.colors}),
        **{k: get_colors(theme.resolve_links(k)) for k, _ in theme.styles()},
    )
