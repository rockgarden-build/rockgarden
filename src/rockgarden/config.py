"""Configuration loading and defaults for rockgarden."""

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class SiteConfig(BaseModel):
    """Site-level configuration."""

    title: str = "My Site"
    description: str = ""
    og_image: str = ""
    source: Path = Path(".")
    output: Path = Path("_site")
    clean_urls: bool = True
    base_url: str = ""
    base_path: str = ""
    url_style: str = "slug"

    @field_validator("url_style", mode="after")
    @classmethod
    def validate_url_style(cls, v: str) -> str:
        allowed = ("slug", "preserve-case", "preserve")
        if v not in allowed:
            msg = f"url_style must be one of {allowed}, got {v!r}"
            raise ValueError(msg)
        return v

    @field_validator("base_url", mode="after")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")

    @field_validator("base_path", mode="after")
    @classmethod
    def normalize_base_path(cls, v: str) -> str:
        v = v.rstrip("/")
        if v and not v.startswith("/"):
            v = "/" + v
        return v


class BuildConfig(BaseModel):
    """Build-related configuration."""

    ignore_patterns: list[str] = [
        ".obsidian",
        "private",
        "templates",
        "Templates",
        "_static",
    ]
    icons_dir: Path | None = None
    assets_dir: str = "_assets"
    inline_icons: bool = True


class ThemeConfig(BaseModel):
    """Theme configuration.

    Contains both theme-general settings (which any well-built theme should
    honour) and default-theme-specific settings (DaisyUI, build info footer,
    nav display state).
    """

    # Theme selection
    name: str = ""
    default_layout: str = ""

    # Theme-general feature flags
    toc: bool = True
    backlinks: bool = True
    search: bool = True
    tag_index: bool = True

    # Math rendering
    math: bool = False

    # Default theme specific
    daisyui_default: str = "light"
    daisyui_themes: list[str] = Field(default_factory=list)
    nav_default_state: str = "collapsed"
    show_build_info: bool = True
    show_build_commit: bool = False
    main_content_padding: str = "px-12"


class NavLinkConfig(BaseModel):
    """A custom navigation link entry (supports nesting)."""

    label: str
    url: str = ""
    children: list["NavLinkConfig"] = Field(default_factory=list)


NavLinkConfig.model_rebuild()


class NavConfig(BaseModel):
    """Navigation structure configuration."""

    hide: list[str] = Field(default_factory=list)
    labels: dict[str, str] = Field(default_factory=dict)
    sort: str = "files-first"
    link_auto_index: bool = False
    links: list[NavLinkConfig] = Field(default_factory=list)
    links_position: str = "after"


class TocConfig(BaseModel):
    """Table of contents extraction configuration."""

    max_depth: int = 4


class SearchConfig(BaseModel):
    """Search index configuration."""

    include_content: bool = True


class DatesConfig(BaseModel):
    """Date display configuration."""

    modified_date_fields: list[str] = ["modified", "updated", "last_modified"]
    created_date_fields: list[str] = ["created", "date", "date_created"]
    modified_date_fallback: bool = False
    timezone: str = "UTC"


class FeedConfig(BaseModel):
    """Atom feed configuration."""

    enabled: bool = False
    path: str = "/feed.xml"
    limit: int = 20
    author: str = ""
    include_paths: list[str] = Field(default_factory=list)
    collections: list[str] = Field(default_factory=list)


class LlmsTxtConfig(BaseModel):
    """llms.txt generation configuration."""

    enabled: bool = False
    description: str = ""
    full: bool = False


class HooksConfig(BaseModel):
    """Build hook commands executed at lifecycle stages."""

    pre_build: list[str] = Field(default_factory=list)
    post_collect: list[str] = Field(default_factory=list)
    post_build: list[str] = Field(default_factory=list)


class CollectionConfig(BaseModel):
    """Configuration for a named content collection."""

    name: str
    source: str
    template: str | None = None
    url_pattern: str | None = None
    pages: bool = True
    nav: bool = False
    model: str | None = None


class Config(BaseModel):
    """Root configuration object."""

    site: SiteConfig = Field(default_factory=SiteConfig)
    build: BuildConfig = Field(default_factory=BuildConfig)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    nav: NavConfig = Field(default_factory=NavConfig)
    toc: TocConfig = Field(default_factory=TocConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    dates: DatesConfig = Field(default_factory=DatesConfig)
    feed: FeedConfig = Field(default_factory=FeedConfig)
    llms_txt: LlmsTxtConfig = Field(default_factory=LlmsTxtConfig)
    hooks: HooksConfig = Field(default_factory=HooksConfig)
    collections: list[CollectionConfig] = Field(default_factory=list)

    @classmethod
    def load(cls, config_path: Path | None = None) -> "Config":
        """Load configuration from TOML file.

        Args:
            config_path: Path to config file. If None, looks for rockgarden.toml
                        in current directory.

        Returns:
            Config object with values from file merged with defaults.
        """
        if config_path is None:
            config_path = Path("rockgarden.toml")

        if not config_path.exists():
            return cls()

        with open(config_path, "rb") as f:
            data = tomllib.load(f)

        return cls.model_validate(data)
