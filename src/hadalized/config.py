"""Module containing all underlying color definitions and gamut info."""

from enum import StrEnum, auto
from itertools import product
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Self

from cyclopts.parameter import Parameter
from pydantic import AfterValidator, Field, PrivateAttr, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from hadalized.base import BaseNode, Home
from hadalized.color import ColorRep, ColorSpace
from hadalized.palette import Palette
from hadalized.theme import AbstractTheme, Theme, ThemeCollection

if TYPE_CHECKING:
    from collections.abc import Iterator

type Context = Theme | ThemeCollection


def _split_template(tmpl: Path) -> tuple[str, str]:
    """Split template path into its effective name and suffix.

    Examples:
        - "shrc" -> ("shrc", "")
        - "shrc.j2" -> ("shrc", "")
        - "wezterm.toml" -> ("wezterm.toml", ".toml")
        - "wezterm.toml.j2" -> ("wezterm.toml", ".toml")

    Returns:
        The name and suffix pair, ignoring parts that indicate a jinja template.

    """
    if tmpl.suffix in {".j2", ".jinja", ".jinja2"}:
        name = tmpl.stem  # e.g., wezterm.toml.j2 -> wezterm.toml
        suffix = tmpl.suffixes[-2] if len(tmpl.suffixes) > 1 else ""
    else:
        name = tmpl.name
        suffix = tmpl.suffix
    return name, suffix


class ContextType(StrEnum):
    """Values determine which context expose to template when building a theme."""

    theme = auto()
    """A single Theme instance will be passed to the `context` variable of a
    template."""
    full = auto()
    """A collection of themes will be passed to the `context` variable."""


class BuiltinThemes(StrEnum):
    """Enumerates the list of themes that are handled by the builder."""

    neovim = auto()
    wezterm = auto()
    starship = auto()


class BuildConfig(BaseNode):
    """Information about which files should be generatted specific app."""

    name: str = Field(
        examples=["neovim", "myapp", "html-examples"],
    )
    """Application name or category. Controls where"""
    subdir: str = ""
    """Build sub-directory where theme files are placed. Defaults to `name`."""
    template: Path
    """Template filename relative to the templates directory. When the path
    suffix indicates a jinja filetype, """
    filename: str = ""
    """Output file name, including extension. For builds that target full
    context (a collection of themes), the default value is the template name,
    with the suffix indicating a jinja template removed. For applications
    that expect one theme per file, output names are of the form
    `{theme.fullname}{template.suffix}`, e.g., "hadalized-dark.toml"
    """
    context_type: ContextType = ContextType.theme
    """The underlying context type to pass to the template."""
    gamut: ColorSpace = Field(default=ColorSpace.srgb, examples=["display-p3"])
    """Which gamut to map color definitions into."""
    color_rep: ColorRep = ColorRep.hex
    """How each Palette should be transformed when presented as context
    to the template."""
    # TODO(?): Consider allowing per-app specification.
    # palettes: list[str] | None = None
    # """Palettes to include. Defaults to all defined palettes."""
    # themes: list[str] | None = None
    # """Themes to include. Defaults to all defined themes."""
    _filename: str = PrivateAttr(default="")
    _subdir: Path = PrivateAttr(default=Path("./"))
    _template_name: str = PrivateAttr(default="")
    _template_suffix: str = PrivateAttr(default="")

    def model_post_init(self, context: Any, /) -> None:
        """Post init."""
        name, suffix = _split_template(self.template)
        self._filename = self.filename
        if not self._filename:
            match self.context_type:
                case ContextType.theme:
                    self._filename = "{theme.fullname}" + suffix
                case ContextType.full:
                    self._filename = name
        self._template_name = name
        self._template_suffix = suffix
        self._subdir = Path(self.subdir or self.name)

    def format_path(self, context: Context) -> Path:
        """File output path relative to build directory.

        Returns:
            The absolute path where a file should be written.

        """
        return self._subdir / self._filename.format(theme=context)

    @staticmethod
    def builtin() -> dict[str, BuildConfig]:
        """Builtin build configs.

        Returns:
            The default build instructions used to generate theme files.

        """
        builds = [
            BuildConfig(
                name="neovim",
                template=Path("neovim.lua"),
                color_rep=ColorRep.hex,
                context_type=ContextType.theme,
            ),
            BuildConfig(
                name="wezterm",
                template=Path("wezterm.toml.j2"),
                color_rep=ColorRep.hex,
                context_type=ContextType.theme,
            ),
            BuildConfig(
                name="starship",
                template=Path("starship.toml"),
                color_rep=ColorRep.hex,
                context_type=ContextType.full,
            ),
            BuildConfig(
                name="theme-info",
                subdir="info",
                template=Path("theme.json"),
                color_rep=ColorRep.info,
                context_type=ContextType.theme,
            ),
            BuildConfig(
                name="theme-html",
                subdir="info",
                template=Path("theme.html"),
                color_rep=ColorRep.css,
                context_type=ContextType.theme,
            ),
        ]
        return {x.name: x for x in builds}


def validate_nullable_path(val: str | Path | None) -> Path | None:
    """Convert special values of `null` or `none` to None.

    Returns:
        A ``Path`` instance or None.

    """
    match str(val).lower():
        case "null" | "none":
            out = None
        case _:
            out = Path(val) if isinstance(val, str) else val
    return out


@Parameter(name="*")
class Options(BaseNode):
    """Common options available to all CLI commands and configuration."""

    # fixme: Annotated[
    #     Path | None,
    #     Parameter(alias=["--fix"]),
    #     AfterValidator(validate_nullable_path),
    # ] = None
    cache_dir: Annotated[Path, Parameter(parse=True)] = Home.cache()
    """Location of cache directory."""
    config_file: Path | None = None
    """Specify a toml file to load configuration from. When specified,
    the standard configurations specified in ``UserConfig`` are ignored.
    """
    cache_in_memory: Annotated[bool, Parameter(negative="")] = False
    """Whether to use in-memory application cache."""
    dry_run: Annotated[bool, Parameter(alias="-n", negative="")] = False
    """Do not output any files or write to cache."""
    force: Annotated[bool, Parameter(alias="-f", negative="")] = False
    """Force rewriting of files. If set during theme building, files will
    be regenerated and cache populated."""
    no_cache: Annotated[bool, Parameter(negative="")] = False
    """Ignore cache completely. If set during theme building, hash digests
    of generated files will not be cached."""
    no_config: Annotated[bool, Parameter(negative="")] = False
    """Do not read settings from user config files. Implies `--no-templates`."""
    no_templates: Annotated[bool, Parameter(negative="")] = False
    """Ignore user defined templates. Implied by `--no-config`."""
    output_dir: Annotated[
        Path | None,
        Parameter(alias=["--output", "--out", "-o"]),
        AfterValidator(validate_nullable_path),
    ] = Field(
        default=None,
        examples=[Path("./build"), Path("./colors")],
    )
    """Directory to copy built theme files to or output files."""
    include_builds: Annotated[
        set[str],
        Parameter(name="app", alias=["-a"], negative=""),
    ] = Field(default=set())
    """Application themes to build. The elements must correspond to a
    ``Config.builds`` item name, which is typically an application name.
    If not specified, all applications in ``Config.builds`` will be
    generated.
    """
    include_palettes: Annotated[
        set[str],
        Parameter(name="palette", alias=["-p"], negative=""),
    ] = Field(default=set())
    """Palettes to include when building application theme files. The
    items must be palette names. If not specified, all palettes will be used.
    """
    include_themes: Annotated[
        set[str],
        Parameter(name="theme", alias=["-t"], negative=""),
    ] = Field(default=set())
    """Defined abstract themes to include when building application theme files.
    The items must theme names. If not specified, all themes will be used.
    """
    prefix: Annotated[bool, Parameter()] = True
    """When set in conjunction with an output directory, built themes will
    be placed in a subdirectory determined by built theme file's parent
    directory. Typically this is just the applicate name, e.g., 'neovim'."""
    quiet: Annotated[bool, Parameter(alias="-q", negative="")] = False
    """Suppress logging to stdout."""
    state_dir: Annotated[Path, Parameter(parse=True)] = Home.state()
    """Directory containing application state such as built theme files."""
    template_dir: Annotated[Path, Parameter(parse=True)] = Home.template()
    """Directory where templates will be searched for initially. If a template
    is not found in this directory, it will be loaded from those defined in the
    package."""
    verbose: Annotated[bool, Parameter(alias="-v", negative="")] = False
    """Log more details."""

    @model_validator(mode="after")
    def _check_flags(self) -> Self:
        """Check if settings do not conflict.

        Returns:
            Validated instance.

        Raises:
            ValueError: When mutually exclusive options are set.

        """
        if self.verbose and self.quiet:
            raise ValueError("Cannot set both verbose and quiet.")
        if self.no_cache and self.cache_in_memory:
            raise ValueError("Cannot set both no_cache and cache_in_memory.")
        if self.no_config and self.config_file:
            raise ValueError("Cannot set both no_config and config_file.")
        return self

    @property
    def build_dir(self) -> Path:
        """Location of built theme files."""
        return self.state_dir / "build"

    @property
    def use_cache(self) -> bool:
        """Opposite of `no_cache`."""
        return not self.no_cache

    @property
    def use_templates(self) -> bool:
        """Whether to use user-defined templates.

        False if ``no_config`` is set.

        """
        return not self.no_config and not self.no_templates

    def is_included(self, inst: BuildConfig | Palette | AbstractTheme) -> bool:
        """Determine whether the instance name is in an include list.

        Returns:
            True if the instance name is in the appropirate return list.

        """
        match inst:
            case BuildConfig():
                includes = self.include_builds
            case Palette():
                includes = self.include_palettes
            case AbstractTheme():
                includes = self.include_themes
        return not includes or inst.name in includes


class Config(Options):
    """App configuration.

    Contains information about which app theme files to generate and where
    to write the build artifacts.

    This particular Config will not load settings from anything except
    init arguments, and as such serves as a default Config base.
    """

    builds: dict[str, BuildConfig] = Field(default=BuildConfig.builtin())
    """Build directives specifying how and which theme files are
    generated."""
    palettes: dict[str, Palette] = Field(default=Palette.builtin())
    """Palette color definitions."""
    themes: dict[str, AbstractTheme] = Field(
        default={"default": AbstractTheme.builtin()},
    )
    """Abstract themes referencing generic palette fields."""
    _opts: Options | None = PrivateAttr(default=None)
    _palette_lu: dict[str, Palette] = PrivateAttr(default={})
    _build_lu: dict[str, BuildConfig] = PrivateAttr(default={})
    _theme_lu: dict[str, AbstractTheme] = PrivateAttr(default={})

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Set source loading priority.

        Returns:
            Priority order in which config settings are loaded.

        """
        return (init_settings,)

    def model_post_init(self, context: Any, /) -> None:
        """Post init.

        - Set lookups.

        """
        self._palette_lu = self.palettes | {x.name: x for x in self.palettes.values()}
        self._build_lu = self.builds | {x.name: x for x in self.builds.values()}
        self._theme_lu = self.themes | {x.name: x for x in self.themes.values()}
        return super().model_post_init(context)

    def pairs(self) -> Iterator[tuple[AbstractTheme, Palette]]:
        """Theme, palette pairs.

        Yields:
            An abstract theme, palette pair provided both are included.

        """
        for theme, palette in product(self.themes.values(), self.palettes.values()):
            if self.is_included(theme) and self.is_included(palette):
                yield (theme, palette)

    @property
    def opt(self) -> Options:
        """Access just the runtime options from the configuration."""
        if self._opts is None:
            fields = Options.model_fields
            opts = {k: v for k, v in self if k in fields and k in self.model_fields_set}
            self._opts = Options.model_construct(**opts)
        return self._opts


class UserConfig(Config):
    """User configuration settings.

    While schematically identical to the base ``Config`` parent class, when
    a UserConfig is instantiated a selection of settings locations are
    additionally scanned. The priority of settings is

    - init params, e.g., those passed from the CLI
    - environment variables prefixed with `HADALIZED_`
    - DISABLED in 0.5 ~environment variables in `./.env` prefixed with `HADALIZED_`
    - settings in `./hadalized.toml`
    - settings in `$XDG_CONFIG_DIR/hadalized/config.toml`
    """

    model_config = SettingsConfigDict(
        frozen=True,
        env_file=["hadalized.env"],
        env_file_encoding="utf-8",
        # The env_nested_delimiter=_ and max_split=1 means
        env_nested_delimiter="__",
        # env_nested_max_split=1,
        env_prefix="hadalized_",
        env_parse_none_str="null",
        env_parse_enums=True,
        # env_ignore_empty=True,
        extra="forbid",  # When set, will try to push all .env vars into config.
        # extra="ignore",
        nested_model_default_partial_update=True,
        toml_file=[
            Home.config() / "config.toml",
            Home.config() / "builds.toml",
            Home.config() / "palettes.toml",
            Home.config() / "themes.toml",
            Home.config() / "overrides.toml",
            "hadalized.toml",
        ],
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Set source loading priority.

        Returns:
            Priority order in which config settings are loaded.

        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            TomlConfigSettingsSource(settings_cls),
        )


def load_config(opt: Options | None = None) -> Config:
    """Load a configuration instance with the cli options merged in.

    Handles the cases when a user specifies a specific user config file
    or when only the default configuration should be used.

    Args:
        opt: Options that determine which configuration sources are utilized.

    Returns:
        A Config or UserConfig instance.

    """
    if opt is None:
        config = UserConfig()
    elif opt.config_file is not None:
        import tomllib

        file_data = tomllib.loads(opt.config_file.read_text())
        config = Config.model_validate(file_data | opt.model_dump_set())
    elif opt.no_config:
        config = Config(**opt.model_dump_set())
    else:
        config = UserConfig(**opt.model_dump_set())
    return config
