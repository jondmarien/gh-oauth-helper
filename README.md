# GitHub OAuth Helper

[![PyPI version](https://badge.fury.io/py/gh-oauth-helper.svg)](https://badge.fury.io/py/gh-oauth-helper)
[![Python Support](https://img.shields.io/pypi/pyversions/gh-oauth-helper.svg)](https://pypi.org/project/gh-oauth-helper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A secure, easy-to-use Python library and CLI tool for GitHub OAuth authentication. Handle GitHub OAuth flows without exposing secrets in your code.

## ✨ Features

- 🔐 **Secure by Design**: Never hard-code OAuth secrets
- 🛡️ **CSRF Protection**: Built-in state parameter generation and verification
- 🎨 **Colored CLI**: Beautiful, intuitive command-line interface
- 🔧 **Flexible Usage**: Both programmatic API and CLI tool
- 🌐 **Transport Security**: Automatic HTTP/HTTPS handling with security modes
- 📝 **Comprehensive**: Full OAuth flow support including token revocation
- 🐍 **Python 3.8+**: Modern Python with type hints

## 🚀 Quick Start

### Installation

#### Using uv (Recommended - Fastest Python Package Manager)

```bash
# Install from PyPI
uv add gh-oauth-helper

# Or install with development dependencies
uv add "gh-oauth-helper[dev]"

# For development/testing with all extras
uv add "gh-oauth-helper[dev,docs]"
```

#### Using pip

```bash
# Install from PyPI
pip install gh-oauth-helper

# Or install with development dependencies
pip install "gh-oauth-helper[dev]"
```

### Set Up Environment Variables

```bash
export GITHUB_CLIENT_ID="your_oauth_app_client_id"
export GITHUB_CLIENT_SECRET="your_oauth_app_client_secret"
export GITHUB_REDIRECT_URI="http://localhost:8080/callback"  # Optional
```

### Basic CLI Usage

```bash
# Generate authorization URL and open in browser
gh-oauth-helper auth --open

# Exchange authorization code for token (traditional method)
gh-oauth-helper token --code YOUR_AUTH_CODE

# Or use the easier paste-the-URL method (recommended!)
gh-oauth-helper token --url "http://localhost:8080/callback?code=YOUR_AUTH_CODE&state=YOUR_STATE"

# Test token validity
gh-oauth-helper test --token YOUR_ACCESS_TOKEN
```

### Basic Python Usage

```python
from gh_oauth_helper import GitHubOAuth

# Initialize OAuth helper (uses environment variables)
oauth = GitHubOAuth()

# Generate authorization URL
auth_url, state = oauth.generate_authorization_url(scopes=["user", "repo"])
print(f"Visit: {auth_url}")

# Exchange code for token (after user authorization)
token_data = oauth.exchange_code_for_token(code, state)
access_token = token_data["access_token"]

# Test the token
user_info = oauth.test_api_access(access_token)
print(f"Authenticated as: {user_info['login']}")
```

## 🔧 GitHub OAuth App Setup

Before using this library, you need to create a GitHub OAuth App:

### 1. Create OAuth App

1. Go to **GitHub Settings** → **Developer settings** → **OAuth Apps**
2. Click **"New OAuth App"**
3. Fill in the application details:
   - **Application name**: Your app name
   - **Homepage URL**: Your app's homepage (can be `http://localhost:8080` for development)
   - **Authorization callback URL**: `http://localhost:8080/callback` (for development)
4. Click **"Register application"**

### 2. Get Your Credentials

After creating the app:

1. Copy the **Client ID** (publicly visible)
2. Click **"Generate a new client secret"** and copy the **Client Secret** (keep this secure!)

### 3. Set Environment Variables

```bash
# Required
export GITHUB_CLIENT_ID="your_client_id_here"
export GITHUB_CLIENT_SECRET="your_client_secret_here"

# Optional (defaults to http://localhost:8080/callback)
export GITHUB_REDIRECT_URI="http://localhost:8080/callback"
```

### 4. Production Setup

For production applications:

- Use **HTTPS** for your callback URL: `https://yourapp.com/oauth/callback`
- Use environment variables or secure secret management
- Enable **secure mode** in the CLI: `gh-oauth-helper --secure auth`

## 💻 CLI Usage Examples

### Authorization Flow

```bash
# Basic authorization (opens browser automatically)
gh-oauth-helper auth --open

# Custom scopes
gh-oauth-helper auth --scopes user repo read:org --open

# Production setup with HTTPS
gh-oauth-helper --secure auth --redirect-uri https://myapp.com/callback

# Get JSON output for scripting
gh-oauth-helper --json auth --scopes user
```

### Token Exchange

```bash
# Method 1: Exchange authorization code for access token (traditional)
gh-oauth-helper token --code ghu_1234567890abcdef

# With state verification (recommended)
gh-oauth-helper token --code ghu_1234567890abcdef --state abc123

# Method 2: Paste the full callback URL (easier! - see OAUTH_FLOW_GUIDE.md)
gh-oauth-helper token --url "http://localhost:8080/callback?code=ghu_1234567890abcdef&state=abc123"

# JSON output
gh-oauth-helper --json token --code ghu_1234567890abcdef
```

### Token Management

```bash
# Test token validity
gh-oauth-helper test --token gho_1234567890abcdef

# Revoke token
gh-oauth-helper revoke --token gho_1234567890abcdef

# Verbose output for debugging (shows detailed operation info)
gh-oauth-helper --verbose test --token gho_1234567890abcdef
```

### Common Workflows

```bash
# Complete OAuth flow with verification
gh-oauth-helper auth --open --scopes user repo
# (authorize in browser, get code from callback)
gh-oauth-helper token --code YOUR_CODE --state YOUR_STATE
gh-oauth-helper test --token YOUR_ACCESS_TOKEN

# Easy method: Use the full callback URL (recommended for beginners)
# See OAUTH_FLOW_GUIDE.md for detailed instructions
gh-oauth-helper auth --open
# (authorize in browser, copy the entire callback URL)
gh-oauth-helper token --url "http://localhost:8080/callback?code=ghu_...&state=..."
# Test your token immediately
gh-oauth-helper test --token YOUR_ACCESS_TOKEN

# One-liner for development (using environment variables)
gh-oauth-helper auth --open && echo "Paste your code:" && read CODE && gh-oauth-helper token --code $CODE
```

## 🔍 Python API Reference

### GitHubOAuth Class

```python
from gh_oauth_helper import GitHubOAuth, GitHubOAuthError

# Initialize with explicit credentials
oauth = GitHubOAuth(
    client_id="your_client_id",
    client_secret="your_client_secret", 
    redirect_uri="http://localhost:8080/callback",
    secure_mode=True  # Enforce HTTPS
)

# Or use environment variables
oauth = GitHubOAuth()  # Reads from GITHUB_CLIENT_ID, etc.
```

### Common OAuth Scopes

| Scope | Description |
|-------|-------------|
| `user` | Read user profile information |
| `user:email` | Read user email addresses |
| `repo` | Full access to repositories |
| `public_repo` | Access to public repositories only |
| `read:org` | Read organization membership |
| `admin:org` | Full organization access |
| `gist` | Create and modify gists |
| `notifications` | Access notifications |

### Error Handling

```python
from gh_oauth_helper import GitHubOAuthError

try:
    oauth = GitHubOAuth()
    auth_url, state = oauth.generate_authorization_url()
    # ... OAuth flow
except GitHubOAuthError as e:
    print(f"OAuth error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🔒 Security Features

### Transport Security

- **Automatic HTTPS Detection**: Automatically configures secure transport based on redirect URI
- **Secure Mode**: Use `--secure` flag to enforce HTTPS for non-localhost URLs
- **Localhost Exception**: HTTP allowed for `localhost` development even in secure mode

### Secret Management

- **Environment Variables**: Never hard-code secrets in your code
- **No Logging**: Sensitive data is never logged or exposed
- **Memory Safety**: Credentials are not stored longer than necessary

### CSRF Protection

- **State Parameter**: Automatic generation of cryptographically secure state parameters
- **State Verification**: Built-in verification to prevent CSRF attacks
- **Secure Random**: Uses `secrets` module for cryptographic randomness

### Best Practices

```bash
# ✅ DO: Use environment variables
export GITHUB_CLIENT_SECRET="ghp_..."
gh-oauth-helper auth

# ❌ DON'T: Pass secrets as arguments (visible in process list)
gh-oauth-helper auth --client-secret ghp_...

# ✅ DO: Use HTTPS in production
gh-oauth-helper --secure auth --redirect-uri https://myapp.com/callback

# ✅ DO: Verify state parameter
gh-oauth-helper token --code CODE --state STATE
```

## 📚 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed installation instructions
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Security Guide](docs/security.md)** - Security best practices and features
- **[Examples](examples/)** - Working code examples
- **[Contributing Guide](docs/contributing.md)** - How to contribute to the project

## 🌟 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for details.

### Quick Development Setup

#### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/jondmarien/gh-oauth-helper.git
cd gh-oauth-helper

# Install dependencies and create virtual environment automatically
uv sync --extra dev --extra docs

# Activate the virtual environment (if needed)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run tests
uv run pytest

# Run linting
uv run make lint

# Format code
uv run make format
```

#### Using pip

```bash
# Clone the repository
git clone https://github.com/jondmarien/gh-oauth-helper.git
cd gh-oauth-helper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
make lint

# Format code
make format
```

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes
4. **Add** tests for new functionality
5. **Run** the test suite: `pytest`
6. **Commit** your changes: `git commit -m 'Add amazing feature'`
7. **Push** to your branch: `git push origin feature/amazing-feature`
8. **Create** a Pull Request

### Development Guidelines

- Follow **PEP 8** style guidelines
- Add **type hints** to all functions
- Write **tests** for new features
- Update **documentation** for API changes
- Use **meaningful commit messages**

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [requests-oauthlib](https://github.com/requests/requests-oauthlib)
- Inspired by the GitHub OAuth documentation
- Thanks to all [contributors](https://github.com/jondmarien/gh-oauth-helper/contributors)

### Honorable Mention

[Warp (Preview)](https://warp.dev) really helped me through the harder parts of this project, especially with pypi and making sure everything was up to the required standards. Definitely huge thanks to the Warp Team. Can't wait for their June 24th, 2025 surprise release!!! (👀👀 I wonder what it could be!)

## 🔗 Links

- **[PyPI Package](https://pypi.org/project/gh-oauth-helper/)**
- **[GitHub Repository](https://github.com/jondmarien/gh-oauth-helper)**
- **[Documentation](https://gh-oauth-helper.readthedocs.io)**
- **[Issue Tracker](https://github.com/jondmarien/gh-oauth-helper/issues)**
- **[GitHub OAuth Documentation](https://docs.github.com/en/apps/oauth-apps)**

