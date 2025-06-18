# API Reference

Complete reference for the GitHub OAuth Helper Python API.

## Overview

The GitHub OAuth Helper provides both a programmatic API and a command-line interface for handling GitHub OAuth authentication flows.

## Core Classes

### GitHubOAuth

The main class for handling GitHub OAuth operations.

```python
from gh_oauth_helper import GitHubOAuth, GitHubOAuthError
```

#### Constructor

```python
GitHubOAuth(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None, 
    redirect_uri: Optional[str] = None,
    secure_mode: bool = False
)
```

**Parameters:**

- `client_id` (str, optional): GitHub OAuth app client ID. If not provided, reads from `GITHUB_CLIENT_ID` environment variable.
- `client_secret` (str, optional): GitHub OAuth app client secret. If not provided, reads from `GITHUB_CLIENT_SECRET` environment variable.
- `redirect_uri` (str, optional): OAuth redirect URI. If not provided, reads from `GITHUB_REDIRECT_URI` environment variable or defaults to `http://localhost:8080/callback`.
- `secure_mode` (bool): If True, enforces HTTPS for non-localhost redirect URIs.

**Raises:**

- `GitHubOAuthError`: If required credentials are missing.

**Example:**

```python
# Using environment variables
oauth = GitHubOAuth()

# Using explicit credentials
oauth = GitHubOAuth(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:8080/callback",
    secure_mode=True
)
```

#### Methods

##### `generate_authorization_url(scopes=None, state=None)`

Generate the GitHub authorization URL for the OAuth flow.

**Parameters:**

- `scopes` (List[str], optional): List of OAuth scopes to request. Defaults to `["user:email", "repo"]`.
- `state` (str, optional): CSRF protection state parameter. If not provided, a secure random state is generated.

**Returns:**

- `Tuple[str, str]`: A tuple containing the authorization URL and the state parameter.

**Example:**

```python
auth_url, state = oauth.generate_authorization_url(
    scopes=["user", "public_repo", "read:org"]
)
print(f"Visit: {auth_url}")
print(f"State: {state}")  # Save this for verification
```

##### `exchange_code_for_token(code, state=None)`

Exchange an authorization code for an access token.

**Parameters:**

- `code` (str): The authorization code received from GitHub's callback.
- `state` (str, optional): The state parameter for CSRF verification.

**Returns:**

- `Dict[str, Any]`: Dictionary containing token information including `access_token`, `token_type`, and `scope`.

**Raises:**

- `GitHubOAuthError`: If the code exchange fails or state verification fails.

**Example:**

```python
try:
    token_data = oauth.exchange_code_for_token(
        code="ghu_1234567890abcdef",
        state="abc123"  # From generate_authorization_url
    )
    access_token = token_data["access_token"]
    print(f"Token received: {access_token[:10]}...")
except GitHubOAuthError as e:
    print(f"Token exchange failed: {e}")
```

##### `test_api_access(access_token)`

Test API access with the provided access token.

**Parameters:**

- `access_token` (str): The GitHub access token to test.

**Returns:**

- `Dict[str, Any]`: Dictionary containing authenticated user information.

**Raises:**

- `GitHubOAuthError`: If the token is invalid or API access fails.

**Example:**

```python
try:
    user_info = oauth.test_api_access(access_token)
    print(f"Authenticated as: {user_info['login']}")
    print(f"Name: {user_info.get('name', 'N/A')}")
    print(f"Email: {user_info.get('email', 'N/A')}")
except GitHubOAuthError as e:
    print(f"Token validation failed: {e}")
```

##### `revoke_token(access_token)`

Revoke an access token.

**Parameters:**

- `access_token` (str): The GitHub access token to revoke.

**Returns:**

- `bool`: True if revocation was successful, False otherwise.

**Example:**

```python
success = oauth.revoke_token(access_token)
if success:
    print("Token revoked successfully")
else:
    print("Token revocation failed")
```

## Convenience Functions

For simple use cases, the library provides convenience functions that use environment variables.

### `start_auth_flow(oauth_helper=None, scopes=None)`

Start an OAuth flow using environment variables.

**Parameters:**

- `oauth_helper` (GitHubOAuth, optional): OAuth helper instance. If not provided, creates one using environment variables.
- `scopes` (List[str], optional): OAuth scopes to request.

**Returns:**

- `Tuple[str, str]`: Authorization URL and state parameter.

**Example:**

```python
from gh_oauth_helper import start_auth_flow

auth_url, state = start_auth_flow(scopes=["user", "repo"])
print(f"Visit: {auth_url}")
```

### `complete_auth_flow(code, oauth_helper=None, state=None)`

Complete an OAuth flow by exchanging code for token.

**Parameters:**

- `code` (str): Authorization code from GitHub.
- `oauth_helper` (GitHubOAuth, optional): OAuth helper instance.
- `state` (str, optional): State parameter for verification.

**Returns:**

- `Dict[str, Any]`: Token data from GitHub.

**Example:**

```python
from gh_oauth_helper import complete_auth_flow

token_data = complete_auth_flow(code="ghu_123", state="abc123")
access_token = token_data["access_token"]
```

### `verify_token(access_token, oauth_helper=None)`

Verify an access token by testing API access.

**Parameters:**

- `access_token` (str): Token to verify.
- `oauth_helper` (GitHubOAuth, optional): OAuth helper instance.

**Returns:**

- `Dict[str, Any]`: User information from GitHub API.

**Example:**

```python
from gh_oauth_helper import verify_token

user_info = verify_token(access_token)
print(f"Token valid for user: {user_info['login']}")
```

## Exceptions

### GitHubOAuthError

Base exception class for OAuth-related errors.

```python
class GitHubOAuthError(Exception):
    """Exception raised for GitHub OAuth errors."""
    pass
```

**Common scenarios:**

- Missing credentials
- Invalid authorization codes
- Expired tokens
- Network errors
- API rate limiting

**Example:**

```python
from gh_oauth_helper import GitHubOAuthError

try:
    oauth = GitHubOAuth()
    # ... OAuth operations
except GitHubOAuthError as e:
    print(f"OAuth error: {e}")
    # Handle OAuth-specific errors
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle other errors
```

## Environment Variables

The library supports the following environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GITHUB_CLIENT_ID` | OAuth app client ID | Yes | None |
| `GITHUB_CLIENT_SECRET` | OAuth app client secret | Yes | None |
| `GITHUB_REDIRECT_URI` | OAuth callback URL | No | `http://localhost:8080/callback` |

**Setting environment variables:**

```bash
# Linux/macOS
export GITHUB_CLIENT_ID="your_client_id"
export GITHUB_CLIENT_SECRET="your_client_secret"
export GITHUB_REDIRECT_URI="http://localhost:8080/callback"

# Windows (Command Prompt)
set GITHUB_CLIENT_ID=your_client_id
set GITHUB_CLIENT_SECRET=your_client_secret

# Windows (PowerShell)
$env:GITHUB_CLIENT_ID="your_client_id"
$env:GITHUB_CLIENT_SECRET="your_client_secret"
```

## OAuth Scopes Reference

Common GitHub OAuth scopes:

### User Scopes

- `user` - Read user profile information
- `user:email` - Read user email addresses  
- `user:follow` - Follow/unfollow other users

### Repository Scopes

- `repo` - Full access to repositories (public and private)
- `public_repo` - Access to public repositories only
- `repo:status` - Access to commit status
- `repo_deployment` - Access to deployment status

### Organization Scopes

- `read:org` - Read organization membership
- `write:org` - Write access to organization membership
- `admin:org` - Full organization access

### Other Scopes

- `gist` - Create and modify gists
- `notifications` - Access notifications
- `read:discussion` - Read team discussions
- `workflow` - Access to GitHub Actions workflows

**Example with multiple scopes:**

```python
oauth = GitHubOAuth()
auth_url, state = oauth.generate_authorization_url(
    scopes=["user", "repo", "read:org", "gist"]
)
```

## Type Hints

The library includes comprehensive type hints for better IDE support:

```python
from typing import Dict, List, Optional, Tuple, Any
from gh_oauth_helper import GitHubOAuth

oauth: GitHubOAuth = GitHubOAuth()
auth_url: str
state: str
auth_url, state = oauth.generate_authorization_url()

token_data: Dict[str, Any] = oauth.exchange_code_for_token(code)
user_info: Dict[str, Any] = oauth.test_api_access(token_data["access_token"])
```

## Error Handling Best Practices

```python
import logging
from gh_oauth_helper import GitHubOAuth, GitHubOAuthError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_oauth_flow(code: str, state: str) -> Optional[str]:
    """Handle OAuth flow with proper error handling."""
    try:
        oauth = GitHubOAuth()
        
        # Exchange code for token
        token_data = oauth.exchange_code_for_token(code, state)
        access_token = token_data["access_token"]
        
        # Verify token works
        user_info = oauth.test_api_access(access_token)
        logger.info(f"Successfully authenticated user: {user_info['login']}")
        
        return access_token
        
    except GitHubOAuthError as e:
        logger.error(f"OAuth error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
```

## Advanced Usage

### Custom HTTP Session

```python
import requests
from gh_oauth_helper.core import GitHubOAuth

# Create custom session with timeouts and retries
session = requests.Session()
session.timeout = 30

# Note: Advanced session customization requires modifying the core class
# This is an example of how you might extend the functionality
```

### Batch Operations

```python
def authenticate_multiple_users(codes_and_states):
    """Authenticate multiple users in batch."""
    oauth = GitHubOAuth()
    results = []
    
    for code, state in codes_and_states:
        try:
            token_data = oauth.exchange_code_for_token(code, state)
            user_info = oauth.test_api_access(token_data["access_token"])
            results.append({
                "success": True,
                "user": user_info["login"],
                "token": token_data["access_token"]
            })
        except GitHubOAuthError as e:
            results.append({
                "success": False,
                "error": str(e)
            })
    
    return results
```

## Security Considerations

When using the API programmatically:

1. **Never log sensitive data**: Tokens and secrets should never appear in logs
2. **Use secure storage**: Store tokens securely (environment variables, key stores)
3. **Implement token rotation**: Refresh tokens when possible
4. **Validate inputs**: Always validate and sanitize user inputs
5. **Use HTTPS**: Ensure all OAuth flows use HTTPS in production
6. **Handle errors gracefully**: Don't expose sensitive error details to users

```python
def secure_token_storage(access_token: str) -> None:
    """Example of secure token handling."""
    # DON'T: Log the full token
    # logger.info(f"Received token: {access_token}")
    
    # DO: Log only partial information
    logger.info(f"Received token: {access_token[:10]}...")
    
    # DO: Store securely (example with environment variable)
    import os
    os.environ["USER_GITHUB_TOKEN"] = access_token
```

