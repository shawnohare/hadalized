"""Render templates and write outputs."""

from contextlib import suppress
from functools import cache
from hashlib import blake2b
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

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

from hadalized import utils
from hadalized.base import APP_NAME
from hadalized.cache import Cache
from hadalized.config import ContextType
from hadalized.theme import ThemeCollection

if TYPE_CHECKING:
    from hadalized.config import BuildConfig, Config, Context


@cache
def _encode(val: Template | Context) -> bytes:
    if isinstance(val, Template):
        data: bytes = b"null"
        if (fname := val.filename) is not None:
            with suppress(FileNotFoundError):
                data = Path(fname).read_bytes()
    else:
        data = val.model_dump_json().encode()

    return data


def _hash(template: Template, context: Context) -> str:
    data = _encode(template) + b":::" + _encode(context)
    return blake2b(data, digest_size=32).hexdigest()


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
        # Filter out excluded items.
        # self.palettes = [x for x in config.palettes.values() if config.is_included(x)]
        self.builds = [x for x in config.builds.values() if config.is_included(x)]
        # self.themes = [x for x in config.themes.values() if config.is_included(x)]

        self.cache = Cache(config)
        self._fs_template_env = Environment(
            loader=FileSystemLoader(searchpath=config.template_dir),
            undefined=StrictUndefined,
            autoescape=select_autoescape("html", "xml"),
        )
        self.config = config

    def _must_build(self, path: Path, digest: str) -> bool:
        """Whether a particular file has been generated.

        Returns:
            A bool indicating that a theme template file should be regenerated.
            This can either because the user forces a rebuild, ignores the
            cache, or the output of an existing build would change.

        """
        return (
            self.config.force
            or self.config.no_cache
            or not path.exists()
            or self.cache.get(path) != digest
        )

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

    def copy_file(self, build_path: Path) -> Path | None:
        """Copy a built theme file to an output directory.

        Args:
            build_path: Path to a built theme file, typically saved in
                the applicate state directory.

        Returns:
            The path of the copied file or None if no copy was performed.

        """
        opt = self.config
        if opt.output_dir is None:
            return None

        output_dir = opt.output_dir
        if opt.prefix:
            output_dir /= build_path.parent.name
        copy_path = (output_dir / build_path.name).absolute()
        if not opt.quiet:
            logger.info(f"Copying {build_path} to {output_dir}")
        if not opt.dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            build_path.copy(copy_path)
        return copy_path

    def build_file(
        self,
        bconf: BuildConfig,
        context: Context,
    ) -> tuple[Path, bool]:
        """Build a single color theme file.

        When an output dir is specified, the generated file is copied to
        the output dir from the application state directory.

        Returns:
            A path of the built file and whether it was generated.

        """
        opt = self.config
        template = self.get_template(bconf.template)
        path = self.config.build_dir / bconf.format_path(context)
        digest = _hash(template, context)

        if self._must_build(path, digest):
            if not opt.quiet:
                logger.info(f"Building {path} {digest}.")
            text = template.render(context=context, build=bconf, utils=utils)
            if not opt.dry_run:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            if opt.use_cache and not opt.dry_run:
                self.cache.add(path, digest)
            was_built = True
        else:
            if opt.verbose:
                logger.info(f"Already built {path} with hash {digest}.")
            was_built = False

        self.copy_file(path)
        return path, was_built

    def build(self, bconf: BuildConfig) -> list[Path]:
        """Generate color theme files for a specific app.

        Args:
            bconf: A configuration specifying how theme files shoud be built.

        Returns:
            A list of theme file paths that were built.

        """
        opt = self.config
        if opt.verbose:
            logger.info(f"Handling themes for {bconf.name}.")

        themes = (
            theme.make(pal.transform(bconf.gamut, bconf.color_rep))
            for theme, pal in self.config.pairs()
        )

        match bconf.context_type:
            case ContextType.theme:
                contexts = themes
            case ContextType.full:
                contexts = [ThemeCollection(themes=tuple(themes))]

        return [
            path
            for path, was_built in (self.build_file(bconf, ctx) for ctx in contexts)
            if was_built
        ]

    def run(self) -> list[Path]:
        """Generate all relevant app theme files.

        Returns:
            A list of file paths that were generated.

        """
        return [p for paths in (self.build(x) for x in self.builds) for p in paths]

    def __enter__(self):
        """Connect to the cache.

        Returns:
            The instance with a connection to the cache db.

        """
        if self.config.use_cache:
            self.cache.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close cache db connection."""
        if exc_type is not None:
            logger.error((exc_type, exc_value, traceback))
        if self.config.use_cache:
            self.cache.close()
