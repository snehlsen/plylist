"""Apple Music platform integration for Plylist"""

import os
import json
import time
from typing import List, Optional, Dict, Any
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta

from .base import PlatformBase
from ..models.track import Track
from ..models.playlist import Playlist


class AppleMusicPlatform(PlatformBase):
    """
    Apple Music platform integration using Apple Music API.

    Requires:
    - Apple Developer Account
    - MusicKit identifier
    - Team ID
    - Key ID
    - Private key (.p8 file)

    Set these environment variables:
    - APPLE_MUSIC_TEAM_ID: Your Apple Developer Team ID
    - APPLE_MUSIC_KEY_ID: Your MusicKit Key ID
    - APPLE_MUSIC_PRIVATE_KEY_PATH: Path to your .p8 private key file
    - APPLE_MUSIC_USER_TOKEN: User music token (obtained via MusicKit JS)
    """

    API_BASE_URL = "https://api.music.apple.com/v1"

    def __init__(self):
        """Initialize Apple Music platform"""
        super().__init__("apple_music")
        self.team_id = os.getenv("APPLE_MUSIC_TEAM_ID")
        self.key_id = os.getenv("APPLE_MUSIC_KEY_ID")
        self.private_key_path = os.getenv("APPLE_MUSIC_PRIVATE_KEY_PATH")
        self.user_token = os.getenv("APPLE_MUSIC_USER_TOKEN")
        self.developer_token = None
        self.developer_token_expiry = None
        self.storefront = "us"  # Default to US, can be configured

    def authenticate(self) -> bool:
        """
        Authenticate with Apple Music API.

        Generates a developer token using JWT and validates user token.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Generate developer token
            if not self._generate_developer_token():
                print("Failed to generate Apple Music developer token")
                return False

            # Validate user token
            if not self.user_token:
                print("Apple Music user token not provided")
                print("User token must be obtained via MusicKit JS in a web context")
                return False

            # Test the authentication by getting user's storefront
            storefront = self._get_user_storefront()
            if storefront:
                self.storefront = storefront
                print(f"Authenticated with Apple Music (storefront: {self.storefront})")
                return True

            return False

        except Exception as e:
            print(f"Apple Music authentication failed: {e}")
            return False

    def _generate_developer_token(self) -> bool:
        """
        Generate Apple Music developer token using JWT.

        Returns:
            True if token generated successfully, False otherwise
        """
        try:
            # Check if token is still valid
            if self.developer_token and self.developer_token_expiry:
                if datetime.utcnow() < self.developer_token_expiry:
                    return True

            # Check required credentials
            if not all([self.team_id, self.key_id, self.private_key_path]):
                print("Missing Apple Music credentials")
                print("Required: APPLE_MUSIC_TEAM_ID, APPLE_MUSIC_KEY_ID, APPLE_MUSIC_PRIVATE_KEY_PATH")
                return False

            # Try to import JWT library
            try:
                import jwt
            except ImportError:
                print("PyJWT library required for Apple Music integration")
                print("Install with: pip install PyJWT cryptography")
                return False

            # Read private key
            with open(self.private_key_path, "r") as key_file:
                private_key = key_file.read()

            # Generate token (valid for 6 months)
            time_now = int(time.time())
            time_expiry = time_now + (180 * 24 * 60 * 60)  # 180 days

            headers = {
                "alg": "ES256",
                "kid": self.key_id
            }

            payload = {
                "iss": self.team_id,
                "iat": time_now,
                "exp": time_expiry
            }

            self.developer_token = jwt.encode(
                payload,
                private_key,
                algorithm="ES256",
                headers=headers
            )

            self.developer_token_expiry = datetime.utcfromtimestamp(time_expiry)
            return True

        except Exception as e:
            print(f"Failed to generate developer token: {e}")
            return False

    def _get_user_storefront(self) -> Optional[str]:
        """
        Get the user's storefront (country code).

        Returns:
            Storefront ID or None if failed
        """
        try:
            url = f"{self.API_BASE_URL}/me/storefront"
            data = self._make_request(url)

            if data and "data" in data and len(data["data"]) > 0:
                return data["data"][0]["id"]

            return None

        except Exception:
            return None

    def _make_request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        use_user_token: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Make an authenticated request to Apple Music API.

        Args:
            url: API endpoint URL
            method: HTTP method
            data: Request payload
            use_user_token: Whether to include user token

        Returns:
            Response data or None if failed
        """
        headers = {
            "Authorization": f"Bearer {self.developer_token}",
            "Content-Type": "application/json"
        }

        if use_user_token and self.user_token:
            headers["Music-User-Token"] = self.user_token

        try:
            request_data = json.dumps(data).encode('utf-8') if data else None
            req = urllib.request.Request(url, data=request_data, headers=headers, method=method)

            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else "No error details"
            print(f"Apple Music API error ({e.code}): {error_body}")
            return None
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def search_track(self, title: str, artist: str) -> Optional[Track]:
        """
        Search for a track on Apple Music.

        Args:
            title: Track title
            artist: Artist name

        Returns:
            Track object with Apple Music ID if found, None otherwise
        """
        try:
            # Build search query
            query = f"{title} {artist}"
            encoded_query = urllib.parse.quote(query)

            url = f"{self.API_BASE_URL}/catalog/{self.storefront}/search"
            url += f"?term={encoded_query}&types=songs&limit=5"

            data = self._make_request(url, use_user_token=False)

            if not data or "results" not in data or "songs" not in data["results"]:
                return None

            songs = data["results"]["songs"]["data"]
            if not songs:
                return None

            # Find best match
            for song in songs:
                attrs = song["attributes"]

                # Simple matching - can be improved
                if (title.lower() in attrs["name"].lower() and
                    artist.lower() in attrs["artistName"].lower()):

                    track = Track(
                        title=attrs["name"],
                        artist=attrs["artistName"],
                        album=attrs.get("albumName"),
                        duration_ms=attrs.get("durationInMillis"),
                        isrc=attrs.get("isrc"),
                    )

                    track.add_platform_id(self.platform_name, song["id"])

                    # Add additional metadata
                    track.metadata["apple_music"] = {
                        "url": attrs.get("url"),
                        "preview_url": attrs.get("previews", [{}])[0].get("url") if attrs.get("previews") else None,
                        "artwork": attrs.get("artwork", {}).get("url"),
                        "genre": attrs.get("genreNames", []),
                    }

                    return track

            return None

        except Exception as e:
            print(f"Search failed: {e}")
            return None

    def get_track(self, platform_id: str) -> Optional[Track]:
        """
        Get track details by Apple Music ID.

        Args:
            platform_id: Apple Music track ID

        Returns:
            Track object if found, None otherwise
        """
        try:
            url = f"{self.API_BASE_URL}/catalog/{self.storefront}/songs/{platform_id}"
            data = self._make_request(url, use_user_token=False)

            if not data or "data" not in data or len(data["data"]) == 0:
                return None

            song = data["data"][0]
            attrs = song["attributes"]

            track = Track(
                title=attrs["name"],
                artist=attrs["artistName"],
                album=attrs.get("albumName"),
                duration_ms=attrs.get("durationInMillis"),
                isrc=attrs.get("isrc"),
            )

            track.add_platform_id(self.platform_name, song["id"])

            track.metadata["apple_music"] = {
                "url": attrs.get("url"),
                "preview_url": attrs.get("previews", [{}])[0].get("url") if attrs.get("previews") else None,
                "artwork": attrs.get("artwork", {}).get("url"),
                "genre": attrs.get("genreNames", []),
            }

            return track

        except Exception as e:
            print(f"Get track failed: {e}")
            return None

    def create_playlist(self, playlist: Playlist) -> Optional[str]:
        """
        Create a playlist on Apple Music.

        Args:
            playlist: Playlist to create

        Returns:
            Apple Music playlist ID if successful, None otherwise
        """
        try:
            url = f"{self.API_BASE_URL}/me/library/playlists"

            # Build track list
            track_items = []
            for track in playlist.tracks:
                am_id = track.get_platform_id(self.platform_name)
                if not am_id:
                    # Try to find the track on Apple Music
                    found_track = self.search_track(track.title, track.artist)
                    if found_track:
                        am_id = found_track.get_platform_id(self.platform_name)

                if am_id:
                    track_items.append({
                        "id": am_id,
                        "type": "songs"
                    })

            payload = {
                "attributes": {
                    "name": playlist.name,
                    "description": playlist.description or ""
                },
                "relationships": {
                    "tracks": {
                        "data": track_items
                    }
                }
            }

            data = self._make_request(url, method="POST", data=payload)

            if data and "data" in data and len(data["data"]) > 0:
                return data["data"][0]["id"]

            return None

        except Exception as e:
            print(f"Create playlist failed: {e}")
            return None

    def update_playlist(self, playlist: Playlist) -> bool:
        """
        Update an existing playlist on Apple Music.

        Args:
            playlist: Playlist with updated data

        Returns:
            True if successful, False otherwise
        """
        try:
            am_id = playlist.get_platform_id(self.platform_name)
            if not am_id:
                print("Playlist does not have Apple Music ID")
                return False

            # Update metadata
            url = f"{self.API_BASE_URL}/me/library/playlists/{am_id}"

            payload = {
                "attributes": {
                    "name": playlist.name,
                    "description": playlist.description or ""
                }
            }

            data = self._make_request(url, method="PATCH", data=payload)

            if not data:
                return False

            # Update tracks (replace all)
            track_ids = []
            for track in playlist.tracks:
                am_track_id = track.get_platform_id(self.platform_name)
                if not am_track_id:
                    found_track = self.search_track(track.title, track.artist)
                    if found_track:
                        am_track_id = found_track.get_platform_id(self.platform_name)

                if am_track_id:
                    track_ids.append(am_track_id)

            return self._replace_playlist_tracks(am_id, track_ids)

        except Exception as e:
            print(f"Update playlist failed: {e}")
            return False

    def _replace_playlist_tracks(self, playlist_id: str, track_ids: List[str]) -> bool:
        """Replace all tracks in a playlist"""
        try:
            # First, get existing tracks to clear them
            url = f"{self.API_BASE_URL}/me/library/playlists/{playlist_id}/tracks"

            # Then add new tracks
            track_data = [{"id": tid, "type": "songs"} for tid in track_ids]

            payload = {
                "data": track_data
            }

            data = self._make_request(url, method="POST", data=payload)
            return data is not None

        except Exception as e:
            print(f"Replace tracks failed: {e}")
            return False

    def delete_playlist(self, platform_id: str) -> bool:
        """
        Delete a playlist from Apple Music.

        Args:
            platform_id: Apple Music playlist ID

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.API_BASE_URL}/me/library/playlists/{platform_id}"
            data = self._make_request(url, method="DELETE")

            # DELETE returns None on success
            return True

        except Exception as e:
            print(f"Delete playlist failed: {e}")
            return False

    def get_playlist(self, platform_id: str) -> Optional[Playlist]:
        """
        Get playlist from Apple Music.

        Args:
            platform_id: Apple Music playlist ID

        Returns:
            Playlist object if found, None otherwise
        """
        try:
            url = f"{self.API_BASE_URL}/me/library/playlists/{platform_id}"
            data = self._make_request(url)

            if not data or "data" not in data or len(data["data"]) == 0:
                return None

            pl_data = data["data"][0]
            attrs = pl_data["attributes"]

            playlist = Playlist(
                name=attrs["name"],
                description=attrs.get("description", {}).get("standard") if attrs.get("description") else None,
            )

            playlist.add_platform_id(self.platform_name, platform_id)

            # Get tracks
            tracks_url = f"{url}/tracks"
            tracks_data = self._make_request(tracks_url)

            if tracks_data and "data" in tracks_data:
                for track_data in tracks_data["data"]:
                    track_attrs = track_data["attributes"]

                    track = Track(
                        title=track_attrs["name"],
                        artist=track_attrs["artistName"],
                        album=track_attrs.get("albumName"),
                        duration_ms=track_attrs.get("durationInMillis"),
                    )

                    track.add_platform_id(self.platform_name, track_data["id"])
                    playlist.add_track(track)

            return playlist

        except Exception as e:
            print(f"Get playlist failed: {e}")
            return None

    def get_user_playlists(self) -> List[Playlist]:
        """
        Get all playlists for the authenticated user.

        Returns:
            List of playlists
        """
        playlists = []

        try:
            url = f"{self.API_BASE_URL}/me/library/playlists"
            data = self._make_request(url)

            if not data or "data" not in data:
                return playlists

            for pl_data in data["data"]:
                attrs = pl_data["attributes"]

                playlist = Playlist(
                    name=attrs["name"],
                    description=attrs.get("description", {}).get("standard") if attrs.get("description") else None,
                )

                playlist.add_platform_id(self.platform_name, pl_data["id"])
                playlists.append(playlist)

            return playlists

        except Exception as e:
            print(f"Get user playlists failed: {e}")
            return playlists

    def add_tracks_to_playlist(self, platform_playlist_id: str, track_ids: List[str]) -> bool:
        """
        Add tracks to a playlist on Apple Music.

        Args:
            platform_playlist_id: Apple Music playlist ID
            track_ids: List of Apple Music track IDs

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.API_BASE_URL}/me/library/playlists/{platform_playlist_id}/tracks"

            track_data = [{"id": tid, "type": "songs"} for tid in track_ids]

            payload = {
                "data": track_data
            }

            data = self._make_request(url, method="POST", data=payload)
            return data is not None

        except Exception as e:
            print(f"Add tracks failed: {e}")
            return False

    def remove_tracks_from_playlist(self, platform_playlist_id: str, track_ids: List[str]) -> bool:
        """
        Remove tracks from a playlist on Apple Music.

        Note: Apple Music API doesn't support direct track removal.
        This would require fetching all tracks, filtering out unwanted ones,
        and replacing the entire playlist.

        Args:
            platform_playlist_id: Apple Music playlist ID
            track_ids: List of Apple Music track IDs to remove

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current playlist
            playlist = self.get_playlist(platform_playlist_id)
            if not playlist:
                return False

            # Filter out tracks to remove
            remaining_track_ids = []
            for track in playlist.tracks:
                am_id = track.get_platform_id(self.platform_name)
                if am_id and am_id not in track_ids:
                    remaining_track_ids.append(am_id)

            # Replace with remaining tracks
            return self._replace_playlist_tracks(platform_playlist_id, remaining_track_ids)

        except Exception as e:
            print(f"Remove tracks failed: {e}")
            return False
