"""Application commands."""

import json
from contextlib import suppress
from shutil import rmtree

from cyclopts import App
from rich import print_json

from hadalized.base import Home
from hadalized.color import ColorRep, ColorSpace
from hadalized.config import Config, Options, load_config
from hadalized.writer import ThemeWriter

app = App()
cache_app = app.command(App(name="cache", help="Interact with the application cache."))
config_app = app.command(
    App(name="config", help="Interact with the application config.")
)
palette_app = app.command(App(name="palette", help="Interact with palettes."))
theme_app = app.command(App(name="theme", help="Interact with universal themes."))
state_app = app.command(
    App(name="state", help="Interact with application state files.")
)


@app.command
def build(opt: Options | None = None):
    """Build application color themes files.

    When no applications or palette is specified, themes will be built for all
    application and palette pairs. Built files are cached in the build cache and
    copied only when an output directory or output name is specified.

    Usage examples:
    - hdl build --output-dir="build"
    - hdl build --app=neovim --output-dir=colors --no-prefix -> colors/hadalized*.lua

    Args:
        opt: Options.

    """
    opt = opt or Options()
    config = load_config(opt)

    if opt.verbose:
        print("opt fields set:")
        print_json(json.dumps(list(opt.model_fields_set)))
        print("Options:")
        print_json(opt.model_dump_json())
    if opt.dry_run:
        print("DRY-RUN. No theme files will be generated or copied.")
    with ThemeWriter(config) as writer:
        info = writer.run()
        if opt.verbose:
            print_json(info.model_dump_json())


@config_app.command(name="schema")
def config_schema():
    """Display configuration schema."""
    print_json(json.dumps(Config.model_json_schema()))


@config_app.command(name="init")
def config_init(opts: Options | None = None):
    """Populate application configuration toml file.

    When `--output-dir=stdout` the toml contents will be printed.
    """
    import tomli_w as toml

    config = load_config(opts)
    data = config.model_dump(mode="json", exclude_none=True)
    if str(config.output_dir) == "stdout":
        print(toml.dumps(data))
        return
    output = config.output_dir or Home.config()
    if output.suffix != ".toml":
        output /= "config.toml"

    output_exists = output.exists()
    if output_exists and not config.quiet:
        print(f"{output} already exists.")
    if output_exists and not config.force:
        return

    if not config.quiet:
        action = "Would create" if config.dry_run else "Creating"
        print(f"{action} {output}")
    if not config.dry_run:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("wb") as fp:
            toml.dump(data, fp)
    # except TypeError as exc:
    #     print(f"Unable to write config file: {exc}")
    #     output.unlink()


@config_app.command(name="options")
def config_options(opts: Options | None = None):
    """Show the configuration `Options` that are loaded."""
    config = load_config(opts)
    print_json(config.opt.model_dump_json())


@palette_app.command(name="info")
def palette_info(
    name: str,
    gamut: ColorSpace = ColorSpace.srgb,
    opt: Options | None = None,
):
    """Show color information for palettes.

    Usage examples:
    - hdl palette info hadalized-dark
    - hdl palette info hadalized-dark --gamut="display-p3"

    Args:
        name: A named palette.
        gamut: A specified gamut to parse against. Defaults to srgb.
        opt: Options

    """
    opt = opt or Options()
    config = load_config(opt)
    raw_palette = config.palettes[name]
    parsed = raw_palette.parse(gamut)
    colors = {
        k: v.model_dump(mode="json", exclude_unset=True) for k, v in parsed.items()
    }
    out = raw_palette.model_dump(mode="json", exclude_unset=True) | colors
    print_json(json.dumps(out))


@cache_app.command(name="clean")
def cache_clean(opt: Options | None = None):
    """Clear the application cache."""
    config = load_config(opt)
    if config.dry_run and not config.quiet:
        print("DRY-RUN: Cache files will not be deleted.")
    if not config.quiet:
        print(f"Clearing {config.cache_dir}")
    if config.verbose:
        files = "\n".join(str(x) for x in config.cache_dir.glob("**/*") if x.is_file())
        print(files)
    if not config.dry_run:
        with suppress(FileNotFoundError):
            rmtree(config.cache_dir)


@cache_app.command(name="dir")
def cache_dir(opt: Options | None = None):
    """Show the cache directory."""
    config = load_config(opt)
    print(config.cache_dir)


@cache_app.command(name="list", alias=["ls"])
def cache_list(opt: Options | None = None):
    """List the contents of the application cache."""
    config = load_config(opt)
    files = "\n".join(str(x) for x in config.cache_dir.glob("**/*") if x.is_file())
    print(files)


@state_app.command(name="dir")
def state_dir(opt: Options | None = None):
    """Show the application state directory."""
    config = load_config(opt)
    print(config.opt.state_dir)


@state_app.command(name="clean")
def state_clean(opt: Options | None = None):
    """Clear application state files."""
    config = load_config(opt)
    if config.dry_run and not config.quiet:
        print("DRY-RUN. No state files will be deleted.")
    if not config.quiet:
        print(f"Clearing {config.state_dir}")
        files = "\n".join(str(x) for x in config.state_dir.glob("**/*") if x.is_file())
        if files:
            print(files)
    if not config.dry_run:
        with suppress(FileNotFoundError):
            rmtree(config.state_dir)


@state_app.command(name="list", alias=["ls"])
def state_list(opt: Options | None = None):
    """List application state files."""
    config = load_config(opt)
    files = "\n".join(str(x) for x in config.state_dir.glob("**/*") if x.is_file())
    print(files)


@app.command
def clean(opt: Options | None = None):
    """Clean cache and state files."""
    cache_clean(opt)
    state_clean(opt)


@theme_app.command(name="info")
def theme_info(
    palette: str,
    gamut: ColorSpace = ColorSpace.srgb,
    color_rep: ColorRep = ColorRep.hex,
    opt: Options | None = None,
):
    """Show information about a particular theme.

    Usage examples:
    - hdl theme info --palette="hadalized-dark" --gamut="srgb" --color-rep="hex"

    Args:
        palette: The name of the palette to resolve the theme against.
        gamut: The colorspace to use.
        color_rep: Color representation.
        opt: Additional options

    """
    opt = opt or Options()
    config = load_config(opt)

    raw_palette = config.palettes[palette]
    theme = config.theme.resolve(raw_palette.transform(gamut, color_rep))
    jdata = theme.model_dump_json(exclude_unset=True, indent=4)
    print_json(jdata)


# @app.command
# def debug(opt: Options | None = None):
#     """Debug things."""
#
#     config = load_config(opt)
#     print(f"{config.cache_dir=}")
#     print(f"{config.dry_run=}")
#     print(f"{opt=}")
#     if opt is not None:
#         print(f"{opt.model_fields_set=}")
#     print("config.opt")
#     print_json(config.opt.model_dump_json())
#     print(f"{config.model_fields_set=}")
#     print(f"{config.opt.model_fields_set=}")
