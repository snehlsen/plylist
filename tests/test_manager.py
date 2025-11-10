"""Tests for PlaylistManager"""

import unittest
import tempfile
import shutil
from pathlib import Path
from plylist.manager import PlaylistManager
from plylist.storage.json_storage import JSONStorage
from plylist.models.track import Track


class TestPlaylistManager(unittest.TestCase):
    """Test PlaylistManager"""

    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test storage
        self.test_dir = tempfile.mkdtemp()
        self.storage = JSONStorage(storage_dir=self.test_dir)
        self.manager = PlaylistManager(storage=self.storage)

    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_create_playlist(self):
        """Test creating a playlist"""
        playlist = self.manager.create_playlist(
            name="Test Playlist",
            description="A test",
            tags=["test"],
        )

        self.assertIsNotNone(playlist)
        self.assertEqual(playlist.name, "Test Playlist")
        self.assertEqual(playlist.description, "A test")
        self.assertEqual(playlist.tags, ["test"])

    def test_get_playlist(self):
        """Test retrieving a playlist"""
        created = self.manager.create_playlist(name="Test")
        retrieved = self.manager.get_playlist(created.playlist_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.playlist_id, created.playlist_id)
        self.assertEqual(retrieved.name, "Test")

    def test_get_nonexistent_playlist(self):
        """Test retrieving a non-existent playlist"""
        playlist = self.manager.get_playlist("nonexistent-id")
        self.assertIsNone(playlist)

    def test_delete_playlist(self):
        """Test deleting a playlist"""
        playlist = self.manager.create_playlist(name="Test")
        result = self.manager.delete_playlist(playlist.playlist_id)

        self.assertTrue(result)

        # Verify it's gone
        retrieved = self.manager.get_playlist(playlist.playlist_id)
        self.assertIsNone(retrieved)

    def test_list_playlists(self):
        """Test listing playlists"""
        self.manager.create_playlist(name="Playlist 1")
        self.manager.create_playlist(name="Playlist 2")
        self.manager.create_playlist(name="Playlist 3")

        playlists = self.manager.list_playlists()
        self.assertEqual(len(playlists), 3)

    def test_list_playlists_with_search(self):
        """Test listing playlists with search"""
        self.manager.create_playlist(name="Rock Mix")
        self.manager.create_playlist(name="Pop Mix")
        self.manager.create_playlist(name="Rock Classics")

        playlists = self.manager.list_playlists(query="rock")
        self.assertEqual(len(playlists), 2)

    def test_list_playlists_with_tags(self):
        """Test listing playlists filtered by tags"""
        self.manager.create_playlist(name="Playlist 1", tags=["workout"])
        self.manager.create_playlist(name="Playlist 2", tags=["chill"])
        self.manager.create_playlist(name="Playlist 3", tags=["workout", "energetic"])

        playlists = self.manager.list_playlists(tags=["workout"])
        self.assertEqual(len(playlists), 2)

    def test_add_track_to_playlist(self):
        """Test adding a track to a playlist"""
        playlist = self.manager.create_playlist(name="Test")
        track = Track(title="Song", artist="Artist")

        result = self.manager.add_track_to_playlist(playlist.playlist_id, track)
        self.assertTrue(result)

        # Verify track was added
        updated = self.manager.get_playlist(playlist.playlist_id)
        self.assertEqual(len(updated.tracks), 1)
        self.assertEqual(updated.tracks[0].title, "Song")

    def test_remove_track_from_playlist(self):
        """Test removing a track from a playlist"""
        playlist = self.manager.create_playlist(name="Test")
        track = Track(title="Song", artist="Artist")
        self.manager.add_track_to_playlist(playlist.playlist_id, track)

        result = self.manager.remove_track_from_playlist(playlist.playlist_id, track.track_id)
        self.assertTrue(result)

        # Verify track was removed
        updated = self.manager.get_playlist(playlist.playlist_id)
        self.assertEqual(len(updated.tracks), 0)

    def test_rename_playlist(self):
        """Test renaming a playlist"""
        playlist = self.manager.create_playlist(name="Old Name")
        result = self.manager.rename_playlist(playlist.playlist_id, "New Name")

        self.assertTrue(result)

        # Verify rename
        updated = self.manager.get_playlist(playlist.playlist_id)
        self.assertEqual(updated.name, "New Name")

    def test_duplicate_playlist(self):
        """Test duplicating a playlist"""
        original = self.manager.create_playlist(name="Original")
        track = Track(title="Song", artist="Artist")
        self.manager.add_track_to_playlist(original.playlist_id, track)

        duplicate = self.manager.duplicate_playlist(original.playlist_id, "Copy")

        self.assertIsNotNone(duplicate)
        self.assertEqual(duplicate.name, "Copy")
        self.assertEqual(len(duplicate.tracks), 1)
        self.assertNotEqual(duplicate.playlist_id, original.playlist_id)

    def test_merge_playlists(self):
        """Test merging playlists"""
        playlist1 = self.manager.create_playlist(name="Playlist 1")
        playlist2 = self.manager.create_playlist(name="Playlist 2")

        track1 = Track(title="Song 1", artist="Artist")
        track2 = Track(title="Song 2", artist="Artist")

        self.manager.add_track_to_playlist(playlist1.playlist_id, track1)
        self.manager.add_track_to_playlist(playlist2.playlist_id, track2)

        merged = self.manager.merge_playlists(
            [playlist1.playlist_id, playlist2.playlist_id],
            "Merged Playlist",
        )

        self.assertIsNotNone(merged)
        self.assertEqual(merged.name, "Merged Playlist")
        self.assertEqual(len(merged.tracks), 2)

    def test_merge_playlists_remove_duplicates(self):
        """Test merging playlists with duplicate removal"""
        playlist1 = self.manager.create_playlist(name="Playlist 1")
        playlist2 = self.manager.create_playlist(name="Playlist 2")

        # Add the same track to both playlists
        track = Track(title="Song", artist="Artist")
        self.manager.add_track_to_playlist(playlist1.playlist_id, track)

        # Add a track with same title/artist to second playlist
        duplicate_track = Track(title="Song", artist="Artist")
        self.manager.add_track_to_playlist(playlist2.playlist_id, duplicate_track)

        merged = self.manager.merge_playlists(
            [playlist1.playlist_id, playlist2.playlist_id],
            "Merged",
            remove_duplicates=True,
        )

        # Should only have 1 track after deduplication
        self.assertEqual(len(merged.tracks), 1)

    def test_get_stats(self):
        """Test getting statistics"""
        self.manager.create_playlist(name="Playlist 1")
        playlist2 = self.manager.create_playlist(name="Playlist 2")

        track = Track(title="Song", artist="Artist")
        self.manager.add_track_to_playlist(playlist2.playlist_id, track)

        stats = self.manager.get_stats()

        self.assertEqual(stats["total_playlists"], 2)
        self.assertEqual(stats["total_tracks"], 1)


if __name__ == "__main__":
    unittest.main()
