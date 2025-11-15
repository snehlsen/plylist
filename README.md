# Plylist - Platform-Agnostic Playlist Manager

Plylist is a Python application for managing music playlists independent of any streaming platform. Keep your carefully curated playlists under your control and sync them across different services.

## Features

- **Platform-Agnostic**: Manage playlists without being locked to any specific streaming service
- **Apple Music Integration**: Full support for syncing with Apple Music (authentication, search, sync)
- **Full CRUD Operations**: Create, read, update, and delete playlists
- **Track Management**: Add, remove, and reorder tracks within playlists
- **Import/Export**: Support for JSON and CSV formats
- **Tagging System**: Organize playlists with custom tags
- **Playlist Operations**: Duplicate and merge playlists
- **CLI Interface**: Easy-to-use command-line interface
- **Extensible**: Platform abstraction layer ready for Spotify, YouTube Music, and other integrations

## Installation

### Using uv (recommended)

```bash
# Clone the repository
git clone <repository-url>
cd plylist

# Install the package
uv pip install -e .

# Or install with development dependencies
uv pip install -e ".[dev]"
```

### Using pip (alternative)

```bash
# Clone the repository
git clone <repository-url>
cd plylist

# Install the package
pip install -e .

# Or with Apple Music support
pip install -e ".[apple-music]"

# Or with all platform integrations
pip install -e ".[all]"
```

## Quick Start

### Using the CLI

```bash
# Create a new playlist
python -m plylist create "My Playlist" -d "Description" -t "tag1,tag2"

# List all playlists
python -m plylist list

# Add a track to a playlist
python -m plylist add-track <playlist-id> "Song Title" "Artist Name" -a "Album"

# Show playlist details
python -m plylist show <playlist-id>

# Export a playlist
python -m plylist export <playlist-id> output.json

# Import a playlist
python -m plylist import input.json
```

### Using the Python API

```python
from plylist import PlaylistManager, Track

# Initialize the manager
manager = PlaylistManager()

# Create a playlist
playlist = manager.create_playlist(
    name="Workout Mix",
    description="High energy music",
    tags=["workout", "energetic"]
)

# Add tracks
track = Track(
    title="Eye of the Tiger",
    artist="Survivor",
    album="Eye of the Tiger",
    duration_ms=246000
)
manager.add_track_to_playlist(playlist.playlist_id, track)

# Get playlist
playlist = manager.get_playlist(playlist.playlist_id)
print(f"{playlist.name}: {len(playlist.tracks)} tracks")
```

## CLI Commands

### Playlist Management

- `create` - Create a new playlist
- `list` - List all playlists
- `show` - Show detailed playlist information
- `delete` - Delete a playlist
- `rename` - Rename a playlist
- `duplicate` - Create a copy of a playlist
- `merge` - Merge multiple playlists into one

### Track Management

- `add-track` - Add a track to a playlist
- `remove-track` - Remove a track from a playlist

### Organization

- `tag` - Add tags to a playlist

### Import/Export

- `export` - Export a playlist to JSON or CSV
- `import` - Import a playlist from JSON or CSV

### Statistics

- `stats` - Show overall statistics

## Architecture

Plylist is designed with a modular architecture:

```
plylist/
├── models/          # Data models (Track, Playlist)
├── storage/         # Storage backends (JSON, future: SQLite)
├── platforms/       # Platform integrations (base classes)
├── cli/            # Command-line interface
└── manager.py      # Core playlist manager
```

### Core Components

**Track Model**: Represents a music track with metadata
- Title, artist, album
- Duration and ISRC
- Platform-specific IDs
- Additional metadata

**Playlist Model**: Collection of tracks
- Name, description, tags
- Track list with ordering
- Platform-specific IDs
- Creation and update timestamps

**Storage Layer**: Persist playlists locally
- JSON-based file storage
- Index for fast lookups
- Import/export capabilities

**Platform Abstraction**: Ready for streaming service integration
- Base class for platform implementations
- Sync playlists to/from platforms
- Search and retrieve tracks

## Storage

By default, playlists are stored in `~/.plylist/playlists/` as JSON files. Each playlist has:
- A unique ID
- Individual JSON file with full data
- Entry in the index for quick listing

## Platform Integrations

### Apple Music (Available)

Plylist now includes full Apple Music integration! Sync your playlists, search for tracks, and manage your Apple Music library.

#### Installation

```bash
# Install with Apple Music support
pip install -e ".[apple-music]"
```

#### Setup

1. Create an Apple Developer account
2. Enable MusicKit and create a key
3. Set up environment variables (see [Apple Music Setup Guide](docs/apple_music_setup.md))

```bash
export APPLE_MUSIC_TEAM_ID="your-team-id"
export APPLE_MUSIC_KEY_ID="your-key-id"
export APPLE_MUSIC_PRIVATE_KEY_PATH="/path/to/key.p8"
export APPLE_MUSIC_USER_TOKEN="your-user-token"
```

#### Usage

```python
from plylist import PlaylistManager, AppleMusicPlatform

# Initialize
manager = PlaylistManager()
apple_music = AppleMusicPlatform()

# Authenticate
if apple_music.authenticate():
    manager.register_platform(apple_music)

    # Search for tracks
    track = apple_music.search_track("Billie Jean", "Michael Jackson")

    # Sync playlist to Apple Music
    manager.sync_to_platform(playlist_id, "apple_music")

    # Import from Apple Music
    imported = manager.sync_from_platform("apple_music", am_playlist_id)
```

See the [Apple Music Setup Guide](docs/apple_music_setup.md) for detailed instructions.

### Future Platforms

The platform abstraction layer is ready for additional streaming services:
- Spotify (planned)
- YouTube Music (planned)
- Tidal (planned)

To implement a new platform, extend the `PlatformBase` class:

```python
from plylist.platforms.base import PlatformBase

class SpotifyPlatform(PlatformBase):
    """Spotify integration"""
    # Implement abstract methods
    pass
```

## Data Format

### JSON Export Format

```json
{
  "name": "My Playlist",
  "description": "A great playlist",
  "playlist_id": "uuid",
  "created_at": "2025-11-10T12:00:00",
  "updated_at": "2025-11-10T12:30:00",
  "tags": ["workout", "rock"],
  "tracks": [
    {
      "title": "Song Title",
      "artist": "Artist Name",
      "album": "Album Name",
      "duration_ms": 240000,
      "isrc": "USRC12345678",
      "track_id": "uuid",
      "platform_ids": {
        "spotify": "spotify-track-id"
      }
    }
  ]
}
```

### CSV Export Format

Simple CSV format for easy sharing:
```csv
Title,Artist,Album,Duration (ms),ISRC,Additional Artists
Song Title,Artist Name,Album Name,240000,USRC12345678,
```

## Examples

See the `examples/` directory for detailed usage examples:
- `basic_usage.py` - Comprehensive walkthrough of core features
- `apple_music_integration.py` - Apple Music platform integration example

## Development

### Project Structure

```
plylist/
├── plylist/           # Main package
│   ├── models/       # Data models
│   ├── storage/      # Storage implementations
│   ├── platforms/    # Platform integrations
│   ├── cli/         # CLI application
│   └── manager.py   # Core manager
├── tests/           # Unit tests
├── examples/        # Usage examples
└── README.md        # This file
```

### Running Tests

```bash
# With uv
uv pip install -e ".[dev]"
pytest tests/

# Or use uv run (if you have a uv project set up)
uv run pytest tests/
```

## Use Cases

- **Backup Your Playlists**: Keep local copies of your streaming playlists
- **Cross-Platform Migration**: Move playlists between services
- **Playlist Management**: Organize and curate music collections
- **Sharing**: Export playlists to share with friends
- **Archival**: Maintain historical records of playlists

## Future Enhancements

- Platform integrations (Spotify, Apple Music, YouTube Music)
- Advanced search and filtering
- Playlist recommendations
- Collaborative playlists
- Web interface
- Database backend option
- Smart playlist rules

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.