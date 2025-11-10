"""Basic usage example for Plylist"""

from plylist import PlaylistManager, Playlist, Track


def main():
    """Demonstrate basic Plylist functionality"""

    # Initialize the playlist manager
    manager = PlaylistManager()

    print("=== Plylist Basic Usage Example ===\n")

    # Create a new playlist
    print("1. Creating a new playlist...")
    workout_playlist = manager.create_playlist(
        name="Workout Mix",
        description="High energy tracks for the gym",
        tags=["workout", "high-energy"],
    )
    print(f"   Created: {workout_playlist.name}")
    print(f"   ID: {workout_playlist.playlist_id}\n")

    # Add tracks to the playlist
    print("2. Adding tracks...")
    tracks_to_add = [
        Track(
            title="Eye of the Tiger",
            artist="Survivor",
            album="Eye of the Tiger",
            duration_ms=246000,
        ),
        Track(
            title="Lose Yourself",
            artist="Eminem",
            album="8 Mile Soundtrack",
            duration_ms=326000,
        ),
        Track(
            title="Stronger",
            artist="Kanye West",
            album="Graduation",
            duration_ms=311000,
        ),
    ]

    for track in tracks_to_add:
        manager.add_track_to_playlist(workout_playlist.playlist_id, track)
        print(f"   Added: {track}")

    print()

    # List all playlists
    print("3. Listing all playlists...")
    all_playlists = manager.list_playlists()
    for p in all_playlists:
        print(f"   - {p['name']} ({p['track_count']} tracks)")

    print()

    # Show playlist details
    print("4. Getting playlist details...")
    playlist = manager.get_playlist(workout_playlist.playlist_id)
    print(f"   Name: {playlist.name}")
    print(f"   Description: {playlist.description}")
    print(f"   Total tracks: {len(playlist.tracks)}")
    print(f"   Duration: {playlist.get_duration_str()}")
    print(f"   Tags: {', '.join(playlist.tags)}")

    print()

    # Show tracks in the playlist
    print("5. Tracks in playlist:")
    for i, track in enumerate(playlist.tracks, 1):
        print(f"   {i}. {track}")

    print()

    # Create another playlist
    print("6. Creating a chill playlist...")
    chill_playlist = manager.create_playlist(
        name="Chill Vibes",
        description="Relaxing music for studying",
        tags=["chill", "study"],
    )

    chill_tracks = [
        Track(title="Weightless", artist="Marconi Union", duration_ms=378000),
        Track(title="Clair de Lune", artist="Claude Debussy", duration_ms=300000),
    ]

    for track in chill_tracks:
        manager.add_track_to_playlist(chill_playlist.playlist_id, track)

    print(f"   Created: {chill_playlist.name} with {len(chill_tracks)} tracks\n")

    # Search playlists by tag
    print("7. Searching playlists with 'workout' tag...")
    workout_playlists = manager.list_playlists(tags=["workout"])
    for p in workout_playlists:
        print(f"   - {p['name']}")

    print()

    # Export playlist
    print("8. Exporting workout playlist to JSON...")
    export_path = "/tmp/workout_playlist.json"
    if manager.export_playlist(workout_playlist.playlist_id, export_path, format="json"):
        print(f"   Exported to: {export_path}")

    print()

    # Duplicate a playlist
    print("9. Duplicating the workout playlist...")
    duplicate = manager.duplicate_playlist(workout_playlist.playlist_id, "Workout Mix - Copy")
    if duplicate:
        print(f"   Created duplicate: {duplicate.name}")
        print(f"   New ID: {duplicate.playlist_id}")

    print()

    # Get statistics
    print("10. Overall statistics:")
    stats = manager.get_stats()
    print(f"    Total playlists: {stats['total_playlists']}")
    print(f"    Total tracks: {stats['total_tracks']}")
    print(f"    Storage location: {stats['storage_directory']}")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
