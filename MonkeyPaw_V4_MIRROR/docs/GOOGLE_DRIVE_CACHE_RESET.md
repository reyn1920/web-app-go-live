# Google Drive Cache Clean-Reset Guide

## Purpose

The cache clean-reset removes Google Drive's local logs and cache while preserving your account configuration and Stream mode settings. This is a **safe operation** that forces Drive to re-index your files without re-downloading them.

## When to Use

Run `make drive-cache-reset` if you experience:

- **Persistent "Unsynced items" popup** after running recovery
- **Stuck sync status** that won't update
- **Stale file listings** or missing files in mount
- **Drive re-indexing issues** after moving files

## What It Does

### Safe Operations (Preserved)
✅ Account configuration
✅ Stream mode settings  
✅ Sign-in credentials
✅ Shared drive associations
✅ File availability preferences

### Cleared (Will Be Recreated)
🗑️ DriveFS logs (`~/Library/Application Support/Google/DriveFS/Logs`)
🗑️ DriveFS cache (`~/Library/Caches/com.google.drivefs`)
🗑️ Additional caches (`~/Library/Caches/com.google.GoogleDrive`)

## Usage

### Quick Command
```bash
make drive-cache-reset
```

### Manual Steps (equivalent)
```bash
# 1. Quit Google Drive
killall "Google Drive" 2>/dev/null || true

# 2. Clear cache directories
rm -rf "$HOME/Library/Application Support/Google/DriveFS/Logs" || true
rm -rf "$HOME/Library/Caches/com.google.drivefs" || true
rm -rf "$HOME/Library/Caches/com.google.GoogleDrive" || true

# 3. Restart Google Drive
open -a "Google Drive"

# 4. Run health checks
sleep 10
make gdrive-guard
make gdrive-recover
```

## Expected Behavior

### Immediate Effects
- Google Drive will restart
- Mount will disappear briefly (~5-10 seconds)
- Mount will reappear with same path
- Drive icon in menu bar may show "Indexing..."

### Short-Term (Minutes)
- Drive re-indexes all files (no download)
- Sync status updates to current state
- "Unsynced items" popup should stop
- File listings may update

### No Impact On
- **Local files:** Your Stream files stay available
- **Download size:** No re-download of 5TB+ libraries
- **Account settings:** Sign-in, preferences preserved
- **Shared drives:** Associations maintained

## Safety Notes

### This Operation Is Safe Because:
1. **No file deletion:** Only clears logs and temp cache
2. **No re-download:** Stream mode preserved, files not re-copied
3. **No account loss:** Configuration files untouched
4. **Reversible:** Drive recreates cache automatically

### Critical Directories NOT Touched:
- `~/Library/Application Support/Google/DriveFS/[account_id]/`
- `~/Library/CloudStorage/GoogleDrive-*` (your mounts)
- Account-specific configuration

## Workflow Integration

### Recommended Order for Persistent Issues:
```bash
# 1. Initial recovery
make drive-recover

# 2. If popup persists, clean cache
make drive-cache-reset

# 3. Health check
make gdrive-health

# 4. Monitor status
make gdrive-dashboard
```

### Full Recovery Workflow:
```bash
# Complete reset and recovery
make drive-cache-reset
sleep 10
make drive-recovery-full
make gdrive-health
```

## Troubleshooting

### If Cache Reset Doesn't Help:

**Check permissions:**
```bash
make drive-status
```
Ensure Google Drive has "Files and Folders" access in System Settings.

**Check mount health:**
```bash
make gdrive-health
```
Look for mount accessibility issues.

**Clean old mounts:**
```bash
make drive-cleanup
```
Remove duplicate/stale mounts.

**Last resort - Sign out/in:**
Only if all else fails:
1. Google Drive menu → Settings → Accounts → Sign out
2. Run `make drive-cache-reset`
3. Sign back in
4. Run `make drive-recovery-full`

## Monitoring

### After Cache Reset:
```bash
# Watch real-time status (updates every 5s)
make gdrive-dashboard

# Or single check
make gdrive-dashboard-once
```

### Health Score:
A successful reset should show:
- **Health Score:** 90-100 (Excellent/Good)
- **Process Running:** ✅
- **Single Mount:** ✅  
- **No Unsynced Files:** ✅

## Technical Details

### What Happens Internally:
1. **Stop Drive:** Graceful quit, force kill if needed
2. **Clear cache:** Remove logs, caches (preserving config)
3. **Restart Drive:** Launch app, wait for mount
4. **Re-index:** Drive scans CloudStorage structure
5. **Verify:** Run guard and recovery checks

### Cache Structure:
```
~/Library/
├── Application Support/
│   └── Google/
│       └── DriveFS/
│           ├── Logs/           ← Cleared (recreated)
│           ├── [account_id]/    ← PRESERVED
│           └── Content_cache/   ← Cleared
├── Caches/
│   ├── com.google.drivefs/      ← Cleared
│   └── com.google.GoogleDrive/  ← Cleared
└── CloudStorage/
    └── GoogleDrive-*/           ← PRESERVED (your mount)
```

## Additional Resources

- **Health monitoring:** `make gdrive-health`
- **Automated fixes:** `make gdrive-guard`
- **Recovery workflow:** `make drive-recovery-full`
- **Mount detection:** `make drive-detect`
- **Status check:** `make drive-status`
