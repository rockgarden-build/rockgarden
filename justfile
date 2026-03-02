_default:
    @just --list

# Install dependencies
install:
    uv sync
    npm install

# Lint and format check
check:
    uv run ruff check .
    uv run ruff format --check .

alias lint := check

# Auto-fix lint issues and format
format:
    uv run ruff check --fix .
    uv run ruff format .

alias fmt := format

# Run all tests
test *ARGS:
    uv run pytest {{ARGS}}

# Run tests and lint/format check (CI equivalent)
ci: check test

# Build the demo site (./site)
build *ARGS:
    uv run rockgarden build --clean {{ARGS}}

# Build the docs site (./docs)
build-docs *ARGS:
    uv run rockgarden build --source docs/ --output _site/ --clean {{ARGS}}

# Serve the output directory locally
serve:
    uv run rockgarden serve

# Compile Tailwind CSS
css:
    npm run build:css

# Watch and recompile Tailwind CSS
css-watch:
    npm run watch:css
