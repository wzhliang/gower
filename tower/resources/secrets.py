"""Pulumi resources for GitHub secrets and variables."""

import pulumi_github as github


def create_secret(repo_name: str, name: str, value: str) -> github.ActionsSecret:
    """Create a repository secret."""
    return github.ActionsSecret(
        f"{repo_name}-secret-{name}",
        repository=repo_name,
        secret_name=name,
        plaintext_value=value,
    )


def create_variable(repo_name: str, name: str, value: str) -> github.ActionsVariable:
    """Create a repository variable."""
    return github.ActionsVariable(
        f"{repo_name}-var-{name}",
        repository=repo_name,
        variable_name=name,
        value=value,
    )
