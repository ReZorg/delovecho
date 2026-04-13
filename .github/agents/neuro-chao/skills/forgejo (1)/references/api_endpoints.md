

# Forgejo API Endpoints

This document provides a summary of the Forgejo API endpoints, based on the analysis of the Swagger documentation and the Forgejo codebase.

## Version

Forgejo API 14.0.0-90-1a3e2737+gitea-1.22.0, OAS 2.0
Base URL: /api/v1

## API Categories (Endpoint Groups)

1.  **activitypub** - ActivityPub federation (actor, inbox, outbox for instances, repos, users)
2.  **admin** - Server administration (cron, emails, hooks, orgs, quota, runners, users)
3.  **miscellaneous** - Templates, licenses, markdown rendering, nodeinfo, signing keys, version
4.  **notification** - User notification threads (list, mark read, per-repo)
5.  **organization** - Org CRUD, actions (secrets/variables/runners), hooks, labels, members, quota, repos, teams
6.  **package** - Package management
7.  **issue** - Issue tracking
8.  **repository** - Repository management
9.  **settings** - Server settings
10. **user** - User management

## Key Differences from GitHub/Gitea

-   ActivityPub federation support (unique to Forgejo)
-   Quota management system (groups, rules, per-user/org)
-   Actions runner management
-   Built on Gitea codebase (gitea-1.22.0 compatible)

## Admin Endpoints Include

-   Cron tasks, emails, hooks, orgs, quota groups/rules, runners, unadopted repos, users
-   User management: create, delete, edit, rename, SSH keys, quota

## Organization Endpoints Include

-   CRUD orgs, actions secrets/variables/runners, hooks, labels, members, public_members, quota, repos, teams, block/unblock users

## Repository Endpoints (continued)
- Repo CRUD, avatar, assignees
- Branch protections (CRUD)
- Branches (list, create, get, delete, update)
- Collaborators (list, check, add, delete, permissions)
- Commits (list, combined status, statuses, pull, compare)
- Contents (metadata, CRUD files, multiple files)
- Convert mirror, diffpatch, editorconfig
- Flags (list, replace, delete, check, add)
- Forks (list, create)
- Git objects (blobs, commits, diffs, notes, refs, tags, trees)
- Hooks (list, CRUD, git hooks, test webhook)
- Issue config, templates, pinned issues
- Deploy keys (CRUD)
- Languages, media files
- Mirror sync, push mirrors (CRUD, sync)
- Pull requests (list, create, get, update, diff, commits, files, merge, reviewers, reviews, comments, dismiss)
- Raw files
- Releases (list, create, latest, by tag, CRUD, assets)
- Reviewers, signing keys
- Stargazers, statuses, subscribers/watchers
- Fork sync (info, sync, per-branch)
- Tag protections (CRUD)
- Tags (list, create, get, delete)
- Teams (list, check, add, delete)
- Tracked times (per-repo, per-user)
- Topics (list, replace, add, delete)
- Transfer (initiate, accept, reject)
- Wiki (create, get, delete, edit, list pages, revisions)
- Generate from template
- Repository by ID
- Topic search

## Settings Endpoints
- /settings/api - Global API settings
- /settings/attachment - Attachment settings
- /settings/repository - Repository settings
- /settings/ui - UI settings

## User Endpoints
- Authenticated user info, actions (runners, secrets, variables)
- OAuth2 applications (CRUD)
- Avatar, block/unblock users
- Emails (list, add, delete)
- Followers/following (list, check, follow, unfollow)
- GPG keys (list, create, get, delete, verify token)
- SSH keys (list, create, get, delete)
- Repos (list, create)
- Settings (get, update)
- Starred repos (list, check, star, unstar)
- Stopwatches, subscriptions, teams, tracked times
- Public user profiles, heatmaps
- Access tokens (list, create, delete)

## Actions Endpoints (within repos)
- /repos/{owner}/{repo}/actions/runners/jobs
- /repos/{owner}/{repo}/actions/runners/registration-token
- /repos/{owner}/{repo}/actions/secrets (CRUD)
- /repos/{owner}/{repo}/actions/variables (CRUD)
- /repos/{owner}/{repo}/actions/workflows/{workflowname}/dispatches

## Key Data Models
Major models: Repository, User, Organization, Team, Issue, PullRequest, Release, Branch, BranchProtection, Commit, Comment, Label, Milestone, Hook, DeployKey, GPGKey, PublicKey, OAuth2Application, Package, QuotaGroup, QuotaRuleInfo, ActionRun, ActionRunJob, ActionTask, WikiPage, Tag, TagProtection, PushMirror, Notification, Reaction, TrackedTime, StopWatch, etc.
