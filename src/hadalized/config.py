"""Module containing all underlying color definitions and gamut info."""

from enum import StrEnum, auto
from pathlib import Path
from typing import Annotated, Any, ClassVar, Self

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
from hadalized.palette import Palette, PaletteMetadata
from hadalized.theme import Theme


def split_template(path: Path) -> tuple[str, str]:
    """Parse the template name and non-template suffix.

    Args:
        path: The template path, e.g. "myapp.toml.jinja"

    Returns:
        A pair consisting of the template name without template suffix
        and underlying suffix. For example
        "myapp.toml.jinja" -> ("myapp.toml", ".toml")

    """
    if path.suffix in {".j2", ".jinja", ".jinja2"}:
        name = path.stem
        suffix = path.suffixes[-2] if len(path.suffixes) > 1 else ""
    else:
        name = path.name
        suffix = path.suffix
    return name, suffix


def validate_nullable_path(val: str | Path | None) -> Path | None:
    """Convert special values of `null` or `none` to None.

    Returns:
        A ``Path`` instance or None.

    """
    match str(val).lower():
        case "null" | "none" | "nil":
            out = None
        case _:
            out = Path(val) if isinstance(val, str) else val
    return out


class AppConfig(BaseNode):
    """Information about which files should be generatted specific app."""

    name: str = Field(
        examples=["neovim", "myapp", "html-examples"],
    )
    """Application name or category. Controls where built theme files
    are cached."""
    template: Path
    """Template filename relative to the templates directory. When the path
    suffix indicates a jinja filetype, """
    gamut: ColorSpace = Field(default=ColorSpace.srgb, examples=["display-p3"])
    """The gamut to fit colors to. For example, if the theme targets css
    a wide gamut might be appropriate. For many terminal applications it
    is best to use srgb."""
    color_rep: ColorRep = ColorRep.hex
    """How each ColorInfo should be transformed when presented as context
    to the template. Typically indicates which leaf of a ColorInfo to use, e.g.,
    `"hex"` for chases where the application expects hex color codes."""
    _template_name: str = PrivateAttr(default="")
    """Template name ignoring jinja specific parts."""
    _template_suffix: str = PrivateAttr(default="")
    """Template suffix ignoring jinja specific parts."""

    def model_post_init(self, context: Any, /) -> None:
        """Post init."""
        self._template_name, self._template_suffix = split_template(self.template)

    @property
    def extension(self) -> str:
        """The output file extension."""
        return self._template_suffix


@Parameter(name="*")
class Options(BaseNode):
    """Common options available to all CLI commands and configuration."""

    cache_dir: Annotated[Path, Parameter(parse=True)] = Home.cache()
    """Location of cache directory."""
    config_file: Annotated[
        Path | None,
        Parameter(alias=["--config", "-c"]),
        AfterValidator(validate_nullable_path),
    ] = Field(default=None)
    """Specify a toml file to load configuration from. When specified,
    the standard configurations specified in ``UserConfig`` are ignored.
    """
    gamut: ColorSpace | None = Field(default=None, examples=["display-p3"])
    """The gamut to fit colors to. Overrides the settings in an individual
    application configuration.
    """
    color_rep: Annotated[
        ColorRep | None,
        Parameter(alias=["--rep"]),
    ] = Field(default=None)
    """How each color should be encoded when presented as context
    to the template. Overrides the setings in individual application configurations.
    """
    dry_run: Annotated[bool, Parameter(alias="-D", negative="")] = False
    """Do not output any files or write to cache."""
    force: Annotated[bool, Parameter(alias="-f", negative="")] = False
    """Force generation of application theme files. If set during theme
    building, cache is ignored.
    """
    no_cache: Annotated[bool, Parameter(negative="")] = False
    """Ignore cache completely."""
    no_config: Annotated[bool, Parameter(negative="")] = False
    """Do not read settings from user config files. Implies `--no-templates`."""
    no_templates: Annotated[bool, Parameter(negative="")] = False
    """Ignore user defined templates. Implied by `--no-config`."""
    output_dir: Annotated[
        Path | None,
        Parameter(alias=["--outdir", "-d"]),
        AfterValidator(validate_nullable_path),
    ] = Field(
        default=None,
        examples=[Path("./build"), Path("./colors")],
    )
    """Directory to write built theme files. By default, each application's
    theme files are included in a subdirectory of this directory, unless the
    ``no-prefix`` flag is set."""
    output_name: Annotated[
        Path | None,
        Parameter(alias=["--outname", "-n"]),
        AfterValidator(validate_nullable_path),
    ] = Field(
        default=None,
        examples=[Path("./starship.toml"), Path("./colors/mytheme.lua")],
    )
    """Name of the output theme file. Can be set when building a
    single theme file by specifying one application and one palette.
    """
    include_apps: Annotated[
        set[str],
        Parameter(name="app", alias=["-a"], negative=""),
    ] = Field(
        default=set(),
        examples=[{"neovim"}],
    )
    """Application theme files to build. The elements must correspond to a
    ``Config.apps`` key, which is typically an application name.
    If not specified, theme files for all applications in ``Config.apps`` will be
    generated.
    """
    include_palettes: Annotated[
        set[str],
        Parameter(name="palette", alias=["-p"], negative=""),
    ] = Field(default=set())
    """Palettes to include when building application theme files. The
    items must be a key in ``Config.palettes``. If not specified, theme files
    for each palette will be generated.
    """
    prefix: Annotated[bool, Parameter()] = True
    """When set in conjunction with an output directory, built themes will
    be placed in a subdirectory determined by built theme file's parent
    directory. Typically this is just the applicate name, e.g., 'neovim'."""
    quiet: Annotated[bool, Parameter(alias="-q", negative="")] = False
    """Suppress logging to stdout."""
    state_dir: Annotated[Path, Parameter(parse=True)] = Home.state()
    """Directory containing application state."""
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
        if self.no_config and self.config_file:
            raise ValueError("Cannot set both no_config and config_file.")
        if self.output_dir and self.output_name:
            raise ValueError("Cannot set both output_dir and output_name.")
        return self

    @property
    def build_dir(self) -> Path:
        """Location of cached theme files."""
        return self.cache_dir / "build"

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

    def is_included(self, inst: AppConfig | Palette) -> bool:
        """Determine whether the instance name is in an include list.

        Returns:
            True if the instance name is in the appropirate return list.

        """
        match inst:
            case AppConfig():
                includes = self.include_apps
                name = inst.name
            case Palette():
                includes = self.include_palettes
                name = inst.name
            # case Theme():
            #     includes = self.include_themes
            #     name = inst.meta.name
        return not includes or name in includes


class Colors:
    """Builtin color definitions."""

    # blues, high chroma
    blue12: str = "oklch(0.125 0.0225 220)"
    blue13: str = "oklch(0.130 0.030 220)"
    blue14: str = "oklch(0.140 0.030 220)"
    blue16: str = "oklch(0.1625 0.030 220)"
    blue20: str = "oklch(0.200 .030 220)"
    blue25: str = "oklch(0.250 .030 220)"
    blue30: str = "oklch(0.300 .035 220)"
    blue35: str = "oklch(0.350 .035 220)"
    # grays, mid / low chroma
    gray10: str = "oklch(0.100 .010 220)"
    gray12: str = "oklch(0.125 .010 220)"
    gray13: str = "oklch(0.130 .010 220)"
    gray14: str = "oklch(0.140 .010 220)"
    gray16: str = "oklch(0.160 .010 220)"
    gray20: str = "oklch(0.200 .010 220)"
    gray25: str = "oklch(0.250 .010 220)"
    gray30: str = "oklch(0.300 .010 220)"
    gray35: str = "oklch(0.350 .010 220)"
    gray40: str = "oklch(0.40 .010 220)"
    gray45: str = "oklch(0.450 .010 220)"
    gray50: str = "oklch(0.500 .010 220)"
    gray55: str = "oklch(0.550 .010 220)"
    gray60: str = "oklch(0.600 .010 220)"
    gray65: str = "oklch(0.650 .010 220)"
    gray70: str = "oklch(0.700 .010 220)"
    gray75: str = "oklch(0.750 .010 220)"
    gray80: str = "oklch(0.800 .005 220)"
    gray85: str = "oklch(0.850 .005 100)"
    gray90: str = "oklch(0.900 .005 220)"
    gray91: str = "oklch(0.910 .005 100)"
    gray92: str = "oklch(0.925 .005 100)"
    gray95: str = "oklch(0.950 .005 100)"
    gray97: str = "oklch(0.975 .005 100)"
    gray99: str = "oklch(0.990 .005 100)"
    gray100: str = "oklch(0.995 .005 100)"
    # Sun / Day high chroma
    sun12: str = "oklch(0.125 .020 100)"
    sun14: str = "oklch(0.14 .020 100)"
    sun16: str = "oklch(0.16 .020 100)"
    sun20: str = "oklch(0.200 .020 100)"
    sun30: str = "oklch(0.300 .020 100)"
    sun40: str = "oklch(0.400 .020 100)"
    sun50: str = "oklch(0.500 .020 100)"
    sun60: str = "oklch(0.600 .020 100)"
    sun70: str = "oklch(0.700 .020 100)"
    sun80: str = "oklch(0.800 .020 100)"
    sun85: str = "oklch(0.850 .020 100)"
    sun90: str = "oklch(0.900 .020 100)"
    sun91: str = "oklch(0.910 .020 100)"
    sun92: str = "oklch(0.925 .020 100)"
    sun95: str = "oklch(0.950 .020 100)"
    sun97: str = "oklch(0.975 .015 100)"
    sun99: str = "oklch(0.990 .010 100)"
    sun100: str = "oklch(0.995 .010 100)"


class Config(Options):
    """App configuration.

    Contains information about which app theme files to generate and where
    to write the build artifacts.

    This particular Config will not load settings from anything except
    init arguments, and as such serves as a default Config base.
    """

    builtin_colors: ClassVar[type] = Colors

    builtin_palette_dark: ClassVar[Palette] = Palette(
        meta=PaletteMetadata(
            name="hadalized-dark",
            desc="Main dark palette with darker solarized inspired bases.",
            version="2.1",
            mode="dark",
        ),
    )

    builtin_palette_gray: ClassVar[Palette] = Palette(
        meta=PaletteMetadata(
            name="hadalized-gray",
            desc="Dark theme variant with more grayish backgrounds.",
            version="2.1",
            mode="dark",
        ),
        base00=Colors.gray13,
        base01=Colors.gray14,
        base02=Colors.gray16,
        base03=Colors.gray20,
        base04=Colors.gray25,
        base05=Colors.gray30,
        base06=Colors.gray35,
    )

    builtin_palette_day: ClassVar[Palette] = Palette(
        meta=PaletteMetadata(
            name="hadalized-day",
            desc="Light theme variant with sunny backgrounds.",
            version="2.1",
            mode="light",
        ),
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

    builtin_palette_light: ClassVar[Palette] = builtin_palette_day | Palette(
        meta=PaletteMetadata(
            name="hadalized-light",
            desc="Light theme variant with whiter backgrounds.",
            version="2.1",
            mode="light",
        ),
        base00=Colors.gray100,
        base01=Colors.gray99,
        base02=Colors.gray95,
        base03=Colors.gray92,
        base04=Colors.gray99,
        base05=Colors.gray85,
        base06=Colors.gray80,
    )

    builtin_palettes: ClassVar[dict[str, Palette]] = {
        builtin_palette_dark.name: builtin_palette_dark,
        builtin_palette_light.name: builtin_palette_light,
        builtin_palette_gray.name: builtin_palette_gray,
        builtin_palette_day.name: builtin_palette_day,
    }

    builtin_apps: ClassVar[dict[str, AppConfig]] = {
        "neovim": AppConfig(
            name="neovim",
            template=Path("neovim.lua.jinja"),
            color_rep=ColorRep.hex,
            # theme_mapping=utils.Neovim.mapping(),
        ),
        "wezterm": AppConfig(
            name="wezterm",
            template=Path("wezterm.toml.jinja"),
            color_rep=ColorRep.hex,
        ),
        "starship": AppConfig(
            name="starship",
            template=Path("starship.toml.jinja"),
            color_rep=ColorRep.hex,
        ),
        "theme-html": AppConfig(
            name="theme-html",
            template=Path("theme.html"),
            color_rep=ColorRep.css,
        ),
    }

    apps: dict[str, AppConfig] = Field(default=builtin_apps)
    """Build directives specifying how and which theme files are
    generated for a specific application."""
    palettes: dict[str, Palette] = Field(default=builtin_palettes)
    """Palette color definitions."""
    theme: Theme = Field(default=Theme())
    """Abstract themes referencing generic palette fields."""
    _opts: Options | None = PrivateAttr(default=None)

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

    # def model_post_init(self, context: Any, /) -> None:
    #     """Post init.
    #
    #     - Set lookups.
    #
    #     """
    #     for bconf in BUILTIN_APP_CONFIGS:
    #         if bconf.name not in self.apps:
    #             self.apps[bconf.name] = bconf
    #     return super().model_post_init(context)

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
            Home.config() / "apps.toml",
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
