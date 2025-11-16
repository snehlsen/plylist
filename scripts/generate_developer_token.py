"""
Helper script to generate Apple Music developer token

This script generates a developer token that you can use in the MusicKit JS
example to obtain a user token.

Usage:
    python generate_developer_token.py

Make sure these environment variables are set:
    APPLE_MUSIC_TEAM_ID
    APPLE_MUSIC_KEY_ID
    APPLE_MUSIC_PRIVATE_KEY_PATH
"""

import os
import sys
import time


def generate_developer_token():
    """Generate Apple Music developer token"""

    # Check for required dependencies
    try:
        import jwt
    except ImportError:
        print("Error: PyJWT library is required")
        print("Install with: pip install PyJWT cryptography")
        return None

    # Get credentials from environment
    team_id = os.getenv("APPLE_MUSIC_TEAM_ID")
    key_id = os.getenv("APPLE_MUSIC_KEY_ID")
    private_key_path = os.getenv("APPLE_MUSIC_PRIVATE_KEY_PATH")

    # Validate credentials
    if not all([team_id, key_id, private_key_path]):
        print("Error: Missing required environment variables")
        print("\nPlease set:")
        if not team_id:
            print("  - APPLE_MUSIC_TEAM_ID")
        if not key_id:
            print("  - APPLE_MUSIC_KEY_ID")
        if not private_key_path:
            print("  - APPLE_MUSIC_PRIVATE_KEY_PATH")
        return None

    # Read private key
    try:
        with open(private_key_path, "r") as key_file:
            private_key = key_file.read()
    except FileNotFoundError:
        print(f"Error: Private key file not found: {private_key_path}")
        return None
    except Exception as e:
        print(f"Error reading private key: {e}")
        return None

    # Generate token (valid for 180 days)
    time_now = int(time.time())
    time_expiry = time_now + (180 * 24 * 60 * 60)  # 180 days

    headers = {
        "alg": "ES256",
        "kid": key_id
    }

    payload = {
        "iss": team_id,
        "iat": time_now,
        "exp": time_expiry
    }

    try:
        token = jwt.encode(
            payload,
            private_key,
            algorithm="ES256",
            headers=headers
        )
        return token
    except Exception as e:
        print(f"Error generating token: {e}")
        return None


def main():
    """Main entry point"""
    print("Apple Music Developer Token Generator")
    print("=" * 50)
    print()

    token = generate_developer_token()

    if token:
        print("✓ Developer token generated successfully!")
        print()
        print("Your developer token:")
        print("-" * 50)
        print(token)
        print("-" * 50)
        print()
        print("This token is valid for 180 days.")
        print()
        print("To use it:")
        print("1. Copy the token above")
        print("2. Open the MusicKit HTML example")
        print("3. Replace 'YOUR_DEVELOPER_TOKEN_HERE' with this token")
        print("4. Open the HTML file in a browser")
        print("5. Click 'Authorize Apple Music'")
        print("6. Copy the user token that appears")
        print("7. Set it as APPLE_MUSIC_USER_TOKEN environment variable")
        return 0
    else:
        print("\n✗ Failed to generate developer token")
        return 1


if __name__ == "__main__":
    sys.exit(main())
