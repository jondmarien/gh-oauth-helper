"""
Core OAuth functionality for GitHub authentication.

This module provides the main OAuth flow functions for GitHub authentication,
including authorization URL generation, token exchange, and API testing.
"""

import os
import secrets
import urllib.parse
import warnings
from typing import Dict, Optional, Tuple, Any
import requests


class GitHubOAuthError(Exception):
    """Custom exception for GitHub OAuth errors."""
    pass


def _configure_transport_security(redirect_uri: str, secure_mode: bool = False) -> None:
    """
    Configure transport security settings based on redirect URI and secure mode.
    
    Args:
        redirect_uri: The OAuth redirect URI to check
        secure_mode: Whether strict security mode is enabled
    """
    # Check if redirect URI is localhost
    is_localhost = (
        redirect_uri.startswith('http://localhost') or 
        redirect_uri.startswith('http://127.0.0.1') or
        redirect_uri.startswith('http://[::1]')
    )
    
    if secure_mode:
        # In secure mode, ensure HTTPS for non-localhost URIs
        if not redirect_uri.startswith('https://') and not is_localhost:
            raise GitHubOAuthError(
                "Secure mode requires HTTPS redirect URI for non-localhost addresses"
            )
        # Disable insecure transport in secure mode
        os.environ.pop('OAUTHLIB_INSECURE_TRANSPORT', None)
    else:
        # For localhost, allow insecure transport by default
        if is_localhost:
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        else:
            # For non-localhost, warn about potential security risks
            if redirect_uri.startswith('http://'):
                warnings.warn(
                    "Using HTTP redirect URI for non-localhost address. "
                    "Consider using HTTPS or pass --secure flag for production use.",
                    UserWarning
                )
                os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


class GitHubOAuth:
    """
    GitHub OAuth helper class for handling authentication flows.
    
    This class manages the OAuth flow without hard-coding secrets,
    instead relying on environment variables or explicit parameters.
    """
    
    # GitHub OAuth endpoints
    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    API_BASE_URL = "https://api.github.com"
    
    def __init__(
        self, 
        client_id: Optional[str] = None, 
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        secure_mode: bool = False
    ):
        """
        Initialize GitHub OAuth helper.
        
        Args:
            client_id: GitHub OAuth app client ID. If None, reads from GITHUB_CLIENT_ID env var.
            client_secret: GitHub OAuth app client secret. If None, reads from GITHUB_CLIENT_SECRET env var.
            redirect_uri: OAuth redirect URI. If None, reads from GITHUB_REDIRECT_URI env var.
            secure_mode: Whether to enable strict security mode (HTTPS only).
            
        Raises:
            GitHubOAuthError: If required credentials are not provided or found in environment.
        """
        self.client_id = client_id or os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("GITHUB_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8080/callback")
        self.secure_mode = secure_mode
        
        if not self.client_id:
            raise GitHubOAuthError(
                "GitHub client ID is required. Provide it as parameter or set GITHUB_CLIENT_ID environment variable."
            )
        
        if not self.client_secret:
            raise GitHubOAuthError(
                "GitHub client secret is required. Provide it as parameter or set GITHUB_CLIENT_SECRET environment variable."
            )
        
        # Configure transport security based on redirect URI and secure mode
        _configure_transport_security(self.redirect_uri, self.secure_mode)
    
    def generate_authorization_url(
        self, 
        scopes: Optional[list] = None, 
        state: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate GitHub OAuth authorization URL.
        
        Args:
            scopes: List of OAuth scopes to request. Defaults to ['user:email', 'repo'].
            state: CSRF protection state parameter. If None, generates a secure random state.
            
        Returns:
            Tuple of (authorization_url, state) where state should be stored for verification.
        """
        if scopes is None:
            scopes = ["user:email", "repo"]
        
        if state is None:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "response_type": "code"
        }
        
        auth_url = f"{self.AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
        return auth_url, state
    
    def exchange_code_for_token(self, code: str, state: Optional[str] = None) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code received from GitHub callback.
            state: State parameter for CSRF verification (optional but recommended).
            
        Returns:
            Dictionary containing token information including 'access_token', 'token_type', and 'scope'.
            
        Raises:
            GitHubOAuthError: If token exchange fails or returns an error.
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        headers = {
            "Accept": "application/json",
            "User-Agent": "gh-oauth-helper/1.0"
        }
        
        try:
            response = requests.post(
                self.TOKEN_URL,
                data=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            
            if "error" in token_data:
                raise GitHubOAuthError(
                    f"Token exchange failed: {token_data.get('error_description', token_data['error'])}"
                )
            
            if "access_token" not in token_data:
                raise GitHubOAuthError("No access token in response")
            
            return token_data
            
        except requests.RequestException as e:
            raise GitHubOAuthError(f"Failed to exchange code for token: {str(e)}")
    
    def test_api_access(self, access_token: str) -> Dict[str, Any]:
        """
        Test API access with the provided access token.
        
        Args:
            access_token: GitHub access token to test.
            
        Returns:
            Dictionary containing user information from GitHub API.
            
        Raises:
            GitHubOAuthError: If API test fails or token is invalid.
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "gh-oauth-helper/1.0"
        }
        
        try:
            response = requests.get(
                f"{self.API_BASE_URL}/user",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            user_data = response.json()
            return user_data
            
        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    raise GitHubOAuthError("Invalid or expired access token")
                elif e.response.status_code == 403:
                    raise GitHubOAuthError("Access token lacks required permissions")
            
            raise GitHubOAuthError(f"API test failed: {str(e)}")
    
    def revoke_token(self, access_token: str) -> bool:
        """
        Revoke an access token.
        
        Args:
            access_token: GitHub access token to revoke.
            
        Returns:
            True if token was successfully revoked, False otherwise.
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "gh-oauth-helper/1.0"
        }
        
        try:
            response = requests.delete(
                f"{self.API_BASE_URL}/applications/{self.client_id}/token",
                headers=headers,
                json={"access_token": access_token},
                timeout=30
            )
            return response.status_code == 204
            
        except requests.RequestException:
            return False


# Convenience functions for direct usage
def create_oauth_helper(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    secure_mode: bool = False
) -> GitHubOAuth:
    """
    Create a GitHubOAuth instance with the provided or environment-based credentials.
    
    Args:
        client_id: GitHub OAuth app client ID.
        client_secret: GitHub OAuth app client secret.
        redirect_uri: OAuth redirect URI.
        secure_mode: Whether to enable strict security mode (HTTPS only).
        
    Returns:
        Configured GitHubOAuth instance.
    """
    return GitHubOAuth(client_id, client_secret, redirect_uri, secure_mode)


def start_auth_flow(
    oauth_helper: Optional[GitHubOAuth] = None,
    scopes: Optional[list] = None
) -> Tuple[str, str]:
    """
    Start the OAuth authorization flow.
    
    Args:
        oauth_helper: GitHubOAuth instance. If None, creates one from environment variables.
        scopes: List of OAuth scopes to request.
        
    Returns:
        Tuple of (authorization_url, state).
    """
    if oauth_helper is None:
        oauth_helper = create_oauth_helper()
    
    return oauth_helper.generate_authorization_url(scopes)


def complete_auth_flow(
    code: str,
    oauth_helper: Optional[GitHubOAuth] = None,
    state: Optional[str] = None
) -> Dict[str, Any]:
    """
    Complete the OAuth authorization flow by exchanging code for token.
    
    Args:
        code: Authorization code from GitHub callback.
        oauth_helper: GitHubOAuth instance. If None, creates one from environment variables.
        state: State parameter for CSRF verification.
        
    Returns:
        Token information dictionary.
    """
    if oauth_helper is None:
        oauth_helper = create_oauth_helper()
    
    return oauth_helper.exchange_code_for_token(code, state)


def verify_token(
    access_token: str,
    oauth_helper: Optional[GitHubOAuth] = None
) -> Dict[str, Any]:
    """
    Verify an access token by testing API access.
    
    Args:
        access_token: GitHub access token to verify.
        oauth_helper: GitHubOAuth instance. If None, creates one from environment variables.
        
    Returns:
        User information from GitHub API.
    """
    if oauth_helper is None:
        oauth_helper = create_oauth_helper()
    
    return oauth_helper.test_api_access(access_token)

