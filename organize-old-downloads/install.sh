#!/bin/bash
# Installs (or reinstalls) the organize-old-downloads launch agent.
set -e
LABEL="com.yourname.organize-old-downloads"
DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/Library/LaunchAgents/$LABEL.plist"

mkdir -p "$HOME/Library/LaunchAgents"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
# Fill in this machine's paths; the plist in the repo only has placeholders.
sed -e "s|__DIR__|$DIR|g" -e "s|__HOME__|$HOME|g" "$DIR/$LABEL.plist" > "$TARGET"
ln -sf "$HOME/Library/Logs/OrganizeOldDownloads.log" "$DIR/OrganizeOldDownloads.log"
launchctl bootstrap "gui/$(id -u)" "$TARGET"
echo "Installed. View log: ~/Library/Logs/OrganizeOldDownloads.log"
