"""
Plylist - A platform-agnostic playlist manager

Manage your music playlists across different streaming platforms
without being locked into any specific service.
"""

__version__ = "0.1.0"
__author__ = "Plylist Contributors"

from .models.track import Track
from .models.playlist import Playlist
from .manager import PlaylistManager
from .platforms.apple_music import AppleMusicPlatform

__all__ = ["Track", "Playlist", "PlaylistManager", "AppleMusicPlatform"]
