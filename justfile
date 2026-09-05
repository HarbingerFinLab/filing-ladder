_env := ".env"

default:
    @just --list

# Create the virtual environment and install everything
venv:
    uv venv
    @just install

# Install dependencies; provisions .env from the template and the git hooks on first run
install:
    @test -f {{_env}} || cp .env.example {{_env}}
    @just install-hooks
    uv sync --all-extras

# Point git at the repo's hooks (idempotent)
install-hooks:
    git config core.hooksPath .githooks

# Upgrade the lockfile
update:
    uv lock --upgrade
    uv sync --all-extras

# The tools live in the `dev` extra. Naming it here means a plain `uv sync`, which prunes
# extras, cannot leave `uv run pytest` falling through to whatever pytest is on PATH.
test:
    uv run --extra dev pytest -q

lint:
    uv run --extra dev ruff check .
    uv run --extra dev ruff format --check .

format:
    uv run --extra dev ruff format .
    uv run --extra dev ruff check --fix .

typecheck:
    uv run --extra dev basedpyright

test-all:
    @just test
    @just lint
    @just typecheck

# Materialize one filing into every representation (-> ./data/<accession>/)
materialize cik accno:
    uv run filing-ladder materialize --cik {{cik}} --accno {{accno}}

# Token table for a materialized filing (bytes/4 estimate; --exact uses the Anthropic token counter)
tokens accno *args:
    uv run filing-ladder tokens --accno {{accno}} {{args}}

# Validate the question sets and print their pre-registration hashes
questions:
    uv run filing-ladder questions

# Run rungs on a question set (see `filing-ladder run --help`)
run *args:
    uv run filing-ladder run {{args}}

# Write the question-set manifest the frozen protocol publishes, and show the tag command
freeze:
    uv run filing-ladder tokens-export
    uv run filing-ladder questions > questions/manifest.json
    @echo "questions/manifest.json written — commit it, then tag: git tag -a protocol-vX.Y -m 'Filing Ladder protocol vX.Y'"

# Create a feature branch from origin/main and push it (the only way branches are created here)
create-feature branch_type="feature" branch_name="" base_branch="main" update="no":
    bin/create-feature.sh {{branch_type}} {{branch_name}} {{base_branch}} {{update}}

clean:
    rm -rf .pytest_cache .ruff_cache
    find . -type d -name "__pycache__" -exec rm -rf {} +

help:
    @just --list
