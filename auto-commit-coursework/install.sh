#!/bin/bash
# Installs (or reinstalls) the coursework auto-commit launch agent (daily at 4:00 AM).
set -e
LABEL="com.hcoderdm.coursework-autocommit"
DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/Library/LaunchAgents/$LABEL.plist"

mkdir -p "$HOME/Library/LaunchAgents"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
# Fill in this machine's paths; the plist in the repo only has placeholders.
sed -e "s|__DIR__|$DIR|g" -e "s|__HOME__|$HOME|g" "$DIR/$LABEL.plist" > "$TARGET"
ln -sf "$HOME/Library/Logs/coursework-autocommit.log" "$DIR/coursework-autocommit.log"
launchctl bootstrap "gui/$(id -u)" "$TARGET"
echo "Installed. View log: ~/Library/Logs/coursework-autocommit.log"
