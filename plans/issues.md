# Known Issues

## CI

- **Bump version PRs don't trigger CI checks**: The `bump-version.yml` workflow uses `GITHUB_TOKEN` to push the branch and create the PR. GitHub suppresses workflow triggers from `GITHUB_TOKEN` to prevent loops, so test/lint/review workflows never run on bump PRs. Fix: use a GitHub App token instead of `GITHUB_TOKEN` for the push and PR creation steps.

## Performance

- **Mermaid ESM import lacks SRI integrity check**: KaTeX uses `integrity="sha384-..."` on its `<script>` tag, but ES module `import` statements don't support `integrity` directly. Could use an import map with integrity metadata to get equivalent protection. Low priority since the version is pinned.

## Feature gaps

- **Add brand icon library support**: Lucide intentionally excludes brand/logo icons. Need a second icon library for social/brand icons. The resolver's `LIBRARY_ALIASES` and multi-library dispatch are already wired up — implementation is mostly adding a new loader. Candidates: Simple Icons, Font Awesome, Iconify.

## Content

- **Flesh out example site and publish as demo**: The existing small example site isn't built or published anywhere. Expand it to cover most features and publish as a standalone demo site.
