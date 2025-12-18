# Tower - GitHub Repository Management

default:
    @just --list

# Install all dependencies
install:
    uv sync --all-extras

# Run all tests
test:
    uv run pytest

# Run a specific test
test-one TEST:
    uv run pytest {{TEST}} -v

# Run tests with coverage
test-cov:
    uv run pytest --cov=tower --cov-report=term-missing

# Lint code
lint:
    uv run ruff check .

# Format code
fmt:
    uv run ruff format .

# Fix lint issues
fix:
    uv run ruff check . --fix

# Type check
typecheck:
    uv run pyright

# Run all checks (lint, typecheck, test)
check: lint typecheck test

# Pulumi preview
preview:
    uv run pulumi preview

# Pulumi deploy
deploy:
    uv run pulumi up

# Pulumi destroy
destroy:
    uv run pulumi destroy
