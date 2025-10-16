#!/usr/bin/env bash
#
# Backup MonkeyPaw Production v4 to Google Drive - COMPLETE BACKUP
#

set -euo pipefail

PROJECT_DIR="/Users/thomasbrianreynolds/monkey paw production v4"
BACKUP_NAME="monkeypaw_backup_$(date +'%Y%m%d_%H%M%S')"

echo "🔄 Creating COMPLETE backup to Google Drive..."
echo ""

# Find Google Drive directory
GDRIVE_PATH=$(find "$HOME/Library/CloudStorage" -maxdepth 1 -name "GoogleDrive-*" -type d 2>/dev/null | head -1)

if [ -z "$GDRIVE_PATH" ]; then
    echo "❌ Google Drive not found!"
    echo ""
    echo "Please ensure Google Drive is:"
    echo "  1. Installed on your Mac"
    echo "  2. Signed in and syncing"
    echo "  3. Located in ~/Library/CloudStorage/"
    echo ""
    exit 1
fi

# Use custom path if set, otherwise use found Google Drive
if [ -n "${GDRIVE_BACKUP_DIR:-}" ]; then
    BACKUP_DIR="$GDRIVE_BACKUP_DIR"
else
    BACKUP_DIR="$GDRIVE_PATH/My Drive/MonkeyPaw Backups"
fi

echo "📂 Backup destination: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Create COMPLETE backup archive (including output files!)
BACKUP_FILE="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"

cd "$PROJECT_DIR"

echo "📦 Creating COMPLETE archive (including all output files)..."
tar -czf "$BACKUP_FILE" \
    --exclude='.venv' \
    --exclude='venv_mlx' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='node_modules' \
    .

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

echo ""
echo "✅ COMPLETE backup finished!"
echo "📁 Location: $BACKUP_FILE"
echo "📊 Size: $BACKUP_SIZE"
echo ""
echo "Backed up:"
echo "  ✅ All Python code"
echo "  ✅ All configurations"
echo "  ✅ All documentation"
echo "  ✅ All databases"
echo "  ✅ ALL OUTPUT FILES (avatars, TTS, bgrem)"
echo "  ✅ Everything needed for YouTube shipping"
echo ""
echo "To restore:"
echo "  cd /path/to/restore"
echo "  tar -xzf '$BACKUP_FILE'"
echo ""
