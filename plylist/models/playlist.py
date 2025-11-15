"""Playlist model representing a collection of tracks"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid

from .track import Track


@dataclass
class Playlist:
    """
    Represents a playlist in a platform-agnostic way.

    Attributes:
        name: Playlist name
        description: Optional playlist description
        tracks: List of tracks in the playlist
        playlist_id: Unique identifier for this playlist
        created_at: Timestamp when playlist was created
        updated_at: Timestamp when playlist was last updated
        platform_ids: Dictionary mapping platform names to
            platform-specific IDs
        metadata: Additional platform-specific metadata
        tags: List of tags for categorization
    """

    name: str
    description: Optional[str] = None
    tracks: List[Track] = field(default_factory=list)
    playlist_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    platform_ids: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        """String representation of the playlist"""
        track_count = len(self.tracks)
        track_word = "track" if track_count == 1 else "tracks"
        return f"{self.name} ({track_count} {track_word})"

    def __len__(self) -> int:
        """Return number of tracks in playlist"""
        return len(self.tracks)

    def add_track(self, track: Track) -> None:
        """
        Add a track to the playlist

        Args:
            track: Track to add
        """
        self.tracks.append(track)
        self._update_timestamp()

    def remove_track(self, track_id: str) -> bool:
        """
        Remove a track from the playlist by ID

        Args:
            track_id: ID of the track to remove

        Returns:
            True if track was removed, False if not found
        """
        initial_length = len(self.tracks)
        self.tracks = [t for t in self.tracks if t.track_id != track_id]
        if len(self.tracks) < initial_length:
            self._update_timestamp()
            return True
        return False

    def remove_track_at_index(self, index: int) -> Optional[Track]:
        """
        Remove a track at a specific index

        Args:
            index: Index of the track to remove

        Returns:
            The removed track or None if index is invalid
        """
        if 0 <= index < len(self.tracks):
            track = self.tracks.pop(index)
            self._update_timestamp()
            return track
        return None

    def get_track(self, track_id: str) -> Optional[Track]:
        """
        Get a track by ID

        Args:
            track_id: ID of the track to retrieve

        Returns:
            Track if found, None otherwise
        """
        for track in self.tracks:
            if track.track_id == track_id:
                return track
        return None

    def move_track(self, from_index: int, to_index: int) -> bool:
        """
        Move a track from one position to another

        Args:
            from_index: Current index of the track
            to_index: Target index for the track

        Returns:
            True if track was moved, False if indices are invalid
        """
        if (
            0 <= from_index < len(self.tracks)
            and 0 <= to_index < len(self.tracks)
        ):
            track = self.tracks.pop(from_index)
            self.tracks.insert(to_index, track)
            self._update_timestamp()
            return True
        return False

    def clear(self) -> None:
        """Remove all tracks from the playlist"""
        self.tracks.clear()
        self._update_timestamp()

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def add_platform_id(self, platform: str, platform_id: str) -> None:
        """
        Add a platform-specific ID for this playlist

        Args:
            platform: Platform name (e.g., 'spotify', 'apple_music')
            platform_id: The platform-specific playlist ID
        """
        self.platform_ids[platform] = platform_id
        self._update_timestamp()

    def get_platform_id(self, platform: str) -> Optional[str]:
        """
        Get the platform-specific ID for this playlist

        Args:
            platform: Platform name

        Returns:
            Platform-specific ID or None if not found
        """
        return self.platform_ids.get(platform)

    def add_tag(self, tag: str) -> None:
        """Add a tag to the playlist"""
        if tag not in self.tags:
            self.tags.append(tag)
            self._update_timestamp()

    def remove_tag(self, tag: str) -> bool:
        """
        Remove a tag from the playlist

        Returns:
            True if tag was removed, False if not found
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self._update_timestamp()
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert playlist to dictionary"""
        data = asdict(self)
        # Convert track objects to dictionaries
        data["tracks"] = [track.to_dict() for track in self.tracks]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Playlist":
        """Create playlist from dictionary"""
        # Convert track dictionaries back to Track objects
        track_dicts = data.pop("tracks", [])
        tracks = [Track.from_dict(t) for t in track_dicts]
        playlist = cls(**data)
        playlist.tracks = tracks
        return playlist

    def get_duration_ms(self) -> int:
        """
        Calculate total playlist duration in milliseconds

        Returns:
            Total duration or 0 if track durations are not available
        """
        return sum(track.duration_ms or 0 for track in self.tracks)

    def get_duration_str(self) -> str:
        """
        Get human-readable duration string

        Returns:
            Duration string like "1h 23m 45s"
        """
        total_ms = self.get_duration_ms()
        if total_ms == 0:
            return "Unknown"

        total_seconds = total_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts)
