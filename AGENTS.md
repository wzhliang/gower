# AGENTS.md

## Build/Test/Lint Commands
- **Install deps**: `uv sync`
- **Run all tests**: `uv run pytest`
- **Run single test**: `uv run pytest tests/test_file.py::test_name -v`
- **Lint**: `uv run ruff check .`
- **Format**: `uv run ruff format .`
- **Type check**: `uv run pyright`
- **Common tasks**: `just <task>` (see justfile)
- **Pulumi preview**: `uv run pulumi preview`
- **Pulumi deploy**: `uv run pulumi up`

## Code Style
- **Imports**: Group stdlib, third-party, local; use absolute imports; sort with ruff
- **Types**: Full type hints on all functions; use Pydantic models for config/data validation
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_SNAKE for constants
- **Error handling**: Raise specific exceptions with context; use Pydantic validation for input errors
- **Structure**: Modular design—separate Pulumi resources by concern (repos, rulesets, secrets, variables)
- **Formatting**: ruff format (88 char line length), double quotes for strings
- **Pydantic**: Use for all external config, repo definitions, and GitHub resource schemas
