"""Example usage of Apple Music integration with Plylist"""

import os
from plylist import PlaylistManager, Track, AppleMusicPlatform


def main():
    """Demonstrate Apple Music integration"""

    print("=== Plylist Apple Music Integration Example ===\n")

    # Check if credentials are set
    required_env_vars = [
        "APPLE_MUSIC_TEAM_ID",
        "APPLE_MUSIC_KEY_ID",
        "APPLE_MUSIC_PRIVATE_KEY_PATH",
        "APPLE_MUSIC_USER_TOKEN"
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print("Apple Music credentials not configured!")
        print("\nRequired environment variables:")
        for var in required_env_vars:
            status = "✓" if var not in missing_vars else "✗"
            print(f"  {status} {var}")

        print("\nTo use Apple Music integration:")
        print("1. Create an Apple Developer account")
        print("2. Enable MusicKit")
        print("3. Create a MusicKit identifier and key")
        print("4. Download the .p8 private key file")
        print("5. Obtain a user music token via MusicKit JS")
        print("\nSet the environment variables and run again.")
        return

    # Initialize the playlist manager
    manager = PlaylistManager()

    # Initialize and register Apple Music platform
    print("1. Initializing Apple Music platform...")
    apple_music = AppleMusicPlatform()

    # Authenticate
    print("2. Authenticating with Apple Music...")
    if not apple_music.authenticate():
        print("   Failed to authenticate with Apple Music")
        return

    print("   ✓ Authenticated successfully\n")

    # Register the platform with the manager
    manager.register_platform(apple_music)

    # Create a local playlist
    print("3. Creating a local playlist...")
    playlist = manager.create_playlist(
        name="Apple Music Test",
        description="Testing Apple Music integration",
        tags=["test", "apple-music"]
    )
    print(f"   Created: {playlist.name}")
    print(f"   ID: {playlist.playlist_id}\n")

    # Search for tracks on Apple Music
    print("4. Searching for tracks on Apple Music...")

    search_tracks = [
        ("Billie Jean", "Michael Jackson"),
        ("Bohemian Rhapsody", "Queen"),
        ("Imagine", "John Lennon"),
    ]

    for title, artist in search_tracks:
        print(f"   Searching: {title} by {artist}")
        track = apple_music.search_track(title, artist)

        if track:
            print(f"   ✓ Found: {track}")
            manager.add_track_to_playlist(playlist.playlist_id, track)
        else:
            print(f"   ✗ Not found")

    print()

    # Show the playlist
    print("5. Local playlist contents:")
    updated_playlist = manager.get_playlist(playlist.playlist_id)
    for i, track in enumerate(updated_playlist.tracks, 1):
        print(f"   {i}. {track}")

    print()

    # Sync playlist to Apple Music
    print("6. Syncing playlist to Apple Music...")
    if manager.sync_to_platform(playlist.playlist_id, "apple_music"):
        print("   ✓ Playlist synced to Apple Music")

        # Get the Apple Music playlist ID
        synced_playlist = manager.get_playlist(playlist.playlist_id)
        am_id = synced_playlist.get_platform_id("apple_music")
        print(f"   Apple Music Playlist ID: {am_id}")
    else:
        print("   ✗ Failed to sync playlist")

    print()

    # Get user's Apple Music playlists
    print("7. Fetching your Apple Music playlists...")
    user_playlists = apple_music.get_user_playlists()

    if user_playlists:
        print(f"   Found {len(user_playlists)} playlists:")
        for pl in user_playlists[:5]:  # Show first 5
            am_id = pl.get_platform_id("apple_music")
            print(f"   - {pl.name} (ID: {am_id})")
    else:
        print("   No playlists found")

    print()

    # Import an Apple Music playlist
    if user_playlists:
        print("8. Importing a playlist from Apple Music...")
        am_playlist = user_playlists[0]
        am_id = am_playlist.get_platform_id("apple_music")

        imported = manager.sync_from_platform("apple_music", am_id)

        if imported:
            print(f"   ✓ Imported: {imported.name}")
            print(f"   Tracks: {len(imported.tracks)}")

            if imported.tracks:
                print("   First 3 tracks:")
                for track in imported.tracks[:3]:
                    print(f"     - {track}")
        else:
            print("   ✗ Failed to import playlist")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
