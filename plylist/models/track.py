"""Track model representing a music track"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


@dataclass
class Track:
    """
    Represents a music track in a platform-agnostic way.

    Attributes:
        title: The track title
        artist: Primary artist name
        album: Album name (optional)
        duration_ms: Duration in milliseconds (optional)
        isrc: International Standard Recording Code (optional)
        platform_ids: Dictionary mapping platform names to
            platform-specific IDs
        track_id: Unique identifier for this track
        added_at: Timestamp when track was added
        additional_artists: List of additional artists/collaborators
        metadata: Additional platform-specific metadata
    """

    title: str
    artist: str
    album: Optional[str] = None
    duration_ms: Optional[int] = None
    isrc: Optional[str] = None
    platform_ids: Dict[str, str] = field(default_factory=dict)
    track_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    added_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    additional_artists: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation of the track"""
        artists = [self.artist] + self.additional_artists
        artist_str = ", ".join(artists)
        if self.album:
            return f"{self.title} by {artist_str} (from {self.album})"
        return f"{self.title} by {artist_str}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert track to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Track":
        """Create track from dictionary"""
        return cls(**data)

    def add_platform_id(self, platform: str, platform_id: str) -> None:
        """
        Add a platform-specific ID for this track

        Args:
            platform: Platform name (e.g., 'spotify', 'apple_music')
            platform_id: The platform-specific track ID
        """
        self.platform_ids[platform] = platform_id

    def get_platform_id(self, platform: str) -> Optional[str]:
        """
        Get the platform-specific ID for this track

        Args:
            platform: Platform name

        Returns:
            Platform-specific ID or None if not found
        """
        return self.platform_ids.get(platform)

    def matches(self, other: "Track", strict: bool = False) -> bool:
        """
        Check if this track matches another track

        Args:
            other: Another track to compare with
            strict: If True, requires exact title/artist match

        Returns:
            True if tracks are considered a match
        """
        # If both have ISRC, use that for matching
        if self.isrc and other.isrc:
            return self.isrc == other.isrc

        # Normalize strings for comparison
        title_match = (
            self.title.lower().strip() == other.title.lower().strip()
        )
        artist_match = (
            self.artist.lower().strip() == other.artist.lower().strip()
        )

        if strict:
            return title_match and artist_match

        # Fuzzy matching: check if main components match
        return title_match and artist_match
