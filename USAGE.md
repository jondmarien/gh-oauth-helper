# GitHub OAuth Helper - Usage Guide

This library provides a clean, secure way to handle GitHub OAuth authentication without hard-coding secrets.

## Installation

```bash
pip install gh-oauth-helper
```

## Quick Start

### 1. Set Environment Variables

The library reads credentials from environment variables by default:

```bash
export GITHUB_CLIENT_ID="your_oauth_app_client_id"
export GITHUB_CLIENT_SECRET="your_oauth_app_client_secret"
export GITHUB_REDIRECT_URI="http://localhost:8080/callback"  # Optional
```

### 2. Basic Usage

```python
from gh_oauth_helper import start_auth_flow, complete_auth_flow, verify_token

# Start the OAuth flow
auth_url, state = start_auth_flow(scopes=["user:email", "repo"])
print(f"Visit: {auth_url}")

# After user authorization, exchange the code for a token
token_data = complete_auth_flow(authorization_code)
access_token = token_data["access_token"]

# Test the token
user_info = verify_token(access_token)
print(f"Authenticated as: {user_info['login']}")
```

### 3. Using the GitHubOAuth Class

```python
from gh_oauth_helper import GitHubOAuth, GitHubOAuthError

# Create OAuth helper
oauth = GitHubOAuth(
    client_id="your_client_id",      # Or use environment variables
    client_secret="your_secret",
    redirect_uri="http://localhost:8080/callback"
)

# Generate authorization URL
auth_url, state = oauth.generate_authorization_url(
    scopes=["user", "public_repo"]
)

# Exchange authorization code for token
try:
    token_data = oauth.exchange_code_for_token(code, state)
    access_token = token_data["access_token"]
    
    # Test API access
    user_data = oauth.test_api_access(access_token)
    print(f"Hello, {user_data['name']}!")
    
except GitHubOAuthError as e:
    print(f"OAuth error: {e}")
```

## Security Features

### No Hard-Coded Secrets
- Credentials are read from environment variables or passed explicitly
- No secrets are embedded in the code
- Clear error messages when credentials are missing

### CSRF Protection
- Automatic generation of secure state parameters
- State verification support for preventing CSRF attacks

### Secure Token Handling
- Tokens are never logged or exposed
- Proper error handling for invalid/expired tokens
- Optional token revocation support

## API Reference

### GitHubOAuth Class

#### `__init__(client_id=None, client_secret=None, redirect_uri=None)`
Initialize the OAuth helper.

**Parameters:**
- `client_id`: GitHub OAuth app client ID (or use `GITHUB_CLIENT_ID` env var)
- `client_secret`: GitHub OAuth app client secret (or use `GITHUB_CLIENT_SECRET` env var)  
- `redirect_uri`: OAuth redirect URI (or use `GITHUB_REDIRECT_URI` env var, defaults to `http://localhost:8080/callback`)

#### `generate_authorization_url(scopes=None, state=None)`
Generate the GitHub authorization URL.

**Parameters:**
- `scopes`: List of OAuth scopes (defaults to `["user:email", "repo"]`)
- `state`: CSRF protection state (auto-generated if not provided)

**Returns:**
- Tuple of `(authorization_url, state)`

#### `exchange_code_for_token(code, state=None)`
Exchange authorization code for access token.

**Parameters:**
- `code`: Authorization code from GitHub callback
- `state`: State parameter for CSRF verification (optional)

**Returns:**
- Dictionary containing token information

#### `test_api_access(access_token)`
Test API access with the provided token.

**Parameters:**
- `access_token`: GitHub access token

**Returns:**
- Dictionary containing user information

#### `revoke_token(access_token)`
Revoke an access token.

**Parameters:**
- `access_token`: GitHub access token to revoke

**Returns:**
- `True` if successful, `False` otherwise

### Convenience Functions

#### `start_auth_flow(oauth_helper=None, scopes=None)`
Start OAuth flow using environment variables.

#### `complete_auth_flow(code, oauth_helper=None, state=None)`
Complete OAuth flow by exchanging code for token.

#### `verify_token(access_token, oauth_helper=None)`
Verify a token by testing API access.

## Common Scopes

- `user`: Read user profile information
- `user:email`: Read user email addresses
- `repo`: Full access to repositories
- `public_repo`: Access to public repositories only
- `read:org`: Read organization membership
- `write:org`: Write access to organization

## Error Handling

The library raises `GitHubOAuthError` for OAuth-related issues:

```python
from gh_oauth_helper import GitHubOAuthError

try:
    oauth = GitHubOAuth()
    # ... OAuth operations
except GitHubOAuthError as e:
    print(f"OAuth error: {e}")
```

Common error scenarios:
- Missing credentials
- Invalid authorization codes
- Expired or invalid tokens
- Network connectivity issues
- API rate limiting

## Examples

See the `examples/oauth_example.py` file for a complete working example.

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GITHUB_CLIENT_ID` | OAuth app client ID | Yes | None |
| `GITHUB_CLIENT_SECRET` | OAuth app client secret | Yes | None |
| `GITHUB_REDIRECT_URI` | OAuth callback URL | No | `http://localhost:8080/callback` |

