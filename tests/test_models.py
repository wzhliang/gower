"""Tests for repository configuration models."""

from tower.models import (
    BranchProtection,
    RepositoryDefaults,
    RepositoryOverride,
    RepositoryVariable,
    merge_config,
)


def test_merge_uses_defaults() -> None:
    """Test that merge_config applies defaults when no overrides specified."""
    defaults = RepositoryDefaults(
        visibility="private",
        has_wiki=False,
        topics=["managed-by-tower"],
    )
    override = RepositoryOverride(name="test-repo", description="A test repo")

    config = merge_config(defaults, override)

    assert config.name == "test-repo"
    assert config.visibility == "private"
    assert config.has_wiki is False
    assert config.topics == ["managed-by-tower"]


def test_merge_override_specific_fields() -> None:
    """Test that specific fields can be overridden."""
    defaults = RepositoryDefaults(visibility="private", has_wiki=False)
    override = RepositoryOverride(
        name="public-repo",
        description="A public repo",
        visibility="public",
        has_wiki=True,
    )

    config = merge_config(defaults, override)

    assert config.visibility == "public"
    assert config.has_wiki is True


def test_merge_extra_topics_extends_defaults() -> None:
    """Test that extra_topics adds to default topics."""
    defaults = RepositoryDefaults(topics=["managed-by-tower"])
    override = RepositoryOverride(
        name="data-repo",
        extra_topics=["data", "etl"],
    )

    config = merge_config(defaults, override)

    assert config.topics == ["managed-by-tower", "data", "etl"]


def test_merge_topics_override_replaces_defaults() -> None:
    """Test that setting topics replaces defaults entirely."""
    defaults = RepositoryDefaults(topics=["managed-by-tower"])
    override = RepositoryOverride(
        name="custom-repo",
        topics=["custom", "special"],
    )

    config = merge_config(defaults, override)

    assert config.topics == ["custom", "special"]


def test_merge_branch_protection_disabled() -> None:
    """Test that branch protection can be explicitly disabled."""
    defaults = RepositoryDefaults(
        branch_protection=BranchProtection(pattern="main", required_reviews=1)
    )
    override = RepositoryOverride(
        name="docs-repo",
        branch_protection_disabled=True,
    )

    config = merge_config(defaults, override)

    assert config.branch_protection is None


def test_merge_branch_protection_override() -> None:
    """Test that branch protection can be overridden."""
    defaults = RepositoryDefaults(
        branch_protection=BranchProtection(required_reviews=1)
    )
    override = RepositoryOverride(
        name="critical-repo",
        branch_protection=BranchProtection(required_reviews=3),
    )

    config = merge_config(defaults, override)

    assert config.branch_protection is not None
    assert config.branch_protection.required_reviews == 3


def test_merge_preserves_secrets_and_variables() -> None:
    """Test that secrets and variables from override are preserved."""
    defaults = RepositoryDefaults()
    override = RepositoryOverride(
        name="repo-with-vars",
        variables=[
            RepositoryVariable(name="ENV", value="prod"),
        ],
    )

    config = merge_config(defaults, override)

    assert len(config.variables) == 1
    assert config.variables[0].name == "ENV"
