# Apple Music Integration Setup Guide

This guide walks you through setting up Apple Music integration with Plylist.

## Prerequisites

- Apple Developer Account (free or paid)
- Python 3.8 or higher
- PyJWT and cryptography libraries

## Step 1: Apple Developer Account Setup

1. Go to [Apple Developer](https://developer.apple.com/)
2. Sign in with your Apple ID
3. Enroll in the Apple Developer Program (if not already enrolled)

## Step 2: Enable MusicKit

1. Go to [Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources/)
2. Select **Identifiers** from the sidebar
3. Click the **+** button to create a new identifier
4. Select **MusicKit IDs** and click **Continue**
5. Enter a description and identifier (e.g., `com.yourcompany.plylist`)
6. Click **Register**

## Step 3: Create MusicKit Key

1. In the Apple Developer portal, select **Keys** from the sidebar
2. Click the **+** button to create a new key
3. Enter a key name (e.g., "Plylist MusicKit Key")
4. Check **MusicKit** under Key Services
5. Click **Continue**, then **Register**
6. **Important**: Download the `.p8` file immediately - you can only download it once!
7. Note your **Key ID** (displayed on the page)
8. Note your **Team ID** (found in the top-right corner of the page or in Membership section)

## Step 4: Store Your Credentials

Save the `.p8` file in a secure location. You'll need:
- **Team ID**: Found in your Apple Developer account
- **Key ID**: From the key you just created
- **Private Key Path**: Path to your `.p8` file

## Step 5: Obtain User Music Token

User music tokens are required for accessing user-specific data. There are two ways to obtain them:

### Option A: Using MusicKit JS (Recommended for Web Apps)

1. Create a simple HTML page with MusicKit JS
2. Request user authorization
3. Retrieve the music user token

Example HTML:

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://js-cdn.music.apple.com/musickit/v3/musickit.js"></script>
</head>
<body>
    <button id="auth-button">Authorize Apple Music</button>
    <div id="token-display"></div>

    <script>
        document.addEventListener('musickitloaded', async function() {
            await MusicKit.configure({
                developerToken: 'YOUR_DEVELOPER_TOKEN_HERE',
                app: {
                    name: 'Plylist',
                    build: '1.0.0'
                }
            });

            const music = MusicKit.getInstance();

            document.getElementById('auth-button').addEventListener('click', async () => {
                try {
                    await music.authorize();
                    const userToken = music.musicUserToken;
                    document.getElementById('token-display').innerHTML =
                        `<p>User Token: <code>${userToken}</code></p>`;
                    console.log('User Token:', userToken);
                } catch (error) {
                    console.error('Authorization failed:', error);
                }
            });
        });
    </script>
</body>
</html>
```

### Option B: For Testing (Limited Functionality)

For testing without user-specific operations, you can work with catalog operations that don't require a user token (like searching tracks).

## Step 6: Install Required Dependencies

```bash
pip install PyJWT cryptography
```

## Step 7: Set Environment Variables

Set these environment variables before running Plylist with Apple Music:

### On macOS/Linux:

```bash
export APPLE_MUSIC_TEAM_ID="ABC1234567"
export APPLE_MUSIC_KEY_ID="XYZ9876543"
export APPLE_MUSIC_PRIVATE_KEY_PATH="/path/to/AuthKey_XYZ9876543.p8"
export APPLE_MUSIC_USER_TOKEN="your-user-token-here"
```

### On Windows (Command Prompt):

```cmd
set APPLE_MUSIC_TEAM_ID=ABC1234567
set APPLE_MUSIC_KEY_ID=XYZ9876543
set APPLE_MUSIC_PRIVATE_KEY_PATH=C:\path\to\AuthKey_XYZ9876543.p8
set APPLE_MUSIC_USER_TOKEN=your-user-token-here
```

### On Windows (PowerShell):

```powershell
$env:APPLE_MUSIC_TEAM_ID="ABC1234567"
$env:APPLE_MUSIC_KEY_ID="XYZ9876543"
$env:APPLE_MUSIC_PRIVATE_KEY_PATH="C:\path\to\AuthKey_XYZ9876543.p8"
$env:APPLE_MUSIC_USER_TOKEN="your-user-token-here"
```

### Using a .env file:

Create a `.env` file in your project root:

```
APPLE_MUSIC_TEAM_ID=ABC1234567
APPLE_MUSIC_KEY_ID=XYZ9876543
APPLE_MUSIC_PRIVATE_KEY_PATH=/path/to/AuthKey_XYZ9876543.p8
APPLE_MUSIC_USER_TOKEN=your-user-token-here
```

Then load it in your Python code:

```python
from dotenv import load_dotenv
load_dotenv()

# Now environment variables are available
```

## Step 8: Test the Integration

Run the example script:

```bash
python examples/apple_music_integration.py
```

Or use in your own code:

```python
from plylist import PlaylistManager, AppleMusicPlatform

# Initialize
manager = PlaylistManager()
apple_music = AppleMusicPlatform()

# Authenticate
if apple_music.authenticate():
    print("Successfully authenticated with Apple Music!")

    # Register with manager
    manager.register_platform(apple_music)

    # Search for a track
    track = apple_music.search_track("Billie Jean", "Michael Jackson")
    if track:
        print(f"Found: {track}")
else:
    print("Authentication failed")
```

## Troubleshooting

### "PyJWT library required"

Install PyJWT:
```bash
pip install PyJWT cryptography
```

### "Failed to generate developer token"

- Verify your Team ID and Key ID are correct
- Ensure the path to your `.p8` file is correct and accessible
- Check that the `.p8` file is valid and not corrupted

### "Apple Music user token not provided"

- The user token must be obtained via MusicKit JS
- For catalog-only operations (like searching tracks), you can skip user token authentication

### "Failed to authenticate with Apple Music"

- Check your internet connection
- Verify all environment variables are set correctly
- Ensure your Apple Developer account is active

### API Rate Limits

Apple Music API has rate limits:
- Developer tokens: Up to 180 days validity
- User tokens: Expire and need renewal
- API calls: Rate limited per user/app

## Security Best Practices

1. **Never commit credentials**: Add `.env` and `.p8` files to `.gitignore`
2. **Rotate keys regularly**: Generate new keys periodically
3. **Limit key permissions**: Only enable necessary services
4. **Secure storage**: Store private keys securely
5. **User token handling**: Never log or expose user tokens

## API Capabilities

With Apple Music integration, you can:

- ✅ Search for tracks in the Apple Music catalog
- ✅ Get track details
- ✅ Create playlists in user's library
- ✅ Update existing playlists
- ✅ Delete playlists
- ✅ Get user's playlists
- ✅ Add tracks to playlists
- ✅ Remove tracks from playlists
- ✅ Sync local playlists to Apple Music
- ✅ Import Apple Music playlists to local storage

## Limitations

- User token required for library operations
- User token must be obtained via web-based MusicKit JS
- Some metadata may differ from other platforms
- Regional restrictions apply based on user's storefront

## Resources

- [Apple Music API Documentation](https://developer.apple.com/documentation/applemusicapi/)
- [MusicKit JS Documentation](https://developer.apple.com/documentation/musickitjs/)
- [Apple Developer Portal](https://developer.apple.com/)

## Support

For issues specific to Plylist's Apple Music integration, please open an issue on GitHub.

For Apple Music API issues, refer to Apple's developer forums or documentation.
