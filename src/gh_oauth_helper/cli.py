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
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich import print as rprint
    from rich.columns import Columns
    from rich.align import Align
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    
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

# Initialize Rich console
console = Console() if HAS_RICH else None


def show_header() -> None:
    """Display the ASCII art header with author and date info."""
    if HAS_RICH:
        # ASCII art for gh-oauth-helper with rainbow gradient
        ascii_lines = [
            " ██████╗ ██╗  ██╗      ██████╗  █████╗ ██╗   ██╗████████╗██╗  ██╗",
            "██╔════╝ ██║  ██║     ██╔═══██╗██╔══██╗██║   ██║╚══██╔══╝██║  ██║",
            "██║  ███╗███████║     ██║   ██║███████║██║   ██║   ██║   ███████║",
            "██║   ██║██╔══██║     ██║   ██║██╔══██║██║   ██║   ██║   ██╔══██║",
            "╚██████╔╝██║  ██║     ╚██████╔╝██║  ██║╚██████╔╝   ██║   ██║  ██║",
            " ╚═════╝ ╚═╝  ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝",
            "",
            "    ██╗  ██╗███████╗██╗     ██████╗ ███████╗██████╗ ",
            "    ██║  ██║██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗",
            "    ███████║█████╗  ██║     ██████╔╝█████╗  ██████╔╝",
            "    ██╔══██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══██╗",
            "    ██║  ██║███████╗███████╗██║     ███████╗██║  ██║",
            "    ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝"
        ]
        
        # Rainbow gradient colors
        rainbow_colors = [
            "bright_red", "red", "bright_yellow", "yellow", 
            "bright_green", "green", "bright_cyan", "cyan",
            "bright_blue", "blue", "bright_magenta", "magenta"
        ]
        
        # Create rainbow gradient ASCII art
        ascii_art = Text()
        for i, line in enumerate(ascii_lines):
            color = rainbow_colors[i % len(rainbow_colors)]
            ascii_art.append(line + "\n", style=f"bold {color}")
        
        # Author and version info
        info_table = Table.grid()
        info_table.add_column(style="dim")
        info_table.add_column(style="bold white")
        
        current_year = datetime.now().year
        info_table.add_row("Author:", "Jonathan Marien (@jondmarien)")
        info_table.add_row("Email:", "jon@chron0.tech")
        info_table.add_row("Year:", str(current_year))
        info_table.add_row("License:", "MIT")
        
        # Create panels with centered ASCII art
        art_panel = Panel(
            Align.center(ascii_art),
            border_style="bright_blue",
            padding=(0, 1)
        )
        
        info_panel = Panel(
            Align.center(info_table),
            title="[bold cyan]About[/bold cyan]",
            border_style="green",
            padding=(1, 2)
        )
        
        # Display header
        console.print(art_panel)
        console.print(info_panel)
        console.print()
        
    else:
        # Fallback ASCII art for terminals without Rich
        header_text = f"""
{Fore.CYAN}{Style.BRIGHT}
 ██████╗ ██╗  ██╗      ██████╗  █████╗ ██╗   ██╗████████╗██╗  ██╗
██╔════╝ ██║  ██║     ██╔═══██╗██╔══██╗██║   ██║╚══██╔══╝██║  ██║
██║  ███╗███████║     ██║   ██║███████║██║   ██║   ██║   ███████║
██║   ██║██╔══██║     ██║   ██║██╔══██║██║   ██║   ██║   ██╔══██║
╚██████╔╝██║  ██║     ╚██████╔╝██║  ██║╚██████╔╝   ██║   ██║  ██║
 ╚═════╝ ╚═╝  ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝

    ██╗  ██╗███████╗██╗     ██████╗ ███████╗██████╗ 
    ██║  ██║██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗
    ███████║█████╗  ██║     ██████╔╝█████╗  ██████╔╝
    ██╔══██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══██╗
    ██║  ██║███████╗███████╗██║     ███████╗██║  ██║
    ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝
{Style.RESET_ALL}

{Fore.GREEN}{Style.BRIGHT}GitHub OAuth Helper{Style.RESET_ALL}
{Fore.WHITE}Author: Jonathan Marien (@jondmarien){Style.RESET_ALL}
{Fore.WHITE}Email: jon@chron0.tech{Style.RESET_ALL}
{Fore.WHITE}Year: {datetime.now().year}{Style.RESET_ALL}
{Fore.WHITE}License: MIT{Style.RESET_ALL}

{'-' * 60}
"""
        print(header_text)


def print_rich_success(text: str) -> None:
    """Print success message with rich formatting."""
    if HAS_RICH:
        console.print(f"[bold green]✓[/bold green] {text}")
    else:
        print_success(text)


def print_rich_error(text: str) -> None:
    """Print error message with rich formatting."""
    if HAS_RICH:
        console.print(f"[bold red]✗[/bold red] {text}")
    else:
        print_error(text)


def print_rich_warning(text: str) -> None:
    """Print warning message with rich formatting."""
    if HAS_RICH:
        console.print(f"[bold yellow]⚠[/bold yellow] {text}")
    else:
        print_warning(text)


def print_rich_info(text: str) -> None:
    """Print info message with rich formatting."""
    if HAS_RICH:
        console.print(f"[bold blue]ℹ[/bold blue] {text}")
    else:
        print_info(text)


def display_rich_table(data: Dict[str, Any], title: str = "Information") -> None:
    """Display data in a rich table format."""
    if HAS_RICH:
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        for key, value in data.items():
            # Format key nicely
            formatted_key = key.replace('_', ' ').title()
            table.add_row(formatted_key, str(value))
        
        console.print(table)
    else:
        print_colored(f"\n{title}:", "cyan", bold=True)
        for key, value in data.items():
            print_colored(f"  {key.replace('_', ' ').title()}: {value}", "white")


def display_code_block(code: str, language: str = "bash") -> None:
    """Display a syntax-highlighted code block."""
    if HAS_RICH:
        syntax = Syntax(code, language, theme="monokai", line_numbers=False)
        console.print(syntax)
    else:
        print_colored(f"\n{code}", "white")


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

  # Exchange code for token (method 1: provide code directly)
  gh-oauth-helper token --client-id YOUR_ID --client-secret YOUR_SECRET --code AUTH_CODE
  
  # Exchange code for token (method 2: provide full callback URL)
  gh-oauth-helper token --client-id YOUR_ID --client-secret YOUR_SECRET --url "http://localhost:8080/callback?code=AUTH_CODE&state=STATE"

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
    parser.add_argument(
        '--no-header',
        action='store_true',
        help='Disable ASCII art header display'
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
    
    # Create mutually exclusive group for code input methods
    code_group = token_parser.add_mutually_exclusive_group(required=True)
    code_group.add_argument(
        '--code',
        help='Authorization code from GitHub callback'
    )
    code_group.add_argument(
        '--url',
        help='Full callback URL from GitHub (will extract code and state automatically)'
    )
    
    token_parser.add_argument(
        '--state',
        help='State parameter for CSRF verification (not needed if using --url)'
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
            print_rich_info("Initializing GitHub OAuth helper...")
        
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
            print_rich_success("Generated GitHub OAuth authorization URL")
            
            if args.verbose:
                info_data = {
                    'scopes_requested': ', '.join(args.scopes),
                    'state_parameter': state,
                    'redirect_uri': oauth.redirect_uri
                }
                display_rich_table(info_data, "OAuth Configuration")
            
            if HAS_RICH:
                console.print("\n[bold cyan]Authorization URL:[/bold cyan]")
                console.print(f"[link]{auth_url}[/link]")
                console.print(f"\n[bold yellow]State (save this for verification):[/bold yellow] [cyan]{state}[/cyan]")
            else:
                print_colored("Authorization URL:", "cyan", bold=True)
                print_colored(auth_url, "white")
                print()
                print_colored(f"State (save this for verification): {state}", "yellow")
            
            if args.open:
                print_rich_info("Opening authorization URL in browser...")
                try:
                    webbrowser.open(auth_url)
                    print_rich_success("Browser opened successfully")
                except Exception as e:
                    print_rich_warning(f"Could not open browser: {e}")
                    print_rich_info("Please copy and paste the URL manually")
            
    except GitHubOAuthError as e:
        print_rich_error(f"OAuth Error: {e}")
        sys.exit(1)
    except Exception as e:
        print_rich_error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            if HAS_RICH:
                console.print(f"[red]{traceback.format_exc()}[/red]")
            else:
                print_colored(traceback.format_exc(), "red")
        sys.exit(1)


def cmd_token(args: argparse.Namespace) -> None:
    """Handle token command - exchange code for token."""
    try:
        if args.verbose:
            print_rich_info("Exchanging authorization code for access token...")
        
        # Extract code and state from URL if provided
        if args.url:
            parsed_url = urlparse(args.url)
            query_params = parse_qs(parsed_url.query)
            
            # Extract code
            if 'code' not in query_params:
                raise ValueError("No 'code' parameter found in the provided URL")
            code = query_params['code'][0]
            
            # Extract state if present
            state = query_params.get('state', [None])[0]
            
            if args.verbose:
                print_rich_info(f"Extracted code from URL: {code[:8]}...")
                if state:
                    print_rich_info(f"Extracted state from URL: {state}")
        else:
            code = args.code
            state = args.state
        
        oauth = create_oauth_helper(args)
        token_data = oauth.exchange_code_for_token(
            code=code,
            state=state
        )
        
        if args.json:
            output_result(token_data, args)
        else:
            print_rich_success("Successfully exchanged authorization code for access token")
            
            if args.verbose:
                token_info = {
                    'token_type': token_data.get('token_type', 'N/A'),
                    'scope': token_data.get('scope', 'N/A'),
                    'expires_in_seconds': token_data.get('expires_in', 'N/A')
                }
                display_rich_table(token_info, "Token Details")
            
            if HAS_RICH:
                console.print("\n[bold cyan]Access Token:[/bold cyan]")
                console.print(f"[green]{token_data.get('access_token')}[/green]")
                
                if 'refresh_token' in token_data:
                    console.print(f"\n[bold yellow]Refresh Token:[/bold yellow] [yellow]{token_data['refresh_token']}[/yellow]")
                if 'expires_in' in token_data:
                    console.print(f"\n[bold blue]ℹ[/bold blue] Expires in: [white]{token_data['expires_in']}[/white] seconds")
            else:
                print_colored("Access Token:", "cyan", bold=True)
                print_colored(token_data.get('access_token'), "white")
                
                if 'refresh_token' in token_data:
                    print_colored(f"\nRefresh Token: {token_data['refresh_token']}", "yellow")
                if 'expires_in' in token_data:
                    print_info(f"Expires in: {token_data['expires_in']} seconds")
                
    except GitHubOAuthError as e:
        print_rich_error(f"OAuth Error: {e}")
        sys.exit(1)
    except Exception as e:
        print_rich_error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            if HAS_RICH:
                console.print(f"[red]{traceback.format_exc()}[/red]")
            else:
                print_colored(traceback.format_exc(), "red")
        sys.exit(1)


def cmd_test(args: argparse.Namespace) -> None:
    """Handle test command - test token validity."""
    try:
        if args.verbose:
            print_rich_info("Testing access token validity...")
        
        oauth = create_oauth_helper(args)
        user_data = oauth.test_api_access(args.token)
        
        if args.json:
            output_result(user_data, args)
        else:
            print_rich_success("Token is valid! User information:")
            
            # Create user info table
            user_info = {
                'username': user_data.get('login', 'N/A'),
                'name': user_data.get('name', 'N/A'),
                'email': user_data.get('email', 'N/A'),
                'user_id': str(user_data.get('id', 'N/A')),
                'account_type': user_data.get('type', 'N/A'),
                'public_repos': str(user_data.get('public_repos', 'N/A')),
                'followers': str(user_data.get('followers', 'N/A')),
                'following': str(user_data.get('following', 'N/A'))
            }
            
            if user_data.get('company'):
                user_info['company'] = user_data.get('company')
            if user_data.get('location'):
                user_info['location'] = user_data.get('location')
            if user_data.get('blog'):
                user_info['blog'] = user_data.get('blog')
            
            display_rich_table(user_info, "GitHub User Information")
            
    except GitHubOAuthError as e:
        print_rich_error(f"OAuth Error: {e}")
        sys.exit(1)
    except Exception as e:
        print_rich_error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            if HAS_RICH:
                console.print(f"[red]{traceback.format_exc()}[/red]")
            else:
                print_colored(traceback.format_exc(), "red")
        sys.exit(1)


def cmd_revoke(args: argparse.Namespace) -> None:
    """Handle revoke command - revoke access token."""
    try:
        if args.verbose:
            print_rich_info("Revoking access token...")
        
        oauth = create_oauth_helper(args)
        success = oauth.revoke_token(args.token)
        
        result = {'revoked': success}
        
        if args.json:
            output_result(result, args)
        else:
            if success:
                print_rich_success("Token successfully revoked")
                if HAS_RICH:
                    console.print("[dim]The token can no longer be used to access GitHub's API.[/dim]")
            else:
                print_rich_warning("Failed to revoke token (it may already be invalid)")
                
    except GitHubOAuthError as e:
        print_rich_error(f"OAuth Error: {e}")
        sys.exit(1)
    except Exception as e:
        print_rich_error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            if HAS_RICH:
                console.print(f"[red]{traceback.format_exc()}[/red]")
            else:
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
    
    # Show header unless disabled or JSON output
    if not getattr(args, 'no_header', False) and not getattr(args, 'json', False):
        show_header()
    
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

