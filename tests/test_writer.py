import pytest
from jinja2.exceptions import TemplateNotFound

from hadalized.config import AppConfig, Config
from hadalized.writer import ThemeWriter


def test_theme_writer_run_uses_cache(config: Config):
    with ThemeWriter(config) as writer:
        for item in writer.run().files:
            assert item.path.exists()
            assert item.cache_used is False
        for item in writer.run().files:
            assert item.cache_used is True


def test_dry_run_build(dry_config: Config, build_config: AppConfig):
    with ThemeWriter(dry_config) as writer:
        for item in writer.build(build_config):
            assert not item.path.exists()


def test_build_with_copy(config: Config, build_config: AppConfig):
    with ThemeWriter(config) as writer:
        for item in writer.build(build_config):
            assert item.copy_path is not None
            assert item.copy_path.exists()


def test_writer_exits_with_exception(config: Config):
    with pytest.raises(ValueError), ThemeWriter(config):
        raise ValueError("bomb")


def test_writer_get_package_template(config: Config):
    assert ThemeWriter(config).get_template("neovim.lua.jinja")


def test_writer_get_fs_template(config: Config):
    assert ThemeWriter(config).get_template("template.txt.j2")


def test_writer_get_template_fail():
    config = Config(no_templates=True)
    with pytest.raises(TemplateNotFound):
        _ = ThemeWriter(config).get_template("bomb")
