"""Lua utilities."""


def dumps(data, indent: str | None = "    ", indent_level: int = 0):
    """Wrap luadata.serialize.

    Returns:
        Serialized lua data.

    """
    import luadata

    return luadata.serialize(data, indent=indent, indent_level=indent_level)
