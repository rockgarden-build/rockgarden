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


@dataclass
class BuildConfig:
    """Build-related configuration."""

    ignore_patterns: list[str] = field(
        default_factory=lambda: [".obsidian", "private", "templates", "Templates"]
    )


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
class SearchConfig:
    """Search configuration."""

    enabled: bool = True
    include_content: bool = True


@dataclass
class Config:
    """Root configuration object."""

    site: SiteConfig = field(default_factory=SiteConfig)
    build: BuildConfig = field(default_factory=BuildConfig)
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    nav: NavConfig = field(default_factory=NavConfig)
    backlinks: BacklinksConfig = field(default_factory=BacklinksConfig)
    search: SearchConfig = field(default_factory=SearchConfig)

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
        search_data = data.get("search", {})

        site = SiteConfig(
            title=site_data.get("title", SiteConfig.title),
            source=Path(site_data.get("source", ".")),
            output=Path(site_data.get("output", "_site")),
            clean_urls=site_data.get("clean_urls", True),
        )

        build = BuildConfig(
            ignore_patterns=build_data.get(
                "ignore_patterns", BuildConfig().ignore_patterns
            ),
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

        search = SearchConfig(
            enabled=search_data.get("enabled", True),
            include_content=search_data.get("include_content", True),
        )

        return cls(
            site=site,
            build=build,
            theme=theme,
            nav=nav,
            backlinks=backlinks,
            search=search,
        )
