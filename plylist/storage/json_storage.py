"""JSON-based storage for playlists"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from ..models.playlist import Playlist


class JSONStorage:
    """
    Store playlists in JSON format on the local filesystem
    """

    def __init__(self, storage_dir: str = None):
        """
        Initialize JSON storage

        Args:
            storage_dir: Directory to store playlist files.
                        Defaults to ~/.plylist/playlists
        """
        if storage_dir is None:
            storage_dir = os.path.join(Path.home(), ".plylist", "playlists")

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Index file to track all playlists
        self.index_file = self.storage_dir / "index.json"
        self._ensure_index()

    def _ensure_index(self) -> None:
        """Ensure the index file exists"""
        if not self.index_file.exists():
            self._save_index({})

    def _load_index(self) -> Dict[str, Any]:
        """Load the playlist index"""
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_index(self, index: Dict[str, Any]) -> None:
        """Save the playlist index"""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

    def _get_playlist_path(self, playlist_id: str) -> Path:
        """Get the file path for a playlist"""
        return self.storage_dir / f"{playlist_id}.json"

    def save(self, playlist: Playlist) -> bool:
        """
        Save a playlist to storage

        Args:
            playlist: Playlist to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Save playlist file
            playlist_path = self._get_playlist_path(playlist.playlist_id)
            with open(playlist_path, "w", encoding="utf-8") as f:
                json.dump(playlist.to_dict(), f, indent=2, ensure_ascii=False)

            # Update index
            index = self._load_index()
            index[playlist.playlist_id] = {
                "name": playlist.name,
                "track_count": len(playlist.tracks),
                "created_at": playlist.created_at,
                "updated_at": playlist.updated_at,
                "tags": playlist.tags,
            }
            self._save_index(index)

            return True
        except Exception as e:
            print(f"Error saving playlist: {e}")
            return False

    def load(self, playlist_id: str) -> Optional[Playlist]:
        """
        Load a playlist from storage

        Args:
            playlist_id: ID of the playlist to load

        Returns:
            Playlist object if found, None otherwise
        """
        try:
            playlist_path = self._get_playlist_path(playlist_id)
            if not playlist_path.exists():
                return None

            with open(playlist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Playlist.from_dict(data)
        except Exception as e:
            print(f"Error loading playlist: {e}")
            return None

    def delete(self, playlist_id: str) -> bool:
        """
        Delete a playlist from storage

        Args:
            playlist_id: ID of the playlist to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            playlist_path = self._get_playlist_path(playlist_id)
            if playlist_path.exists():
                playlist_path.unlink()

            # Update index
            index = self._load_index()
            if playlist_id in index:
                del index[playlist_id]
                self._save_index(index)

            return True
        except Exception as e:
            print(f"Error deleting playlist: {e}")
            return False

    def list_all(self) -> List[Dict[str, Any]]:
        """
        List all playlists in storage

        Returns:
            List of playlist metadata dictionaries
        """
        index = self._load_index()
        return [
            {"playlist_id": pid, **info} for pid, info in index.items()
        ]

    def search(
        self, query: str = None, tags: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for playlists

        Args:
            query: Search term to match against playlist name
            tags: List of tags to filter by

        Returns:
            List of matching playlist metadata dictionaries
        """
        all_playlists = self.list_all()

        if query:
            query = query.lower()
            all_playlists = [
                p for p in all_playlists
                if query in p["name"].lower()
            ]

        if tags:
            all_playlists = [
                p for p in all_playlists
                if any(tag in p.get("tags", []) for tag in tags)
            ]

        return all_playlists

    def export_playlist(
        self, playlist_id: str, export_path: str, format: str = "json"
    ) -> bool:
        """
        Export a playlist to a file

        Args:
            playlist_id: ID of the playlist to export
            export_path: Path to export the playlist to
            format: Export format ('json' or 'csv')

        Returns:
            True if successful, False otherwise
        """
        playlist = self.load(playlist_id)
        if playlist is None:
            return False

        try:
            if format == "json":
                with open(export_path, "w", encoding="utf-8") as f:
                    json.dump(
                        playlist.to_dict(), f, indent=2, ensure_ascii=False
                    )
            elif format == "csv":
                import csv
                with open(export_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "Title",
                        "Artist",
                        "Album",
                        "Duration (ms)",
                        "ISRC",
                        "Additional Artists",
                    ])
                    for track in playlist.tracks:
                        writer.writerow([
                            track.title,
                            track.artist,
                            track.album or "",
                            track.duration_ms or "",
                            track.isrc or "",
                            ", ".join(track.additional_artists),
                        ])
            else:
                return False

            return True
        except Exception as e:
            print(f"Error exporting playlist: {e}")
            return False

    def import_playlist(
        self, import_path: str, format: str = "json"
    ) -> Optional[Playlist]:
        """
        Import a playlist from a file

        Args:
            import_path: Path to the file to import
            format: Import format ('json' or 'csv')

        Returns:
            Imported Playlist object if successful, None otherwise
        """
        try:
            if format == "json":
                with open(import_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    playlist = Playlist.from_dict(data)
                    self.save(playlist)
                    return playlist
            elif format == "csv":
                import csv
                from ..models.track import Track

                tracks = []
                with open(import_path, "r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        track = Track(
                            title=row["Title"],
                            artist=row["Artist"],
                            album=row.get("Album") or None,
                            duration_ms=(
                                int(row["Duration (ms)"])
                                if row.get("Duration (ms)")
                                else None
                            ),
                            isrc=row.get("ISRC") or None,
                            additional_artists=(
                                row.get("Additional Artists", "").split(", ")
                                if row.get("Additional Artists")
                                else []
                            ),
                        )
                        tracks.append(track)

                # Create playlist with filename as name
                playlist_name = Path(import_path).stem
                playlist = Playlist(name=playlist_name, tracks=tracks)
                self.save(playlist)
                return playlist
            else:
                return None

        except Exception as e:
            print(f"Error importing playlist: {e}")
            return None

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics

        Returns:
            Dictionary with storage statistics
        """
        all_playlists = self.list_all()
        total_tracks = sum(p.get("track_count", 0) for p in all_playlists)

        return {
            "total_playlists": len(all_playlists),
            "total_tracks": total_tracks,
            "storage_directory": str(self.storage_dir),
        }
