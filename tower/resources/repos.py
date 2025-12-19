"""Pulumi resources for GitHub repository management."""

import pulumi
import pulumi_github as github

from tower.models import RepositoryConfig


def get_repository(full_name: str) -> github.GetRepositoryResult:
    """Get an existing repository by full name (owner/repo)."""
    return github.get_repository(f"fullName={full_name}")


def _resource_name(name: str) -> str:
    """Convert repo name to valid Pulumi resource name."""
    return name.replace("/", "-")


def _repo_name(name: str) -> str:
    """Extract repo name from full name (owner/repo -> repo)."""
    return name.split("/")[-1] if "/" in name else name


def configure_repository(config: RepositoryConfig) -> github.Repository:
    """Configure settings for an existing GitHub repository.

    Uses Pulumi import to adopt existing repos instead of creating new ones.
    """
    repo_name = _repo_name(config.name)

    return github.Repository(
        _resource_name(config.name),
        name=repo_name,
        description=config.description,
        visibility=config.visibility,
        has_issues=config.has_issues,
        has_wiki=config.has_wiki,
        has_projects=config.has_projects,
        delete_branch_on_merge=config.delete_branch_on_merge,
        allow_merge_commit=config.allow_merge_commit,
        allow_squash_merge=config.allow_squash_merge,
        allow_rebase_merge=config.allow_rebase_merge,
        topics=config.topics,
        opts=pulumi.ResourceOptions(import_=repo_name),
    )


def configure_branch_protection(
    config: RepositoryConfig,
) -> github.BranchProtection | None:
    """Configure branch protection rules for a repository."""
    if not config.branch_protection:
        return None

    bp = config.branch_protection
    return github.BranchProtection(
        f"{_resource_name(config.name)}-{bp.pattern}-protection",
        repository_id=_repo_name(config.name),
        pattern=bp.pattern,
        required_pull_request_reviews=[
            github.BranchProtectionRequiredPullRequestReviewsArgs(
                required_approving_review_count=bp.required_reviews,
                dismiss_stale_reviews=bp.dismiss_stale_reviews,
                require_code_owner_reviews=bp.require_code_owner_reviews,
            )
        ],
    )
