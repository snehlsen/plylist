# Apple Music CLI Guide

This guide explains how to use the Apple Music integration via the Plylist CLI.

## Setup

Before using Apple Music commands, make sure you have:

1. Installed Apple Music dependencies:
   ```bash
   pip install "plylist[apple-music]"
   ```

2. Configured your Apple Music credentials (see [Apple Music Setup Guide](apple_music_setup.md)):
   ```bash
   export APPLE_MUSIC_TEAM_ID="your-team-id"
   export APPLE_MUSIC_KEY_ID="your-key-id"
   export APPLE_MUSIC_PRIVATE_KEY_PATH="/path/to/key.p8"
   export APPLE_MUSIC_USER_TOKEN="your-user-token"
   ```

## How It Works

### Local vs Remote Playlists

- **Local playlists**: Stored in `~/.plylist/playlists/` on your computer
- **Apple Music playlists**: Stored in your Apple Music library in the cloud
- **Synced playlists**: Playlists that exist in both locations with a link between them

### Workflow

1. **Create playlists locally** - Use `plylist create` to make playlists
2. **Add tracks** - Use `plylist add-track` to add songs
3. **Sync to Apple Music** - Use `plylist apple-music sync-to` to upload
4. **Import from Apple Music** - Use `plylist apple-music sync-from` to download

## Apple Music Commands

All Apple Music commands are under the `apple-music` subcommand:

```bash
plylist apple-music <command> [options]
```

### Authentication

Test your Apple Music credentials:

```bash
plylist apple-music auth
```

**Output:**
```
Testing Apple Music authentication...
✓ Successfully authenticated with Apple Music
  Storefront: us
```

### Search for Tracks

Search for a track on Apple Music:

```bash
plylist apple-music search "<title>" "<artist>"
```

**Example:**
```bash
plylist apple-music search "Billie Jean" "Michael Jackson"
```

**Output:**
```
Searching Apple Music for: Billie Jean by Michael Jackson

✓ Found: Billie Jean by Michael Jackson (from Thriller)
  Apple Music ID: 269572838
  Album: Thriller
  Duration: 4:54
```

### Sync Local Playlist to Apple Music

Upload a local playlist to your Apple Music library:

```bash
plylist apple-music sync-to <playlist-id>
```

**Example:**
```bash
# Create a local playlist
plylist create "Workout Mix"
# Copy the playlist ID from output

# Add some tracks
plylist add-track <playlist-id> "Eye of the Tiger" "Survivor"
plylist add-track <playlist-id> "Lose Yourself" "Eminem"

# Sync to Apple Music
plylist apple-music sync-to <playlist-id>
```

**Output:**
```
Syncing 'Workout Mix' to Apple Music...
  Tracks to sync: 2
✓ Successfully synced to Apple Music
  Apple Music Playlist ID: p.abc123def456
```

**What happens:**
- Plylist searches for each track on Apple Music
- Creates a new playlist in your Apple Music library
- Adds all found tracks to the playlist
- Stores the Apple Music playlist ID locally for future syncs

### Import Playlist from Apple Music

Download a playlist from Apple Music to local storage:

```bash
plylist apple-music sync-from <apple-music-playlist-id>
```

**Example:**
```bash
# First, list your Apple Music playlists to find the ID
plylist apple-music playlists

# Then import the one you want
plylist apple-music sync-from p.abc123def456
```

**Output:**
```
Importing playlist from Apple Music (ID: p.abc123def456)...
✓ Successfully imported: My Favorites
  Local Playlist ID: e8f7g6h5-i4j3-k2l1-m0n9-o8p7q6r5s4t3
  Tracks: 25
```

**What happens:**
- Fetches the playlist metadata from Apple Music
- Downloads all track information
- Creates a local playlist with all tracks
- Stores the link between local and Apple Music playlists

### List Apple Music Playlists

See all playlists in your Apple Music library:

```bash
plylist apple-music playlists
```

**Output:**
```
Fetching your Apple Music playlists...

Found 12 Apple Music playlist(s):

  My Favorites
    Apple Music ID: p.abc123def456
    Description: All my favorite songs

  Workout Mix
    Apple Music ID: p.xyz789uvw012

  Chill Vibes
    Apple Music ID: p.mno345pqr678
    Description: Music for studying and relaxing
```

### Check Sync Status

See which local playlists are synced to Apple Music:

```bash
plylist apple-music status
```

**Output:**
```
Sync Status:
  Total local playlists: 5
  Synced to Apple Music: 2
  Local only: 3

Playlists:
  [✓ Synced] Workout Mix
      Local ID: e8f7g6h5-i4j3-k2l1-m0n9-o8p7q6r5s4t3
      Apple Music ID: p.xyz789uvw012

  [  Local only] Chill Playlist
      Local ID: a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6

  [✓ Synced] My Favorites
      Local ID: f9e8d7c6-b5a4-9382-7261-5049382716ab
      Apple Music ID: p.abc123def456

  [  Local only] Rock Classics
      Local ID: 1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p

  [  Local only] Jazz Standards
      Local ID: 9z8y7x6w-5v4u-3t2s-1r0q-9p8o7n6m5l4k
```

## Regular Commands with Sync Info

Regular Plylist commands now show sync status:

### List Playlists

```bash
plylist list
```

**Output shows sync status:**
```
Found 5 playlist(s):

  Workout Mix [Synced: apple_music]
    ID: e8f7g6h5-i4j3-k2l1-m0n9-o8p7q6r5s4t3
    Tracks: 15

  Chill Playlist [Local only]
    ID: a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
    Tracks: 8
```

### Show Playlist Details

```bash
plylist show <playlist-id>
```

**Output includes platform IDs:**
```
Playlist: Workout Mix
ID: e8f7g6h5-i4j3-k2l1-m0n9-o8p7q6r5s4t3
Description: High energy music for the gym
Tracks: 15
Duration: 1h 2m 15s
Created: 2025-11-15T10:30:00
Updated: 2025-11-15T14:45:00
Tags: workout, high-energy
Platform IDs:
  apple_music: p.xyz789uvw012
```

## Common Workflows

### Create and Sync a New Playlist

```bash
# 1. Create local playlist
plylist create "Summer Hits 2025" -d "Best songs for summer" -t "summer,pop"

# 2. Add tracks
plylist add-track <playlist-id> "Song Title" "Artist Name"
plylist add-track <playlist-id> "Another Song" "Another Artist"

# 3. View the playlist
plylist show <playlist-id>

# 4. Sync to Apple Music
plylist apple-music sync-to <playlist-id>

# 5. Verify sync status
plylist apple-music status
```

### Import and Modify Apple Music Playlist

```bash
# 1. List Apple Music playlists
plylist apple-music playlists

# 2. Import one
plylist apple-music sync-from <apple-music-id>

# 3. Add more tracks locally
plylist add-track <playlist-id> "New Song" "New Artist"

# 4. Sync changes back to Apple Music
plylist apple-music sync-to <playlist-id>
```

### Search and Add Tracks

```bash
# 1. Search for a track
plylist apple-music search "Bohemian Rhapsody" "Queen"
# Note the track details

# 2. Add it to your playlist
plylist add-track <playlist-id> "Bohemian Rhapsody" "Queen" -a "A Night at the Opera"

# 3. Sync to Apple Music
plylist apple-music sync-to <playlist-id>
```

### Keep Playlists in Sync

```bash
# After making local changes
plylist apple-music sync-to <playlist-id>

# To refresh from Apple Music (if you made changes there)
# Note: This will replace local tracks with Apple Music version
plylist delete <playlist-id> -f
plylist apple-music sync-from <apple-music-id>
```

## Understanding Sync Behavior

### First Sync (sync-to)
- Creates a new playlist in Apple Music
- Searches for each track on Apple Music
- Adds found tracks to the Apple Music playlist
- Saves the Apple Music playlist ID locally

### Subsequent Syncs (sync-to)
- Updates the existing Apple Music playlist
- Replaces all tracks with current local tracks
- Maintains the same Apple Music playlist ID

### Import (sync-from)
- Fetches playlist from Apple Music
- Creates a new local playlist
- Downloads all track information
- Links local and Apple Music playlists

## Troubleshooting

### "Failed to authenticate with Apple Music"

Check your environment variables:
```bash
echo $APPLE_MUSIC_TEAM_ID
echo $APPLE_MUSIC_KEY_ID
echo $APPLE_MUSIC_PRIVATE_KEY_PATH
echo $APPLE_MUSIC_USER_TOKEN
```

See the [Apple Music Setup Guide](apple_music_setup.md) for detailed setup instructions.

### "Track not found on Apple Music"

When syncing, some tracks might not be available on Apple Music:
- Check the exact title and artist name
- Some tracks might be region-specific
- Try searching manually first with `apple-music search`

### "Apple Music integration requires additional dependencies"

Install the Apple Music extras:
```bash
pip install "plylist[apple-music]"
```

### Playlist Not Appearing in Apple Music

- Check the sync output for errors
- Use `plylist show <playlist-id>` to verify the Apple Music ID was saved
- Log into Apple Music and check your library
- It may take a few minutes for changes to propagate

## Tips

1. **Use tags** to organize playlists: `plylist tag <playlist-id> "workout,morning"`
2. **Check sync status regularly**: `plylist apple-music status`
3. **Search before adding** to ensure tracks exist on Apple Music
4. **Export backups**: `plylist export <playlist-id> backup.json`
5. **Test with small playlists** first before syncing large collections

## Next Steps

- Learn about [manual playlist management](../README.md#cli-commands)
- Read the [Apple Music API documentation](https://developer.apple.com/documentation/applemusicapi/)
- Set up additional platforms (Spotify, YouTube Music) when available
