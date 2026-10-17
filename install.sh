#!/bin/bash
# Installs (or reinstalls) automations as launchd agents.
#
# Usage: ./install.sh [NAME...]   e.g. ./install.sh organize-old-downloads
#   With no names, installs every folder that has an automation.conf.
#
# macOS won't let a launchd job read ~/Documents or ~/Downloads without permission, so each
# script is wrapped in its own small app in ~/Applications/Automations. The app asks for access
# to just that automation's folder, so bash and python never need Full Disk Access. The script
# is sealed inside the signed app, so editing it means running this again to rebuild the app,
# and macOS may ask for access again.
#
# Each automation folder has:
#   automation.conf  INTERPRETER, SCRIPT, ACCESS_DIR (relative to $HOME),
#                    USAGE_KEY (e.g. NSDownloadsFolderUsageDescription), USAGE_TEXT
#   launchd.plist    launchd plist with __LABEL__, __PROGRAM__ and __LOG__ placeholders
# The launchd label, app and log are named after the folder, so `organize-old-downloads` is
# com.hcoderdm.organize-old-downloads, OrganizeOldDownloads.app and organize-old-downloads.log.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
APPS="$HOME/Applications/Automations"
PREFIX="com.hcoderdm"

# Builds $APPS/$APP_NAME.app around $DIR/$SCRIPT with launcher.c as its executable, and signs it.
build_app() {
    APP="$APPS/$APP_NAME.app"
    rm -rf "$APP"
    mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
    clang -O2 -Wall -o "$APP/Contents/MacOS/$APP_NAME" "$ROOT/launcher.c" \
        -DINTERPRETER="\"$INTERPRETER\"" -DSCRIPT="\"$SCRIPT\"" -DACCESS_DIR="\"$ACCESS_DIR\""
    cp "$DIR/$SCRIPT" "$APP/Contents/Resources/"
    cat > "$APP/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleIdentifier</key>
  <string>$LABEL</string>
  <key>CFBundleName</key>
  <string>$APP_NAME</string>
  <key>CFBundleExecutable</key>
  <string>$APP_NAME</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSUIElement</key>
  <true/>
  <key>$USAGE_KEY</key>
  <string>$USAGE_TEXT</string>
</dict>
</plist>
EOF
    codesign --force --sign - --identifier "$LABEL" "$APP" 2>/dev/null
}

install_one() {
    DIR="$ROOT/${1%/}"
    [ -f "$DIR/automation.conf" ] || { echo "No automation.conf in $DIR"; return 1; }
    # shellcheck source=/dev/null
    . "$DIR/automation.conf"
    NAME=$(basename "$DIR")
    LABEL="$PREFIX.$NAME"
    APP_NAME=$(echo "$NAME" | awk -F- '{for (i = 1; i <= NF; i++) printf "%s", toupper(substr($i, 1, 1)) substr($i, 2)}')
    LOG="$NAME.log"
    TARGET="$HOME/Library/LaunchAgents/$LABEL.plist"
    echo "== $NAME"

    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
    build_app

    # Ask for folder access now, while someone is here to click Allow, not at 4:00 AM.
    echo "Checking access to ~/$ACCESS_DIR. If macOS asks, click Allow."
    out=$(mktemp)
    open -W -g --stdout "$out" --stderr "$out" "$APP" --args --check-access
    cat "$out"; rm -f "$out"

    # Fill in this machine's paths; the plist in the repo only has placeholders.
    mkdir -p "$HOME/Library/LaunchAgents"
    sed -e "s|__LABEL__|$LABEL|g" -e "s|__PROGRAM__|$APP/Contents/MacOS/$APP_NAME|g" \
        -e "s|__LOG__|$HOME/Library/Logs/$LOG|g" "$DIR/launchd.plist" > "$TARGET"
    ln -sf "$HOME/Library/Logs/$LOG" "$DIR/$LOG"
    launchctl bootstrap "gui/$(id -u)" "$TARGET"
    echo "Installed. View log: ~/Library/Logs/$LOG"
}

if [ $# -eq 0 ]; then
    set -- $(cd "$ROOT" && ls -d */ | while read -r d; do [ -f "$d/automation.conf" ] && echo "$d"; done)
fi
for name in "$@"; do
    install_one "$name"
done
