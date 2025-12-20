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


def configure_ruleset(
    config: RepositoryConfig,
) -> github.RepositoryRuleset | None:
    """Configure repository ruleset for branch protection.

    Rulesets are the modern replacement for branch protection rules,
    offering more flexibility and better enforcement options.
    """
    if not config.ruleset:
        return None

    rs = config.ruleset
    repo_name = _repo_name(config.name)

    # Build bypass actors list
    bypass_actors: list[github.RepositoryRulesetBypassActorArgs] = []
    if rs.bypass_admins:
        bypass_actors.append(
            github.RepositoryRulesetBypassActorArgs(
                actor_type="RepositoryRole",
                actor_id=5,  # 5 = Repository Admin role ID
                bypass_mode="always",
            )
        )

    # Build pull request rules
    pull_request_args = github.RepositoryRulesetRulesPullRequestArgs(
        required_approving_review_count=rs.pull_request.required_approving_review_count,
        dismiss_stale_reviews_on_push=rs.pull_request.dismiss_stale_reviews_on_push,
        require_code_owner_review=rs.pull_request.require_code_owner_review,
        require_last_push_approval=rs.pull_request.require_last_push_approval,
        required_review_thread_resolution=rs.pull_request.required_review_thread_resolution,
    )

    # Build required status checks if any
    required_status_checks_args = None
    if rs.required_status_checks:
        required_checks = [
            github.RepositoryRulesetRulesRequiredStatusChecksRequiredCheckArgs(
                context=check.context,
                integration_id=check.integration_id,
            )
            for check in rs.required_status_checks
        ]
        required_status_checks_args = (
            github.RepositoryRulesetRulesRequiredStatusChecksArgs(
                required_checks=required_checks,
                strict_required_status_checks_policy=False,
            )
        )

    # Build rules args
    rules_args = github.RepositoryRulesetRulesArgs(
        pull_request=pull_request_args,
        required_status_checks=required_status_checks_args,
        non_fast_forward=rs.block_force_pushes,
        deletion=rs.block_deletions,
        required_linear_history=rs.require_linear_history,
        required_signatures=rs.require_signed_commits,
    )

    # Build conditions (which branches to apply to)
    conditions_args = github.RepositoryRulesetConditionsArgs(
        ref_name=github.RepositoryRulesetConditionsRefNameArgs(
            includes=[rs.branch_pattern],
            excludes=[],
        )
    )

    return github.RepositoryRuleset(
        f"{_resource_name(config.name)}-{rs.name}",
        repository=repo_name,
        name=rs.name,
        target=rs.target,
        enforcement=rs.enforcement,
        bypass_actors=bypass_actors if bypass_actors else None,
        conditions=conditions_args,
        rules=rules_args,
    )
