"""Tests for Plylist data models"""

from plylist.models.track import Track
from plylist.models.playlist import Playlist


class TestTrack:
    """Test Track model"""

    def test_track_creation(self):
        """Test creating a track"""
        track = Track(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration_ms=180000,
        )
        assert track.title == "Test Song"
        assert track.artist == "Test Artist"
        assert track.album == "Test Album"
        assert track.duration_ms == 180000
        assert track.track_id is not None

    def test_track_to_dict(self):
        """Test track serialization"""
        track = Track(title="Song", artist="Artist")
        data = track.to_dict()
        assert isinstance(data, dict)
        assert data["title"] == "Song"
        assert data["artist"] == "Artist"

    def test_track_from_dict(self):
        """Test track deserialization"""
        data = {
            "title": "Song",
            "artist": "Artist",
            "album": None,
            "duration_ms": None,
            "isrc": None,
            "platform_ids": {},
            "track_id": "test-id",
            "added_at": "2025-01-01T00:00:00",
            "additional_artists": [],
            "metadata": {},
        }
        track = Track.from_dict(data)
        assert track.title == "Song"
        assert track.artist == "Artist"
        assert track.track_id == "test-id"

    def test_track_platform_ids(self):
        """Test adding and getting platform IDs"""
        track = Track(title="Song", artist="Artist")
        track.add_platform_id("spotify", "spotify-123")
        track.add_platform_id("apple_music", "am-456")

        assert track.get_platform_id("spotify") == "spotify-123"
        assert track.get_platform_id("apple_music") == "am-456"
        assert track.get_platform_id("youtube") is None

    def test_track_matches(self):
        """Test track matching"""
        track1 = Track(title="Song", artist="Artist")
        track2 = Track(title="Song", artist="Artist")
        track3 = Track(title="Different", artist="Artist")

        assert track1.matches(track2) is True
        assert track1.matches(track3) is False

    def test_track_matches_with_isrc(self):
        """Test track matching using ISRC"""
        track1 = Track(title="Song", artist="Artist", isrc="US123")
        track2 = Track(
            title="Different Title", artist="Different Artist", isrc="US123"
        )
        track3 = Track(title="Song", artist="Artist", isrc="US456")

        # Same ISRC should match even with different title/artist
        assert track1.matches(track2) is True
        # Different ISRC should not match
        assert track1.matches(track3) is False


class TestPlaylist:
    """Test Playlist model"""

    def test_playlist_creation(self):
        """Test creating a playlist"""
        playlist = Playlist(
            name="Test Playlist",
            description="A test playlist",
            tags=["test", "demo"],
        )
        assert playlist.name == "Test Playlist"
        assert playlist.description == "A test playlist"
        assert playlist.tags == ["test", "demo"]
        assert len(playlist.tracks) == 0
        assert playlist.playlist_id is not None

    def test_add_track(self):
        """Test adding tracks to playlist"""
        playlist = Playlist(name="Test")
        track1 = Track(title="Song 1", artist="Artist 1")
        track2 = Track(title="Song 2", artist="Artist 2")

        playlist.add_track(track1)
        playlist.add_track(track2)

        assert len(playlist.tracks) == 2
        assert playlist.tracks[0].title == "Song 1"
        assert playlist.tracks[1].title == "Song 2"

    def test_remove_track(self):
        """Test removing tracks from playlist"""
        playlist = Playlist(name="Test")
        track = Track(title="Song", artist="Artist")
        playlist.add_track(track)

        assert len(playlist.tracks) == 1
        result = playlist.remove_track(track.track_id)

        assert result is True
        assert len(playlist.tracks) == 0

    def test_remove_track_not_found(self):
        """Test removing non-existent track"""
        playlist = Playlist(name="Test")
        result = playlist.remove_track("non-existent-id")
        assert result is False

    def test_move_track(self):
        """Test moving tracks in playlist"""
        playlist = Playlist(name="Test")
        track1 = Track(title="Song 1", artist="Artist")
        track2 = Track(title="Song 2", artist="Artist")
        track3 = Track(title="Song 3", artist="Artist")

        playlist.add_track(track1)
        playlist.add_track(track2)
        playlist.add_track(track3)

        # Move track from index 0 to index 2
        result = playlist.move_track(0, 2)

        assert result is True
        assert playlist.tracks[0].title == "Song 2"
        assert playlist.tracks[1].title == "Song 3"
        assert playlist.tracks[2].title == "Song 1"

    def test_get_duration(self):
        """Test calculating playlist duration"""
        playlist = Playlist(name="Test")
        track1 = Track(title="Song 1", artist="Artist", duration_ms=180000)
        track2 = Track(title="Song 2", artist="Artist", duration_ms=240000)

        playlist.add_track(track1)
        playlist.add_track(track2)

        assert playlist.get_duration_ms() == 420000

    def test_to_dict_and_from_dict(self):
        """Test playlist serialization and deserialization"""
        playlist = Playlist(name="Test", description="Description")
        track = Track(title="Song", artist="Artist")
        playlist.add_track(track)

        # Serialize
        data = playlist.to_dict()
        assert isinstance(data, dict)
        assert data["name"] == "Test"
        assert len(data["tracks"]) == 1

        # Deserialize
        restored = Playlist.from_dict(data)
        assert restored.name == "Test"
        assert restored.description == "Description"
        assert len(restored.tracks) == 1
        assert restored.tracks[0].title == "Song"

    def test_tags(self):
        """Test playlist tags"""
        playlist = Playlist(name="Test")

        playlist.add_tag("rock")
        playlist.add_tag("classic")

        assert "rock" in playlist.tags
        assert "classic" in playlist.tags

        result = playlist.remove_tag("rock")
        assert result is True
        assert "rock" not in playlist.tags

        # Try removing non-existent tag
        result = playlist.remove_tag("pop")
        assert result is False
