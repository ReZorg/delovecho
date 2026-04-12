#!/usr/bin/env python3
"""
Forgejo API Client Library
===========================

A comprehensive, reusable Python wrapper for the Forgejo REST API.
Works with any Forgejo or Gitea-based instance, including Codeberg.

Configuration:
    Set the following environment variables before use:
    - FORGEJO_BASE_URL: The base URL for the API (default: https://codeberg.org/api/v1)
    - FORGEJO_TOKEN: Your personal access token.

Usage:
    from forgejo_client import ForgejoAPI
    api = ForgejoAPI()
    user = api.get_current_user()
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class ForgejoConfig:
    """Configuration for the Forgejo API client."""
    base_url: Optional[str] = None
    token: Optional[str] = None

    def __post_init__(self):
        if self.token is None:
            self.token = os.environ.get("FORGEJO_TOKEN")
        if self.base_url is None:
            self.base_url = os.environ.get(
                "FORGEJO_BASE_URL", "https://codeberg.org/api/v1"
            )


class ForgejoAPI:
    """
    Forgejo API Client.

    A comprehensive wrapper for the Forgejo REST API, supporting user
    management, repositories, issues, pull requests, organizations, and more.
    """

    def __init__(self, config: Optional[ForgejoConfig] = None):
        self.config = config or ForgejoConfig()
        self.session = requests.Session()
        if self.config.token:
            self.session.headers["Authorization"] = f"token {self.config.token}"
        self.session.headers["Accept"] = "application/json"
        self.session.headers["Content-Type"] = "application/json"

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make an API request and return the JSON response."""
        url = f"{self.config.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        if response.status_code == 204 or not response.text:
            return {}
        return response.json()

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        return self._request("GET", endpoint, params=params)

    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        return self._request("POST", endpoint, json=data)

    def _put(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        return self._request("PUT", endpoint, json=data)

    def _patch(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        return self._request("PATCH", endpoint, json=data)

    def _delete(self, endpoint: str) -> Any:
        return self._request("DELETE", endpoint)

    # =========================================================================
    # VERSION & SETTINGS
    # =========================================================================

    def get_version(self) -> Dict[str, str]:
        """Get the Forgejo version running on the instance."""
        return self._get("/version")

    def get_api_settings(self) -> Dict[str, Any]:
        """Get API settings including pagination limits."""
        return self._get("/settings/api")

    # =========================================================================
    # USER MANAGEMENT
    # =========================================================================

    def get_current_user(self) -> Dict[str, Any]:
        """Get the authenticated user's information."""
        return self._get("/user")

    def get_user(self, username: str) -> Dict[str, Any]:
        """Get a user's public profile by username."""
        return self._get(f"/users/{username}")

    def search_users(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for users by username or email."""
        return self._get("/users/search", params={"q": query, "limit": limit})

    def get_user_repos(self, username: str, limit: int = 50) -> List[Dict]:
        """Get a user's public repositories."""
        return self._get(f"/users/{username}/repos", params={"limit": limit})

    def get_current_user_repos(self, limit: int = 50) -> List[Dict]:
        """Get the authenticated user's repositories."""
        return self._get("/user/repos", params={"limit": limit})

    def get_user_followers(self, username: str) -> List[Dict]:
        """Get a user's followers."""
        return self._get(f"/users/{username}/followers")

    def get_user_following(self, username: str) -> List[Dict]:
        """Get users that a user is following."""
        return self._get(f"/users/{username}/following")

    def follow_user(self, username: str) -> None:
        """Follow a user."""
        self._put(f"/user/following/{username}")

    def unfollow_user(self, username: str) -> None:
        """Unfollow a user."""
        self._delete(f"/user/following/{username}")

    def get_starred_repos(self) -> List[Dict]:
        """Get repositories starred by the authenticated user."""
        return self._get("/user/starred")

    def star_repo(self, owner: str, repo: str) -> None:
        """Star a repository."""
        self._put(f"/user/starred/{owner}/{repo}")

    def unstar_repo(self, owner: str, repo: str) -> None:
        """Unstar a repository."""
        self._delete(f"/user/starred/{owner}/{repo}")

    # =========================================================================
    # REPOSITORY MANAGEMENT
    # =========================================================================

    def search_repos(
        self, query: str, limit: int = 10, sort: str = "updated"
    ) -> Dict[str, Any]:
        """Search for repositories. Sort by: alpha, created, updated, size, id."""
        return self._get(
            "/repos/search", params={"q": query, "limit": limit, "sort": sort}
        )

    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository details."""
        return self._get(f"/repos/{owner}/{repo}")

    def create_repo(
        self, name: str, description: str = "", private: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Create a new repository for the authenticated user."""
        data = {"name": name, "description": description, "private": private, **kwargs}
        return self._post("/user/repos", data=data)

    def create_org_repo(
        self, org: str, name: str, description: str = "", private: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Create a new repository under an organization."""
        data = {"name": name, "description": description, "private": private, **kwargs}
        return self._post(f"/orgs/{org}/repos", data=data)

    def delete_repo(self, owner: str, repo: str) -> None:
        """Delete a repository (requires admin access)."""
        self._delete(f"/repos/{owner}/{repo}")

    def fork_repo(
        self, owner: str, repo: str, new_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fork a repository."""
        data = {}
        if new_name:
            data["name"] = new_name
        return self._post(f"/repos/{owner}/{repo}/forks", data=data)

    def get_repo_contents(
        self, owner: str, repo: str, path: str = "", ref: Optional[str] = None
    ) -> Any:
        """Get repository contents at a path."""
        params = {"ref": ref} if ref else {}
        endpoint = f"/repos/{owner}/{repo}/contents/{path}".rstrip("/")
        return self._get(endpoint, params=params)

    def create_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str = "Create file",
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a file in a repository. Content must be base64-encoded."""
        data = {"content": content, "message": message}
        if branch:
            data["branch"] = branch
        return self._post(f"/repos/{owner}/{repo}/contents/{path}", data=data)

    def update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        sha: str,
        message: str = "Update file",
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a file in a repository. Content must be base64-encoded."""
        data = {"content": content, "sha": sha, "message": message}
        if branch:
            data["branch"] = branch
        return self._put(f"/repos/{owner}/{repo}/contents/{path}", data=data)

    def delete_file(
        self,
        owner: str,
        repo: str,
        path: str,
        sha: str,
        message: str = "Delete file",
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete a file in a repository."""
        data = {"sha": sha, "message": message}
        if branch:
            data["branch"] = branch
        return self._delete(f"/repos/{owner}/{repo}/contents/{path}")

    def get_repo_branches(self, owner: str, repo: str, limit: int = 50) -> List[Dict]:
        """Get repository branches."""
        return self._get(
            f"/repos/{owner}/{repo}/branches", params={"limit": limit}
        )

    def create_branch(
        self, owner: str, repo: str, branch_name: str, old_branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new branch."""
        data = {"new_branch_name": branch_name}
        if old_branch:
            data["old_branch_name"] = old_branch
        return self._post(f"/repos/{owner}/{repo}/branches", data=data)

    def get_repo_commits(
        self, owner: str, repo: str, limit: int = 10, sha: Optional[str] = None
    ) -> List[Dict]:
        """Get repository commits."""
        params = {"limit": limit}
        if sha:
            params["sha"] = sha
        return self._get(f"/repos/{owner}/{repo}/commits", params=params)

    def get_repo_tags(self, owner: str, repo: str, limit: int = 50) -> List[Dict]:
        """Get repository tags."""
        return self._get(f"/repos/{owner}/{repo}/tags", params={"limit": limit})

    def get_repo_releases(self, owner: str, repo: str, limit: int = 10) -> List[Dict]:
        """Get repository releases."""
        return self._get(
            f"/repos/{owner}/{repo}/releases", params={"limit": limit}
        )

    def create_release(
        self,
        owner: str,
        repo: str,
        tag_name: str,
        name: str = "",
        body: str = "",
        draft: bool = False,
        prerelease: bool = False,
        target_commitish: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new release."""
        data = {
            "tag_name": tag_name,
            "name": name or tag_name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease,
        }
        if target_commitish:
            data["target_commitish"] = target_commitish
        return self._post(f"/repos/{owner}/{repo}/releases", data=data)

    def get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get repository language statistics."""
        return self._get(f"/repos/{owner}/{repo}/languages")

    def get_repo_topics(self, owner: str, repo: str) -> Dict[str, List[str]]:
        """Get repository topics."""
        return self._get(f"/repos/{owner}/{repo}/topics")

    def update_repo_topics(self, owner: str, repo: str, topics: List[str]) -> None:
        """Update repository topics."""
        self._put(f"/repos/{owner}/{repo}/topics", data={"topics": topics})

    # =========================================================================
    # ISSUES
    # =========================================================================

    def get_repo_issues(
        self, owner: str, repo: str, state: str = "open", limit: int = 50
    ) -> List[Dict]:
        """Get repository issues. State: open, closed, all."""
        return self._get(
            f"/repos/{owner}/{repo}/issues",
            params={"state": state, "limit": limit, "type": "issues"},
        )

    def get_issue(self, owner: str, repo: str, index: int) -> Dict[str, Any]:
        """Get a specific issue by index."""
        return self._get(f"/repos/{owner}/{repo}/issues/{index}")

    def create_issue(
        self, owner: str, repo: str, title: str, body: str = "", **kwargs
    ) -> Dict[str, Any]:
        """Create a new issue. kwargs: assignees, labels, milestone."""
        data = {"title": title, "body": body, **kwargs}
        return self._post(f"/repos/{owner}/{repo}/issues", data=data)

    def update_issue(
        self, owner: str, repo: str, index: int, **kwargs
    ) -> Dict[str, Any]:
        """Update an issue (title, body, state, assignees, labels, etc.)."""
        return self._patch(f"/repos/{owner}/{repo}/issues/{index}", data=kwargs)

    def close_issue(self, owner: str, repo: str, index: int) -> Dict[str, Any]:
        """Close an issue."""
        return self.update_issue(owner, repo, index, state="closed")

    def reopen_issue(self, owner: str, repo: str, index: int) -> Dict[str, Any]:
        """Reopen an issue."""
        return self.update_issue(owner, repo, index, state="open")

    def get_issue_comments(
        self, owner: str, repo: str, index: int
    ) -> List[Dict]:
        """Get comments on an issue."""
        return self._get(f"/repos/{owner}/{repo}/issues/{index}/comments")

    def create_issue_comment(
        self, owner: str, repo: str, index: int, body: str
    ) -> Dict[str, Any]:
        """Add a comment to an issue."""
        return self._post(
            f"/repos/{owner}/{repo}/issues/{index}/comments", data={"body": body}
        )

    # =========================================================================
    # PULL REQUESTS
    # =========================================================================

    def get_repo_pulls(
        self, owner: str, repo: str, state: str = "open", limit: int = 50
    ) -> List[Dict]:
        """Get repository pull requests."""
        return self._get(
            f"/repos/{owner}/{repo}/pulls",
            params={"state": state, "limit": limit},
        )

    def get_pull(self, owner: str, repo: str, index: int) -> Dict[str, Any]:
        """Get a specific pull request."""
        return self._get(f"/repos/{owner}/{repo}/pulls/{index}")

    def create_pull(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: str = "",
    ) -> Dict[str, Any]:
        """Create a pull request. head: source branch, base: target branch."""
        data = {"title": title, "head": head, "base": base, "body": body}
        return self._post(f"/repos/{owner}/{repo}/pulls", data=data)

    def merge_pull(
        self, owner: str, repo: str, index: int, merge_style: str = "merge"
    ) -> None:
        """Merge a PR. Styles: merge, rebase, rebase-merge, squash, fast-forward-only."""
        self._post(
            f"/repos/{owner}/{repo}/pulls/{index}/merge",
            data={"Do": merge_style},
        )

    def get_pull_commits(self, owner: str, repo: str, index: int) -> List[Dict]:
        """Get commits in a pull request."""
        return self._get(f"/repos/{owner}/{repo}/pulls/{index}/commits")

    def get_pull_files(self, owner: str, repo: str, index: int) -> List[Dict]:
        """Get changed files in a pull request."""
        return self._get(f"/repos/{owner}/{repo}/pulls/{index}/files")

    # =========================================================================
    # LABELS & MILESTONES
    # =========================================================================

    def get_repo_labels(self, owner: str, repo: str) -> List[Dict]:
        """Get repository labels."""
        return self._get(f"/repos/{owner}/{repo}/labels")

    def create_label(
        self, owner: str, repo: str, name: str, color: str, description: str = ""
    ) -> Dict[str, Any]:
        """Create a new label."""
        data = {"name": name, "color": color, "description": description}
        return self._post(f"/repos/{owner}/{repo}/labels", data=data)

    def delete_label(self, owner: str, repo: str, label_id: int) -> None:
        """Delete a label."""
        self._delete(f"/repos/{owner}/{repo}/labels/{label_id}")

    def get_repo_milestones(
        self, owner: str, repo: str, state: str = "open"
    ) -> List[Dict]:
        """Get repository milestones."""
        return self._get(
            f"/repos/{owner}/{repo}/milestones", params={"state": state}
        )

    def create_milestone(
        self,
        owner: str,
        repo: str,
        title: str,
        description: str = "",
        due_on: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new milestone."""
        data = {"title": title, "description": description}
        if due_on:
            data["due_on"] = due_on
        return self._post(f"/repos/{owner}/{repo}/milestones", data=data)

    # =========================================================================
    # ORGANIZATIONS
    # =========================================================================

    def get_user_orgs(self) -> List[Dict]:
        """Get organizations the authenticated user belongs to."""
        return self._get("/user/orgs")

    def get_org(self, org: str) -> Dict[str, Any]:
        """Get organization details."""
        return self._get(f"/orgs/{org}")

    def get_org_repos(self, org: str, limit: int = 50) -> List[Dict]:
        """Get organization repositories."""
        return self._get(f"/orgs/{org}/repos", params={"limit": limit})

    def get_org_members(self, org: str) -> List[Dict]:
        """Get organization members."""
        return self._get(f"/orgs/{org}/members")

    def get_org_teams(self, org: str) -> List[Dict]:
        """Get organization teams."""
        return self._get(f"/orgs/{org}/teams")

    def create_org(
        self, name: str, full_name: str = "", description: str = "", **kwargs
    ) -> Dict[str, Any]:
        """Create a new organization."""
        data = {
            "username": name,
            "full_name": full_name,
            "description": description,
            **kwargs,
        }
        return self._post("/orgs", data=data)

    # =========================================================================
    # WEBHOOKS
    # =========================================================================

    def get_repo_hooks(self, owner: str, repo: str) -> List[Dict]:
        """Get repository webhooks."""
        return self._get(f"/repos/{owner}/{repo}/hooks")

    def create_repo_hook(
        self,
        owner: str,
        repo: str,
        hook_type: str,
        url: str,
        content_type: str = "json",
        events: Optional[List[str]] = None,
        active: bool = True,
    ) -> Dict[str, Any]:
        """Create a repository webhook."""
        data = {
            "type": hook_type,
            "config": {"url": url, "content_type": content_type},
            "events": events or ["push"],
            "active": active,
        }
        return self._post(f"/repos/{owner}/{repo}/hooks", data=data)

    def delete_repo_hook(self, owner: str, repo: str, hook_id: int) -> None:
        """Delete a repository webhook."""
        self._delete(f"/repos/{owner}/{repo}/hooks/{hook_id}")

    # =========================================================================
    # NOTIFICATIONS
    # =========================================================================

    def get_notifications(
        self, all_notifications: bool = False, limit: int = 50
    ) -> List[Dict]:
        """Get user notifications."""
        return self._get(
            "/notifications", params={"all": all_notifications, "limit": limit}
        )

    def mark_notifications_read(self) -> None:
        """Mark all notifications as read."""
        self._put("/notifications")

    # =========================================================================
    # TOPICS
    # =========================================================================

    def search_topics(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for topics."""
        return self._get("/topics/search", params={"q": query, "limit": limit})

    # =========================================================================
    # ACTIVITY
    # =========================================================================

    def get_user_activity(self, username: str) -> List[Dict]:
        """Get a user's public activity feed."""
        return self._get(f"/users/{username}/activities/feeds")
