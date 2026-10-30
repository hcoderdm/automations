#!/bin/bash
# Removes automations' launchd agents and their apps.
#
# Usage: ./uninstall.sh [NAME...]   e.g. ./uninstall.sh organize-old-downloads
#   With no names, uninstalls every folder that has an automation.conf.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
[ -f "$ROOT/.env" ] && . "$ROOT/.env"
PREFIX="${LABEL_PREFIX:-com.$(id -un)}"

if [ $# -eq 0 ]; then
    set -- $(cd "$ROOT" && ls -d */ | while read -r d; do [ -f "$d/automation.conf" ] && echo "$d"; done)
fi

for name in "$@"; do
    DIR="$ROOT/${name%/}"
    [ -f "$DIR/automation.conf" ] || { echo "No automation.conf in $DIR"; exit 1; }
    # shellcheck source=/dev/null
    . "$DIR/automation.conf"
    # Named after the folder, as in install.sh.
    NAME=$(basename "$DIR")
    LABEL="$PREFIX.$NAME"
    APP_NAME=$(echo "$NAME" | awk -F- '{for (i = 1; i <= NF; i++) printf "%s", toupper(substr($i, 1, 1)) substr($i, 2)}')
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
    rm -f "$HOME/Library/LaunchAgents/$LABEL.plist"
    rm -rf "$HOME/Applications/Automations/$APP_NAME.app"
    rm -f "$DIR/$NAME.log"
    echo "Uninstalled $NAME."
done
rmdir "$HOME/Applications/Automations" 2>/dev/null || true
