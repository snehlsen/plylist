"""Integration tests for Plylist

These tests verify end-to-end functionality of the playlist manager,
including CLI commands and Python API calls as documented in the README.
"""

import pytest
import tempfile
import shutil
import subprocess
import json
from pathlib import Path
from plylist import PlaylistManager, Track
from plylist.storage.json_storage import JSONStorage


@pytest.fixture
def api_setup():
    """Fixture for API integration tests"""
    test_dir = tempfile.mkdtemp()
    storage = JSONStorage(storage_dir=test_dir)
    manager = PlaylistManager(storage=storage)

    yield manager

    shutil.rmtree(test_dir)


@pytest.fixture
def cli_setup():
    """Fixture for CLI integration tests"""
    test_dir = tempfile.mkdtemp()
    storage_dir = Path(test_dir) / "playlists"
    storage_dir.mkdir(parents=True)

    def run_cli(*args):
        """Helper to run CLI commands"""
        env = {"HOME": test_dir}
        result = subprocess.run(
            ["python", "-m", "plylist"] + list(args),
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, **env}
        )
        return result

    yield run_cli

    shutil.rmtree(test_dir)


class TestIntegrationAPI:
    """Integration tests for Python API"""

    def test_readme_example_workflow(self, api_setup):
        """Test the example workflow from README"""
        manager = api_setup

        # Create a playlist (as shown in README)
        playlist = manager.create_playlist(
            name="Workout Mix",
            description="High energy music",
            tags=["workout", "energetic"]
        )

        assert playlist is not None
        assert playlist.name == "Workout Mix"
        assert playlist.description == "High energy music"
        assert "workout" in playlist.tags
        assert "energetic" in playlist.tags

        # Add tracks (as shown in README)
        track = Track(
            title="Eye of the Tiger",
            artist="Survivor",
            album="Eye of the Tiger",
            duration_ms=246000
        )
        result = manager.add_track_to_playlist(playlist.playlist_id, track)
        assert result is True

        # Get playlist and verify track was added
        retrieved_playlist = manager.get_playlist(playlist.playlist_id)
        assert retrieved_playlist is not None
        assert len(retrieved_playlist.tracks) == 1
        assert retrieved_playlist.tracks[0].title == "Eye of the Tiger"
        assert retrieved_playlist.tracks[0].artist == "Survivor"

    def test_add_track_to_empty_playlist(self, api_setup):
        """Test adding a track to an empty playlist - the main bug fix"""
        manager = api_setup

        # Create an empty playlist
        playlist = manager.create_playlist(name="Empty Playlist")
        assert len(playlist.tracks) == 0

        # This should work even though the playlist is empty
        track = Track(title="Test Song", artist="Test Artist")
        result = manager.add_track_to_playlist(playlist.playlist_id, track)

        # Verify the operation succeeded
        assert result is True, "Adding track to empty playlist should succeed"

        # Verify the track was actually added
        updated_playlist = manager.get_playlist(playlist.playlist_id)
        assert updated_playlist is not None
        assert len(updated_playlist.tracks) == 1
        assert updated_playlist.tracks[0].title == "Test Song"

    def test_add_multiple_tracks_to_empty_playlist(self, api_setup):
        """Test adding multiple tracks to an initially empty playlist"""
        manager = api_setup
        playlist = manager.create_playlist(name="Test Playlist")

        # Add first track to empty playlist
        track1 = Track(title="Song 1", artist="Artist 1")
        result1 = manager.add_track_to_playlist(playlist.playlist_id, track1)
        assert result1 is True

        # Add second track to playlist that now has one track
        track2 = Track(title="Song 2", artist="Artist 2")
        result2 = manager.add_track_to_playlist(playlist.playlist_id, track2)
        assert result2 is True

        # Add third track
        track3 = Track(title="Song 3", artist="Artist 3")
        result3 = manager.add_track_to_playlist(playlist.playlist_id, track3)
        assert result3 is True

        # Verify all tracks were added
        final_playlist = manager.get_playlist(playlist.playlist_id)
        assert len(final_playlist.tracks) == 3
        assert final_playlist.tracks[0].title == "Song 1"
        assert final_playlist.tracks[1].title == "Song 2"
        assert final_playlist.tracks[2].title == "Song 3"

    def test_operations_on_empty_playlist(self, api_setup):
        """Test various operations on empty playlists work correctly"""
        manager = api_setup
        empty_playlist = manager.create_playlist(name="Empty")

        # Get empty playlist should work
        retrieved = manager.get_playlist(empty_playlist.playlist_id)
        assert retrieved is not None
        assert len(retrieved.tracks) == 0

        # Rename empty playlist should work
        result = manager.rename_playlist(
            empty_playlist.playlist_id, "Renamed Empty"
        )
        assert result is True
        renamed = manager.get_playlist(empty_playlist.playlist_id)
        assert renamed.name == "Renamed Empty"

        # Add tags to empty playlist should work
        result = manager.add_tags_to_playlist(
            empty_playlist.playlist_id, ["tag1", "tag2"]
        )
        assert result is True
        tagged = manager.get_playlist(empty_playlist.playlist_id)
        assert "tag1" in tagged.tags
        assert "tag2" in tagged.tags

        # Duplicate empty playlist should work
        duplicate = manager.duplicate_playlist(
            empty_playlist.playlist_id, "Duplicate"
        )
        assert duplicate is not None
        assert duplicate.name == "Duplicate"
        assert len(duplicate.tracks) == 0

    def test_export_empty_playlist(self, api_setup):
        """Test exporting an empty playlist"""
        manager = api_setup
        test_dir = tempfile.mkdtemp()

        try:
            playlist = manager.create_playlist(name="Export Test")

            # Export to JSON
            export_path = Path(test_dir) / "export_test.json"
            result = manager.export_playlist(
                playlist.playlist_id,
                str(export_path),
                format="json"
            )
            assert result is True
            assert export_path.exists()

            # Verify exported content
            with open(export_path, 'r') as f:
                data = json.load(f)
                assert data['name'] == "Export Test"
                assert data['tracks'] == []
        finally:
            shutil.rmtree(test_dir)


class TestIntegrationCLI:
    """Integration tests for CLI commands"""

    def test_cli_create_and_add_track(self, cli_setup):
        """Test creating a playlist and adding a track via CLI"""
        run_cli = cli_setup

        # Create playlist
        result = run_cli(
            "create", "Test Playlist", "-d", "Testing", "-t", "test,cli"
        )
        assert result.returncode == 0, f"Create failed: {result.stderr}"
        assert "Created playlist" in result.stdout

        # Extract playlist ID from output
        lines = result.stdout.strip().split('\n')
        playlist_id = None
        for line in lines:
            if line.startswith("Playlist ID:"):
                playlist_id = line.split(":")[1].strip()
                break

        assert playlist_id is not None, "Could not find playlist ID in output"

        # Add track to the (initially empty) playlist
        result = run_cli(
            "add-track",
            playlist_id,
            "Test Song",
            "Test Artist",
            "-a", "Test Album"
        )
        assert result.returncode == 0, f"Add track failed: {result.stderr}"
        assert "Added track" in result.stdout

        # Verify track was added by showing the playlist
        result = run_cli("show", playlist_id)
        assert result.returncode == 0, f"Show failed: {result.stderr}"
        assert "Test Song" in result.stdout
        assert "Test Artist" in result.stdout
        assert "Tracks: 1" in result.stdout

    def test_cli_add_multiple_tracks(self, cli_setup):
        """Test adding multiple tracks to empty playlist via CLI"""
        run_cli = cli_setup

        # Create empty playlist
        result = run_cli("create", "Multi Track Test")
        assert result.returncode == 0

        # Extract playlist ID
        playlist_id = None
        for line in result.stdout.strip().split('\n'):
            if line.startswith("Playlist ID:"):
                playlist_id = line.split(":")[1].strip()
                break

        assert playlist_id is not None

        # Add first track
        result = run_cli("add-track", playlist_id, "Song 1", "Artist 1")
        assert result.returncode == 0

        # Add second track
        result = run_cli("add-track", playlist_id, "Song 2", "Artist 2")
        assert result.returncode == 0

        # Add third track
        result = run_cli("add-track", playlist_id, "Song 3", "Artist 3")
        assert result.returncode == 0

        # Verify all tracks
        result = run_cli("show", playlist_id)
        assert result.returncode == 0
        assert "Tracks: 3" in result.stdout
        assert "Song 1" in result.stdout
        assert "Song 2" in result.stdout
        assert "Song 3" in result.stdout

    def test_cli_show_empty_playlist(self, cli_setup):
        """Test showing details of an empty playlist via CLI"""
        run_cli = cli_setup

        # Create empty playlist
        result = run_cli("create", "Empty Playlist")
        assert result.returncode == 0

        # Extract playlist ID
        playlist_id = None
        for line in result.stdout.strip().split('\n'):
            if line.startswith("Playlist ID:"):
                playlist_id = line.split(":")[1].strip()
                break

        # Show should work for empty playlist
        result = run_cli("show", playlist_id)
        assert (
            result.returncode == 0
        ), "Show command should work for empty playlist"
        assert "Empty Playlist" in result.stdout
        assert "Tracks: 0" in result.stdout
