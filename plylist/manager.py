"""Main playlist manager for Plylist"""

from typing import List, Optional, Dict, Any
from .models.playlist import Playlist
from .models.track import Track
from .storage.json_storage import JSONStorage
from .platforms.base import PlatformBase


class PlaylistManager:
    """
    Central manager for playlist operations

    Handles CRUD operations for playlists and provides integration
    with different streaming platforms.
    """

    def __init__(self, storage: JSONStorage = None):
        """
        Initialize the playlist manager

        Args:
            storage: Storage backend to use. Defaults to JSONStorage.
        """
        self.storage = storage or JSONStorage()
        self.platforms: Dict[str, PlatformBase] = {}

    def register_platform(self, platform: PlatformBase) -> None:
        """
        Register a streaming platform integration

        Args:
            platform: Platform integration instance
        """
        self.platforms[platform.platform_name] = platform

    def create_playlist(self, name: str, description: str = None, tags: List[str] = None) -> Playlist:
        """
        Create a new playlist

        Args:
            name: Playlist name
            description: Optional description
            tags: Optional list of tags

        Returns:
            Created Playlist object
        """
        playlist = Playlist(name=name, description=description, tags=tags or [])
        self.storage.save(playlist)
        return playlist

    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """
        Get a playlist by ID

        Args:
            playlist_id: Playlist ID

        Returns:
            Playlist object if found, None otherwise
        """
        return self.storage.load(playlist_id)

    def update_playlist(self, playlist: Playlist) -> bool:
        """
        Update a playlist

        Args:
            playlist: Playlist with updated data

        Returns:
            True if successful, False otherwise
        """
        return self.storage.save(playlist)

    def delete_playlist(self, playlist_id: str) -> bool:
        """
        Delete a playlist

        Args:
            playlist_id: ID of playlist to delete

        Returns:
            True if successful, False otherwise
        """
        return self.storage.delete(playlist_id)

    def list_playlists(self, query: str = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        List all playlists, optionally filtered

        Args:
            query: Optional search query
            tags: Optional list of tags to filter by

        Returns:
            List of playlist metadata dictionaries
        """
        if query or tags:
            return self.storage.search(query=query, tags=tags)
        return self.storage.list_all()

    def add_track_to_playlist(self, playlist_id: str, track: Track) -> bool:
        """
        Add a track to a playlist

        Args:
            playlist_id: Playlist ID
            track: Track to add

        Returns:
            True if successful, False otherwise
        """
        playlist = self.get_playlist(playlist_id)
        if playlist is None:
            return False

        playlist.add_track(track)
        return self.update_playlist(playlist)

    def remove_track_from_playlist(self, playlist_id: str, track_id: str) -> bool:
        """
        Remove a track from a playlist

        Args:
            playlist_id: Playlist ID
            track_id: Track ID to remove

        Returns:
            True if successful, False otherwise
        """
        playlist = self.get_playlist(playlist_id)
        if playlist is None:
            return False

        if playlist.remove_track(track_id):
            return self.update_playlist(playlist)
        return False

    def move_track(self, playlist_id: str, from_index: int, to_index: int) -> bool:
        """
        Move a track within a playlist

        Args:
            playlist_id: Playlist ID
            from_index: Current track index
            to_index: Target track index

        Returns:
            True if successful, False otherwise
        """
        playlist = self.get_playlist(playlist_id)
        if playlist is None:
            return False

        if playlist.move_track(from_index, to_index):
            return self.update_playlist(playlist)
        return False

    def rename_playlist(self, playlist_id: str, new_name: str) -> bool:
        """
        Rename a playlist

        Args:
            playlist_id: Playlist ID
            new_name: New name for the playlist

        Returns:
            True if successful, False otherwise
        """
        playlist = self.get_playlist(playlist_id)
        if playlist is None:
            return False

        playlist.name = new_name
        return self.update_playlist(playlist)

    def add_tags_to_playlist(self, playlist_id: str, tags: List[str]) -> bool:
        """
        Add tags to a playlist

        Args:
            playlist_id: Playlist ID
            tags: List of tags to add

        Returns:
            True if successful, False otherwise
        """
        playlist = self.get_playlist(playlist_id)
        if playlist is None:
            return False

        for tag in tags:
            playlist.add_tag(tag)

        return self.update_playlist(playlist)

    def export_playlist(self, playlist_id: str, export_path: str, format: str = "json") -> bool:
        """
        Export a playlist to a file

        Args:
            playlist_id: Playlist ID
            export_path: Path to export to
            format: Export format ('json' or 'csv')

        Returns:
            True if successful, False otherwise
        """
        return self.storage.export_playlist(playlist_id, export_path, format)

    def import_playlist(self, import_path: str, format: str = "json") -> Optional[Playlist]:
        """
        Import a playlist from a file

        Args:
            import_path: Path to import from
            format: Import format ('json' or 'csv')

        Returns:
            Imported Playlist if successful, None otherwise
        """
        return self.storage.import_playlist(import_path, format)

    def sync_to_platform(self, playlist_id: str, platform_name: str) -> bool:
        """
        Sync a playlist to a streaming platform

        Args:
            playlist_id: Playlist ID
            platform_name: Name of the platform to sync to

        Returns:
            True if successful, False otherwise
        """
        playlist = self.get_playlist(playlist_id)
        if playlist is None:
            return False

        platform = self.platforms.get(platform_name)
        if not platform:
            print(f"Platform '{platform_name}' not registered")
            return False

        if platform.sync_playlist_to_platform(playlist):
            # Save updated playlist with platform ID
            return self.update_playlist(playlist)
        return False

    def sync_from_platform(self, platform_name: str, platform_playlist_id: str) -> Optional[Playlist]:
        """
        Sync a playlist from a streaming platform

        Args:
            platform_name: Name of the platform
            platform_playlist_id: Platform-specific playlist ID

        Returns:
            Synced Playlist if successful, None otherwise
        """
        platform = self.platforms.get(platform_name)
        if not platform:
            print(f"Platform '{platform_name}' not registered")
            return None

        playlist = platform.sync_playlist_from_platform(platform_playlist_id)
        if playlist is not None:
            self.storage.save(playlist)
            return playlist
        return None

    def duplicate_playlist(self, playlist_id: str, new_name: str = None) -> Optional[Playlist]:
        """
        Create a duplicate of a playlist

        Args:
            playlist_id: ID of playlist to duplicate
            new_name: Optional new name (defaults to "Copy of [original name]")

        Returns:
            New Playlist if successful, None otherwise
        """
        original = self.get_playlist(playlist_id)
        if original is None:
            return None

        # Create a new playlist with duplicated data
        duplicate = Playlist(
            name=new_name or f"Copy of {original.name}",
            description=original.description,
            tracks=[Track.from_dict(t.to_dict()) for t in original.tracks],
            tags=original.tags.copy(),
        )

        if self.storage.save(duplicate):
            return duplicate
        return None

    def merge_playlists(self, playlist_ids: List[str], new_name: str, remove_duplicates: bool = True) -> Optional[Playlist]:
        """
        Merge multiple playlists into a new playlist

        Args:
            playlist_ids: List of playlist IDs to merge
            new_name: Name for the merged playlist
            remove_duplicates: Whether to remove duplicate tracks

        Returns:
            Merged Playlist if successful, None otherwise
        """
        all_tracks = []
        seen_tracks = set()

        for pid in playlist_ids:
            playlist = self.get_playlist(pid)
            if playlist is None:
                continue

            for track in playlist.tracks:
                if remove_duplicates:
                    # Create a simple hash for duplicate detection
                    track_hash = f"{track.title.lower()}|{track.artist.lower()}"
                    if track_hash in seen_tracks:
                        continue
                    seen_tracks.add(track_hash)

                all_tracks.append(Track.from_dict(track.to_dict()))

        merged = Playlist(name=new_name, tracks=all_tracks)
        if self.storage.save(merged):
            return merged
        return None

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about all playlists

        Returns:
            Dictionary with statistics
        """
        return self.storage.get_storage_stats()
