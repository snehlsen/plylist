"""Tests for PlaylistManager"""

import pytest
import tempfile
import shutil
from pathlib import Path
from plylist.manager import PlaylistManager
from plylist.storage.json_storage import JSONStorage
from plylist.models.track import Track


@pytest.fixture
def manager():
    """Fixture to create a PlaylistManager with temporary storage"""
    # Create a temporary directory for test storage
    test_dir = tempfile.mkdtemp()
    storage = JSONStorage(storage_dir=test_dir)
    manager_instance = PlaylistManager(storage=storage)

    yield manager_instance

    # Clean up test environment
    shutil.rmtree(test_dir)


class TestPlaylistManager:
    """Test PlaylistManager"""

    def test_create_playlist(self, manager):
        """Test creating a playlist"""
        playlist = manager.create_playlist(
            name="Test Playlist",
            description="A test",
            tags=["test"],
        )

        assert playlist is not None
        assert playlist.name == "Test Playlist"
        assert playlist.description == "A test"
        assert playlist.tags == ["test"]

    def test_get_playlist(self, manager):
        """Test retrieving a playlist"""
        created = manager.create_playlist(name="Test")
        retrieved = manager.get_playlist(created.playlist_id)

        assert retrieved is not None
        assert retrieved.playlist_id == created.playlist_id
        assert retrieved.name == "Test"

    def test_get_nonexistent_playlist(self, manager):
        """Test retrieving a non-existent playlist"""
        playlist = manager.get_playlist("nonexistent-id")
        assert playlist is None

    def test_delete_playlist(self, manager):
        """Test deleting a playlist"""
        playlist = manager.create_playlist(name="Test")
        result = manager.delete_playlist(playlist.playlist_id)

        assert result is True

        # Verify it's gone
        retrieved = manager.get_playlist(playlist.playlist_id)
        assert retrieved is None

    def test_list_playlists(self, manager):
        """Test listing playlists"""
        manager.create_playlist(name="Playlist 1")
        manager.create_playlist(name="Playlist 2")
        manager.create_playlist(name="Playlist 3")

        playlists = manager.list_playlists()
        assert len(playlists) == 3

    def test_list_playlists_with_search(self, manager):
        """Test listing playlists with search"""
        manager.create_playlist(name="Rock Mix")
        manager.create_playlist(name="Pop Mix")
        manager.create_playlist(name="Rock Classics")

        playlists = manager.list_playlists(query="rock")
        assert len(playlists) == 2

    def test_list_playlists_with_tags(self, manager):
        """Test listing playlists filtered by tags"""
        manager.create_playlist(name="Playlist 1", tags=["workout"])
        manager.create_playlist(name="Playlist 2", tags=["chill"])
        manager.create_playlist(name="Playlist 3", tags=["workout", "energetic"])

        playlists = manager.list_playlists(tags=["workout"])
        assert len(playlists) == 2

    def test_add_track_to_playlist(self, manager):
        """Test adding a track to a playlist"""
        playlist = manager.create_playlist(name="Test")
        track = Track(title="Song", artist="Artist")

        result = manager.add_track_to_playlist(playlist.playlist_id, track)
        assert result is True

        # Verify track was added
        updated = manager.get_playlist(playlist.playlist_id)
        assert len(updated.tracks) == 1
        assert updated.tracks[0].title == "Song"

    def test_remove_track_from_playlist(self, manager):
        """Test removing a track from a playlist"""
        playlist = manager.create_playlist(name="Test")
        track = Track(title="Song", artist="Artist")
        manager.add_track_to_playlist(playlist.playlist_id, track)

        result = manager.remove_track_from_playlist(playlist.playlist_id, track.track_id)
        assert result is True

        # Verify track was removed
        updated = manager.get_playlist(playlist.playlist_id)
        assert len(updated.tracks) == 0

    def test_rename_playlist(self, manager):
        """Test renaming a playlist"""
        playlist = manager.create_playlist(name="Old Name")
        result = manager.rename_playlist(playlist.playlist_id, "New Name")

        assert result is True

        # Verify rename
        updated = manager.get_playlist(playlist.playlist_id)
        assert updated.name == "New Name"

    def test_duplicate_playlist(self, manager):
        """Test duplicating a playlist"""
        original = manager.create_playlist(name="Original")
        track = Track(title="Song", artist="Artist")
        manager.add_track_to_playlist(original.playlist_id, track)

        duplicate = manager.duplicate_playlist(original.playlist_id, "Copy")

        assert duplicate is not None
        assert duplicate.name == "Copy"
        assert len(duplicate.tracks) == 1
        assert duplicate.playlist_id != original.playlist_id

    def test_merge_playlists(self, manager):
        """Test merging playlists"""
        playlist1 = manager.create_playlist(name="Playlist 1")
        playlist2 = manager.create_playlist(name="Playlist 2")

        track1 = Track(title="Song 1", artist="Artist")
        track2 = Track(title="Song 2", artist="Artist")

        manager.add_track_to_playlist(playlist1.playlist_id, track1)
        manager.add_track_to_playlist(playlist2.playlist_id, track2)

        merged = manager.merge_playlists(
            [playlist1.playlist_id, playlist2.playlist_id],
            "Merged Playlist",
        )

        assert merged is not None
        assert merged.name == "Merged Playlist"
        assert len(merged.tracks) == 2

    def test_merge_playlists_remove_duplicates(self, manager):
        """Test merging playlists with duplicate removal"""
        playlist1 = manager.create_playlist(name="Playlist 1")
        playlist2 = manager.create_playlist(name="Playlist 2")

        # Add the same track to both playlists
        track = Track(title="Song", artist="Artist")
        manager.add_track_to_playlist(playlist1.playlist_id, track)

        # Add a track with same title/artist to second playlist
        duplicate_track = Track(title="Song", artist="Artist")
        manager.add_track_to_playlist(playlist2.playlist_id, duplicate_track)

        merged = manager.merge_playlists(
            [playlist1.playlist_id, playlist2.playlist_id],
            "Merged",
            remove_duplicates=True,
        )

        # Should only have 1 track after deduplication
        assert len(merged.tracks) == 1

    def test_get_stats(self, manager):
        """Test getting statistics"""
        manager.create_playlist(name="Playlist 1")
        playlist2 = manager.create_playlist(name="Playlist 2")

        track = Track(title="Song", artist="Artist")
        manager.add_track_to_playlist(playlist2.playlist_id, track)

        stats = manager.get_stats()

        assert stats["total_playlists"] == 2
        assert stats["total_tracks"] == 1
