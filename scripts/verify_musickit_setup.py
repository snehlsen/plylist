#!/usr/bin/env python3
"""
Comprehensive verification tool for Apple Music MusicKit setup
This helps identify configuration issues with developer tokens and MusicKit Identifiers
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_check(passed, message):
    """Print a check result"""
    symbol = "✓" if passed else "✗"
    color_start = "\033[92m" if passed else "\033[91m"
    color_end = "\033[0m"
    print(f"{color_start}{symbol}{color_end} {message}")


def decode_jwt(token):
    """Decode JWT without verification"""
    try:
        import base64
        parts = token.split('.')
        if len(parts) != 3:
            return None, None

        # Decode header and payload
        def decode_part(part):
            # Add padding if needed
            padding = len(part) % 4
            if padding:
                part += '=' * (4 - padding)
            return json.loads(base64.urlsafe_b64decode(part))

        header = decode_part(parts[0])
        payload = decode_part(parts[1])
        return header, payload
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None, None


def verify_token_structure(token):
    """Verify the developer token structure"""
    print_section("STEP 1: Verify Token Structure")

    # Check format
    parts = token.split('.')
    print_check(len(parts) == 3, f"Token has 3 parts (found {len(parts)})")

    if len(parts) != 3:
        print("\n✗ Invalid JWT format. Token must have format: header.payload.signature")
        return False

    # Decode and check contents
    header, payload = decode_jwt(token)

    if not header or not payload:
        print_check(False, "Token could not be decoded")
        return False

    print_check(True, "Token decoded successfully")

    # Check header
    print(f"\n  Header:")
    print(f"    Algorithm: {header.get('alg')}")
    print(f"    Key ID: {header.get('kid')}")

    print_check(header.get('alg') == 'ES256', "Algorithm is ES256")
    print_check('kid' in header, "Key ID present in header")

    # Check payload
    print(f"\n  Payload:")
    print(f"    Team ID (iss): {payload.get('iss')}")
    print(f"    Issued at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(payload.get('iat', 0)))}")
    print(f"    Expires: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(payload.get('exp', 0)))}")

    required_fields = ['iss', 'iat', 'exp']
    for field in required_fields:
        print_check(field in payload, f"Required field '{field}' present")

    # Check expiration
    now = int(time.time())
    exp = payload.get('exp', 0)
    is_expired = exp < now

    if not is_expired:
        days_remaining = (exp - now) / 86400
        print_check(True, f"Token not expired ({days_remaining:.1f} days remaining)")
    else:
        print_check(False, "Token is EXPIRED")
        return False

    return True


def test_official_endpoint(token):
    """Test Apple's official token validation endpoint"""
    print_section("STEP 2: Test Official Apple Music Token Endpoint")

    print("Testing /v1/test endpoint (Apple's official validation)...\n")

    try:
        test_url = "https://api.music.apple.com/v1/test"

        req = urllib.request.Request(test_url)
        req.add_header("Authorization", f"Bearer {token}")

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            print_check(True, "Official test endpoint successful")
            print(f"    Response: {json.dumps(data, indent=2)}")
            return True, data

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print_check(False, f"HTTP {e.code} error")
        print(f"    {error_body}")
        return False, None
    except Exception as e:
        print_check(False, f"Request failed: {e}")
        return False, None


def test_catalog_access(token):
    """Test catalog access (public, doesn't need user token)"""
    print_section("STEP 3: Test Catalog Access (Public API)")

    try:
        search_url = "https://api.music.apple.com/v1/catalog/us/search?term=test&types=songs&limit=1"

        req = urllib.request.Request(search_url)
        req.add_header("Authorization", f"Bearer {token}")

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

            if 'results' in data:
                print_check(True, "Catalog search successful")
                print(f"    This confirms your developer token works for public catalog")
                return True
            else:
                print_check(False, "Unexpected response format")
                return False

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print_check(False, f"HTTP {e.code} error")
        print(f"    {error_body}")

        if e.code == 403:
            print("\n    ⚠️  403 Forbidden on catalog endpoint is unusual")
            print("    This suggests your developer token is completely invalid")
            print("    or your Apple Developer account has restrictions")

        return False
    except Exception as e:
        print_check(False, f"Request failed: {e}")
        return False


def test_user_endpoint(token):
    """Test user endpoint (requires user token, but helps diagnose)"""
    print_section("STEP 4: Test User Endpoint (Requires User Token)")

    print("Testing /me/storefront endpoint...")
    print("Note: This SHOULD fail with 401, but the error type tells us important info\n")

    try:
        storefront_url = "https://api.music.apple.com/v1/me/storefront"

        req = urllib.request.Request(storefront_url)
        req.add_header("Authorization", f"Bearer {token}")

        with urllib.request.urlopen(req, timeout=10) as response:
            print_check(False, "Unexpected success - this shouldn't work without user token")
            return "unexpected_success"

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')

        if e.code == 401:
            print_check(True, "Got expected 401 Unauthorized")
            print("    ✓ This is GOOD! It means:")
            print("    ✓ Your developer token is valid for user endpoints")
            print("    ✓ You just need a user token (which requires authorization)")
            print("    ✓ Your MusicKit setup is likely correct")
            return "correct_401"

        elif e.code == 403:
            print_check(False, "Got 403 Forbidden (this is the problem!)")
            print("    ✗ This is BAD! It means:")
            print("    ✗ Your developer token is being rejected for user operations")
            print("    ✗ Even though catalog access works, user endpoints don't")
            print("    ✗ This indicates a MusicKit Identifier or Key configuration issue")

            # Try to parse error details
            try:
                error_json = json.loads(error_body)
                if 'errors' in error_json:
                    for err in error_json['errors']:
                        print(f"\n    Error code: {err.get('code')}")
                        print(f"    Title: {err.get('title')}")
                        print(f"    Detail: {err.get('detail')}")
            except:
                print(f"\n    Raw error: {error_body}")

            return "wrong_403"

        else:
            print_check(False, f"Got unexpected HTTP {e.code}")
            print(f"    {error_body}")
            return f"unexpected_{e.code}"

    except Exception as e:
        print_check(False, f"Request failed: {e}")
        return "error"


def test_recent_plays_endpoint(token):
    """Test another user endpoint"""
    print_section("STEP 5: Test Alternative User Endpoint")

    print("Testing /me/recent/played endpoint...\n")

    try:
        recent_url = "https://api.music.apple.com/v1/me/recent/played"

        req = urllib.request.Request(recent_url)
        req.add_header("Authorization", f"Bearer {token}")

        with urllib.request.urlopen(req, timeout=10) as response:
            print_check(False, "Unexpected success")
            return "unexpected_success"

    except urllib.error.HTTPError as e:
        if e.code == 401:
            print_check(True, "Got expected 401 Unauthorized")
            return "correct_401"
        elif e.code == 403:
            print_check(False, "Got 403 Forbidden")
            return "wrong_403"
        else:
            print_check(False, f"Got HTTP {e.code}")
            return f"unexpected_{e.code}"
    except Exception as e:
        print_check(False, f"Request failed: {e}")
        return "error"


def print_diagnosis(test_ok, catalog_ok, user_result):
    """Print diagnosis based on test results"""
    print_section("DIAGNOSIS")

    if test_ok and catalog_ok and user_result == "correct_401":
        print("\n🎉 GOOD NEWS: Your MusicKit setup appears to be correct!")
        print("\nYour developer token:")
        print("  ✓ Has valid structure and hasn't expired")
        print("  ✓ Passes Apple's official validation endpoint")
        print("  ✓ Works for public catalog access")
        print("  ✓ Works for user endpoints (returns expected 401)")
        print("\nNext steps:")
        print("  1. Use the get_apple_music_user_token.html tool")
        print("  2. Authorization should work now")
        print("  3. If you still get 'Unauthorized', try:")
        print("     - Different browser (Safari works best)")
        print("     - Disable browser extensions")
        print("     - Allow popups and cookies")

    elif test_ok and catalog_ok and user_result == "wrong_403":
        print("\n⚠️  UNUSUAL SITUATION: Token Valid But User Endpoints Fail")
        print("\nYour developer token:")
        print("  ✓ Has valid structure")
        print("  ✓ Passes Apple's official /v1/test endpoint")
        print("  ✓ Works for public catalog access")
        print("  ✗ Does NOT work for user endpoints (403 instead of 401)")
        print("\nThis is a very unusual pattern. Your token is valid according to Apple,")
        print("but user-scoped endpoints reject it. This could indicate:")
        print("\n🔧 POSSIBLE CAUSES:")
        print("\n1. MusicKit Identifier Issues:")
        print("   Even though your token is valid, the MusicKit Identifier might not")
        print("   be properly linked in Apple's authorization system.")
        print("   - Go to: https://developer.apple.com/account/resources/identifiers/list/musicId")
        print("   - Delete and recreate your MusicKit Identifier")
        print("   - Wait 15-20 minutes for full propagation")
        print("\n2. Account-Specific Restrictions:")
        print("   Your Apple Developer account might have regional or subscription restrictions")
        print("   - Verify you have an active Apple Developer Program membership")
        print("   - Check if there are any alerts in Apple Developer Console")
        print("\n3. Apple Backend Issue:")
        print("   This could be a temporary Apple service issue")
        print("   - Try again in a few hours")
        print("   - If persists, contact Apple Developer Support")
        print("\n4. Private Key Service Configuration:")
        print("   - Go to: https://developer.apple.com/account/resources/authkeys/list")
        print("   - Find your key and verify 'MusicKit' is explicitly checked")
        print("   - If uncertain, create a new key with MusicKit enabled")

    elif not catalog_ok:
        print("\n❌ CRITICAL PROBLEM: Developer Token Invalid")
        print("\nYour developer token doesn't work at all.")
        print("\n🔧 FIXES:")
        print("  1. Verify your private key file is correct")
        print("  2. Verify your Team ID and Key ID are correct")
        print("  3. Regenerate the token with: python scripts/generate_developer_token.py")
        print("  4. Make sure the private key has MusicKit enabled")

    else:
        print("\n❓ UNCLEAR ISSUE")
        print(f"\nOfficial test: {'OK' if test_ok else 'Failed'}")
        print(f"Catalog access: {'OK' if catalog_ok else 'Failed'}")
        print(f"User endpoint result: {user_result}")
        print("\nThis is an unusual configuration. Please review the test output above.")


def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  Apple Music MusicKit Setup Verification Tool")
    print("=" * 70)
    print("\nThis tool will diagnose issues with your MusicKit configuration")
    print("by testing your developer token against Apple Music API endpoints.\n")

    # Get token
    token = os.getenv("APPLE_MUSIC_DEVELOPER_TOKEN")
    if not token and len(sys.argv) > 1:
        token = sys.argv[1]

    if not token:
        print("Usage: python verify_musickit_setup.py <developer_token>")
        print("Or set APPLE_MUSIC_DEVELOPER_TOKEN environment variable")
        return 1

    # Run tests
    structure_ok = verify_token_structure(token)

    if not structure_ok:
        print("\n✗ Token structure is invalid. Please regenerate your developer token.")
        return 1

    test_ok, test_data = test_official_endpoint(token)
    catalog_ok = test_catalog_access(token)
    user_result = test_user_endpoint(token)

    # Test another endpoint for confirmation
    if user_result == "wrong_403":
        user_result2 = test_recent_plays_endpoint(token)
        if user_result2 != user_result:
            print(f"\n⚠️  Note: Got different result on second user endpoint: {user_result2}")

    # Print diagnosis
    print_diagnosis(test_ok, catalog_ok, user_result)

    print("\n" + "=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
