"""
Tests for the core OAuth functionality.
"""

import os
import pytest
import urllib.parse
from unittest.mock import Mock, patch, MagicMock
from gh_oauth_helper.core import (
    GitHubOAuth,
    GitHubOAuthError,
    create_oauth_helper,
    start_auth_flow,
    complete_auth_flow,
    verify_token,
)


class TestGitHubOAuth:
    """Test cases for GitHubOAuth class."""
    
    def test_init_with_params(self):
        """Test initialization with explicit parameters."""
        oauth = GitHubOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8080/callback"
        )
        assert oauth.client_id == "test_client_id"
        assert oauth.client_secret == "test_client_secret"
        assert oauth.redirect_uri == "http://localhost:8080/callback"
    
    @patch.dict(os.environ, {
        "GITHUB_CLIENT_ID": "env_client_id",
        "GITHUB_CLIENT_SECRET": "env_client_secret",
        "GITHUB_REDIRECT_URI": "http://localhost:9000/callback"
    })
    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        oauth = GitHubOAuth()
        assert oauth.client_id == "env_client_id"
        assert oauth.client_secret == "env_client_secret"
        assert oauth.redirect_uri == "http://localhost:9000/callback"
    
    def test_init_missing_client_id(self):
        """Test initialization fails when client_id is missing."""
        with pytest.raises(GitHubOAuthError, match="GitHub client ID is required"):
            GitHubOAuth(client_secret="secret")
    
    def test_init_missing_client_secret(self):
        """Test initialization fails when client_secret is missing."""
        with pytest.raises(GitHubOAuthError, match="GitHub client secret is required"):
            GitHubOAuth(client_id="client_id")
    
    def test_generate_authorization_url_default(self):
        """Test generating authorization URL with default parameters."""
        oauth = GitHubOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        auth_url, state = oauth.generate_authorization_url()
        
        # Parse the URL to verify parameters
        parsed_url = urllib.parse.urlparse(auth_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        assert parsed_url.scheme == "https"
        assert parsed_url.netloc == "github.com"
        assert parsed_url.path == "/login/oauth/authorize"
        assert query_params["client_id"][0] == "test_client_id"
        assert query_params["scope"][0] == "user:email repo"
        assert query_params["response_type"][0] == "code"
        assert len(state) > 0
        assert query_params["state"][0] == state
    
    def test_generate_authorization_url_custom_scopes(self):
        """Test generating authorization URL with custom scopes."""
        oauth = GitHubOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        custom_scopes = ["user", "public_repo"]
        auth_url, state = oauth.generate_authorization_url(scopes=custom_scopes)
        
        parsed_url = urllib.parse.urlparse(auth_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        assert query_params["scope"][0] == "user public_repo"
    
    def test_generate_authorization_url_custom_state(self):
        """Test generating authorization URL with custom state."""
        oauth = GitHubOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        custom_state = "custom_state_123"
        auth_url, state = oauth.generate_authorization_url(state=custom_state)
        
        parsed_url = urllib.parse.urlparse(auth_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        assert state == custom_state
        assert query_params["state"][0] == custom_state
    
    @patch('gh_oauth_helper.core.requests.post')
    def test_exchange_code_for_token_success(self, mock_post):
        """Test successful token exchange."""
        oauth = GitHubOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "token_type": "bearer",
            "scope": "user:email,repo"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        token_data = oauth.exchange_code_for_token("test_code")
        
        assert token_data["access_token"] == "test_access_token"
        assert token_data["token_type"] == "bearer"
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == oauth.TOKEN_URL
        assert call_args[1]["data"]["client_id"] == "test_client_id"
        assert call_args[1]["data"]["client_secret"] == "test_client_secret"
        assert call_args[1]["data"]["code"] == "test_code"
    
    @patch('gh_oauth_helper.core.requests.post')
    def test_exchange_code_for_token_error_response(self, mock_post):
        """Test token exchange with error response."""
        oauth = GitHubOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        # Mock error response
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "The provided authorization grant is invalid"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with pytest.raises(GitHubOAuthError, match="Token exchange failed"):
            oauth.exchange_code_for_token("invalid_code")
    
    @patch('gh_oauth_helper.core.requests.post')
    def test_exchange_code_for_token_no_access_token(self, mock_post):
        """Test token exchange when no access token is returned."""
        oauth = GitHubOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        # Mock response without access token
        mock_response = Mock()
        mock_response.json.return_value = {"token_type": "bearer"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with pytest.raises(GitHubOAuthError, match="No access token in response"):
            oauth.exchange_code_for_token("test_code")
    
    @patch('gh_oauth_helper.core.requests.get')
    def test_test_api_access_success(self, mock_get):
        """Test successful API access test."""
        oauth = GitHubOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "login": "testuser",
            "id": 12345,
            "email": "test@example.com"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        user_data = oauth.test_api_access("test_access_token")
        
        assert user_data["login"] == "testuser"
        assert user_data["id"] == 12345
        assert user_data["email"] == "test@example.com"
        
        # Verify the request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == f"{oauth.API_BASE_URL}/user"
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_access_token"
    
    @patch('gh_oauth_helper.core.requests.get')
    def test_test_api_access_invalid_token(self, mock_get):
        """Test API access test with invalid token."""
        oauth = GitHubOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.side_effect = Exception("HTTP 401")
        mock_get.side_effect.response = mock_response
        
        with pytest.raises(GitHubOAuthError, match="Invalid or expired access token"):
            oauth.test_api_access("invalid_token")
    
    @patch('gh_oauth_helper.core.requests.delete')
    def test_revoke_token_success(self, mock_delete):
        """Test successful token revocation."""
        oauth = GitHubOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        # Mock successful revocation response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        result = oauth.revoke_token("test_access_token")
        
        assert result is True
        
        # Verify the request was made correctly
        mock_delete.assert_called_once()
        call_args = mock_delete.call_args
        assert call_args[0][0] == f"{oauth.API_BASE_URL}/applications/{oauth.client_id}/token"
    
    @patch('gh_oauth_helper.core.requests.delete')
    def test_revoke_token_failure(self, mock_delete):
        """Test failed token revocation."""
        oauth = GitHubOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        # Mock failed revocation response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_delete.return_value = mock_response
        
        result = oauth.revoke_token("test_access_token")
        
        assert result is False


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    @patch.dict(os.environ, {
        "GITHUB_CLIENT_ID": "env_client_id",
        "GITHUB_CLIENT_SECRET": "env_client_secret"
    })
    def test_create_oauth_helper(self):
        """Test creating OAuth helper with environment variables."""
        helper = create_oauth_helper()
        assert isinstance(helper, GitHubOAuth)
        assert helper.client_id == "env_client_id"
        assert helper.client_secret == "env_client_secret"
    
    def test_create_oauth_helper_with_params(self):
        """Test creating OAuth helper with explicit parameters."""
        helper = create_oauth_helper(
            client_id="test_id",
            client_secret="test_secret"
        )
        assert isinstance(helper, GitHubOAuth)
        assert helper.client_id == "test_id"
        assert helper.client_secret == "test_secret"
    
    @patch('gh_oauth_helper.core.create_oauth_helper')
    def test_start_auth_flow(self, mock_create_helper):
        """Test starting auth flow convenience function."""
        mock_helper = Mock()
        mock_helper.generate_authorization_url.return_value = ("http://auth.url", "state123")
        mock_create_helper.return_value = mock_helper
        
        auth_url, state = start_auth_flow()
        
        assert auth_url == "http://auth.url"
        assert state == "state123"
        mock_create_helper.assert_called_once()
        mock_helper.generate_authorization_url.assert_called_once_with(None)
    
    @patch('gh_oauth_helper.core.create_oauth_helper')
    def test_complete_auth_flow(self, mock_create_helper):
        """Test completing auth flow convenience function."""
        mock_helper = Mock()
        mock_helper.exchange_code_for_token.return_value = {"access_token": "token123"}
        mock_create_helper.return_value = mock_helper
        
        token_data = complete_auth_flow("test_code")
        
        assert token_data["access_token"] == "token123"
        mock_create_helper.assert_called_once()
        mock_helper.exchange_code_for_token.assert_called_once_with("test_code", None)
    
    @patch('gh_oauth_helper.core.create_oauth_helper')
    def test_verify_token(self, mock_create_helper):
        """Test token verification convenience function."""
        mock_helper = Mock()
        mock_helper.test_api_access.return_value = {"login": "testuser"}
        mock_create_helper.return_value = mock_helper
        
        user_data = verify_token("test_token")
        
        assert user_data["login"] == "testuser"
        mock_create_helper.assert_called_once()
        mock_helper.test_api_access.assert_called_once_with("test_token")

