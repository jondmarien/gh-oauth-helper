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

### 2. Basic Python Examples

```python
from gh_oauth_helper import start_auth_flow, complete_auth_flow, verify_token

# Start the OAuth flow
auth_url, state = start_auth_flow(scopes=["user:email", "repo"])
print(f"Visit: {auth_url}")

# After user authorization, exchange the code for a token
# (Alternatively, use the new paste-the-URL method - see OAUTH_FLOW_GUIDE.md)
token_data = complete_auth_flow(authorization_code)
access_token = token_data["access_token"]

# Test the token
user_info = verify_token(access_token)
print(f"Authenticated as: {user_info['login']}")
```

### 3. CLI Quick-Start: Paste-the-URL OAuth Flow

The simplest way to get a GitHub access token - just paste the full callback URL after authorization, no manual code extraction needed.

#### Step-by-Step Example

1. **Setup Env Variables (or use them in the cli):**
   ```bash
   gh-oauth-helper auth --open --scopes user repo
   ```

2. **Authorize in browser (opens automatically)**
   • GitHub opens asking for permissions
   • Click "Authorize application"
   • Browser redirects to: `http://localhost:8080/callback?code=abc123def456&state=xyz789`

   Output:
   
   ![Standard CLI Output - Auth](images/gh-oauth-helper-1.png)
   
   ```
   🚀 Opening GitHub authorization page...
   📋 After authorization, run `gh-oauth-helper token --url "FULL CALLBACK URL"
   ```

3. **Paste the complete URL:**
   
   ![Standard CLI Output - Token Exchange](images/gh-oauth-helper-2.png)
   
   ```
   📋 After authorization, paste the complete callback URL here:
   > gh-oauth-helper token --url http://localhost:8080/callback?code=abc123def456&state=xyz789
   ```

   Output:
   ```
   ✅ Access token generated successfully!
   Token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

#### Verify Your Token

Immediately test that your token works:
```bash
gh-oauth-helper test --token TOKEN
```

Output:
```
✅ Token is valid
User: your-username
Scopes: repo, user:email
```

#### Verbose Mode Comparison

Use `--verbose` on both commands for detailed information about operations, API calls, and token details:

| Normal mode | Verbose mode |
|-------------|-------------|
| ![Standard CLI Output](images/gh-oauth-helper-3.png) | ![Verbose CLI Output](images/gh-oauth-helper-verbose-1.png) |
| ✅ Token is valid | ![Verbose CLI Output - Token Test](images/gh-oauth-helper-verbose-2.png) |

#### Platform-Specific Notes

> **Windows (PowerShell)**
> ```powershell
> gh-oauth-helper token --url "http://localhost:8080/callback"
> ```

> **Windows (Command Prompt)**
> ```cmd
> gh-oauth-helper token --url "http://localhost:8080/callback"
> ```

> **macOS/Linux (Bash/Zsh)**
> ```bash
> gh-oauth-helper token --url "http://localhost:8080/callback"
> ```

> 💡 **Pro Tip**: On all platforms, make sure to wrap the callback URL in quotes to handle special characters properly.

Need more control? See the [Complete CLI Reference](#complete-cli-reference) below for advanced options, custom scopes, and power-user features.

### 4. Using the GitHubOAuth Class

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
# For easier flows, consider using the new paste-the-URL method (see OAUTH_FLOW_GUIDE.md)
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

## OAuth Flow Methods

The library supports two methods for exchanging authorization codes:

1. **Traditional method**: Extract code manually from callback URL
2. **Paste-the-URL method**: Copy entire callback URL (recommended - see [OAUTH_FLOW_GUIDE.md](OAUTH_FLOW_GUIDE.md))

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
- Invalid authorization codes (use --verbose for detailed error info)
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

