#!/bin/bash
# Moves items in ~/Downloads older than 30 days into ~/Archive/Old Downloads/YYYY-MM.
# Triggered daily at 4:00 AM (and at login, to catch up on missed runs) by the launchd agent com.hcoderdm.organize-old-downloads.

SOURCE="$HOME/Downloads"
DEST="$HOME/Archive/Old Downloads"

STAMP="$HOME/.local/state/organize-old-downloads/last_run"

# Run at most once per 4:00 AM cycle. The agent also fires at login, so after the
# Mac was shut down at 4:00 AM this catches up; otherwise it exits immediately.
now=$(date +%s)
last_4am=$(date -j -f "%Y-%m-%d %H:%M:%S" "$(date +%F) 04:00:00" +%s)
[ "$now" -lt "$last_4am" ] && last_4am=$((last_4am - 86400))
last_run=$(cat "$STAMP" 2>/dev/null || echo 0)
[ "$last_run" -ge "$last_4am" ] && exit 0

mkdir -p "$DEST"
echo "---------- $(date '+%Y-%m-%d %H:%M:%S') Starting cleanup ----------"

find "$SOURCE" -mindepth 1 -maxdepth 1 -mtime +30 -print0 | while IFS= read -r -d '' item; do
    mod_epoch=$(stat -f %m "$item")
    year_month=$(date -r "$mod_epoch" +"%Y-%m")
    target="$DEST/$year_month"
    mkdir -p "$target"

    name=$(basename "$item")
    if [ -e "$target/$name" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') Skipped (name already exists in $target): $item"
        continue
    fi

    echo "$(date '+%Y-%m-%d %H:%M:%S') Moving: $item  →  $target  (modified: $(date -r "$mod_epoch"))"
    mv -n "$item" "$target/"
done

mkdir -p "$(dirname "$STAMP")"
date +%s > "$STAMP"
echo "---------- Cleanup finished ----------"
echo ""
