"""Base class for platform integrations"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.track import Track
from ..models.playlist import Playlist


class PlatformBase(ABC):
    """
    Abstract base class for streaming platform integrations.

    This provides a common interface that can be implemented for
    different streaming platforms (Spotify, Apple Music, YouTube Music, etc.)
    """

    def __init__(self, platform_name: str):
        """
        Initialize the platform

        Args:
            platform_name: Name of the platform (e.g., 'spotify')
        """
        self.platform_name = platform_name

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the platform

        Returns:
            True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    def search_track(self, title: str, artist: str) -> Optional[Track]:
        """
        Search for a track on the platform

        Args:
            title: Track title
            artist: Artist name

        Returns:
            Track object with platform ID if found, None otherwise
        """
        pass

    @abstractmethod
    def get_track(self, platform_id: str) -> Optional[Track]:
        """
        Get track details by platform-specific ID

        Args:
            platform_id: Platform-specific track ID

        Returns:
            Track object if found, None otherwise
        """
        pass

    @abstractmethod
    def create_playlist(self, playlist: Playlist) -> Optional[str]:
        """
        Create a playlist on the platform

        Args:
            playlist: Playlist to create

        Returns:
            Platform-specific playlist ID if successful, None otherwise
        """
        pass

    @abstractmethod
    def update_playlist(self, playlist: Playlist) -> bool:
        """
        Update an existing playlist on the platform

        Args:
            playlist: Playlist with updated data

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def delete_playlist(self, platform_id: str) -> bool:
        """
        Delete a playlist from the platform

        Args:
            platform_id: Platform-specific playlist ID

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_playlist(self, platform_id: str) -> Optional[Playlist]:
        """
        Get playlist from the platform

        Args:
            platform_id: Platform-specific playlist ID

        Returns:
            Playlist object if found, None otherwise
        """
        pass

    @abstractmethod
    def get_user_playlists(self) -> List[Playlist]:
        """
        Get all playlists for the authenticated user

        Returns:
            List of playlists
        """
        pass

    @abstractmethod
    def add_tracks_to_playlist(self, platform_playlist_id: str, track_ids: List[str]) -> bool:
        """
        Add tracks to a playlist on the platform

        Args:
            platform_playlist_id: Platform-specific playlist ID
            track_ids: List of platform-specific track IDs

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def remove_tracks_from_playlist(self, platform_playlist_id: str, track_ids: List[str]) -> bool:
        """
        Remove tracks from a playlist on the platform

        Args:
            platform_playlist_id: Platform-specific playlist ID
            track_ids: List of platform-specific track IDs to remove

        Returns:
            True if successful, False otherwise
        """
        pass

    def sync_playlist_to_platform(self, playlist: Playlist) -> bool:
        """
        Sync a local playlist to the platform

        Args:
            playlist: Playlist to sync

        Returns:
            True if successful, False otherwise
        """
        platform_id = playlist.get_platform_id(self.platform_name)

        if platform_id:
            # Update existing playlist
            return self.update_playlist(playlist)
        else:
            # Create new playlist
            new_id = self.create_playlist(playlist)
            if new_id:
                playlist.add_platform_id(self.platform_name, new_id)
                return True
        return False

    def sync_playlist_from_platform(self, platform_id: str) -> Optional[Playlist]:
        """
        Sync a playlist from the platform to local format

        Args:
            platform_id: Platform-specific playlist ID

        Returns:
            Playlist object if successful, None otherwise
        """
        playlist = self.get_playlist(platform_id)
        if playlist:
            playlist.add_platform_id(self.platform_name, platform_id)
        return playlist
