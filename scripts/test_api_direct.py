#!/usr/bin/env python3
"""
Direct Apple Music API test - bypasses MusicKit JS to test token directly
"""

import os
import sys
import json
import urllib.request
import urllib.error


def test_developer_token():
    """Test if developer token works with Apple Music API"""

    # Get token from environment or command line
    token = os.getenv("APPLE_MUSIC_DEVELOPER_TOKEN")
    if not token and len(sys.argv) > 1:
        token = sys.argv[1]

    if not token:
        print("Usage: python test_api_direct.py <developer_token>")
        print("Or set APPLE_MUSIC_DEVELOPER_TOKEN environment variable")
        return 1

    print("Testing Apple Music API with developer token...")
    print("=" * 60)

    # Test 1: Try to access catalog (doesn't need user token)
    print("\nTest 1: Searching catalog (no user token required)")
    print("-" * 60)

    try:
        search_url = "https://api.music.apple.com/v1/catalog/us/search?term=billie%20jean&types=songs&limit=1"

        req = urllib.request.Request(search_url)
        req.add_header("Authorization", f"Bearer {token}")

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))

            if 'results' in data and 'songs' in data['results']:
                songs = data['results']['songs']['data']
                if songs:
                    song = songs[0]['attributes']
                    print(f"✓ SUCCESS: Found track: {song['name']} by {song['artistName']}")
                    print(f"✓ Developer token works for catalog access")
                else:
                    print("✓ API call succeeded but no results")
            else:
                print("✓ API call succeeded")
                print(f"Response: {json.dumps(data, indent=2)}")

    except urllib.error.HTTPError as e:
        print(f"✗ FAILED: HTTP {e.code}")
        error_body = e.read().decode('utf-8')
        print(f"Error: {error_body}")

        try:
            error_json = json.loads(error_body)
            if 'errors' in error_json:
                for err in error_json['errors']:
                    print(f"\nError Code: {err.get('code')}")
                    print(f"Title: {err.get('title')}")
                    print(f"Detail: {err.get('detail')}")
        except:
            pass
        return 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return 1

    # Test 2: Try to access user's storefront (needs user token BUT should fail gracefully)
    print("\nTest 2: Attempting to access user endpoint")
    print("-" * 60)
    print("Note: This WILL fail (no user token) but the error tells us if the developer token is valid")

    try:
        storefront_url = "https://api.music.apple.com/v1/me/storefront"

        req = urllib.request.Request(storefront_url)
        req.add_header("Authorization", f"Bearer {token}")

        with urllib.request.urlopen(req) as response:
            print("✓ Unexpected success - this shouldn't work without user token")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')

        if e.code == 401:
            print("✓ Expected 401 Unauthorized (user token missing)")
            print("✓ This means your developer token is VALID")
            print("✓ The issue is with MusicKit JS authorization flow, not your token")
        elif e.code == 403:
            print("✗ 403 Forbidden - Developer token issue")
            print("Error:", error_body)

            try:
                error_json = json.loads(error_body)
                if 'errors' in error_json:
                    for err in error_json['errors']:
                        detail = err.get('detail', '')
                        if 'MusicKit' in detail:
                            print("\n✗ PROBLEM: MusicKit not properly configured")
                            print("✗ Even though your key has MusicKit enabled,")
                            print("✗ there may be an issue with your MusicKit Identifier")
            except:
                pass
            return 1
        else:
            print(f"Unexpected error code: {e.code}")
            print(f"Error: {error_body}")

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    print("✓ Your developer token is VALID and works with Apple Music API")
    print("✓ The issue is specifically with MusicKit JS web authorization")
    print("\nPossible causes:")
    print("1. MusicKit Identifier not properly saved/active in Apple Developer")
    print("2. Browser/CORS restrictions")
    print("3. Apple Music account region restrictions")
    print("4. Need to wait for MusicKit Identifier to propagate (can take time)")
    print("\nNext steps:")
    print("1. Go to: https://developer.apple.com/account/resources/identifiers/list/musicId")
    print("2. Verify your MusicKit Identifier is listed and 'Enabled'")
    print("3. Wait 10-15 minutes for changes to propagate")
    print("4. Try authorization again")

    return 0


if __name__ == "__main__":
    sys.exit(test_developer_token())
