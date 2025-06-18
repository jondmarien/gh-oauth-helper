"""
GitHub OAuth Helper - A Python helper package for GitHub OAuth authentication.

This package provides utilities for handling GitHub OAuth authentication flows,
including token management and API interactions.
"""

__version__ = "0.1.1"
__author__ = "Jonathan Marien"
__email__ = "jon@chron0.tech"
__description__ = "A Python helper package for Local GitHub OAuth authentication"

# Import main classes/functions
from .core import (
    GitHubOAuth,
    GitHubOAuthError,
    create_oauth_helper,
    start_auth_flow,
    complete_auth_flow,
    verify_token,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "GitHubOAuth",
    "GitHubOAuthError",
    "create_oauth_helper",
    "start_auth_flow",
    "complete_auth_flow",
    "verify_token",
]
