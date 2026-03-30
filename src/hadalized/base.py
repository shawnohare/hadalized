"""Base container for all model classes."""

from importlib.metadata import version
from pathlib import Path
from typing import ClassVar, Literal, Self

import xdg_base_dirs
from pydantic import PrivateAttr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    # TomlConfigSettingsSource,
)

APP_NAME: str = "hadalized"
APP_DIR = Path(APP_NAME)
APP_VERSION = version("hadalized")


class BaseNode(BaseSettings):
    """An extension of BaseSettings that all model classes inherit.

    Unless overriden, by default only initialization settings are respected.

    Full setting sources are exposed in the ``UserConfig`` subclass.
    """

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        frozen=True,
        extra="forbid",
    )

    _hash: int | None = PrivateAttr(default=None)
    """Cached hash computation so that instances can be passed to cached
    functions and used in dicts."""

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

    @property
    def app_info(self) -> str:
        """App name and version."""
        return f"{APP_NAME} v{APP_VERSION}"

    def model_dump_set(  # noqa: PLR0913
        self,
        *,
        mode: Literal["json", "python"] = "python",
        exclude: set[str] | None = None,
        exclude_computed_fields: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        include: set[str] | None = None,
    ) -> dict:
        """Dump only set items.

        Returns:
            A dict containing only the set fields.

        """
        return self.model_dump(
            mode=mode,
            exclude=exclude,
            exclude_computed_fields=exclude_computed_fields,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            exclude_unset=True,
            include=include,
        )

    def model_dump_lua(  # noqa: PLR0913
        self,
        *,
        indent: str | None = "  ",
        indent_level: int = 0,
        exclude: set[str] | None = None,
        exclude_computed_fields: bool = False,
        exclude_defaults: bool = False,
        exclude_unset: bool = False,
        exclude_none: bool = False,
        include: set[str] | None = None,
    ) -> str:
        """Dump the model as a lua table.

        Returns:
            A human readable lua table string.

        """
        import luadata

        # TODO: Unclear if we want to import luadata just for this
        data = self.model_dump(
            mode="json",
            exclude=exclude,
            exclude_computed_fields=exclude_computed_fields,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
            include=include,
        )
        return luadata.serialize(data, indent=indent, indent_level=indent_level)

    # def set(self, field: str, val):
    #     """Set a model field, even in frozen models.
    #
    #     Raises:
    #         KeyError: If the field is not defined.
    #
    #     """
    #     if field not in self.__class__.model_fields:
    #         raise KeyError(f"Unknown field {field}")
    #     self.__dict__[field] = val
    #     self._hash = 0

    def __getitem__(self, key: str):
        """Provide dict-like lookup for all models.

        Returns:
            The field specified by the input key.

        """
        return getattr(self, key)

    def __hash__(self) -> int:
        """Make an instance hashable for use in cache and dict lookups.

        Defined for type checking purposes. Frozen models are hashable.

        Returns:
            The BaseModel hash.

        """
        if self._hash is None:
            hashed = hash(self.model_dump_json()) or 0
            self._hash = hashed
        return self._hash

    def __len__(self) -> int:
        """Report the number of model fields.

        Returns:
            The length of the set of model fields.

        """
        return len(self.__class__.model_fields)

    # def merge(self, other: BaseNode) -> Self:
    #     """Merge in the set fields of the input.
    #
    #     Returns:
    #         A new instance of the same type as the original instance
    #         with the input fields merged in.
    #
    #     """
    #     self_fields = set(self.__class__.model_fields.keys())
    #     ldump = self.model_dump(exclude_unset=True)
    #     rdump = other.model_dump(exclude_unset=True, include=self_fields)
    #     for key, rval in rdump.items():
    #         if (lval := ldump.get(key)) is not None and isinstance(
    #             rval, (BaseNode, dict)
    #         ):
    #             ldump[key] = lval | rval
    #         else:
    #             ldump[key] = rval
    #     return self.model_validate(ldump)

    def __or__(self, other: Self) -> Self:
        """Merge two instances of the same type.

        Returns:
            A new instance of the right type in x | y.

        """
        return other.__ror__(self)

    def __ror__(self, other: BaseNode) -> Self:
        """Shallow right merge of explicitly set fields.

        Only the explicitly set fields of ``other`` are merged in.
        Fields that are BaseNodes are recursively merged, while dictionary
        fields are merged element-wise at a depth of 1.

        Args:
            other: An instance with the same or subset of fields as `self`.
               The left merge component in other | self

        Returns:
            A new instance of the same type with the set fields of `other` merged in.

        """
        # other | self
        self_fields = set(self.__class__.model_fields.keys())
        ldump = other.model_dump(exclude_unset=True, include=self_fields)
        for key, rval in self:
            if key not in self.model_fields_set:
                continue
            if (lval := ldump.get(key)) is not None and isinstance(
                rval, (BaseNode, dict)
            ):
                ldump[key] = lval | rval
            else:
                ldump[key] = rval
        return self.model_validate(ldump)


class Home:
    """Application home directories.

    Directories follow the XDG specification.
    """

    @staticmethod
    def config() -> Path:
        """Application user configuration home.

        Returns:
            The application configuration home directory.

        """
        return xdg_base_dirs.xdg_config_home() / APP_DIR

    @staticmethod
    def cache() -> Path:
        """Application cache home.

        Returns:
            The application configuration home directory.

        """
        return xdg_base_dirs.xdg_cache_home() / APP_DIR

    @staticmethod
    def state() -> Path:
        """Application state home.

        Returns:
            The application configuration home directory.

        """
        return xdg_base_dirs.xdg_state_home() / APP_DIR

    @staticmethod
    def data() -> Path:
        """Application data home.

        Returns:
            The application configuration home directory.

        """
        return xdg_base_dirs.xdg_data_home() / APP_DIR

    @classmethod
    def template(cls) -> Path:
        """Application user config templates home.

        Returns:
            The application configuration home directory.

        """
        return cls.config() / "templates"

    @classmethod
    def build(cls) -> Path:
        """Application home for built themes.

        Returns:
            The application configuration home directory.

        """
        return cls.state() / "build"
