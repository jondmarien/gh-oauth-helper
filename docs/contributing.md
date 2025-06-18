# Contributing Guide

Thank you for your interest in contributing to the GitHub OAuth Helper! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please read and follow our [Code of Conduct](https://github.com/jondmarien/gh-oauth-helper/blob/main/CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of OAuth 2.0 flows
- Familiarity with Python development

### Types of Contributions

We welcome all types of contributions:

- **Bug Reports**: Found a bug? Let us know!
- **Feature Requests**: Have an idea for improvement? Share it!
- **Code Contributions**: Fix bugs, add features, improve performance
- **Documentation**: Improve docs, add examples, fix typos
- **Testing**: Add test cases, improve test coverage
- **Security**: Report security vulnerabilities responsibly

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/gh-oauth-helper.git
cd gh-oauth-helper

# Add the original repository as upstream
git remote add upstream https://github.com/jondmarien/gh-oauth-helper.git
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
# Install the package in development mode with all dependencies
pip install -e ".[dev,docs]"

# Verify installation
gh-oauth-helper --version
python -c "import gh_oauth_helper; print('Import successful')"
```

### 4. Set Up Pre-commit Hooks (Optional but Recommended)

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run hooks on all files (first time)
pre-commit run --all-files
```

### 5. Run Tests to Verify Setup

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gh_oauth_helper --cov-report=html

# Run linting
make lint

# Run formatting
make format
```

## Making Changes

### 1. Create a Feature Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a new branch for your feature
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 2. Make Your Changes

Follow these guidelines:

- **Small, focused commits**: Make small, logical commits with clear messages
- **Follow existing patterns**: Look at existing code and follow similar patterns
- **Add tests**: Add tests for new functionality or bug fixes
- **Update documentation**: Update relevant documentation
- **Handle errors gracefully**: Follow existing error handling patterns

### 3. Commit Guidelines

We follow conventional commit messages:

```bash
# Format: type(scope): description
# Types: feat, fix, docs, style, refactor, test, chore

# Examples:
git commit -m "feat(cli): add --verbose flag for detailed output"
git commit -m "fix(oauth): handle expired tokens gracefully"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(core): add tests for token validation"
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_core.py

# Run with coverage
pytest --cov=gh_oauth_helper --cov-report=term-missing

# Run tests with verbose output
pytest -v

# Run only fast tests (skip integration tests)
pytest -m "not integration"
```

### Writing Tests

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test complete workflows
- **Mock external services**: Use mocks for GitHub API calls
- **Test error conditions**: Test error handling and edge cases

Example test structure:

```python
import pytest
from unittest.mock import Mock, patch
from gh_oauth_helper import GitHubOAuth, GitHubOAuthError

class TestGitHubOAuth:
    def test_initialization_with_env_vars(self, monkeypatch):
        """Test OAuth initialization with environment variables."""
        monkeypatch.setenv("GITHUB_CLIENT_ID", "test_id")
        monkeypatch.setenv("GITHUB_CLIENT_SECRET", "test_secret")
        
        oauth = GitHubOAuth()
        assert oauth.client_id == "test_id"
        assert oauth.client_secret == "test_secret"
    
    def test_missing_credentials_raises_error(self):
        """Test that missing credentials raise appropriate error."""
        with pytest.raises(GitHubOAuthError):
            GitHubOAuth(client_id=None, client_secret=None)
    
    @patch('requests.post')
    def test_token_exchange_success(self, mock_post):
        """Test successful token exchange."""
        # Mock successful response
        mock_post.return_value.json.return_value = {
            'access_token': 'test_token',
            'token_type': 'bearer'
        }
        
        oauth = GitHubOAuth("test_id", "test_secret")
        result = oauth.exchange_code_for_token("test_code")
        
        assert result['access_token'] == 'test_token'
        mock_post.assert_called_once()
```

### Test Coverage

We aim for high test coverage:

- **Minimum**: 80% overall coverage
- **New code**: 90% coverage for new features
- **Critical paths**: 100% coverage for security-related code

## Code Style

### Python Style Guidelines

We follow PEP 8 with some customizations:

```python
# Line length: 88 characters (Black default)
# Use type hints for all public functions
# Use descriptive variable names
# Add docstrings to all public functions and classes

def generate_authorization_url(
    self, 
    scopes: Optional[List[str]] = None, 
    state: Optional[str] = None
) -> Tuple[str, str]:
    """Generate GitHub OAuth authorization URL.
    
    Args:
        scopes: List of OAuth scopes to request
        state: CSRF protection state parameter
        
    Returns:
        Tuple of (authorization_url, state_parameter)
        
    Raises:
        GitHubOAuthError: If OAuth configuration is invalid
    """
```

### Automated Formatting

We use automated tools for consistency:

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Check style with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/

# Run all checks
make lint
```

### Make Commands

We provide convenient Make commands:

```bash
# Format code
make format

# Run linting
make lint

# Run tests
make test

# Run tests with coverage
make test-cov

# Build package
make build

# Clean build artifacts
make clean

# Install in development mode
make install-dev
```

## Documentation

### Types of Documentation

1. **Code documentation**: Docstrings, type hints, comments
2. **API documentation**: Detailed API reference
3. **User guides**: Installation, usage, examples
4. **Developer documentation**: Architecture, contributing guides

### Writing Documentation

- **Use clear, simple language**
- **Provide examples** for all public APIs
- **Keep documentation up-to-date** with code changes
- **Use proper Markdown formatting**

### Building Documentation

```bash
# Install documentation dependencies
pip install ".[docs]"

# Build Sphinx documentation
cd docs/
make html

# View documentation
open _build/html/index.html
```

## Pull Request Process

### 1. Prepare Your PR

```bash
# Update your branch with latest changes
git checkout main
git pull upstream main
git checkout feature/your-feature
git rebase main

# Run all checks
make lint
make test
```

### 2. Create Pull Request

- **Title**: Clear, descriptive title
- **Description**: Explain what changes you made and why
- **Link issues**: Reference any related issues
- **Add screenshots**: For UI changes
- **Checklist**: Complete the PR checklist

### 3. PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### 4. Review Process

- **Automated checks**: CI/CD pipeline runs automatically
- **Code review**: Maintainers will review your code
- **Address feedback**: Make requested changes
- **Final approval**: PR approved and merged

### 5. After Merge

```bash
# Clean up your local repository
git checkout main
git pull upstream main
git branch -d feature/your-feature

# Delete remote branch (optional)
git push origin --delete feature/your-feature
```

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

For maintainers:

1. **Update version**: Update version in `src/gh_oauth_helper/__init__.py`
2. **Update changelog**: Add release notes
3. **Run tests**: Ensure all tests pass
4. **Create tag**: `git tag -a v1.0.0 -m "Release v1.0.0"`
5. **Push tag**: `git push origin v1.0.0`
6. **Create release**: Use GitHub's release feature
7. **Publish to PyPI**: Automated via GitHub Actions

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Email**: security@example.com (security issues only)

### Resources

- **Python OAuth**: [RFC 6749](https://tools.ietf.org/html/rfc6749)
- **GitHub OAuth**: [GitHub Documentation](https://docs.github.com/en/apps/oauth-apps)
- **Python Packaging**: [Python Packaging Guide](https://packaging.python.org/)
- **Testing**: [pytest Documentation](https://docs.pytest.org/)

### Common Issues

#### Development Environment

**Issue**: Import errors after installation
**Solution**: Ensure you're in the correct virtual environment and installed in development mode

```bash
source venv/bin/activate
pip install -e ".[dev]"
```

**Issue**: Tests failing with permission errors
**Solution**: Check file permissions and virtual environment activation

#### Contributing

**Issue**: Pre-commit hooks failing
**Solution**: Install and run pre-commit

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

**Issue**: Merge conflicts
**Solution**: Rebase your branch on the latest main

```bash
git checkout main
git pull upstream main
git checkout feature/your-branch
git rebase main
```

## Recognition

Contributors will be:

- **Listed in CONTRIBUTORS.md**
- **Mentioned in release notes** for significant contributions
- **Credited in documentation** for documentation improvements
- **Thanked publicly** on social media for major contributions

Thank you for contributing to the GitHub OAuth Helper! 🎉

