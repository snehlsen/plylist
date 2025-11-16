"""Main CLI application for Plylist"""

import argparse
import sys
from typing import Optional
from ..manager import PlaylistManager
from ..models.track import Track
from ..models.playlist import Playlist
from . import apple_music_commands


def format_playlist_info(playlist: Playlist) -> str:
    """Format playlist information for display"""
    lines = [
        f"\nPlaylist: {playlist.name}",
        f"ID: {playlist.playlist_id}",
    ]

    if playlist.description:
        lines.append(f"Description: {playlist.description}")

    lines.extend([
        f"Tracks: {len(playlist.tracks)}",
        f"Duration: {playlist.get_duration_str()}",
        f"Created: {playlist.created_at}",
        f"Updated: {playlist.updated_at}",
    ])

    if playlist.tags:
        lines.append(f"Tags: {', '.join(playlist.tags)}")

    if playlist.platform_ids:
        lines.append("Platform IDs:")
        for platform, pid in playlist.platform_ids.items():
            lines.append(f"  {platform}: {pid}")

    return "\n".join(lines)


def format_track_info(track: Track, index: Optional[int] = None) -> str:
    """Format track information for display"""
    prefix = f"{index + 1}. " if index is not None else ""
    return f"{prefix}{track}"


def cmd_create(args, manager: PlaylistManager) -> int:
    """Create a new playlist"""
    tags = args.tags.split(",") if args.tags else []
    playlist = manager.create_playlist(
        name=args.name,
        description=args.description,
        tags=tags,
    )
    print(f"Created playlist: {playlist.name}")
    print(f"Playlist ID: {playlist.playlist_id}")
    return 0


def cmd_list(args, manager: PlaylistManager) -> int:
    """List all playlists"""
    tags = args.tags.split(",") if args.tags else None
    playlists = manager.list_playlists(query=args.query, tags=tags)

    if not playlists:
        print("No playlists found.")
        return 0

    print(f"\nFound {len(playlists)} playlist(s):\n")
    for p in playlists:
        # Get full playlist to check platform IDs
        playlist = manager.get_playlist(p['playlist_id'])
        synced_platforms = []
        if playlist and playlist.platform_ids:
            synced_platforms = list(playlist.platform_ids.keys())

        sync_status = f" [Synced: {', '.join(synced_platforms)}]" if synced_platforms else " [Local only]"
        print(f"  {p['name']}{sync_status}")
        print(f"    ID: {p['playlist_id']}")
        print(f"    Tracks: {p['track_count']}")
        if p.get('tags'):
            print(f"    Tags: {', '.join(p['tags'])}")
        print()

    return 0


def cmd_show(args, manager: PlaylistManager) -> int:
    """Show playlist details"""
    playlist = manager.get_playlist(args.playlist_id)
    if playlist is None:
        print(f"Playlist not found: {args.playlist_id}")
        return 1

    print(format_playlist_info(playlist))

    if playlist.tracks and not args.no_tracks:
        print("\nTracks:")
        for i, track in enumerate(playlist.tracks):
            print(f"  {format_track_info(track, i)}")

    return 0


def cmd_delete(args, manager: PlaylistManager) -> int:
    """Delete a playlist"""
    if not args.force:
        playlist = manager.get_playlist(args.playlist_id)
        if playlist is not None:
            confirm = input(f"Delete playlist '{playlist.name}'? (y/N): ")
            if confirm.lower() != 'y':
                print("Cancelled.")
                return 0

    if manager.delete_playlist(args.playlist_id):
        print("Playlist deleted successfully.")
        return 0
    else:
        print("Failed to delete playlist.")
        return 1


def cmd_add_track(args, manager: PlaylistManager) -> int:
    """Add a track to a playlist"""
    playlist = manager.get_playlist(args.playlist_id)
    if playlist is None:
        print(f"Playlist not found: {args.playlist_id}")
        return 1

    additional_artists = (
        args.additional_artists.split(",")
        if args.additional_artists
        else []
    )
    track = Track(
        title=args.title,
        artist=args.artist,
        album=args.album,
        duration_ms=args.duration,
        isrc=args.isrc,
        additional_artists=additional_artists,
    )

    if manager.add_track_to_playlist(args.playlist_id, track):
        print(f"Added track: {track}")
        print(f"Track ID: {track.track_id}")
        return 0
    else:
        print("Failed to add track.")
        return 1


def cmd_remove_track(args, manager: PlaylistManager) -> int:
    """Remove a track from a playlist"""
    if manager.remove_track_from_playlist(args.playlist_id, args.track_id):
        print("Track removed successfully.")
        return 0
    else:
        print("Failed to remove track.")
        return 1


def cmd_rename(args, manager: PlaylistManager) -> int:
    """Rename a playlist"""
    if manager.rename_playlist(args.playlist_id, args.new_name):
        print(f"Renamed playlist to: {args.new_name}")
        return 0
    else:
        print("Failed to rename playlist.")
        return 1


def cmd_tag(args, manager: PlaylistManager) -> int:
    """Add tags to a playlist"""
    tags = args.tags.split(",")
    if manager.add_tags_to_playlist(args.playlist_id, tags):
        print(f"Added tags: {', '.join(tags)}")
        return 0
    else:
        print("Failed to add tags.")
        return 1


def cmd_export(args, manager: PlaylistManager) -> int:
    """Export a playlist"""
    if manager.export_playlist(args.playlist_id, args.output, args.format):
        print(f"Exported playlist to: {args.output}")
        return 0
    else:
        print("Failed to export playlist.")
        return 1


def cmd_import(args, manager: PlaylistManager) -> int:
    """Import a playlist"""
    playlist = manager.import_playlist(args.input, args.format)
    if playlist is not None:
        print(f"Imported playlist: {playlist.name}")
        print(f"Playlist ID: {playlist.playlist_id}")
        print(f"Tracks: {len(playlist.tracks)}")
        return 0
    else:
        print("Failed to import playlist.")
        return 1


def cmd_duplicate(args, manager: PlaylistManager) -> int:
    """Duplicate a playlist"""
    duplicate = manager.duplicate_playlist(args.playlist_id, args.name)
    if duplicate:
        print(f"Created duplicate: {duplicate.name}")
        print(f"Playlist ID: {duplicate.playlist_id}")
        return 0
    else:
        print("Failed to duplicate playlist.")
        return 1


def cmd_merge(args, manager: PlaylistManager) -> int:
    """Merge multiple playlists"""
    playlist_ids = args.playlist_ids.split(",")
    merged = manager.merge_playlists(
        playlist_ids,
        args.name,
        remove_duplicates=not args.keep_duplicates,
    )
    if merged:
        print(f"Created merged playlist: {merged.name}")
        print(f"Playlist ID: {merged.playlist_id}")
        print(f"Tracks: {len(merged.tracks)}")
        return 0
    else:
        print("Failed to merge playlists.")
        return 1


def cmd_stats(args, manager: PlaylistManager) -> int:
    """Show statistics"""
    stats = manager.get_stats()
    print("\nPlaylist Statistics:")
    print(f"  Total Playlists: {stats['total_playlists']}")
    print(f"  Total Tracks: {stats['total_tracks']}")
    print(f"  Storage Directory: {stats['storage_directory']}")
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Plylist - Platform-agnostic playlist manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create command
    create_parser = subparsers.add_parser(
        "create", help="Create a new playlist"
    )
    create_parser.add_argument("name", help="Playlist name")
    create_parser.add_argument(
        "-d", "--description", help="Playlist description"
    )
    create_parser.add_argument(
        "-t", "--tags", help="Comma-separated tags"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List playlists")
    list_parser.add_argument("-q", "--query", help="Search query")
    list_parser.add_argument(
        "-t", "--tags", help="Filter by comma-separated tags"
    )

    # Show command
    show_parser = subparsers.add_parser(
        "show", help="Show playlist details"
    )
    show_parser.add_argument("playlist_id", help="Playlist ID")
    show_parser.add_argument(
        "--no-tracks", action="store_true", help="Don't show tracks"
    )

    # Delete command
    delete_parser = subparsers.add_parser(
        "delete", help="Delete a playlist"
    )
    delete_parser.add_argument("playlist_id", help="Playlist ID")
    delete_parser.add_argument(
        "-f", "--force", action="store_true", help="Skip confirmation"
    )

    # Add track command
    add_track_parser = subparsers.add_parser(
        "add-track", help="Add a track to a playlist"
    )
    add_track_parser.add_argument("playlist_id", help="Playlist ID")
    add_track_parser.add_argument("title", help="Track title")
    add_track_parser.add_argument("artist", help="Artist name")
    add_track_parser.add_argument("-a", "--album", help="Album name")
    add_track_parser.add_argument(
        "-d", "--duration", type=int, help="Duration in milliseconds"
    )
    add_track_parser.add_argument("-i", "--isrc", help="ISRC code")
    add_track_parser.add_argument(
        "--additional-artists", help="Comma-separated additional artists"
    )

    # Remove track command
    remove_track_parser = subparsers.add_parser(
        "remove-track", help="Remove a track from a playlist"
    )
    remove_track_parser.add_argument("playlist_id", help="Playlist ID")
    remove_track_parser.add_argument("track_id", help="Track ID")

    # Rename command
    rename_parser = subparsers.add_parser("rename", help="Rename a playlist")
    rename_parser.add_argument("playlist_id", help="Playlist ID")
    rename_parser.add_argument("new_name", help="New playlist name")

    # Tag command
    tag_parser = subparsers.add_parser("tag", help="Add tags to a playlist")
    tag_parser.add_argument("playlist_id", help="Playlist ID")
    tag_parser.add_argument("tags", help="Comma-separated tags")

    # Export command
    export_parser = subparsers.add_parser(
        "export", help="Export a playlist"
    )
    export_parser.add_argument("playlist_id", help="Playlist ID")
    export_parser.add_argument("output", help="Output file path")
    export_parser.add_argument(
        "-f",
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Export format",
    )

    # Import command
    import_parser = subparsers.add_parser(
        "import", help="Import a playlist"
    )
    import_parser.add_argument("input", help="Input file path")
    import_parser.add_argument(
        "-f",
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Import format",
    )

    # Duplicate command
    duplicate_parser = subparsers.add_parser(
        "duplicate", help="Duplicate a playlist"
    )
    duplicate_parser.add_argument(
        "playlist_id", help="Playlist ID to duplicate"
    )
    duplicate_parser.add_argument(
        "-n", "--name", help="Name for the duplicate"
    )

    # Merge command
    merge_parser = subparsers.add_parser(
        "merge", help="Merge multiple playlists"
    )
    merge_parser.add_argument(
        "playlist_ids", help="Comma-separated playlist IDs"
    )
    merge_parser.add_argument("name", help="Name for merged playlist")
    merge_parser.add_argument(
        "--keep-duplicates",
        action="store_true",
        help="Keep duplicate tracks",
    )

    # Stats command
    subparsers.add_parser("stats", help="Show statistics")

    # Apple Music commands
    am_parser = subparsers.add_parser(
        "apple-music", help="Apple Music integration commands"
    )
    am_subparsers = am_parser.add_subparsers(
        dest="am_command", help="Apple Music operations"
    )

    # Apple Music auth
    am_subparsers.add_parser("auth", help="Test Apple Music authentication")

    # Apple Music search
    am_search_parser = am_subparsers.add_parser(
        "search", help="Search for a track on Apple Music"
    )
    am_search_parser.add_argument("title", help="Track title")
    am_search_parser.add_argument("artist", help="Artist name")

    # Apple Music sync-to
    am_sync_to_parser = am_subparsers.add_parser(
        "sync-to", help="Sync a local playlist to Apple Music"
    )
    am_sync_to_parser.add_argument("playlist_id", help="Local playlist ID to sync")

    # Apple Music sync-from
    am_sync_from_parser = am_subparsers.add_parser(
        "sync-from", help="Import a playlist from Apple Music"
    )
    am_sync_from_parser.add_argument(
        "apple_music_id", help="Apple Music playlist ID"
    )

    # Apple Music playlists
    am_subparsers.add_parser(
        "playlists", help="List your Apple Music playlists"
    )

    # Apple Music status
    am_subparsers.add_parser(
        "status", help="Show sync status for all playlists"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize manager
    manager = PlaylistManager()

    # Handle Apple Music subcommands
    if args.command == "apple-music":
        if not hasattr(args, "am_command") or not args.am_command:
            am_parser.print_help()
            return 1

        am_commands = {
            "auth": apple_music_commands.cmd_am_auth,
            "search": apple_music_commands.cmd_am_search,
            "sync-to": apple_music_commands.cmd_am_sync_to,
            "sync-from": apple_music_commands.cmd_am_sync_from,
            "playlists": apple_music_commands.cmd_am_playlists,
            "status": apple_music_commands.cmd_am_status,
        }

        try:
            return am_commands[args.am_command](args, manager)
        except KeyboardInterrupt:
            print("\nCancelled.")
            return 130
        except Exception as e:
            print(f"Error: {e}")
            return 1

    # Command dispatch
    commands = {
        "create": cmd_create,
        "list": cmd_list,
        "show": cmd_show,
        "delete": cmd_delete,
        "add-track": cmd_add_track,
        "remove-track": cmd_remove_track,
        "rename": cmd_rename,
        "tag": cmd_tag,
        "export": cmd_export,
        "import": cmd_import,
        "duplicate": cmd_duplicate,
        "merge": cmd_merge,
        "stats": cmd_stats,
    }

    try:
        return commands[args.command](args, manager)
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
