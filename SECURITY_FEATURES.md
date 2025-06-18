# Security Features and UX Enhancements

This document describes the security hardening and user experience improvements implemented in gh-oauth-helper.

## Security Features

### Transport Security Configuration

The library now automatically configures transport security based on the OAuth redirect URI and security mode:

#### Default Behavior (Standard Mode)
- **Localhost URIs**: Automatically sets `OAUTHLIB_INSECURE_TRANSPORT=1` to allow HTTP for local development
- **Non-localhost HTTP URIs**: Shows a warning and allows HTTP (with `OAUTHLIB_INSECURE_TRANSPORT=1`)
- **HTTPS URIs**: Always secure, no environment variable needed

#### Secure Mode (`--secure` flag)
- **Localhost URIs**: HTTP is allowed for localhost development
- **Non-localhost URIs**: HTTPS is required, HTTP will raise an error
- **Transport**: `OAUTHLIB_INSECURE_TRANSPORT` is disabled for strict security

### Usage Examples

#### Standard Mode (Default)
```bash
# Localhost development - automatically enables insecure transport
gh-oauth-helper auth --redirect-uri http://localhost:8080/callback

# Production with HTTPS - automatically secure
gh-oauth-helper auth --redirect-uri https://myapp.com/oauth/callback

# Non-localhost HTTP - shows warning but allows
gh-oauth-helper auth --redirect-uri http://staging.myapp.com/oauth/callback
```

#### Secure Mode
```bash
# Secure mode with HTTPS - strict security enabled
gh-oauth-helper --secure auth --redirect-uri https://myapp.com/oauth/callback

# Secure mode with localhost - still allows HTTP for localhost
gh-oauth-helper --secure auth --redirect-uri http://localhost:8080/callback

# Secure mode with non-localhost HTTP - will error
gh-oauth-helper --secure auth --redirect-uri http://staging.myapp.com/oauth/callback
# Error: Secure mode requires HTTPS redirect URI for non-localhost addresses
```

## User Experience Enhancements

### Colored Output

The CLI now provides colored, intuitive output when the `colorama` library is available:

- ✅ **Success messages** in green with checkmark
- ❌ **Error messages** in red with X mark  
- ⚠️ **Warning messages** in yellow with warning symbol
- ℹ️ **Info messages** in blue with info symbol
- **Important text** highlighted in cyan or white

### Enhanced Prompts and Messages

#### Before (Plain Text)
```
Generated GitHub OAuth authorization URL
Authorization URL:
https://github.com/login/oauth/authorize?...
State (save this for verification): abc123...
```

#### After (Colored and Enhanced)
```
✅ Generated GitHub OAuth authorization URL
Authorization URL:
https://github.com/login/oauth/authorize?...

State (save this for verification): abc123...
```

### Robust Exception Handling

The CLI now provides better error handling and user feedback:

#### OAuth Errors
```bash
❌ OAuth Error: GitHub client ID is required. Provide it as parameter or set GITHUB_CLIENT_ID environment variable.
```

#### Network Errors
```bash
❌ OAuth Error: Failed to exchange code for token: Connection timeout
```

#### Unexpected Errors (with verbose mode)
```bash
❌ Unexpected error: Invalid JSON response
# With --verbose flag, shows full traceback in red
```

### Browser Integration Improvements

Enhanced browser opening with better error handling:

```bash
ℹ️ Opening authorization URL in browser...
✅ Browser opened successfully

# Or if browser fails:
⚠️ Could not open browser: No web browser found
ℹ️ Please copy and paste the URL manually
```

### Verbose Mode Enhancements

The `--verbose` flag now provides richer, colored diagnostic information:

```bash
ℹ️ Initializing GitHub OAuth helper...
ℹ️ Running in standard mode (HTTP allowed for localhost)
ℹ️ Scopes requested: user:email, repo
ℹ️ State parameter: abc123...
ℹ️ Redirect URI: http://localhost:8080/callback
✅ Generated GitHub OAuth authorization URL
```

## Backward Compatibility

All changes are backward compatible:

- **Existing code**: Works without modification
- **Environment variables**: Still supported and respected
- **API signatures**: Extended with optional parameters (defaults maintain old behavior)
- **Output format**: JSON output unchanged, only human-readable output enhanced

## Configuration

### Environment Variables

The library automatically manages the `OAUTHLIB_INSECURE_TRANSPORT` environment variable:

- **Standard mode**: Set to `'1'` for localhost and HTTP URIs
- **Secure mode**: Removed/unset for strict HTTPS enforcement
- **Manual override**: You can still set this manually if needed

### Dependencies

- **colorama** (≥0.4.4): Added for colored output support
- Graceful fallback if colorama is not installed (plain text output)

## Security Best Practices

1. **Use secure mode in production**: Pass `--secure` flag for production deployments
2. **HTTPS redirect URIs**: Use HTTPS for production OAuth callbacks
3. **Environment variables**: Store sensitive credentials in environment variables, not command-line arguments
4. **State parameter verification**: Always verify the state parameter in OAuth callbacks

## Migration Guide

### From Previous Versions

No code changes required! The new features are opt-in:

```python
# Old usage (still works)
oauth = GitHubOAuth(client_id, client_secret, redirect_uri)

# New usage with security features
oauth = GitHubOAuth(client_id, client_secret, redirect_uri, secure_mode=True)
```

### CLI Migration

```bash
# Old command (still works)
gh-oauth-helper auth --client-id ID --client-secret SECRET

# New secure command
gh-oauth-helper --secure auth --client-id ID --client-secret SECRET

# New verbose command with colors
gh-oauth-helper --verbose auth --client-id ID --client-secret SECRET
```

