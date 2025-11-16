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

User music tokens are required for accessing user-specific data (like your playlists). Here's the complete process:

### Step 5a: Generate Developer Token

First, you need to generate a developer token using your credentials:

**Method 1: Using the Helper Script (Easiest)**

```bash
python scripts/generate_developer_token.py
```

This will output your developer token. Copy it for the next step.

**Method 2: Generate Manually with Python**

```python
import jwt
import time

# Your credentials from previous steps
team_id = "ABC1234567"
key_id = "XYZ9876543"
private_key_path = "/path/to/AuthKey_XYZ9876543.p8"

# Read private key
with open(private_key_path, "r") as f:
    private_key = f.read()

# Generate token (valid for 180 days)
time_now = int(time.time())
time_expiry = time_now + (180 * 24 * 60 * 60)

headers = {"alg": "ES256", "kid": key_id}
payload = {"iss": team_id, "iat": time_now, "exp": time_expiry}

developer_token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
print(developer_token)
```

### Step 5b: Get User Music Token

Now use your developer token to get a user music token via MusicKit JS:

**Method 1: Using the Ready-Made HTML Tool (Easiest)**

1. **Open the HTML file** in a web browser:
   - File location: `scripts/get_apple_music_user_token.html`
   - Just double-click it or open it in your browser

2. **Paste your developer token** from Step 5a into the input field

3. **Click "Authorize Apple Music"** and sign in when prompted

4. **Copy the user token** that appears

5. **Save it** as an environment variable (see Step 6 below)

**Method 2: Create Your Own HTML File**

1. **Create an HTML file** (e.g., `get_user_token.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <title>Apple Music User Token</title>
    <script src="https://js-cdn.music.apple.com/musickit/v3/musickit.js"></script>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        #token-display { margin-top: 20px; padding: 10px; background: #f0f0f0; }
        code { background: #e0e0e0; padding: 2px 5px; }
    </style>
</head>
<body>
    <h1>Get Apple Music User Token</h1>
    <p>Click the button below to authorize with Apple Music and get your user token.</p>
    <button id="auth-button">Authorize Apple Music</button>
    <div id="token-display"></div>

    <script>
        // REPLACE THIS with your developer token from Step 5a
        const DEVELOPER_TOKEN = 'YOUR_DEVELOPER_TOKEN_HERE';

        document.addEventListener('musickitloaded', async function() {
            await MusicKit.configure({
                developerToken: DEVELOPER_TOKEN,
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

                    document.getElementById('token-display').innerHTML = `
                        <h2>Success! ✓</h2>
                        <p><strong>User Token:</strong></p>
                        <p><code>${userToken}</code></p>
                        <p>Copy the token above and set it as your APPLE_MUSIC_USER_TOKEN environment variable.</p>
                    `;

                    console.log('User Token:', userToken);
                } catch (error) {
                    document.getElementById('token-display').innerHTML = `
                        <p style="color: red;"><strong>Error:</strong> ${error.message}</p>
                    `;
                    console.error('Authorization failed:', error);
                }
            });
        });
    </script>
</body>
</html>
```

2. **Replace `YOUR_DEVELOPER_TOKEN_HERE`** with the token from Step 5a

3. **Open the HTML file** in a web browser

4. **Click "Authorize Apple Music"**
   - You'll be prompted to sign in to Apple Music
   - You need an active Apple Music subscription

5. **Copy the user token** that appears on the page

6. **Save it** as an environment variable (see Step 7 below)

### Alternative: Skip User Token for Testing

For testing catalog-only operations (like searching tracks), you can skip the user token. However, you **cannot** access your playlists or create playlists without it.

Operations that work without user token:
- `apple-music search` - Search the Apple Music catalog

Operations that require user token:
- `apple-music auth` - Test authentication with your account
- `apple-music playlists` - List your playlists
- `apple-music sync-to` - Upload playlists to your library
- `apple-music sync-from` - Download your playlists
- `apple-music status` - Check sync status

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
