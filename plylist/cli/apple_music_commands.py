"""Apple Music CLI commands for Plylist"""

import os
from typing import Optional
from ..manager import PlaylistManager
from ..platforms.apple_music import AppleMusicPlatform


def get_apple_music_platform() -> Optional[AppleMusicPlatform]:
    """Initialize and authenticate Apple Music platform"""
    try:
        apple_music = AppleMusicPlatform()
        if apple_music.authenticate():
            return apple_music
        else:
            print("Failed to authenticate with Apple Music")
            print("Please check your credentials:")
            print("  - APPLE_MUSIC_TEAM_ID")
            print("  - APPLE_MUSIC_KEY_ID")
            print("  - APPLE_MUSIC_PRIVATE_KEY_PATH")
            print("  - APPLE_MUSIC_USER_TOKEN")
            return None
    except ImportError:
        print("Apple Music integration requires additional dependencies")
        print("Install with: pip install plylist[apple-music]")
        return None
    except Exception as e:
        print(f"Error initializing Apple Music: {e}")
        return None


def cmd_am_auth(args, manager: PlaylistManager) -> int:
    """Test Apple Music authentication"""
    print("Testing Apple Music authentication...")
    apple_music = get_apple_music_platform()

    if apple_music:
        print(f"✓ Successfully authenticated with Apple Music")
        print(f"  Storefront: {apple_music.storefront}")
        return 0
    return 1


def cmd_am_search(args, manager: PlaylistManager) -> int:
    """Search for tracks on Apple Music"""
    apple_music = get_apple_music_platform()
    if not apple_music:
        return 1

    print(f"Searching Apple Music for: {args.title} by {args.artist}")
    track = apple_music.search_track(args.title, args.artist)

    if track:
        print(f"\n✓ Found: {track}")
        print(f"  Apple Music ID: {track.get_platform_id('apple_music')}")
        if track.album:
            print(f"  Album: {track.album}")
        if track.duration_ms:
            duration_sec = track.duration_ms // 1000
            print(f"  Duration: {duration_sec // 60}:{duration_sec % 60:02d}")
        return 0
    else:
        print("✗ Track not found on Apple Music")
        return 1


def cmd_am_sync_to(args, manager: PlaylistManager) -> int:
    """Sync a local playlist to Apple Music"""
    apple_music = get_apple_music_platform()
    if not apple_music:
        return 1

    # Get the local playlist
    playlist = manager.get_playlist(args.playlist_id)
    if not playlist:
        print(f"Playlist not found: {args.playlist_id}")
        return 1

    # Register platform
    manager.register_platform(apple_music)

    print(f"Syncing '{playlist.name}' to Apple Music...")
    print(f"  Tracks to sync: {len(playlist.tracks)}")

    if manager.sync_to_platform(args.playlist_id, "apple_music"):
        updated_playlist = manager.get_playlist(args.playlist_id)
        am_id = updated_playlist.get_platform_id("apple_music")
        print(f"✓ Successfully synced to Apple Music")
        print(f"  Apple Music Playlist ID: {am_id}")
        return 0
    else:
        print("✗ Failed to sync playlist")
        return 1


def cmd_am_sync_from(args, manager: PlaylistManager) -> int:
    """Import a playlist from Apple Music"""
    apple_music = get_apple_music_platform()
    if not apple_music:
        return 1

    # Register platform
    manager.register_platform(apple_music)

    print(f"Importing playlist from Apple Music (ID: {args.apple_music_id})...")

    imported = manager.sync_from_platform("apple_music", args.apple_music_id)

    if imported:
        print(f"✓ Successfully imported: {imported.name}")
        print(f"  Local Playlist ID: {imported.playlist_id}")
        print(f"  Tracks: {len(imported.tracks)}")
        return 0
    else:
        print("✗ Failed to import playlist")
        return 1


def cmd_am_playlists(args, manager: PlaylistManager) -> int:
    """List playlists from Apple Music"""
    apple_music = get_apple_music_platform()
    if not apple_music:
        return 1

    print("Fetching your Apple Music playlists...")
    playlists = apple_music.get_user_playlists()

    if not playlists:
        print("No playlists found in your Apple Music library")
        return 0

    print(f"\nFound {len(playlists)} Apple Music playlist(s):\n")
    for playlist in playlists:
        am_id = playlist.get_platform_id("apple_music")
        print(f"  {playlist.name}")
        print(f"    Apple Music ID: {am_id}")
        if playlist.description:
            print(f"    Description: {playlist.description}")
        print()

    return 0


def cmd_am_status(args, manager: PlaylistManager) -> int:
    """Show sync status for all playlists"""
    playlists = manager.list_playlists()

    if not playlists:
        print("No local playlists found")
        return 0

    # Count synced playlists
    synced_count = 0
    for p in playlists:
        playlist = manager.get_playlist(p["playlist_id"])
        if playlist and playlist.get_platform_id("apple_music"):
            synced_count += 1

    print(f"\nSync Status:")
    print(f"  Total local playlists: {len(playlists)}")
    print(f"  Synced to Apple Music: {synced_count}")
    print(f"  Local only: {len(playlists) - synced_count}")
    print()

    print("Playlists:")
    for p in playlists:
        playlist = manager.get_playlist(p["playlist_id"])
        if playlist:
            am_id = playlist.get_platform_id("apple_music")
            status = "✓ Synced" if am_id else "  Local only"
            print(f"  [{status}] {playlist.name}")
            print(f"      Local ID: {playlist.playlist_id}")
            if am_id:
                print(f"      Apple Music ID: {am_id}")
            print()

    return 0
