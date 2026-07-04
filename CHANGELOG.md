# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.7.0] -- 2025-03-30

Introduce an initial, experimental theme abstraction `Theme` class that
defines a family of universal `Theme` structures parameterized over palettes.
The abstract theme model is based heavily on neovim's highlight groups.

Universal `Theme` instances now are the primary context passed to templates,
and the underlying build configuration is also passed in as context. This
exposes more semantically meaningful palette references, e.g., one can
use the effective aliases `theme.main.fg` or `theme.string.fg` instead of
pure colors.


## [0.6.0] -- 2025-02-19

Simplify ColorInfo object.

## [0.5.0] -- 2025-02-04

Use dedicated dotenv file.

- Only inspect `hadalized.env` files for configuration options.
- Add `config options` subcommand to inspect configuration options.

BaseSettings appears to pass the entire contents of a dotenv file as
init args, which causes validation errors when extra init args are
forbidden.

## [0.4.0] -- 2026-02-04

### Added
- Load user defined config and template files.
- Suppport dry-runs.

## [0.3.0] -- 2026-01

### Added
- Introduce proper cli as main entry point via cyclopts.
- Targetted builds.
- Lazy `ColorInfo` parsing.
