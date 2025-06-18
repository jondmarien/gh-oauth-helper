# Installation Guide

This guide provides detailed installation instructions for the GitHub OAuth Helper.

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, Linux
- **Network**: Internet connection for OAuth flows

## Installation Methods

### 1. Install from PyPI (Recommended)

```bash
# Basic installation
pip install gh-oauth-helper

# Install with development dependencies
pip install gh-oauth-helper[dev]

# Install with documentation dependencies
pip install gh-oauth-helper[docs]

# Install all optional dependencies
pip install gh-oauth-helper[dev,docs]
```

### 2. Install from Source

```bash
# Clone the repository
git clone https://github.com/jondmarien/gh-oauth-helper.git
cd gh-oauth-helper

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### 3. Install from GitHub

```bash
# Install latest development version
pip install git+https://github.com/jondmarien/gh-oauth-helper.git

# Install specific version/tag
pip install git+https://github.com/jondmarien/gh-oauth-helper.git@v1.0.0
```

## Verification

Verify the installation by checking the version:

```bash
# Check CLI tool
gh-oauth-helper --version

# Check Python package
python -c "import gh_oauth_helper; print(gh_oauth_helper.__version__)"
```

## Virtual Environment Setup (Recommended)

Using a virtual environment is recommended to avoid dependency conflicts:

### Using venv (Python 3.3+)

```bash
# Create virtual environment
python -m venv gh-oauth-env

# Activate on Linux/macOS
source gh-oauth-env/bin/activate

# Activate on Windows
gh-oauth-env\Scripts\activate

# Install the package
pip install gh-oauth-helper

# Deactivate when done
deactivate
```

### Using conda

```bash
# Create conda environment
conda create -n gh-oauth python=3.11
conda activate gh-oauth

# Install the package
pip install gh-oauth-helper

# Deactivate when done
conda deactivate
```

## Dependencies

The package automatically installs these dependencies:

### Required Dependencies

- **requests** (≥2.25.0) - HTTP library
- **requests-oauthlib** (≥1.3.0) - OAuth support for requests
- **urllib3** (≥1.26.0) - HTTP client
- **colorama** (≥0.4.4) - Colored terminal output

### Optional Dependencies

#### Development (`[dev]`)

- **pytest** (≥6.0.0) - Testing framework
- **pytest-cov** (≥2.10.0) - Coverage reporting
- **black** (≥21.0.0) - Code formatter
- **isort** (≥5.0.0) - Import sorter
- **flake8** (≥3.8.0) - Linter
- **mypy** (≥0.812) - Type checker

#### Documentation (`[docs]`)

- **sphinx** (≥4.0.0) - Documentation generator
- **sphinx-rtd-theme** (≥0.5.0) - Read the Docs theme
- **myst-parser** (≥0.15.0) - Markdown parser for Sphinx

## Platform-Specific Notes

### Windows

- Use PowerShell or Command Prompt
- May need to install Visual C++ Build Tools for some dependencies
- Consider using Windows Subsystem for Linux (WSL) for a Unix-like experience

### macOS

- Xcode Command Line Tools may be required: `xcode-select --install`
- Consider using Homebrew for Python installation: `brew install python`

### Linux

- Most distributions include Python 3.8+
- Install development headers if building from source:
  - Ubuntu/Debian: `sudo apt-get install python3-dev`
  - CentOS/RHEL: `sudo yum install python3-devel`
  - Fedora: `sudo dnf install python3-devel`

## Troubleshooting

### Common Issues

#### 1. `gh-oauth-helper: command not found`

**Solution**: Ensure the package is installed and your PATH includes pip's bin directory:

```bash
# Check if installed
pip list | grep gh-oauth-helper

# Find installation path
python -m site --user-base

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$PATH:$(python -m site --user-base)/bin"
```

#### 2. Permission Errors

**Solution**: Use `--user` flag or virtual environment:

```bash
# Install for current user only
pip install --user gh-oauth-helper

# Or use virtual environment (recommended)
python -m venv venv && source venv/bin/activate
pip install gh-oauth-helper
```

#### 3. SSL Certificate Errors

**Solution**: Update certificates or use trusted hosts:

```bash
# Update certificates (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command

# Use trusted host (temporary solution)
pip install --trusted-host pypi.org --trusted-host pypi.python.org gh-oauth-helper
```

#### 4. Dependency Conflicts

**Solution**: Use virtual environment or force reinstall:

```bash
# Create clean environment
python -m venv clean-env
source clean-env/bin/activate
pip install gh-oauth-helper

# Force reinstall dependencies
pip install --force-reinstall gh-oauth-helper
```

### Getting Help

If you encounter installation issues:

1. Check the [GitHub Issues](https://github.com/jondmarien/gh-oauth-helper/issues)
2. Search for existing solutions
3. Create a new issue with:
   - Your operating system and version
   - Python version (`python --version`)
   - Pip version (`pip --version`)
   - Full error message
   - Installation command used

## Next Steps

After installation:

1. [Set up your GitHub OAuth App](../README.md#github-oauth-app-setup)
2. [Configure environment variables](../README.md#set-up-environment-variables)
3. [Try the quick start examples](../README.md#quick-start)
4. [Read the full documentation](api-reference.md)

## Uninstallation

To remove the package:

```bash
# Uninstall package
pip uninstall gh-oauth-helper

# Remove virtual environment (if used)
rm -rf venv  # or gh-oauth-env
```

