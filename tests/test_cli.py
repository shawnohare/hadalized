from pathlib import Path

import pytest

from hadalized.cli import main as m
from hadalized.config import Options

FNAME = "hadalized-dark.lua"


@pytest.fixture
def realopts(tmp_path: Path) -> Options:
    return Options(
        include_palettes={"hadalized-dark"},
        prefix=True,
        state_dir=tmp_path / "state",
        output_dir=tmp_path / "output",
        cache_dir=tmp_path / "cache",
        no_config=True,
        verbose=True,
    )


@pytest.fixture
def dryopts(tmp_path: Path) -> Options:
    return Options(
        include_palettes={"hadalized-dark"},
        prefix=True,
        state_dir=tmp_path / "state",
        output_dir=tmp_path / "output",
        cache_dir=tmp_path / "cache",
        no_config=True,
        verbose=True,
        dry_run=True,
    )


def test_build_single_app(realopts: Options):
    opt = realopts
    m.build(opt=opt | Options(include_apps={"neovim"}))
    assert opt.output_dir is not None
    assert (opt.output_dir / "neovim" / FNAME).exists()


def test_build_single_app_no_copy(realopts: Options):
    opt = realopts | Options(output_dir=None)
    m.build(opt=opt | Options(include_apps={"starship"}))
    assert realopts.output_dir is not None
    assert not (realopts.output_dir / "starship" / "hadalized-dark.toml").exists()


def test_build_all(realopts: Options):
    opt = realopts
    assert opt.output_dir is not None
    m.build(opt=opt)


def test_build_single_app_dry(dryopts: Options):
    opt = dryopts
    m.build(opt=opt)


def test_cache_list():
    m.cache_list()


def test_cache_dir():
    m.cache_dir()


def test_state_list():
    m.state_list()


def test_state_dir():
    m.state_dir()


def test_clean(realopts: Options, dryopts: Options):
    realopts.state_dir.mkdir(parents=True, exist_ok=True)
    realopts.cache_dir.mkdir(parents=True, exist_ok=True)
    db_file = realopts.state_dir / "test.db"
    log_file = realopts.cache_dir / "test.log"
    db_file.touch()
    log_file.touch()
    m.clean(realopts)
    assert not db_file.exists()
    assert not log_file.exists()
    m.clean(dryopts)


def test_config_init_output_file_given(tmp_path: Path):
    output = tmp_path / "hadalized.toml"
    # Initial generation.
    m.config_init(Options(output_dir=output, no_config=True))
    assert output.exists()
    # Force re-generation
    m.config_init(Options(output_dir=output, no_config=True, force=True))
    assert output.exists()
    # Exit early since file exists.
    m.config_init(Options(output_dir=output, no_config=True))
    assert output.exists()


def test_config_init_output_dir_given(tmp_path: Path):
    # No name given to file
    opt = Options(output_dir=tmp_path, no_config=True)
    m.config_init(opt)
    assert (tmp_path / "config.toml").exists()
    m.config_init(Options(output_dir=tmp_path, no_config=True, dry_run=True))


def test_config_init_dry_run_does_not_create_file(tmp_path: Path):
    output = tmp_path / "config.toml"
    m.config_init(Options(output_dir=output, no_config=True, dry_run=True, quiet=True))
    assert not output.exists()


def test_config_options():
    m.config_options()


def test_config_init_output_stdout():
    m.config_init(Options(output_dir=Path("stdout"), no_config=True))


def test_config_schema():
    m.config_schema()


def test_palette_info():
    m.palette_info(name="hadalized-dark")


def test_theme_info(realopts: Options):
    m.theme_info(palette="hadalized-dark", opt=realopts)
