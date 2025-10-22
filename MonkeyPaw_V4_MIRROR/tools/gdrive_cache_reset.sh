#!/usr/bin/env bash
# Google Drive Cache Clean-Reset - Safe cleanup for persistent popup issues
# Removes logs and caches while preserving account configuration

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🧹 GOOGLE DRIVE CACHE CLEAN-RESET${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will clear Google Drive logs and caches${NC}"
echo -e "${YELLOW}   Account configuration and Stream mode settings will be preserved${NC}"
echo -e "${YELLOW}   Contents will re-index without re-downloading files${NC}"
echo ""
echo -e "${BLUE}This operation is safe and recommended for:${NC}"
echo "  • Persistent 'Unsynced items' popups"
echo "  • Sync status stuck or stale"
echo "  • Drive re-indexing after recovery"
echo ""

# Confirmation prompt
read -p "Continue with cache clean-reset? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cancelled by user${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}Step 1: Stopping Google Drive...${NC}"

# Check if Drive is running
if ps aux | grep -i "google drive" | grep -v grep >/dev/null 2>&1; then
    echo "  • Quitting Google Drive app..."
    killall "Google Drive" 2>/dev/null || true
    sleep 3
    
    # Force kill if still running
    if ps aux | grep -i "google drive" | grep -v grep >/dev/null 2>&1; then
        echo "  • Force stopping remaining processes..."
        pkill -9 -i "google drive" 2>/dev/null || true
        sleep 2
    fi
    
    echo -e "  ${GREEN}✅ Google Drive stopped${NC}"
else
    echo -e "  ${BLUE}ℹ️  Google Drive not running${NC}"
fi

echo ""
echo -e "${CYAN}Step 2: Cleaning cache directories...${NC}"

# Clear logs (safe - will be recreated)
LOGS_DIR="$HOME/Library/Application Support/Google/DriveFS/Logs"
if [[ -d "$LOGS_DIR" ]]; then
    echo "  • Removing DriveFS logs..."
    rm -rf "$LOGS_DIR" || true
    echo -e "  ${GREEN}✅ Logs cleared${NC}"
else
    echo -e "  ${BLUE}ℹ️  No logs directory found${NC}"
fi

# Clear caches (safe - will be recreated)
CACHE_DIR="$HOME/Library/Caches/com.google.drivefs"
if [[ -d "$CACHE_DIR" ]]; then
    echo "  • Removing DriveFS cache..."
    rm -rf "$CACHE_DIR" || true
    echo -e "  ${GREEN}✅ Cache cleared${NC}"
else
    echo -e "  ${BLUE}ℹ️  No cache directory found${NC}"
fi

# Also clear any temporary files
TEMP_CACHE="$HOME/Library/Caches/com.google.GoogleDrive"
if [[ -d "$TEMP_CACHE" ]]; then
    echo "  • Removing additional caches..."
    rm -rf "$TEMP_CACHE" || true
    echo -e "  ${GREEN}✅ Additional caches cleared${NC}"
fi

echo ""
echo -e "${CYAN}Step 3: Restarting Google Drive...${NC}"

echo "  • Starting Google Drive app..."
open -a "Google Drive"
sleep 3

# Wait for process to start
WAIT_COUNT=0
while ! ps aux | grep -i "google drive" | grep -v grep >/dev/null 2>&1; do
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
    if [[ $WAIT_COUNT -gt 15 ]]; then
        echo -e "  ${YELLOW}⚠️  Google Drive taking longer than expected to start${NC}"
        echo -e "  ${BLUE}Please check the menu bar for Google Drive icon${NC}"
        break
    fi
done

if ps aux | grep -i "google drive" | grep -v grep >/dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Google Drive started${NC}"
else
    echo -e "  ${YELLOW}⚠️  Please manually check Google Drive status${NC}"
fi

echo ""
echo -e "${CYAN}Step 4: Waiting for mount to initialize...${NC}"

# Wait for mount to appear
MOUNT_WAIT=0
while true; do
    MOUNT_COUNT=$(find ~/Library/CloudStorage -maxdepth 1 -type d -name "GoogleDrive-*" 2>/dev/null | wc -l | xargs)
    if [[ $MOUNT_COUNT -gt 0 ]]; then
        echo -e "  ${GREEN}✅ Mount detected ($MOUNT_COUNT mount(s))${NC}"
        break
    fi
    
    sleep 2
    MOUNT_WAIT=$((MOUNT_WAIT + 2))
    
    if [[ $MOUNT_WAIT -ge 30 ]]; then
        echo -e "  ${YELLOW}⚠️  Mount not yet detected${NC}"
        echo -e "  ${BLUE}Please wait for Google Drive to finish initializing${NC}"
        break
    fi
done

echo ""
echo -e "${CYAN}Step 5: Running post-reset health checks...${NC}"

sleep 5  # Give Drive time to settle

echo ""
echo -e "${BLUE}Running: make gdrive-guard${NC}"
make gdrive-guard || true

echo ""
echo -e "${BLUE}Running: make gdrive-recover${NC}"
make gdrive-recover || true

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ CACHE CLEAN-RESET COMPLETE${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}What happened:${NC}"
echo "  • Cleared DriveFS logs and caches"
echo "  • Preserved account configuration"
echo "  • Restarted Google Drive"
echo "  • Re-indexed mount structure"
echo ""
echo -e "${BLUE}What to expect:${NC}"
echo "  • Drive will re-index your files (no re-download)"
echo "  • Stream mode settings preserved"
echo "  • Sync status will reset and update"
echo "  • Popups should stop appearing"
echo ""
echo -e "${YELLOW}If popup persists:${NC}"
echo "  • Run: make gdrive-health"
echo "  • Check: System Settings → Google Drive permissions"
echo "  • Consider: Signing out and back in (last resort)"
echo ""
echo -e "${CYAN}Monitor status with:${NC}"
echo "  make gdrive-dashboard"
