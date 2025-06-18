"""
Command-line interface for GitHub OAuth Helper.

This module provides a CLI for interacting with GitHub OAuth flows,
supporting authorization URL generation, token exchange, and token management.
"""

import argparse
import sys
import json
import webbrowser
import os
from typing import Optional, Dict, Any

try:
    import colorama
    from colorama import Fore, Style, init
    init(autoreset=True)  # Initialize colorama
    HAS_COLOR = True
except ImportError:
    # Fallback if colorama is not available
    class _DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = Style = _DummyColor()
    HAS_COLOR = False

from .core import GitHubOAuth, GitHubOAuthError


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='gh-oauth-helper',
        description='GitHub OAuth Helper - Manage GitHub OAuth authentication flows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate authorization URL
  gh-oauth-helper auth --client-id YOUR_ID --client-secret YOUR_SECRET

  # Exchange code for token
  gh-oauth-helper token --client-id YOUR_ID --client-secret YOUR_SECRET --code AUTH_CODE

  # Test token validity
  gh-oauth-helper test --client-id YOUR_ID --client-secret YOUR_SECRET --token ACCESS_TOKEN

  # Revoke token
  gh-oauth-helper revoke --client-id YOUR_ID --client-secret YOUR_SECRET --token ACCESS_TOKEN

Environment Variables:
  GITHUB_CLIENT_ID      - GitHub OAuth app client ID
  GITHUB_CLIENT_SECRET  - GitHub OAuth app client secret
  GITHUB_REDIRECT_URI   - OAuth redirect URI (default: http://localhost:8080/callback)
        """
    )
    
    # Global arguments
    parser.add_argument(
        '--client-id',
        help='GitHub OAuth app client ID (can also use GITHUB_CLIENT_ID env var)'
    )
    parser.add_argument(
        '--client-secret',
        help='GitHub OAuth app client secret (can also use GITHUB_CLIENT_SECRET env var)'
    )
    parser.add_argument(
        '--redirect-uri',
        help='OAuth redirect URI (can also use GITHUB_REDIRECT_URI env var)'
    )
    parser.add_argument(
        '--secure',
        action='store_true',
        help='Use secure mode (HTTPS) for redirect URI validation'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Auth command - generate authorization URL
    auth_parser = subparsers.add_parser(
        'auth',
        help='Generate GitHub OAuth authorization URL'
    )
    auth_parser.add_argument(
        '--scopes',
        nargs='*',
        default=['user:email', 'repo'],
        help='OAuth scopes to request (default: user:email repo)'
    )
    auth_parser.add_argument(
        '--state',
        help='Custom state parameter (random generated if not provided)'
    )
    auth_parser.add_argument(
        '--open',
        action='store_true',
        help='Automatically open the authorization URL in browser'
    )
    
    # Token command - exchange code for token
    token_parser = subparsers.add_parser(
        'token',
        help='Exchange authorization code for access token'
    )
    token_parser.add_argument(
        '--code',
        required=True,
        help='Authorization code from GitHub callback'
    )
    token_parser.add_argument(
        '--state',
        help='State parameter for CSRF verification'
    )
    
    # Test command - test token validity
    test_parser = subparsers.add_parser(
        'test',
        help='Test access token validity'
    )
    test_parser.add_argument(
        '--token',
        required=True,
        help='Access token to test'
    )
    
    # Revoke command - revoke access token
    revoke_parser = subparsers.add_parser(
        'revoke',
        help='Revoke access token'
    )
    revoke_parser.add_argument(
        '--token',
        required=True,
        help='Access token to revoke'
    )
    
    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate command-line arguments."""
    if args.secure and args.redirect_uri:
        if not args.redirect_uri.startswith('https://'):
            raise ValueError("Secure mode requires HTTPS redirect URI")


def print_colored(text: str, color: str = "", bold: bool = False) -> None:
    """Print colored text if colors are available."""
    if HAS_COLOR:
        style = Style.BRIGHT if bold else ""
        color_code = getattr(Fore, color.upper(), "") if color else ""
        print(f"{style}{color_code}{text}{Style.RESET_ALL}")
    else:
        print(text)


def print_success(text: str) -> None:
    """Print success message in green."""
    print_colored(f"✓ {text}", "green", bold=True)


def print_error(text: str) -> None:
    """Print error message in red."""
    print_colored(f"✗ {text}", "red", bold=True)


def print_warning(text: str) -> None:
    """Print warning message in yellow."""
    print_colored(f"⚠ {text}", "yellow", bold=True)


def print_info(text: str) -> None:
    """Print info message in blue."""
    print_colored(f"ℹ {text}", "blue")


def create_oauth_helper(args: argparse.Namespace) -> GitHubOAuth:
    """Create GitHubOAuth instance from command-line arguments."""
    redirect_uri = args.redirect_uri
    
    # Apply secure mode validation
    if args.secure and redirect_uri and not redirect_uri.startswith('https://'):
        raise GitHubOAuthError("Secure mode requires HTTPS redirect URI")
    
    # Show security mode status
    if args.verbose:
        if args.secure:
            print_info("Running in secure mode (HTTPS required)")
        else:
            print_info("Running in standard mode (HTTP allowed for localhost)")
    
    return GitHubOAuth(
        client_id=args.client_id,
        client_secret=args.client_secret,
        redirect_uri=redirect_uri,
        secure_mode=args.secure
    )


def output_result(result: Any, args: argparse.Namespace) -> None:
    """Output result in requested format."""
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"{key}: {value}")
        else:
            print(result)


def cmd_auth(args: argparse.Namespace) -> None:
    """Handle auth command - generate authorization URL."""
    try:
        if args.verbose:
            print_info("Initializing GitHub OAuth helper...")
        
        oauth = create_oauth_helper(args)
        auth_url, state = oauth.generate_authorization_url(
            scopes=args.scopes,
            state=args.state
        )
        
        result = {
            'authorization_url': auth_url,
            'state': state,
            'scopes': args.scopes
        }
        
        if args.json:
            output_result(result, args)
        else:
            print_success("Generated GitHub OAuth authorization URL")
            if args.verbose:
                print_info(f"Scopes requested: {', '.join(args.scopes)}")
                print_info(f"State parameter: {state}")
                print_info(f"Redirect URI: {oauth.redirect_uri}")
                print()
            
            print_colored("Authorization URL:", "cyan", bold=True)
            print_colored(auth_url, "white")
            print()
            print_colored(f"State (save this for verification): {state}", "yellow")
            
            if args.open:
                print_info("Opening authorization URL in browser...")
                try:
                    webbrowser.open(auth_url)
                    print_success("Browser opened successfully")
                except Exception as e:
                    print_warning(f"Could not open browser: {e}")
                    print_info("Please copy and paste the URL manually")
            
    except GitHubOAuthError as e:
        print_error(f"OAuth Error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            print_colored(traceback.format_exc(), "red")
        sys.exit(1)


def cmd_token(args: argparse.Namespace) -> None:
    """Handle token command - exchange code for token."""
    try:
        if args.verbose:
            print_info("Exchanging authorization code for access token...")
        
        oauth = create_oauth_helper(args)
        token_data = oauth.exchange_code_for_token(
            code=args.code,
            state=args.state
        )
        
        if args.json:
            output_result(token_data, args)
        else:
            print_success("Successfully exchanged authorization code for access token")
            
            if args.verbose:
                print_info(f"Token type: {token_data.get('token_type', 'N/A')}")
                print_info(f"Scope: {token_data.get('scope', 'N/A')}")
                print()
            
            print_colored("Access Token:", "cyan", bold=True)
            print_colored(token_data.get('access_token'), "white")
            
            if 'refresh_token' in token_data:
                print_colored(f"\nRefresh Token: {token_data['refresh_token']}", "yellow")
            if 'expires_in' in token_data:
                print_info(f"Expires in: {token_data['expires_in']} seconds")
                
    except GitHubOAuthError as e:
        print_error(f"OAuth Error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            print_colored(traceback.format_exc(), "red")
        sys.exit(1)


def cmd_test(args: argparse.Namespace) -> None:
    """Handle test command - test token validity."""
    try:
        if args.verbose:
            print_info("Testing access token validity...")
        
        oauth = create_oauth_helper(args)
        user_data = oauth.test_api_access(args.token)
        
        if args.json:
            output_result(user_data, args)
        else:
            print_success("Token is valid! User information:")
            print()
            print_colored(f"Username: {user_data.get('login')}", "cyan")
            print_colored(f"Name: {user_data.get('name', 'N/A')}", "white")
            print_colored(f"Email: {user_data.get('email', 'N/A')}", "white")
            print_colored(f"User ID: {user_data.get('id')}", "white")
            print_colored(f"Account Type: {user_data.get('type')}", "white")
            if user_data.get('company'):
                print_colored(f"Company: {user_data.get('company')}", "white")
            
    except GitHubOAuthError as e:
        print_error(f"OAuth Error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            print_colored(traceback.format_exc(), "red")
        sys.exit(1)


def cmd_revoke(args: argparse.Namespace) -> None:
    """Handle revoke command - revoke access token."""
    try:
        if args.verbose:
            print_info("Revoking access token...")
        
        oauth = create_oauth_helper(args)
        success = oauth.revoke_token(args.token)
        
        result = {'revoked': success}
        
        if args.json:
            output_result(result, args)
        else:
            if success:
                print_success("Token successfully revoked")
            else:
                print_warning("Failed to revoke token (it may already be invalid)")
                
    except GitHubOAuthError as e:
        print_error(f"OAuth Error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            print_colored(traceback.format_exc(), "red")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Show help if no command specified
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        validate_args(args)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Dispatch to command handlers
    command_handlers = {
        'auth': cmd_auth,
        'token': cmd_token,
        'test': cmd_test,
        'revoke': cmd_revoke
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

