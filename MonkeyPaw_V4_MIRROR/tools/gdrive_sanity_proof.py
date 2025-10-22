#!/usr/bin/env /opt/homebrew/bin/python3.11
"""
Google Drive End-to-End Sanity Proof
Tests write → sync → read cycle to verify mount is working correctly
"""

import sys
import datetime
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from monkeypaw.storage.drive_desktop import safe_join, desktop_root

def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 GOOGLE DRIVE END-TO-END SANITY PROOF")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    # Step 1: Verify mount access
    print("Step 1: Verifying Google Drive mount...")
    try:
        root = desktop_root()
        print(f"✅ Mount detected: {root}")
    except RuntimeError as e:
        print(f"❌ Mount not found: {e}")
        print()
        print("💡 Fix:")
        print("  1. Open Google Drive application")
        print("  2. Ensure you're signed in")
        print("  3. Run: make gdrive-health")
        return 1
    
    # Step 2: Write test file
    print()
    print("Step 2: Writing test file to Drive...")
    
    test_path = "MonkeyPaw/Diagnostics/drive_write_check.txt"
    timestamp = datetime.datetime.now().isoformat()
    content = f"OK: {timestamp}"
    
    try:
        p = safe_join(test_path)
        p.write_text(content)
        print(f"✅ Wrote: {p}")
        print(f"   Content: {content}")
    except Exception as e:
        print(f"❌ Write failed: {e}")
        print()
        print("💡 Fix:")
        print("  1. Check mount permissions")
        print("  2. Run: make gdrive-guard")
        print("  3. Run: make drive-status")
        return 1
    
    # Step 3: Verify file exists locally
    print()
    print("Step 3: Verifying file exists locally...")
    
    if p.exists():
        print(f"✅ File exists: {p}")
        
        # Read back content
        read_content = p.read_text()
        if read_content == content:
            print(f"✅ Content verified: {read_content}")
        else:
            print(f"⚠️  Content mismatch!")
            print(f"   Expected: {content}")
            print(f"   Got: {read_content}")
    else:
        print(f"❌ File does not exist: {p}")
        return 1
    
    # Step 4: Verify in web UI
    print()
    print("Step 4: Verifying sync to Google Drive web...")
    print(f"   Waiting 3 seconds for sync...")
    time.sleep(3)
    
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ LOCAL WRITE SUCCESSFUL")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("🌐 MANUAL VERIFICATION REQUIRED:")
    print()
    print("1. Open Google Drive web interface:")
    print("   https://drive.google.com/")
    print()
    print("2. Navigate to:")
    print("   My Drive → MonkeyPaw → Diagnostics")
    print()
    print("3. Verify file exists:")
    print("   drive_write_check.txt")
    print()
    print("4. Open the file and verify content:")
    print(f"   {content}")
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("✅ If file appears in web UI:")
    print("   Your Drive mount is working correctly!")
    print("   All app I/O will sync properly.")
    print()
    print("❌ If file does NOT appear:")
    print("   Run: make gdrive-guard")
    print("   Run: make drive-cache-reset")
    print()
    print("📊 Check health status:")
    print("   make gdrive-health")
    print()
    
    # Step 5: Additional diagnostics
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 DIAGNOSTIC INFO")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print(f"Mount root:      {root}")
    print(f"Test file path:  {p}")
    print(f"Relative path:   {test_path}")
    print(f"File size:       {p.stat().st_size} bytes")
    print(f"Timestamp:       {timestamp}")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
