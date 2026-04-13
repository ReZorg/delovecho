# Forgejo API Authentication Guide

This guide details the authentication methods supported by the Forgejo API. The recommended and most secure method is to use a personal access token.

## Recommended Method: Personal Access Token

Personal access tokens provide a secure way to authenticate with the API without exposing your password. They can be scoped to grant specific permissions, following the principle of least privilege.

### 1. Generating a Token

You can generate a new token from your user settings page on any Forgejo instance:

- **Token Generation URL:** `https://<your-forgejo-instance>/user/settings/applications`

### 2. Using the Token

All API requests must include the token in the `Authorization` header, prepended with the word "token" and a space.

**Header Format:**
```
Authorization: token YOUR_API_TOKEN
```

**Example with cURL:**
```bash
cURL -H "Authorization: token <your_api_token>" https://<your-forgejo-instance>/api/v1/user
```

## Other Authentication Methods

While token-based authentication is recommended, the Forgejo API supports other methods for specific use cases.

| Method | Type | Description |
| :--- | :--- | :--- |
| **BasicAuth** | Basic | Standard HTTP Basic Authentication using your username and password. Not recommended for automated scripts. |
| **TOTPHeader** | API Key | Must be used in combination with BasicAuth if two-factor authentication is enabled. The OTP is sent in the `X-FORGEJO-OTP` header. |
| **Sudo** | API Key | Allows an admin to perform an API request as another user. Requires admin privileges. Can be sent in the `Sudo` header or as a `sudo` query parameter. |

## Deprecated Methods

The following methods are deprecated and will be removed in future versions of Forgejo. You should update any existing integrations to use the `Authorization: token ...` header format.

- `access_token` (query parameter)
- `token` (query parameter)
