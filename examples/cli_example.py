#!/usr/bin/env python3
"""
Example demonstrating CLI usage for GitHub OAuth Helper.

This script shows how to use the gh-oauth-helper CLI commands
for different OAuth operations.
"""

import subprocess
import sys
import os


def run_cli_command(command_args):
    """Run a CLI command and capture output."""
    cmd = [sys.executable, "-m", "gh_oauth_helper.cli"] + command_args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"stderr: {e.stderr}")
        return None


def main():
    """Demonstrate CLI usage examples."""
    print("GitHub OAuth Helper CLI Examples")
    print("=" * 40)
    
    # Note: These examples use dummy credentials for demonstration
    client_id = "your_client_id_here"
    client_secret = "your_client_secret_here"
    
    print("\n1. Generate Authorization URL:")
    print("Command: gh-oauth-helper --client-id <id> --client-secret <secret> auth")
    
    # Demo with environment variables instead
    print("\n2. Using Environment Variables:")
    print("Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables")
    print("Command: gh-oauth-helper auth --scopes user:email public_repo")
    
    print("\n3. Exchange Code for Token:")
    print("Command: gh-oauth-helper --client-id <id> --client-secret <secret> token --code <auth_code>")
    
    print("\n4. Test Token Validity:")
    print("Command: gh-oauth-helper --client-id <id> --client-secret <secret> test --token <access_token>")
    
    print("\n5. Revoke Token:")
    print("Command: gh-oauth-helper --client-id <id> --client-secret <secret> revoke --token <access_token>")
    
    print("\n6. Using Secure Mode (HTTPS only):")
    print("Command: gh-oauth-helper --client-id <id> --client-secret <secret> --secure --redirect-uri https://example.com/callback auth")
    
    print("\n7. JSON Output:")
    print("Command: gh-oauth-helper --client-id <id> --client-secret <secret> --json auth")
    
    print("\n8. Verbose Output:")
    print("Command: gh-oauth-helper --client-id <id> --client-secret <secret> --verbose auth")
    
    print("\nFor actual usage, replace the placeholder values with real credentials.")
    print("You can also set environment variables:")
    print("  export GITHUB_CLIENT_ID=your_actual_client_id")
    print("  export GITHUB_CLIENT_SECRET=your_actual_client_secret")
    print("  export GITHUB_REDIRECT_URI=https://yourapp.com/callback")


if __name__ == "__main__":
    main()

