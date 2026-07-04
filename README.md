# hadalized (hdl) color theme build

Python package with CLI to build hadalized-style application themes.

## Introduction

The application can build any theme conforming to the hadalized `Palette`
schema for any application with an `AppConfig` and appropriate theme
template.

The builtin [hadalized color palettes](./src/hadalized/config.py)
are defined as oklch color values. Application theme templates are rendered
with the appropriate color type (e.g., hex values for neovim). Under the hood
the `coloraide` python package is used to transform between colorspaces and fit
to gamuts.

Creating a theme builder arises from the desire to use the OKLCH color space
as the basis for any application color theme. When developing the palette, it
quickly becomes tedious to manually convert oklch values to their hex
equivalents.

The builder primarily targets the neovim colorscheme files in
[hadalized.nvim](https://github.com/hadalized/hadalized.nvim), as that is
the editor we primarily use.

## Installation (uv / pip)

We recommend installing the cli application via `uv`

```sh
uv tool install hadalized
```
which exposes the `hdl` application and its longform equivalent `hadalized`.


## Example CLI Usage


If the tool is installed via `uv tool install` or if the virtualenv is activated

```sh
# To build neovim color themes
hdl build --app=neovim --output-dir=colors --no-prefix  # -> colors/hadalized*.lua
# To build all color themes, with outputs to `./build`
hdl build --output-dir=build
```

## Development

Assuming `uv`, `just`, and `prek` are installed

```sh
uv sync --locked
source .venv/bin/activate
# make changes
just fmt
just check
just test
# commit changes
```

## Roadmap / TODOs

- [ ] Consider removing the "in-memory" cache functionality.
- [ ] (B) As an extension of (A), consider lightweight pandoc inspired features
  where an intermediate and generic theme can be defined and referenced in
  editor templates. For example, allow a user to define `integer = "blue"` and
  reference `theme.integer` to color neovim `Integer` highlight groups.
- [ ] Separate out application builder configs / builders from palette and
  themes from the main config. So in this way we can build for a collection of
  palettes and themes for each app independently of a single configuration
  file. Maybe this means allowing specification of a `palette-file` and
  `theme-file` and `build-file`

## References

VSCode, having perhaps more

- https://code.visualstudio.com/api/references/theme-color
- https://gist.github.com/AndreasBackx/ab5c7df0ef214a798cfa8fdeaf59197f
- https://gist.github.com/dcts/5b2af4c8b6918e7d35c4121f11d49fb1
