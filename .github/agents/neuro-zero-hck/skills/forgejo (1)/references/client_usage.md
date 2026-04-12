# Forgejo API Client Usage Guide

This guide provides practical examples of how to use the bundled `ForgejoAPI` Python client to interact with a Forgejo instance.

## 1. Initialization

First, import the `ForgejoAPI` class and create an instance. The client will automatically pick up the `FORGEJO_BASE_URL` and `FORGEJO_TOKEN` environment variables.

```python
from forgejo_client import ForgejoAPI, ForgejoConfig

# Initialize with environment variables
api = ForgejoAPI()

# Or, configure manually
config = ForgejoConfig(
    base_url="https://your-forgejo-instance.com/api/v1",
    token="your_api_token_here"
)
api_manual = ForgejoAPI(config)
```

## 2. Common Operations

### User Management

```python
# Get the current authenticated user
current_user = api.get_current_user()
print(f"Authenticated as: {current_user['login']}")

# Get a specific user's profile
user_profile = api.get_user("some_user")
print(f"Profile for {user_profile['login']}: {user_profile['full_name']}")

# Search for users
search_results = api.search_users("testuser")
for user in search_results['data']:
    print(f"Found user: {user['login']}")
```

### Repository Management

```python
# Create a new private repository
new_repo = api.create_repo(
    name="my-awesome-project",
    description="A new project to change the world.",
    private=True
)
print(f"Created repository: {new_repo['full_name']}")

# Get repository details
repo_details = api.get_repo("my-org", "my-awesome-project")
print(f"Stars: {repo_details['stars_count']}")

# List branches
branches = api.get_repo_branches("my-org", "my-awesome-project")
for branch in branches:
    print(f"Branch: {branch['name']}")
```

### Issue Tracking

```python
# Create a new issue
new_issue = api.create_issue(
    owner="my-org",
    repo="my-awesome-project",
    title="Implement feature X",
    body="We need to implement feature X to solve problem Y."
)
print(f"Created issue #{new_issue['number']}")

# Add a comment to the issue
api.create_issue_comment(
    owner="my-org",
    repo="my-awesome-project",
    index=new_issue['number'],
    body="I'm on it!"
)

# Close the issue
api.close_issue("my-org", "my-awesome-project", new_issue['number'])
```

## 3. Handling Errors

The client uses the `requests` library and will raise an `HTTPError` for any API requests that return a non-2xx status code. You should wrap your API calls in a `try...except` block to handle potential errors.

```python
import requests

try:
    user = api.get_user("non_existent_user")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("User not found!")
    else:
        print(f"An API error occurred: {e}")
```
