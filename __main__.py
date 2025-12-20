"""Tower - Pulumi program for GitHub repository management."""

import pulumi
import yaml

from tower.models import (
    RepositoryDefaults,
    RepositoryOverride,
    merge_config,
)
from tower.resources import (
    configure_repository,
    configure_ruleset,
    create_secret,
    create_variable,
)


def load_repos_config(
    path: str = "repos.yaml",
) -> tuple[RepositoryDefaults, list[RepositoryOverride]]:
    """Load repository configurations from YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)

    defaults = RepositoryDefaults(**data.get("defaults", {}))
    repos = [RepositoryOverride(**repo) for repo in data.get("repositories", [])]
    return defaults, repos


def main() -> None:
    """Main Pulumi program entry point."""
    defaults, repos = load_repos_config()

    for override in repos:
        config = merge_config(defaults, override)

        # Configure existing repository settings
        repo = configure_repository(config)
        configure_ruleset(config)

        for secret in config.secrets:
            create_secret(config.name, secret.name, secret.value)

        for var in config.variables:
            create_variable(config.name, var.name, var.value)

        pulumi.export(f"{config.name}_url", repo.html_url)


main()
