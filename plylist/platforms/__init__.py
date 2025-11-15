"""Platform abstractions for different streaming services"""

from .base import PlatformBase
from .apple_music import AppleMusicPlatform

__all__ = ["PlatformBase", "AppleMusicPlatform"]
