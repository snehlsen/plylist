"""Integration tests for Plylist

These tests verify end-to-end functionality of the playlist manager,
including CLI commands and Python API calls as documented in the README.
"""

import unittest
import tempfile
import shutil
import subprocess
import json
from pathlib import Path
from plylist import PlaylistManager, Track, Playlist
from plylist.storage.json_storage import JSONStorage


class TestIntegrationAPI(unittest.TestCase):
    """Integration tests for Python API"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.storage = JSONStorage(storage_dir=self.test_dir)
        self.manager = PlaylistManager(storage=self.storage)

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)

    def test_readme_example_workflow(self):
        """Test the example workflow from README"""
        # Create a playlist (as shown in README)
        playlist = self.manager.create_playlist(
            name="Workout Mix",
            description="High energy music",
            tags=["workout", "energetic"]
        )

        self.assertIsNotNone(playlist)
        self.assertEqual(playlist.name, "Workout Mix")
        self.assertEqual(playlist.description, "High energy music")
        self.assertIn("workout", playlist.tags)
        self.assertIn("energetic", playlist.tags)

        # Add tracks (as shown in README)
        track = Track(
            title="Eye of the Tiger",
            artist="Survivor",
            album="Eye of the Tiger",
            duration_ms=246000
        )
        result = self.manager.add_track_to_playlist(playlist.playlist_id, track)
        self.assertTrue(result)

        # Get playlist and verify track was added
        retrieved_playlist = self.manager.get_playlist(playlist.playlist_id)
        self.assertIsNotNone(retrieved_playlist)
        self.assertEqual(len(retrieved_playlist.tracks), 1)
        self.assertEqual(retrieved_playlist.tracks[0].title, "Eye of the Tiger")
        self.assertEqual(retrieved_playlist.tracks[0].artist, "Survivor")

    def test_add_track_to_empty_playlist(self):
        """Test adding a track to an empty playlist - the main bug fix"""
        # Create an empty playlist
        playlist = self.manager.create_playlist(name="Empty Playlist")
        self.assertEqual(len(playlist.tracks), 0)

        # This should work even though the playlist is empty
        track = Track(title="Test Song", artist="Test Artist")
        result = self.manager.add_track_to_playlist(playlist.playlist_id, track)

        # Verify the operation succeeded
        self.assertTrue(result, "Adding track to empty playlist should succeed")

        # Verify the track was actually added
        updated_playlist = self.manager.get_playlist(playlist.playlist_id)
        self.assertIsNotNone(updated_playlist)
        self.assertEqual(len(updated_playlist.tracks), 1)
        self.assertEqual(updated_playlist.tracks[0].title, "Test Song")

    def test_add_multiple_tracks_to_empty_playlist(self):
        """Test adding multiple tracks to an initially empty playlist"""
        playlist = self.manager.create_playlist(name="Test Playlist")

        # Add first track to empty playlist
        track1 = Track(title="Song 1", artist="Artist 1")
        result1 = self.manager.add_track_to_playlist(playlist.playlist_id, track1)
        self.assertTrue(result1)

        # Add second track to playlist that now has one track
        track2 = Track(title="Song 2", artist="Artist 2")
        result2 = self.manager.add_track_to_playlist(playlist.playlist_id, track2)
        self.assertTrue(result2)

        # Add third track
        track3 = Track(title="Song 3", artist="Artist 3")
        result3 = self.manager.add_track_to_playlist(playlist.playlist_id, track3)
        self.assertTrue(result3)

        # Verify all tracks were added
        final_playlist = self.manager.get_playlist(playlist.playlist_id)
        self.assertEqual(len(final_playlist.tracks), 3)
        self.assertEqual(final_playlist.tracks[0].title, "Song 1")
        self.assertEqual(final_playlist.tracks[1].title, "Song 2")
        self.assertEqual(final_playlist.tracks[2].title, "Song 3")

    def test_operations_on_empty_playlist(self):
        """Test various operations on empty playlists work correctly"""
        empty_playlist = self.manager.create_playlist(name="Empty")

        # Get empty playlist should work
        retrieved = self.manager.get_playlist(empty_playlist.playlist_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved.tracks), 0)

        # Rename empty playlist should work
        result = self.manager.rename_playlist(empty_playlist.playlist_id, "Renamed Empty")
        self.assertTrue(result)
        renamed = self.manager.get_playlist(empty_playlist.playlist_id)
        self.assertEqual(renamed.name, "Renamed Empty")

        # Add tags to empty playlist should work
        result = self.manager.add_tags_to_playlist(empty_playlist.playlist_id, ["tag1", "tag2"])
        self.assertTrue(result)
        tagged = self.manager.get_playlist(empty_playlist.playlist_id)
        self.assertIn("tag1", tagged.tags)
        self.assertIn("tag2", tagged.tags)

        # Duplicate empty playlist should work
        duplicate = self.manager.duplicate_playlist(empty_playlist.playlist_id, "Duplicate")
        self.assertIsNotNone(duplicate)
        self.assertEqual(duplicate.name, "Duplicate")
        self.assertEqual(len(duplicate.tracks), 0)

    def test_export_empty_playlist(self):
        """Test exporting an empty playlist"""
        playlist = self.manager.create_playlist(name="Export Test")

        # Export to JSON
        export_path = Path(self.test_dir) / "export_test.json"
        result = self.manager.export_playlist(
            playlist.playlist_id,
            str(export_path),
            format="json"
        )
        self.assertTrue(result)
        self.assertTrue(export_path.exists())

        # Verify exported content
        with open(export_path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['name'], "Export Test")
            self.assertEqual(data['tracks'], [])


class TestIntegrationCLI(unittest.TestCase):
    """Integration tests for CLI commands"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.storage_dir = Path(self.test_dir) / "playlists"
        self.storage_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)

    def run_cli(self, *args):
        """Helper to run CLI commands"""
        env = {"HOME": self.test_dir}
        result = subprocess.run(
            ["python", "-m", "plylist"] + list(args),
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, **env}
        )
        return result

    def test_cli_create_and_add_track(self):
        """Test creating a playlist and adding a track via CLI"""
        # Create playlist
        result = self.run_cli("create", "Test Playlist", "-d", "Testing", "-t", "test,cli")
        self.assertEqual(result.returncode, 0, f"Create failed: {result.stderr}")
        self.assertIn("Created playlist", result.stdout)

        # Extract playlist ID from output
        lines = result.stdout.strip().split('\n')
        playlist_id = None
        for line in lines:
            if line.startswith("Playlist ID:"):
                playlist_id = line.split(":")[1].strip()
                break

        self.assertIsNotNone(playlist_id, "Could not find playlist ID in output")

        # Add track to the (initially empty) playlist
        result = self.run_cli(
            "add-track",
            playlist_id,
            "Test Song",
            "Test Artist",
            "-a", "Test Album"
        )
        self.assertEqual(result.returncode, 0, f"Add track failed: {result.stderr}")
        self.assertIn("Added track", result.stdout)

        # Verify track was added by showing the playlist
        result = self.run_cli("show", playlist_id)
        self.assertEqual(result.returncode, 0, f"Show failed: {result.stderr}")
        self.assertIn("Test Song", result.stdout)
        self.assertIn("Test Artist", result.stdout)
        self.assertIn("Tracks: 1", result.stdout)

    def test_cli_add_multiple_tracks(self):
        """Test adding multiple tracks to empty playlist via CLI"""
        # Create empty playlist
        result = self.run_cli("create", "Multi Track Test")
        self.assertEqual(result.returncode, 0)

        # Extract playlist ID
        playlist_id = None
        for line in result.stdout.strip().split('\n'):
            if line.startswith("Playlist ID:"):
                playlist_id = line.split(":")[1].strip()
                break

        self.assertIsNotNone(playlist_id)

        # Add first track
        result = self.run_cli("add-track", playlist_id, "Song 1", "Artist 1")
        self.assertEqual(result.returncode, 0)

        # Add second track
        result = self.run_cli("add-track", playlist_id, "Song 2", "Artist 2")
        self.assertEqual(result.returncode, 0)

        # Add third track
        result = self.run_cli("add-track", playlist_id, "Song 3", "Artist 3")
        self.assertEqual(result.returncode, 0)

        # Verify all tracks
        result = self.run_cli("show", playlist_id)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Tracks: 3", result.stdout)
        self.assertIn("Song 1", result.stdout)
        self.assertIn("Song 2", result.stdout)
        self.assertIn("Song 3", result.stdout)

    def test_cli_show_empty_playlist(self):
        """Test showing details of an empty playlist via CLI"""
        # Create empty playlist
        result = self.run_cli("create", "Empty Playlist")
        self.assertEqual(result.returncode, 0)

        # Extract playlist ID
        playlist_id = None
        for line in result.stdout.strip().split('\n'):
            if line.startswith("Playlist ID:"):
                playlist_id = line.split(":")[1].strip()
                break

        # Show should work for empty playlist
        result = self.run_cli("show", playlist_id)
        self.assertEqual(result.returncode, 0, "Show command should work for empty playlist")
        self.assertIn("Empty Playlist", result.stdout)
        self.assertIn("Tracks: 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
