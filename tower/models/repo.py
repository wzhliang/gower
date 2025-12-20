"""Pydantic models for repository and GitHub resource configuration."""

from typing import Any

from pydantic import BaseModel, Field


class RequiredStatusCheck(BaseModel):
    """Required status check configuration."""

    context: str  # The name of the status check (e.g., "ci", "test", "build")
    integration_id: int | None = None  # Optional GitHub App integration ID


class RulesetPullRequest(BaseModel):
    """Pull request rules within a ruleset."""

    required_approving_review_count: int = 1
    dismiss_stale_reviews_on_push: bool = False
    require_code_owner_review: bool = False
    require_last_push_approval: bool = False
    required_review_thread_resolution: bool = True


class Ruleset(BaseModel):
    """Repository ruleset configuration."""

    name: str = "default-branch-protection"
    target: str = "branch"  # "branch" or "tag"
    enforcement: str = "active"  # "active", "evaluate", or "disabled"
    branch_pattern: str = "~DEFAULT_BRANCH"  # Pattern for branches to protect
    bypass_admins: bool = True  # Allow repository admins to bypass

    # Rules
    pull_request: RulesetPullRequest = Field(default_factory=RulesetPullRequest)
    required_status_checks: list[RequiredStatusCheck] = Field(default_factory=list)
    block_force_pushes: bool = True
    block_deletions: bool = True
    require_linear_history: bool = False
    require_signed_commits: bool = False


class RepositorySecret(BaseModel):
    """Repository secret configuration."""

    name: str
    value: str = Field(exclude=True)  # Exclude from serialization


class RepositoryVariable(BaseModel):
    """Repository variable configuration."""

    name: str
    value: str


class RepositoryDefaults(BaseModel):
    """Default settings applied to all repositories."""

    visibility: str = "private"
    has_issues: bool = True
    has_wiki: bool = False
    has_projects: bool = False
    delete_branch_on_merge: bool = True
    allow_merge_commit: bool = False
    allow_squash_merge: bool = True
    allow_rebase_merge: bool = False
    ruleset: Ruleset | None = None
    topics: list[str] = Field(default_factory=list)


class RepositoryOverride(BaseModel):
    """Repository-specific configuration that overrides defaults."""

    name: str
    description: str = ""
    visibility: str | None = None
    has_issues: bool | None = None
    has_wiki: bool | None = None
    has_projects: bool | None = None
    delete_branch_on_merge: bool | None = None
    allow_merge_commit: bool | None = None
    allow_squash_merge: bool | None = None
    allow_rebase_merge: bool | None = None
    ruleset: Ruleset | None = None
    ruleset_disabled: bool = False  # Explicitly disable if defaults have it
    secrets: list[RepositorySecret] = Field(default_factory=list)
    variables: list[RepositoryVariable] = Field(default_factory=list)
    topics: list[str] | None = None  # None = use defaults, [] = no topics
    extra_topics: list[str] = Field(default_factory=list)  # Added to defaults


class RepositoryConfig(BaseModel):
    """Complete repository configuration (resolved from defaults + overrides)."""

    name: str
    description: str = ""
    visibility: str = "private"
    has_issues: bool = True
    has_wiki: bool = False
    has_projects: bool = False
    delete_branch_on_merge: bool = True
    allow_merge_commit: bool = False
    allow_squash_merge: bool = True
    allow_rebase_merge: bool = False
    ruleset: Ruleset | None = None
    secrets: list[RepositorySecret] = Field(default_factory=list)
    variables: list[RepositoryVariable] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)


def merge_config(
    defaults: RepositoryDefaults, override: RepositoryOverride
) -> RepositoryConfig:
    """Merge defaults with repository-specific overrides."""
    # Start with defaults
    config_dict: dict[str, Any] = {
        "name": override.name,
        "description": override.description,
        "visibility": defaults.visibility,
        "has_issues": defaults.has_issues,
        "has_wiki": defaults.has_wiki,
        "has_projects": defaults.has_projects,
        "delete_branch_on_merge": defaults.delete_branch_on_merge,
        "allow_merge_commit": defaults.allow_merge_commit,
        "allow_squash_merge": defaults.allow_squash_merge,
        "allow_rebase_merge": defaults.allow_rebase_merge,
        "ruleset": defaults.ruleset,
        "secrets": override.secrets,
        "variables": override.variables,
    }

    # Apply overrides (only if explicitly set, i.e., not None)
    if override.visibility is not None:
        config_dict["visibility"] = override.visibility
    if override.has_issues is not None:
        config_dict["has_issues"] = override.has_issues
    if override.has_wiki is not None:
        config_dict["has_wiki"] = override.has_wiki
    if override.has_projects is not None:
        config_dict["has_projects"] = override.has_projects
    if override.delete_branch_on_merge is not None:
        config_dict["delete_branch_on_merge"] = override.delete_branch_on_merge
    if override.allow_merge_commit is not None:
        config_dict["allow_merge_commit"] = override.allow_merge_commit
    if override.allow_squash_merge is not None:
        config_dict["allow_squash_merge"] = override.allow_squash_merge
    if override.allow_rebase_merge is not None:
        config_dict["allow_rebase_merge"] = override.allow_rebase_merge

    # Ruleset: can override or explicitly disable
    if override.ruleset_disabled:
        config_dict["ruleset"] = None
    elif override.ruleset is not None:
        config_dict["ruleset"] = override.ruleset

    # Topics: override completely or extend defaults
    if override.topics is not None:
        config_dict["topics"] = override.topics + override.extra_topics
    else:
        config_dict["topics"] = defaults.topics + override.extra_topics

    return RepositoryConfig(**config_dict)
