.. gh-oauth-helper documentation master file, created by
   sphinx-quickstart on Mon Dec  4 12:00:00 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to GitHub OAuth Helper's documentation!
===============================================

A secure, easy-to-use Python library and CLI tool for GitHub OAuth authentication.
Handle GitHub OAuth flows without exposing secrets in your code.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started:

   installation

.. toctree::
   :maxdepth: 2
   :caption: Reference Documentation:

   api-reference
   cli-reference

.. toctree::
   :maxdepth: 2
   :caption: Security & Best Practices:

   security

.. toctree::
   :maxdepth: 2
   :caption: Contributing:

   contributing

.. toctree::
   :maxdepth: 1
   :caption: External Links:

   GitHub Repository <https://github.com/jondmarien/gh-oauth-helper>
   PyPI Package <https://pypi.org/project/gh-oauth-helper/>
   Issue Tracker <https://github.com/jondmarien/gh-oauth-helper/issues>

Overview
========

The GitHub OAuth Helper is designed with security as a primary concern. It provides:

**Security Features:**

* 🔐 **No Hard-Coded Secrets**: Uses environment variables exclusively
* 🛡️ **CSRF Protection**: Built-in state parameter generation and verification
* 🌐 **Transport Security**: Automatic HTTP/HTTPS handling with security modes
* 📝 **Token Safety**: Secure token handling without logging sensitive data

**Developer Experience:**

* 🎨 **Colored CLI**: Beautiful, intuitive command-line interface
* 🔧 **Flexible Usage**: Both programmatic API and CLI tool
* 🐍 **Modern Python**: Python 3.8+ with comprehensive type hints
* 📚 **Complete Documentation**: Extensive guides and examples

Quick Start
===========

**Installation:**

.. code-block:: bash

   pip install gh-oauth-helper

**CLI Usage:**

.. code-block:: bash

   # Set up environment
   export GITHUB_CLIENT_ID="your_client_id"
   export GITHUB_CLIENT_SECRET="your_client_secret"
   
   # Generate authorization URL and open in browser
   gh-oauth-helper auth --open
   
   # Exchange code for token
   gh-oauth-helper token --code YOUR_AUTH_CODE
   
   # Test token validity
   gh-oauth-helper test --token YOUR_ACCESS_TOKEN

**Python API:**

.. code-block:: python

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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

