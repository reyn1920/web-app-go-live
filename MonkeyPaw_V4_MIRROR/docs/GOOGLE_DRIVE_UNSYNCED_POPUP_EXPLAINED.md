# Google Drive "Unsynced Items" Popup - Root Cause & Fix

## What the Popup Actually Means

The **"Unsynced items recovered by the system"** popup appears when macOS File Provider detects files that were created in a **stray location** instead of the actual Google Drive mount.

### Technical Explanation

**Root Cause:**
Files were written to a path that **looked like** Google Drive but wasn't the active mount:

```
❌ WRONG: ~/Google Drive/MonkeyPaw/video.mp4
❌ WRONG: ~/GoogleDrive/MonkeyPaw/video.mp4
❌ WRONG: ~/Library/CloudStorage/GoogleDrive-old-timestamp/...

✅ RIGHT: ~/Library/CloudStorage/GoogleDrive-brianinpty@gmail.com/My Drive/...
```

**Why This Happens:**
1. Google Drive wasn't running when files were written
2. App used a hardcoded path instead of intelligent detection
3. Multiple mounts existed (old + new)
4. Files went to the wrong mount

**macOS File Provider Response:**
- Detects "orphaned" files in recovery areas
- Moves them to a holding area: `~/Google Drive - Unsynced Items`
- Shows persistent popup until you manually choose destination
- **These files will NEVER sync** until moved to the correct mount

## Why Our Fix Works

### 1. Intelligent Mount Detection
`tools/drive_desktop_detect.py` finds the **active mount**:
```python
# Finds the mount with actual files in "My Drive"
# Ignores old/stale/timestamped mounts
```

### 2. Guaranteed Mount Usage
`monkeypaw/storage/drive_desktop.py` ensures all writes go to correct mount:
```python
from monkeypaw.storage.drive_desktop import safe_join

# ✅ Always uses the detected active mount
p = safe_join("MonkeyPaw/Videos/output.mp4")
p.write_text("content")
```

**Fail-Fast Behavior:**
- If Drive isn't mounted → RuntimeError (prevents stray writes)
- If "My Drive" missing → RuntimeError (prevents wrong location)
- If mount inaccessible → RuntimeError (prevents failed writes)

### 3. Recovery Automation
- `make drive-recover`: Moves unsynced files to correct mount
- `make drive-cleanup`: Removes old/duplicate mounts
- `make gdrive-guard`: Auto-fixes common issues

### 4. Cache Reset
- `make drive-cache-reset`: Clears stale sync state
- Forces Drive to re-index without re-downloading

## End-to-End Sanity Proof

### Purpose
Verify that write → sync → read cycle works correctly.

### How to Run
```bash
make drive-sanity-proof
```

### What It Does
1. **Detects mount**: Uses intelligent detection
2. **Writes test file**: To `My Drive/MonkeyPaw/Diagnostics/drive_write_check.txt`
3. **Verifies locally**: Confirms file exists and content matches
4. **Instructs manual check**: Guides you to verify in web UI

### Expected Output
```
✅ Mount detected: /Users/.../GoogleDrive-brianinpty@gmail.com
✅ Wrote: .../My Drive/MonkeyPaw/Diagnostics/drive_write_check.txt
✅ File exists: ...
✅ Content verified: OK: 2025-10-22T05:11:38.857060
```

### Manual Verification
1. Open https://drive.google.com/
2. Navigate: My Drive → MonkeyPaw → Diagnostics
3. Verify file: `drive_write_check.txt`
4. Check content matches timestamp

## If Popup Still Appears

### Step 1: Run Full Diagnostic
```bash
make gdrive-health
```

### Step 2: Check What Path the Popup Shows
When you click "Choose destination" in the popup, **screenshot the exact folder path** that appears.

**Common Wrong Paths:**
- `~/Google Drive` (without CloudStorage prefix)
- `~/GoogleDrive` (no space, no CloudStorage)
- `~/Library/CloudStorage/GoogleDrive-[old-timestamp]`

**Correct Path Pattern:**
- `~/Library/CloudStorage/GoogleDrive-[email]/My Drive/...`

### Step 3: Run Recovery Workflow
```bash
# If popup shows unsynced files
make drive-recover

# If you still see issues
make drive-cache-reset

# Verify health
make gdrive-health
```

### Step 4: Check Console Output
Run diagnostics and capture output:
```bash
make gdrive-guard > /tmp/guard-output.txt 2>&1
make gdrive-recover > /tmp/recover-output.txt 2>&1
```

**Look for:**
- "Mount not accessible" → Permission issue
- "Multiple mounts detected" → Run `make drive-cleanup`
- "Unsynced files found" → Recovery script should fix
- "RuntimeError" → Mount or path issue

## Technical Details

### File Provider Architecture
```
Your App
    ↓
safe_join("MonkeyPaw/video.mp4")
    ↓
~/Library/CloudStorage/GoogleDrive-email/My Drive/MonkeyPaw/video.mp4
    ↓
macOS File Provider
    ↓
Google Drive Sync Engine
    ↓
Google Drive Cloud
```

### Recovery Holding Areas
macOS puts unsynced files in these locations:
- `~/Google Drive - Unsynced Items`
- `~/GoogleDrive-UnsyncedItems`
- `~/Library/Application Support/Google/DriveFS/Unsynced Items`
- `~/Library/CloudStorage/GoogleDrive-*.recovered`

### Our Recovery Process
1. **Detect active mount** (`drive_desktop_detect.py`)
2. **Find unsynced files** in holding areas
3. **Move safely** using `rsync` (deduplication, resume)
4. **Place in mount** at `My Drive/Recovered_from_system/`
5. **Verify sync** (files now visible in web UI)

## Prevention Strategy

### For Developers
**Always use `safe_join`:**
```python
from monkeypaw.storage.drive_desktop import safe_join

# ✅ Correct - uses active mount
output_path = safe_join("MonkeyPaw/Videos/output.mp4")

# ❌ Wrong - hardcoded path
output_path = Path("~/Google Drive/MonkeyPaw/Videos/output.mp4")
```

### For Operations
**Use health monitoring:**
```bash
# Daily health check
make gdrive-health

# Continuous monitoring
make gdrive-dashboard

# Automated fixes
make gdrive-guard
```

### For CI/CD
**Pre-flight checks:**
```bash
# Before video pipeline runs
make gdrive-health || exit 1
make drive-sanity-proof || exit 1

# Run pipeline
python main_orchestrator.py

# Post-flight verification
make gdrive-health
```

## Debugging Checklist

### If Files Don't Appear in Web UI
- [ ] Run `make drive-sanity-proof` - does it succeed?
- [ ] Check `make gdrive-health` - what's the health score?
- [ ] Multiple mounts? Run `make drive-cleanup`
- [ ] Unsynced files? Run `make drive-recover`
- [ ] Stuck sync? Run `make drive-cache-reset`

### If RuntimeError on Write
- [ ] Is Google Drive running? Check menu bar icon
- [ ] Is mount accessible? Run `make drive-status`
- [ ] Permissions granted? System Settings → Google Drive
- [ ] Correct mount? Run `make drive-detect`

### If Popup Returns
- [ ] Screenshot the "Choose destination" path
- [ ] Run `make gdrive-guard > /tmp/guard.log 2>&1`
- [ ] Run `make drive-recover > /tmp/recover.log 2>&1`
- [ ] Share logs and screenshot for debugging

## Success Indicators

### Your System is Healthy When:
- ✅ `make drive-sanity-proof` succeeds
- ✅ `make gdrive-health` shows 90+ score
- ✅ Single mount detected (no duplicates)
- ✅ No unsynced files in holding areas
- ✅ Test file appears in web UI within 5 seconds
- ✅ No popup after recovery

### All App I/O Will Work When:
- ✅ `desktop_root()` returns correct mount
- ✅ `safe_join()` creates files in mount
- ✅ Files appear in web UI immediately
- ✅ Pipeline can write videos to Drive
- ✅ No RuntimeError during operations

## Additional Resources

- **Health Check:** `make gdrive-health`
- **Auto-Fix:** `make gdrive-guard`
- **Recovery:** `make drive-recovery-full`
- **Sanity Proof:** `make drive-sanity-proof`
- **Monitor:** `make gdrive-dashboard`
- **Cache Reset:** `make drive-cache-reset`
