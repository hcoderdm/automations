#!/bin/bash
# Installs (or reinstalls) the coursework auto-commit launch agent (daily at 4:00 AM).
set -e
LABEL="com.hcoderdm.coursework-autocommit"
DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/Library/LaunchAgents/$LABEL.plist"

mkdir -p "$HOME/Library/LaunchAgents"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
cp "$DIR/$LABEL.plist" "$TARGET"
launchctl bootstrap "gui/$(id -u)" "$TARGET"
echo "Installed. View log: ~/Library/Logs/coursework-autocommit.log"
