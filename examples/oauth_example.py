#!/usr/bin/env python3
"""
Example usage of the gh-oauth-helper library.

This script demonstrates how to use the OAuth functionality without hard-coded secrets.
Set your GitHub OAuth app credentials as environment variables:

    export GITHUB_CLIENT_ID="your_client_id"
    export GITHUB_CLIENT_SECRET="your_client_secret"
    export GITHUB_REDIRECT_URI="http://localhost:8080/callback"  # Optional

Or pass them directly to the functions.
"""

import os
import sys

# Add the src directory to the path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gh_oauth_helper import (
    GitHubOAuth, 
    GitHubOAuthError,
    start_auth_flow,
    complete_auth_flow,
    verify_token
)


def example_basic_usage():
    """Example using the basic convenience functions."""
    print("=== Basic Usage Example ===")
    
    try:
        # Start the auth flow - this reads credentials from environment variables
        auth_url, state = start_auth_flow(scopes=["user:email", "repo"])
        
        print(f"1. Visit this URL to authorize the application:")
        print(f"   {auth_url}")
        print(f"2. After authorization, you'll be redirected with a 'code' parameter")
        print(f"3. Store the state for CSRF protection: {state}")
        print(f"\n💡 Tip: For easier flows, use the CLI's paste-the-URL method!")
        print(f"   See OAUTH_FLOW_GUIDE.md for details")
        
        # Simulate receiving the authorization code
        print("\n--- Simulating code exchange ---")
        # In a real application, you would get this from the callback
        # code = input("Enter the authorization code from the callback: ")
        
        # For demo purposes, we'll skip the actual exchange
        print("(In a real app, call complete_auth_flow(code) here)")
        
    except GitHubOAuthError as e:
        print(f"OAuth Error: {e}")
        return False
    
    return True


def example_class_usage():
    """Example using the GitHubOAuth class directly."""
    print("\n=== Class Usage Example ===")
    
    try:
        # Create OAuth helper with explicit credentials (or use environment variables)
        oauth = GitHubOAuth(
            client_id=os.getenv("GITHUB_CLIENT_ID"),
            client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
            redirect_uri=os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8080/callback")
        )
        
        # Generate authorization URL with custom scopes
        auth_url, state = oauth.generate_authorization_url(
            scopes=["user", "public_repo", "read:org"]
        )
        
        print(f"Authorization URL: {auth_url}")
        print(f"State token: {state}")
        
        # Demo token testing (with a fake token)
        print("\n--- Testing API access ---")
        try:
            # This will fail with a fake token, which is expected
            oauth.test_api_access("fake_token_for_demo")
        except GitHubOAuthError as e:
            print(f"Expected error with fake token: {e}")
        
    except GitHubOAuthError as e:
        print(f"OAuth Error: {e}")
        return False
    
    return True


def example_complete_flow_simulation():
    """Example of a complete OAuth flow simulation."""
    print("\n=== Complete Flow Simulation ===")
    
    # Check if we have credentials
    if not os.getenv("GITHUB_CLIENT_ID") or not os.getenv("GITHUB_CLIENT_SECRET"):
        print("⚠️  Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables to run this example")
        return False
    
    try:
        oauth = GitHubOAuth()
        
        # Step 1: Generate authorization URL
        print("Step 1: Generating authorization URL...")
        auth_url, state = oauth.generate_authorization_url(scopes=["user:email"])
        print(f"✓ Authorization URL generated")
        print(f"  URL: {auth_url[:80]}...")
        print(f"  State: {state[:16]}...")
        
        # Step 2: User would visit the URL and authorize
        print("\nStep 2: User visits URL and authorizes (simulated)")
        print("✓ User authorization completed (simulated)")
        
        # Step 3: Exchange code for token (simulated)
        print("\nStep 3: Exchange authorization code for token (simulated)")
        print("(In real usage, you would call oauth.exchange_code_for_token(code))")
        print("💡 Alternative: Use the CLI with --url for easier flows (see OAUTH_FLOW_GUIDE.md)")
        
        # Step 4: Test API access (simulated)
        print("\nStep 4: Test API access (simulated)")
        print("(In real usage, you would call oauth.test_api_access(access_token))")
        
        print("\n✅ OAuth flow completed successfully!")
        
    except GitHubOAuthError as e:
        print(f"❌ OAuth Error: {e}")
        return False
    
    return True


def main():
    """Run all examples."""
    print("GitHub OAuth Helper - Example Usage")
    print("=" * 50)
    
    # Check for environment variables
    env_vars = ["GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET"]
    missing_vars = [var for var in env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nSet these variables to run the full examples:")
        print("   export GITHUB_CLIENT_ID='your_client_id'")
        print("   export GITHUB_CLIENT_SECRET='your_client_secret'")
        print("   export GITHUB_REDIRECT_URI='http://localhost:8080/callback'  # Optional")
        print("\nRunning limited examples...\n")
    
    # Run examples
    success = True
    success &= example_basic_usage()
    success &= example_class_usage()
    success &= example_complete_flow_simulation()
    
    if success:
        print("\n🎉 All examples completed!")
    else:
        print("\n❌ Some examples failed. Check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

