"""Configuration loading and defaults for rockgarden."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SiteConfig:
    """Site-level configuration."""

    title: str = "My Site"
    source: Path = field(default_factory=lambda: Path("."))
    output: Path = field(default_factory=lambda: Path("_site"))
    clean_urls: bool = True
    base_url: str = ""


@dataclass
class BuildConfig:
    """Build-related configuration."""

    ignore_patterns: list[str] = field(
        default_factory=lambda: [".obsidian", "private", "templates", "Templates"]
    )
    icons_dir: Path | None = None
    show_build_info: bool = True


@dataclass
class ThemeConfig:
    """Theme configuration."""

    name: str = ""
    daisyui_default: str = "light"
    daisyui_themes: list[str] = field(default_factory=list)


@dataclass
class NavConfig:
    """Navigation configuration."""

    default_state: str = "collapsed"
    hide: list[str] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    sort: str = "files-first"
    link_auto_index: bool = False


@dataclass
class BacklinksConfig:
    """Backlinks configuration."""

    enabled: bool = True


@dataclass
class TocConfig:
    """Table of contents configuration."""

    enabled: bool = True
    max_depth: int = 4


@dataclass
class SearchConfig:
    """Search configuration."""

    enabled: bool = True
    include_content: bool = True


@dataclass
class DatesConfig:
    """Date display configuration."""

    modified_date_fields: list[str] = field(
        default_factory=lambda: ["modified", "updated", "last_modified"]
    )
    created_date_fields: list[str] = field(
        default_factory=lambda: ["created", "date", "date_created"]
    )
    modified_date_fallback: bool = True


@dataclass
class Config:
    """Root configuration object."""

    site: SiteConfig = field(default_factory=SiteConfig)
    build: BuildConfig = field(default_factory=BuildConfig)
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    nav: NavConfig = field(default_factory=NavConfig)
    backlinks: BacklinksConfig = field(default_factory=BacklinksConfig)
    toc: TocConfig = field(default_factory=TocConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    dates: DatesConfig = field(default_factory=DatesConfig)

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

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create Config from dictionary (parsed TOML)."""
        site_data = data.get("site", {})
        build_data = data.get("build", {})
        theme_data = data.get("theme", {})
        nav_data = data.get("nav", {})
        backlinks_data = data.get("backlinks", {})
        toc_data = data.get("toc", {})
        search_data = data.get("search", {})
        dates_data = data.get("dates", {})

        site = SiteConfig(
            title=site_data.get("title", SiteConfig.title),
            source=Path(site_data.get("source", ".")),
            output=Path(site_data.get("output", "_site")),
            clean_urls=site_data.get("clean_urls", True),
            base_url=site_data.get("base_url", "").rstrip("/"),
        )

        icons_dir_raw = build_data.get("icons_dir")
        build = BuildConfig(
            ignore_patterns=build_data.get(
                "ignore_patterns", BuildConfig().ignore_patterns
            ),
            icons_dir=Path(icons_dir_raw) if icons_dir_raw else None,
            show_build_info=build_data.get("show_build_info", True),
        )

        theme = ThemeConfig(
            name=theme_data.get("name", ""),
            daisyui_default=theme_data.get("daisyui_default", "light"),
            daisyui_themes=theme_data.get("daisyui_themes", []),
        )

        nav = NavConfig(
            default_state=nav_data.get("default_state", "collapsed"),
            hide=nav_data.get("hide", []),
            labels=nav_data.get("labels", {}),
            sort=nav_data.get("sort", "files-first"),
            link_auto_index=nav_data.get("link_auto_index", False),
        )

        backlinks = BacklinksConfig(
            enabled=backlinks_data.get("enabled", True),
        )

        toc = TocConfig(
            enabled=toc_data.get("enabled", True),
            max_depth=toc_data.get("max_depth", 4),
        )

        search = SearchConfig(
            enabled=search_data.get("enabled", True),
            include_content=search_data.get("include_content", True),
        )

        dates_defaults = DatesConfig()
        dates = DatesConfig(
            modified_date_fields=dates_data.get(
                "modified_date_fields",
                dates_defaults.modified_date_fields,
            ),
            created_date_fields=dates_data.get(
                "created_date_fields",
                dates_defaults.created_date_fields,
            ),
            modified_date_fallback=dates_data.get(
                "modified_date_fallback", True
            ),
        )

        return cls(
            site=site,
            build=build,
            theme=theme,
            nav=nav,
            backlinks=backlinks,
            toc=toc,
            search=search,
            dates=dates,
        )
