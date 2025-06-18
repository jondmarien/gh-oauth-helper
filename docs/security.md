# Security Guide

This guide covers the security features and best practices for using the GitHub OAuth Helper safely.

## Overview

The GitHub OAuth Helper is designed with security as a primary concern. This guide explains the built-in security features and provides recommendations for secure usage.

## Built-in Security Features

### 1. No Hard-Coded Secrets

The library never hard-codes OAuth secrets in source code:

```python
# ✅ SECURE: Uses environment variables
oauth = GitHubOAuth()  # Reads from GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

# ❌ INSECURE: Hard-coded secrets
oauth = GitHubOAuth(
    client_id="ghp_hardcoded_secret",  # Visible in source code
    client_secret="secret_123"         # Security risk
)
```

**Why this matters:**
- Prevents accidental exposure in version control
- Reduces risk of secrets in compiled binaries
- Enables secure deployment practices

### 2. Environment Variable Management

Automatic environment variable handling with validation:

```python
import os
from gh_oauth_helper import GitHubOAuth, GitHubOAuthError

# The library validates that required variables are set
try:
    oauth = GitHubOAuth()
except GitHubOAuthError as e:
    print(f"Missing required environment variables: {e}")
```

**Required variables:**
- `GITHUB_CLIENT_ID`: Your OAuth app client ID
- `GITHUB_CLIENT_SECRET`: Your OAuth app client secret

**Optional variables:**
- `GITHUB_REDIRECT_URI`: Callback URL (defaults to localhost)

### 3. CSRF Protection with State Parameters

Automatic generation and verification of state parameters:

```python
# State parameter automatically generated
auth_url, state = oauth.generate_authorization_url()

# Save state for verification (in session, database, etc.)
session['oauth_state'] = state

# Later, verify the state when processing the callback
try:
    token_data = oauth.exchange_code_for_token(
        code=request.args.get('code'),
        state=session.get('oauth_state')  # Verify against saved state
    )
except GitHubOAuthError as e:
    print(f"CSRF verification failed: {e}")
```

**State parameter features:**
- Cryptographically secure random generation
- Prevents cross-site request forgery attacks
- Automatic verification during token exchange

### 4. Transport Security

Automatic HTTPS enforcement based on context:

#### Standard Mode (Default)
```python
oauth = GitHubOAuth()  # Standard mode

# Localhost development - HTTP allowed
auth_url, state = oauth.generate_authorization_url()
# Uses redirect_uri = "http://localhost:8080/callback"

# Production HTTPS - automatically secure
oauth = GitHubOAuth(redirect_uri="https://myapp.com/oauth/callback")
```

#### Secure Mode
```python
oauth = GitHubOAuth(secure_mode=True)  # Strict HTTPS enforcement

# This will raise an error in secure mode
oauth = GitHubOAuth(
    redirect_uri="http://example.com/callback",  # Non-localhost HTTP
    secure_mode=True
)
# GitHubOAuthError: Secure mode requires HTTPS redirect URI
```

**Transport security rules:**
- **Localhost**: HTTP allowed in both modes (development)
- **Non-localhost**: HTTP allowed in standard mode (with warning), HTTPS required in secure mode
- **HTTPS**: Always secure in both modes

### 5. Token Safety

Secure token handling throughout the library:

```python
# Tokens are never logged or exposed in error messages
try:
    user_info = oauth.test_api_access(access_token)
except GitHubOAuthError as e:
    # Error message doesn't contain the token
    print(f"Token validation failed: {e}")

# Tokens are not stored longer than necessary
token_data = oauth.exchange_code_for_token(code, state)
# Token is returned immediately, not cached
```

**Token safety features:**
- No logging of sensitive data
- No caching of tokens in memory
- Secure error handling without token exposure
- Proper cleanup of sensitive variables

## CLI Security Features

### 1. Secure Parameter Handling

```bash
# ✅ SECURE: Environment variables (not visible in process list)
export GITHUB_CLIENT_SECRET="ghp_secret"
gh-oauth-helper auth

# ❌ INSECURE: Command-line parameters (visible in `ps` output)
gh-oauth-helper auth --client-secret ghp_secret
```

### 2. Secure Mode Flag

```bash
# Enable strict HTTPS enforcement
gh-oauth-helper --secure auth --redirect-uri https://myapp.com/callback

# This will fail in secure mode:
gh-oauth-helper --secure auth --redirect-uri http://staging.com/callback
# Error: Secure mode requires HTTPS redirect URI for non-localhost addresses
```

### 3. Colored Security Warnings

The CLI provides visual security warnings:

```bash
# Warning for HTTP redirect URIs
⚠️ Warning: Using HTTP redirect URI for non-localhost address. Consider using HTTPS in production.

# Error for security violations
❌ OAuth Error: Secure mode requires HTTPS redirect URI for non-localhost addresses
```

## Best Practices

### 1. Environment Variable Security

#### Development Environment
```bash
# Use .env files (add to .gitignore)
echo "GITHUB_CLIENT_ID=your_id" >> .env
echo "GITHUB_CLIENT_SECRET=your_secret" >> .env
echo ".env" >> .gitignore

# Load environment variables
export $(cat .env | xargs)
```

#### Production Environment
```bash
# Use your platform's secret management
# Examples:

# Docker
docker run -e GITHUB_CLIENT_ID="$CLIENT_ID" myapp

# Kubernetes
kubectl create secret generic github-oauth \
  --from-literal=client-id="$CLIENT_ID" \
  --from-literal=client-secret="$CLIENT_SECRET"

# AWS Systems Manager Parameter Store
aws ssm put-parameter \
  --name "/myapp/github/client-id" \
  --value "$CLIENT_ID" \
  --type "SecureString"
```

### 2. HTTPS Configuration

#### Production Setup
```python
# Always use HTTPS in production
oauth = GitHubOAuth(
    redirect_uri="https://myapp.com/oauth/callback",
    secure_mode=True  # Enforce HTTPS
)
```

#### SSL Certificate Validation
```python
import ssl
import requests

# Ensure SSL certificates are validated
session = requests.Session()
session.verify = True  # Default, but explicit is better

# Don't disable SSL verification in production
# session.verify = False  # ❌ NEVER DO THIS
```

### 3. State Parameter Management

#### Web Application Example
```python
from flask import Flask, session, request, redirect
from gh_oauth_helper import GitHubOAuth, GitHubOAuthError

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Use a proper secret

@app.route('/login')
def login():
    oauth = GitHubOAuth()
    auth_url, state = oauth.generate_authorization_url()
    
    # Store state in session
    session['oauth_state'] = state
    
    return redirect(auth_url)

@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = session.pop('oauth_state', None)
    
    # Verify state parameter
    if not stored_state or state != stored_state:
        return "CSRF verification failed", 400
    
    try:
        oauth = GitHubOAuth()
        token_data = oauth.exchange_code_for_token(code, state)
        # Handle successful authentication
        return f"Authenticated successfully!"
    except GitHubOAuthError as e:
        return f"Authentication failed: {e}", 400
```

### 4. Token Storage and Management

#### Secure Token Storage
```python
import os
import keyring  # Optional: for OS keychain integration

def store_token_securely(username: str, token: str) -> None:
    """Store token using OS keychain (recommended)."""
    try:
        keyring.set_password("github-oauth", username, token)
    except Exception:
        # Fallback to environment variable
        os.environ[f"GITHUB_TOKEN_{username.upper()}"] = token

def get_stored_token(username: str) -> str:
    """Retrieve token from secure storage."""
    try:
        return keyring.get_password("github-oauth", username)
    except Exception:
        return os.environ.get(f"GITHUB_TOKEN_{username.upper()}")
```

#### Token Rotation
```python
import time
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self):
        self.tokens = {}  # In production, use secure database
    
    def store_token(self, user_id: str, token_data: dict) -> None:
        """Store token with metadata."""
        self.tokens[user_id] = {
            'access_token': token_data['access_token'],
            'created_at': datetime.now(),
            'expires_in': token_data.get('expires_in', 3600),
            'scope': token_data.get('scope', '')
        }
    
    def is_token_expired(self, user_id: str) -> bool:
        """Check if token needs refresh."""
        if user_id not in self.tokens:
            return True
        
        token_info = self.tokens[user_id]
        expires_at = token_info['created_at'] + timedelta(
            seconds=token_info['expires_in']
        )
        
        # Refresh 5 minutes before expiry
        return datetime.now() >= (expires_at - timedelta(minutes=5))
    
    def revoke_token(self, user_id: str) -> None:
        """Revoke and remove token."""
        if user_id in self.tokens:
            oauth = GitHubOAuth()
            oauth.revoke_token(self.tokens[user_id]['access_token'])
            del self.tokens[user_id]
```

### 5. Error Handling and Logging

#### Secure Error Handling
```python
import logging
from gh_oauth_helper import GitHubOAuthError

# Configure logging to exclude sensitive data
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        # Remove tokens from log messages
        if hasattr(record, 'msg'):
            record.msg = self.sanitize_message(record.msg)
        return True
    
    def sanitize_message(self, message):
        import re
        # Remove GitHub tokens (ghp_, gho_, etc.)
        return re.sub(r'gh[a-z]_[A-Za-z0-9_]{36}', '[REDACTED]', str(message))

# Set up logging
logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())

def handle_oauth_error(e: GitHubOAuthError) -> dict:
    """Handle OAuth errors securely."""
    # Log the error without exposing sensitive details
    logger.error(f"OAuth operation failed: {type(e).__name__}")
    
    # Return generic error to user
    return {
        'error': 'Authentication failed',
        'message': 'Please try again or contact support',
        'code': 'OAUTH_ERROR'
    }
```

### 6. Input Validation

#### Validate OAuth Parameters
```python
import re
from gh_oauth_helper import GitHubOAuthError

def validate_oauth_code(code: str) -> str:
    """Validate GitHub authorization code format."""
    if not code:
        raise ValueError("Authorization code is required")
    
    # GitHub codes are typically 20 characters, alphanumeric
    if not re.match(r'^[a-zA-Z0-9]{20}$', code):
        raise ValueError("Invalid authorization code format")
    
    return code

def validate_state_parameter(state: str) -> str:
    """Validate state parameter."""
    if not state:
        raise ValueError("State parameter is required")
    
    # State should be at least 8 characters
    if len(state) < 8:
        raise ValueError("State parameter too short")
    
    # Should contain only safe characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', state):
        raise ValueError("State parameter contains invalid characters")
    
    return state
```

## Security Checklist

### Development
- [ ] Store OAuth secrets in environment variables
- [ ] Add `.env` files to `.gitignore`
- [ ] Use HTTPS for redirect URIs in staging/production
- [ ] Implement proper state parameter verification
- [ ] Validate all user inputs
- [ ] Use secure logging practices

### Production
- [ ] Use secure secret management (AWS Secrets Manager, Azure Key Vault, etc.)
- [ ] Enable secure mode for OAuth helper
- [ ] Use HTTPS everywhere
- [ ] Implement token rotation
- [ ] Set up proper monitoring and alerting
- [ ] Regular security audits
- [ ] Implement rate limiting
- [ ] Use secure session management

### CLI Usage
- [ ] Use environment variables instead of command-line arguments
- [ ] Enable secure mode with `--secure` flag
- [ ] Use HTTPS redirect URIs in production
- [ ] Implement proper secret rotation procedures

## Common Security Mistakes to Avoid

### 1. Hard-coding Secrets
```python
# ❌ DON'T
oauth = GitHubOAuth(
    client_id="ghp_hardcoded",
    client_secret="secret123"
)

# ✅ DO
oauth = GitHubOAuth()  # Uses environment variables
```

### 2. Ignoring State Verification
```python
# ❌ DON'T
token_data = oauth.exchange_code_for_token(code)  # No state verification

# ✅ DO
token_data = oauth.exchange_code_for_token(code, state)  # Verify state
```

### 3. Using HTTP in Production
```python
# ❌ DON'T
oauth = GitHubOAuth(redirect_uri="http://myapp.com/callback")

# ✅ DO
oauth = GitHubOAuth(
    redirect_uri="https://myapp.com/callback",
    secure_mode=True
)
```

### 4. Logging Sensitive Data
```python
# ❌ DON'T
logger.info(f"Received token: {access_token}")

# ✅ DO
logger.info(f"Token received: {access_token[:10]}...")
```

### 5. Not Revoking Tokens
```python
# ✅ DO: Always revoke tokens when done
def logout_user(access_token):
    oauth = GitHubOAuth()
    oauth.revoke_token(access_token)
    # Clear from storage
```

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. Email the maintainers directly at security@example.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

We follow responsible disclosure practices and will acknowledge security reports within 48 hours.

## Security Updates

- Monitor the [GitHub repository](https://github.com/jondmarien/gh-oauth-helper) for security updates
- Subscribe to release notifications
- Keep the library updated to the latest version
- Review the [SECURITY.md](../SECURITY.md) file for the latest security policies

