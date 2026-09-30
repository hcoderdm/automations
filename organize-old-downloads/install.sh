#!/bin/bash
# Installs (or reinstalls) the organize-old-downloads launch agent.
set -e
LABEL="com.hcoderdm.organize-old-downloads"
DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/Library/LaunchAgents/$LABEL.plist"

mkdir -p "$HOME/Library/LaunchAgents"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
cp "$DIR/$LABEL.plist" "$TARGET"
launchctl bootstrap "gui/$(id -u)" "$TARGET"
echo "Installed. View log: ~/Library/Logs/OrganizeOldDownloads.log"
