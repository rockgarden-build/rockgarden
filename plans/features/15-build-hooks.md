# Feature 15: Build Hooks

Shell commands executed at build lifecycle stages.

## Status: Complete

## Goal

```toml
[hooks]
pre_build = ["python scripts/fetch_data.py"]
post_collect = ["python scripts/generate_og_images.py"]
post_build = ["npx tailwindcss -o _site/css/styles.css --minify"]
```

Hooks keep the core unopinionated while enabling:
- External data fetching before build
- Derived asset generation from collected data (OG images, search indexes)
- CSS/JS compilation after build
- Image optimization
- Any custom processing

## Use Cases

- Fetch conference data from APIs before building
- Generate OpenGraph preview images from page metadata (post-collect)
- Build a search index from collected content (post-collect)
- Compile SCSS or run Tailwind JIT after HTML is generated
- Optimize images in the output directory
- Run linters or validators on output

## Configuration

```toml
[hooks]
pre_build = [
    "python scripts/fetch_data.py",
    "python scripts/download_images.py",
]
post_collect = [
    "python scripts/generate_og_images.py",
]
post_build = [
    "npx tailwindcss -i _site/css/input.css -o _site/css/styles.css --minify",
]
```

Commands run sequentially within each stage. Build aborts if any command fails.

## Hook Stages

| Stage | When | Content Data Available | Use Cases |
|---|---|---|---|
| `pre_build` | Before content loading | No | Data fetching, file generation |
| `post_collect` | After content collected, before render | Yes (JSON export) | Derived assets (OG images), search index, data transforms |
| `post_build` | After all output written | Yes (JSON export) | Asset compilation, optimization, validation |

The `post_collect` stage is critical — it runs after content is collected and exported to `.rockgarden/content.json` (Feature 14), so hook scripts can read and query content data to generate derived assets.

## Implementation Plan

### 1. Config

```python
@dataclass
class HooksConfig:
    pre_build: list[str] = field(default_factory=list)
    post_collect: list[str] = field(default_factory=list)
    post_build: list[str] = field(default_factory=list)
```

### 2. Hook Runner

```python
def run_hooks(commands: list[str], stage: str) -> None:
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, cwd=source_dir)
        if result.returncode != 0:
            raise BuildError(f"Hook failed at {stage}: {cmd}")
```

### 3. Integration

In `builder.py`, wrap the build pipeline:
1. Run `pre_build` hooks
2. Load content into collections, export to `.rockgarden/content.json`
3. Run `post_collect` hooks (content JSON available)
4. Render templates, write output
5. Run `post_build` hooks

## Open Questions (Resolve During Implementation)

Decide and document during implementation, informed by deploying example sites:

- **Environment variables**: What vars are passed to hooks? (source dir, output dir, content data path, etc.)
- **Working directory**: What is `cwd` for hook execution? Document for hook authors.
- **Output/logging**: Display hook stdout/stderr by default? Quiet mode? Verbose flag?
- **Timeout**: Default timeout for hung hooks?
- **Error reporting**: How much context on hook failure? (command, exit code, stderr?)

TODO: Write a hook authoring guide once these are settled.

## Key Files to Create/Modify

- `config.py` — Add `HooksConfig` dataclass
- `hooks.py` — New module: hook runner
- `output/builder.py` — Call hooks at appropriate stages
