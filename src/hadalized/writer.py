"""Render templates and write outputs."""

from contextlib import suppress
from functools import cache
from hashlib import blake2b
from pathlib import Path
from typing import ClassVar, final, override

from jinja2 import (
    Environment,
    FileSystemLoader,
    PackageLoader,
    StrictUndefined,
    Template,
    TemplateNotFound,
    select_autoescape,
)
from loguru import logger
from pydantic import BaseModel

from hadalized import utils
from hadalized.base import APP_NAME, BaseNode
from hadalized.config import AppConfig, Config, Options
from hadalized.palette import Palette, PaletteMetadata  # noqa: TC001
from hadalized.theme import Theme  # noqa: TC001


class Context(BaseNode):
    """Main context data passed to a template."""

    palette: Palette
    """Palette with application specific transformation applied."""
    theme: Theme
    """Concrete theme with colors resolved against the `palette`."""
    app: AppConfig
    """Application specific build configuration."""

    @override
    def __hash__(self) -> int:
        return super().__hash__()


class FileBuildInfo(BaseModel):
    """Information about a built theme file."""

    app: AppConfig
    palette_meta: PaletteMetadata
    path: Path
    digest: str
    cache_used: bool
    copy_path: Path | None


class RunInfo(BaseModel):
    """Information about a run of a ThemeWritter instance."""

    opt: Options
    files: list[FileBuildInfo]


@cache
def _encode_template(val: Template) -> bytes:
    data: bytes = b"null"
    if (fname := val.filename) is not None:
        with suppress(FileNotFoundError):
            data = Path(fname).read_bytes()
    return data


def _hash(template: Template, context: Context) -> str:
    data = _encode_template(template) + b":" + context.model_dump_json().encode()
    return blake2b(data, digest_size=32).hexdigest()


@final
class ThemeWriter:
    """Generate application theme files."""

    _package_template_env: ClassVar[Environment] = Environment(
        loader=PackageLoader(APP_NAME),
        undefined=StrictUndefined,
        # autoescape=True,
        autoescape=select_autoescape("html", "xml"),
    )

    def __init__(self, config: Config):
        """Prepare an instance for writing files.

        Initializtion does not connect to the cache database or write
        any files.

        Args:
            config: A configuration instance if customization is required.

        """
        # self.cache: Cache = Cache(config)
        self._fs_template_env = Environment(
            loader=FileSystemLoader(searchpath=config.template_dir),
            undefined=StrictUndefined,
            autoescape=select_autoescape("html", "xml"),
        )
        self.config: Config = config

    def get_template(self, name: str | Path) -> Template:
        """Load theme template.

        Returns:
            A jinja2.Template instance.

        """
        tname = str(name)
        if self.config.no_templates or self.config.no_config:
            template = self._package_template_env.get_template(tname)
        else:
            try:
                template = self._fs_template_env.get_template(tname)
            except TemplateNotFound:
                template = self._package_template_env.get_template(tname)
        return template

    def _copy_file(self, context: Context, build_path: Path) -> Path | None:
        opt = self.config
        app = context.app

        if opt.output_name is not None:
            copy_path = opt.output_name.absolute()
        elif opt.output_dir is not None:
            output_dir = opt.output_dir / app.name
            if not opt.prefix:
                output_dir = output_dir.parent
            fname = context.palette.name + app.extension
            copy_path = (output_dir / fname).absolute()
        else:
            return None

        if not opt.quiet:
            logger.info(f"Copying {build_path} to {copy_path}")
        if not opt.dry_run:
            copy_path.parent.mkdir(parents=True, exist_ok=True)
            _ = build_path.copy(copy_path)
        return copy_path

    def build_file(self, context: Context) -> FileBuildInfo:
        """Build a single color theme file.

        When an output dir is specified, the generated file is copied to
        the output dir from the application state directory.

        Returns:
            A path of the built file and whether it was generated.

        """
        app = context.app
        opt = self.config
        template = self.get_template(app.template)
        digest = _hash(template, context)
        path = opt.build_dir / digest

        # Generate file and write to build dir if necessary.
        if opt.force or opt.no_cache or not path.exists():
            if not opt.quiet:
                logger.info(f"Building {path}.")
            text = template.render(
                theme=context.theme,
                palette=context.palette,
                app=context.app,
                config=self.config,
                utils=utils,
            )
            if not opt.dry_run:
                path.parent.mkdir(parents=True, exist_ok=True)
                _ = path.write_text(text, encoding="utf-8")
            was_built = True
        else:
            if opt.verbose:
                logger.info(f"Already built {path}.")
            was_built = False

        copy_path = self._copy_file(context, path)

        return FileBuildInfo(
            app=app,
            palette_meta=context.palette.meta,
            path=path,
            cache_used=not was_built,
            copy_path=copy_path,
            digest=digest,
        )

    def build(self, app_config: AppConfig) -> list[FileBuildInfo]:
        """Generate color theme files for a specific application.

        Args:
            app_config: A configuration specifying how theme files shoud be built.

        Returns:
            A list of theme file paths and an indicator which was built.

        """
        opt = self.config

        # Apply config overrides to application config if necessary.
        if opt.gamut or opt.color_rep:
            app_config |= AppConfig(
                name=app_config.name,
                template=app_config.template,
                gamut=opt.gamut or app_config.gamut,
                color_rep=opt.color_rep or app_config.color_rep,
            )

        def make_context(raw_palette: Palette) -> Context:
            palette = raw_palette.transform(app_config.gamut, app_config.color_rep)
            return Context(
                palette=palette,
                theme=opt.theme.resolve(palette),
                app=app_config,
            )

        if opt.verbose:
            logger.info(f"Handling themes for {app_config.name}.")
        return [
            self.build_file(make_context(p))
            for p in self.config.palettes.values()
            if self.config.is_included(p)
        ]

    def run(self) -> RunInfo:
        """Generate all relevant app theme files.

        Returns:
            A list of file paths that were generated.

        """
        config = self.config
        builds = (self.build(x) for x in config.apps.values() if config.is_included(x))
        files = [p for paths in builds for p in paths]
        return RunInfo(
            opt=config.opt,
            files=files,
        )

    def __enter__(self):
        """Connect to the cache.

        Returns:
            The instance with a connection to the cache db.

        """
        # NOTE: Could be useful to keep around for storing application state.
        # if self.config.use_cache:
        #     self.cache.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close cache db connection."""
        if exc_type is not None:
            logger.error((exc_type, exc_value, traceback))
        # NOTE: Could be useful to keep around for storing application state.
        # if self.config.use_cache:
        #     self.cache.close()
