"""Tests for repository configuration models."""

from tower.models import (
    RepositoryDefaults,
    RepositoryOverride,
    RepositoryVariable,
    Ruleset,
    RulesetPullRequest,
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


def test_merge_ruleset_from_defaults() -> None:
    """Test that ruleset from defaults is applied."""
    defaults = RepositoryDefaults(
        ruleset=Ruleset(
            name="default-protection",
            pull_request=RulesetPullRequest(required_approving_review_count=1),
        )
    )
    override = RepositoryOverride(name="repo-with-ruleset")

    config = merge_config(defaults, override)

    assert config.ruleset is not None
    assert config.ruleset.name == "default-protection"
    assert config.ruleset.pull_request.required_approving_review_count == 1


def test_merge_ruleset_disabled() -> None:
    """Test that ruleset can be explicitly disabled."""
    defaults = RepositoryDefaults(ruleset=Ruleset(name="default-protection"))
    override = RepositoryOverride(
        name="repo-no-ruleset",
        ruleset_disabled=True,
    )

    config = merge_config(defaults, override)

    assert config.ruleset is None


def test_merge_ruleset_override() -> None:
    """Test that ruleset can be overridden."""
    defaults = RepositoryDefaults(
        ruleset=Ruleset(
            name="default-protection",
            pull_request=RulesetPullRequest(required_approving_review_count=1),
        )
    )
    override = RepositoryOverride(
        name="critical-repo",
        ruleset=Ruleset(
            name="strict-protection",
            pull_request=RulesetPullRequest(required_approving_review_count=2),
        ),
    )

    config = merge_config(defaults, override)

    assert config.ruleset is not None
    assert config.ruleset.name == "strict-protection"
    assert config.ruleset.pull_request.required_approving_review_count == 2


def test_ruleset_defaults() -> None:
    """Test that Ruleset has sensible defaults."""
    ruleset = Ruleset()

    assert ruleset.name == "default-branch-protection"
    assert ruleset.target == "branch"
    assert ruleset.enforcement == "active"
    assert ruleset.branch_pattern == "~DEFAULT_BRANCH"
    assert ruleset.bypass_admins is True
    assert ruleset.block_force_pushes is True
    assert ruleset.block_deletions is True
    assert ruleset.require_linear_history is False
    assert ruleset.require_signed_commits is False
    assert ruleset.pull_request.required_approving_review_count == 1
    assert ruleset.pull_request.required_review_thread_resolution is True
