#!/bin/bash
# Moves items in ~/Downloads added more than 30 days ago into ~/Downloads/YYYY/MM, by date added.
# Triggered daily at 4:00 AM (and at login, to catch up on missed runs) by the launchd agent com.yourname.organize-old-downloads.

DOWNLOADS="$HOME/Downloads"

STAMP="$HOME/.local/state/organize-old-downloads/last_run"

# Run at most once per 4:00 AM cycle. The agent also fires at login, so after the
# Mac was shut down at 4:00 AM this catches up; otherwise it exits immediately.
now=$(date +%s)
last_4am=$(date -j -f "%Y-%m-%d %H:%M:%S" "$(date +%F) 04:00:00" +%s)
[ "$now" -lt "$last_4am" ] && last_4am=$((last_4am - 86400))
last_run=$(cat "$STAMP" 2>/dev/null || echo 0)
[ "$last_run" -ge "$last_4am" ] && exit 0

# Without access granted to the OrganizeOldDownloads app, launchd can't read ~/Downloads. Say so instead of
# silently moving nothing, and don't stamp the run so it retries at next login.
if ! ls "$DOWNLOADS" >/dev/null 2>&1; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') Stopped: can't read $DOWNLOADS (run ./install.sh organize-old-downloads and click Allow, or allow OrganizeOldDownloads in System Settings > Privacy & Security > Files & Folders)"
    exit 1
fi

echo "---------- $(date '+%Y-%m-%d %H:%M:%S') Starting cleanup ----------"

# When an item landed in Downloads. Modified dates are no good for this, since many downloads
# keep the server's date; fall back to it only when Spotlight has no "date added".
added_epoch() {
    local added
    added=$(mdls -raw -name kMDItemDateAdded "$1" 2>/dev/null)
    if [ -n "$added" ] && [ "$added" != "(null)" ] && date -j -f "%Y-%m-%d %H:%M:%S %z" "$added" +%s 2>/dev/null; then
        return
    fi
    stat -f %m "$1"
}

cutoff=$((now - 30 * 86400))

# Skip hidden files (.DS_Store, .localized) and the year folders themselves.
find "$DOWNLOADS" -mindepth 1 -maxdepth 1 ! -name '.*' ! -regex '.*/[0-9]\{4\}' -print0 | while IFS= read -r -d '' item; do
    added=$(added_epoch "$item")
    [ "$added" -ge "$cutoff" ] && continue
    target="$DOWNLOADS/$(date -r "$added" +%Y)/$(date -r "$added" +%m)"

    name=$(basename "$item")
    if [ -e "$target/$name" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') Skipped (name already exists in $target): $item"
        continue
    fi

    mkdir -p "$target"
    echo "$(date '+%Y-%m-%d %H:%M:%S') Moving: $item  →  $target  (added: $(date -r "$added"))"
    mv -n "$item" "$target/"
done

mkdir -p "$(dirname "$STAMP")"
date +%s > "$STAMP"
echo "---------- Cleanup finished ----------"
echo ""
