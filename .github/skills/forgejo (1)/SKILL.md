---
name: forgejo
description: Interact with Forgejo and Gitea-based Git hosting platforms like Codeberg. Use for managing repositories, users, organizations, issues, pull requests, and other platform features via the REST API. Also covers self-hosting deployment with Docker Compose, hardware sizing, database selection, reverse proxy configuration, backup strategies, and production hardening. Triggers on mentions of Forgejo, Gitea, Codeberg, self-hosted git forge, or Forgejo deployment.
---

# Forgejo & Gitea API Skill

This skill provides a comprehensive toolkit for interacting with any Forgejo or Gitea-based Git hosting platform, such as Codeberg. It includes a Python client library for the REST API, detailed documentation on endpoints and authentication, and practical examples for common operations.

## Core Capabilities

*   **Full API Coverage**: Manage repositories, users, organizations, issues, pull requests, webhooks, and more.
*   **Flexible Authentication**: Supports token-based authentication for secure API access.
*   **Instance Agnostic**: Works with any Forgejo or Gitea instance by configuring the API base URL.
*   **Bundled Python Client**: A ready-to-use Python script (`scripts/forgejo_client.py`) provides a convenient wrapper for all major API endpoints.
*   **Self-Hosting Guide**: Complete deployment reference with Docker Compose templates, hardware sizing, reverse proxy configs, backup procedures, and security hardening.

## Getting Started

### 1. Configuration

Before using the client, you must configure it with your Forgejo instance URL and an API token. Set the following environment variables:

```bash
export FORGEJO_BASE_URL="https://your-forgejo-instance.com/api/v1"
export FORGEJO_TOKEN="your_api_token_here"
```

If `FORGEJO_BASE_URL` is not set, it will default to Codeberg's API (`https://codeberg.org/api/v1`).

### 2. Using the Python Client

The `forgejo_client.py` script provides a `ForgejoAPI` class that can be imported and used in your Python code. See the **Client Usage Guide** for detailed examples:

*   **Read:** `/home/ubuntu/skills/forgejo/references/client_usage.md`

### 3. API Reference

For a detailed breakdown of all available API endpoints, data models, and parameters, consult the comprehensive API reference documents:

*   **API Endpoints**: `/home/ubuntu/skills/forgejo/references/api_endpoints.md`
*   **Authentication Guide**: `/home/ubuntu/skills/forgejo/references/authentication.md`

## Common Workflows

### Repository Management

*   **Create a repository**: Use `api.create_repo(name, description, private=True)`.
*   **List user repositories**: Use `api.get_current_user_repos()`.
*   **Get repository details**: Use `api.get_repo(owner, repo_name)`.

### Issue Tracking

*   **List issues**: Use `api.get_repo_issues(owner, repo_name, state='open')`.
*   **Create an issue**: Use `api.create_issue(owner, repo_name, title, body)`.
*   **Comment on an issue**: Use `api.create_issue_comment(owner, repo_name, issue_index, body)`.

### Organization Management

*   **List your organizations**: Use `api.get_user_orgs()`.
*   **Get organization details**: Use `api.get_org(org_name)`.
*   **List organization members**: Use `api.get_org_members(org_name)`.

## Self-Hosting & Deployment

For deploying your own Forgejo instance, the skill includes a comprehensive self-hosting guide and a production-ready Docker Compose template.

*   **Self-Hosting Guide**: `/home/ubuntu/skills/forgejo/references/self_hosting.md`
*   **Docker Compose Template**: `/home/ubuntu/skills/forgejo/templates/docker-compose.yml`

The self-hosting guide covers:

1.  **Installation Methods**: Docker (recommended), binary, Podman, and from-source builds.
2.  **Hardware Sizing**: Specifications for personal, small team, medium org, and large-scale deployments.
3.  **Database Selection**: When to use SQLite vs. PostgreSQL vs. MySQL, with configuration examples.
4.  **Reverse Proxy**: Nginx, Caddy, and Apache configurations with HTTPS and security headers.
5.  **Backup & Restore**: Using `forgejo dump` for scheduled backups and disaster recovery.
6.  **Security Hardening**: CAPTCHA, SSH configuration, firewall rules, and update strategies.
7.  **Forgejo Actions (CI/CD)**: Enabling Actions and deploying a Forgejo Runner.
