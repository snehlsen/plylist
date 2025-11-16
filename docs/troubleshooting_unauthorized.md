# Troubleshooting "Unauthorized" Error

If you're getting `AUTHORIZATION_ERROR: Unauthorized` when trying to authorize with Apple Music, follow these steps.

## What You Know Works

✅ Developer token format is valid
✅ MusicKit.configure() succeeds
✅ You have an Apple Music subscription
✅ MusicKit is enabled on your key

## What's Failing

❌ `musicKitInstance.authorize()` returns "Unauthorized"

## Root Cause

The "Unauthorized" error during `authorize()` almost always means your **MusicKit Identifier** isn't properly configured or active in Apple Developer portal.

## Solution: Verify MusicKit Identifier Configuration

### Step 1: Check MusicKit Identifier Status

1. Go to: https://developer.apple.com/account/resources/identifiers/list/musicId

2. Look for your MusicKit Identifier

3. **Check the status column** - it should say "Enabled" or "Active"

4. **If it's not there** or shows as "Disabled":
   - Create a new one or enable it
   - Click on it and make sure it's properly configured

### Step 2: Verify Identifier Details

Click on your MusicKit Identifier and verify:

- **Description**: Has a name (e.g., "Plylist")
- **Identifier**: Has a bundle ID format (e.g., `com.yourname.plylist`)
- **Status**: Shows as active/enabled
- **Date Created**: Shows recent date

### Step 3: Wait for Propagation (Important!)

After creating or modifying a MusicKit Identifier:

⏱️ **Wait 10-15 minutes** for Apple's systems to propagate the changes

This is a common issue! Even though you just created it, Apple's backend needs time to activate it across all services.

### Step 4: Run Comprehensive Verification

Run this comprehensive diagnostic tool to identify the exact issue:

```bash
python scripts/verify_musickit_setup.py <your-developer-token>
```

This will:
- ✅ Verify token structure and expiration
- ✅ Test catalog access (public API)
- ✅ Test user endpoints and identify the specific error type
- ✅ Provide a clear diagnosis with specific fixes

**Expected output if setup is correct:**
```
✓ Token has 3 parts
✓ Token decoded successfully
✓ Algorithm is ES256
✓ Catalog search successful
✓ Got expected 401 Unauthorized (user endpoints)
✓ Your MusicKit setup appears to be correct!
```

**If you see 403 Forbidden on user endpoints:**
This means your Private Key or MusicKit Identifier has a configuration issue. See the diagnosis section for specific fixes.

### Step 5: Try Authorization Again

After waiting 10-15 minutes:

1. Open `scripts/get_apple_music_user_token.html`
2. Paste your developer token
3. Click "Authorize Apple Music"
4. It should now work!

## Specific Fix: 403 Forbidden on User Endpoints

If the verification tool shows **403 Forbidden** instead of the expected **401 Unauthorized** for user endpoints, this indicates a specific configuration problem:

### What This Means

- ✓ Your developer token structure is valid
- ✓ Your token works for public catalog searches
- ✗ Your token is rejected for user-scoped operations

This pattern means your **Private Key** or **MusicKit Identifier** isn't properly configured for user authorization, even though they appear enabled.

### Fix 1: Verify Private Key Configuration

1. Go to: https://developer.apple.com/account/resources/authkeys/list
2. Find the key with the **Key ID** shown in the verification tool output
3. Click on it to view details
4. **Critical check**: Under "Services", verify that **MusicKit** is checked
5. **Also verify**: The key status is "Active"

**If MusicKit is NOT checked:**
- You cannot edit an existing key to add services
- You must create a new key:
  1. Click "+ Create a key"
  2. Enter a name (e.g., "Apple Music Key 2")
  3. **Check the "MusicKit" checkbox**
  4. Click "Continue" and "Register"
  5. Download the .p8 file (you can only download once!)
  6. Note the new Key ID
  7. Update your environment variable: `APPLE_MUSIC_KEY_ID=<new-key-id>`
  8. Regenerate developer token: `python scripts/generate_developer_token.py`

### Fix 2: Verify Team ID Match

The Team ID in your token must match the team that owns your MusicKit Identifier:

1. Check the Team ID in your token (shown in verification tool output)
2. Go to: https://developer.apple.com/account
3. Verify the Team ID matches under "Membership"
4. Go to: https://developer.apple.com/account/resources/identifiers/list/musicId
5. Your MusicKit Identifier should be under the same team

**If Team IDs don't match:** You need to use the correct Team ID when generating your developer token.

### Fix 3: Recreate MusicKit Identifier

Sometimes the MusicKit Identifier appears enabled but isn't fully activated in Apple's systems:

1. Go to: https://developer.apple.com/account/resources/identifiers/list/musicId
2. Delete your existing MusicKit Identifier (if delete option is available)
3. Create a new one:
   - Click "+ Register an identifier"
   - Select "MusicKit IDs"
   - Click "Continue"
   - Description: "Plylist Production" (or any unique name)
   - Identifier: `com.yourname.plylist.v2` (use a different identifier)
   - Click "Register"
4. **Wait 15-20 minutes** for Apple to activate it
5. Try again (you don't need to regenerate your developer token)

## Alternative: Recreate MusicKit Identifier

If the above doesn't work, try creating a fresh MusicKit Identifier:

### Delete Old One (if exists)

1. Go to: https://developer.apple.com/account/resources/identifiers/list/musicId
2. Click on your existing identifier
3. Click "Delete" (if the option is available)

### Create New One

1. Click the "+" button
2. Select "MusicKit IDs"
3. Click "Continue"
4. Fill in:
   - **Description**: "Plylist Production"
   - **Identifier**: `com.yourname.plylist.prod` (use a different name)
5. Click "Register"
6. **Important**: Wait 15 minutes before testing

### Regenerate Token (Optional)

You don't need to regenerate your developer token - it's not tied to a specific MusicKit Identifier. The same token will work with any MusicKit Identifier under your account.

## Still Not Working?

### Check These Common Issues:

**1. Apple Music Account Region**

Some regions have restrictions. Try:
```bash
# In the diagnostic tool, check your storefront
# Should return 'us', 'gb', etc.
```

**2. Family Sharing Issues**

If you're on a Family Sharing plan:
- Make sure YOUR account has Apple Music access
- Family organizer might need to enable it for your account

**3. Free Trial Expired**

- Check if your Apple Music subscription is active
- Try playing a song in the Apple Music app

**4. Browser Issues**

Try a different browser:
- Safari usually works best for Apple services
- Chrome/Firefox also work but may have CORS issues
- Make sure cookies are enabled
- Make sure you're not in private/incognito mode

### Get More Details

Run the diagnostic tool and check the full error:

1. Open `scripts/diagnose_apple_music.html`
2. Follow all steps
3. Click "Show Debug Info"
4. Copy the log and check for specific error messages

## Technical Explanation

The authorization flow works like this:

1. **MusicKit.configure()** - Validates developer token ✅ (This works for you)
2. **musicKitInstance.authorize()** - Opens popup for user to sign in ❌ (This fails)
3. **Apple checks**:
   - Is the developer token valid? ✅
   - Does the account have an active MusicKit Identifier? ❓ (Likely issue)
   - Does the user have Apple Music subscription? ✅
4. **Returns user token** - Only if all checks pass

The "Unauthorized" error at step 2 means Apple rejected the authorization request before even showing you the login popup (or right after). This is different from a 403 during API calls.

## Success Indicators

You'll know it's fixed when:

✅ Authorization popup appears and you can sign in
✅ No "Unauthorized" error
✅ User token appears in the page
✅ Token is a long string (several hundred characters)

## Contact Support

If none of this works:

1. Copy your diagnostic logs
2. Check Apple Developer Forums
3. Contact Apple Developer Support (might be an account-specific issue)

## Quick Checklist

- [ ] MusicKit Identifier created in Apple Developer portal
- [ ] MusicKit Identifier shows as "Enabled"
- [ ] Waited 10-15 minutes after creating/modifying
- [ ] Tested developer token with test_api_direct.py (passes)
- [ ] Apple Music subscription is active (can play songs)
- [ ] Tried in Safari or Chrome (not incognito mode)
- [ ] Allowed cookies and popups for the page

If all boxes are checked and it still doesn't work, there may be an Apple-side issue with your account or region.
