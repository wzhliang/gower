"""Pulumi resources for GitHub repository management."""

import pulumi_github as github

from tower.models import RepositoryConfig


def create_repository(config: RepositoryConfig) -> github.Repository:
    """Create a GitHub repository from configuration."""
    return github.Repository(
        config.name,
        name=config.name,
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
    )


def create_branch_protection(
    repo: github.Repository, config: RepositoryConfig
) -> github.BranchProtection | None:
    """Create branch protection rules for a repository."""
    if not config.branch_protection:
        return None

    bp = config.branch_protection
    return github.BranchProtection(
        f"{config.name}-{bp.pattern}-protection",
        repository_id=repo.node_id,
        pattern=bp.pattern,
        required_pull_request_reviews=[
            github.BranchProtectionRequiredPullRequestReviewsArgs(
                required_approving_review_count=bp.required_reviews,
                dismiss_stale_reviews=bp.dismiss_stale_reviews,
                require_code_owner_reviews=bp.require_code_owner_reviews,
            )
        ],
    )
