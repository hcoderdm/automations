# Organize Old Downloads

Moves anything added to `~/Downloads` more than 30 days ago into a year folder and then a month folder inside `~/Downloads` (`2026/08`, `2026/09`, and so on). The age, year and month come from the date the item was added to Downloads (falling back to its modified date when Spotlight doesn't know), since many downloads keep the server's modified date. Hidden files and the year folders themselves are left alone.

It's scheduled for 4:00 AM. If the Mac is asleep then, launchd runs it when the Mac wakes, and it also runs at login, so if the Mac was off it catches up then. It only does the cleanup once per day either way.

If a file with the same name is already in the month folder, it leaves the download where it is and notes that in the log.

## Setup

```bash
./install.sh
./uninstall.sh
```

launchd needs permission to read `~/Downloads`: in System Settings > Privacy & Security > Full Disk Access, add `/bin/bash` (press Cmd+Shift+G in the file picker and type the path). Without it the log says it can't read Downloads, and it tries again at next login.

## Running

```bash
./organize_old_downloads.sh
```

If it already ran since the last 4:00 AM it exits without doing anything. Delete `~/.local/state/organize-old-downloads/last_run` to force it.

The log is at `~/Library/Logs/OrganizeOldDownloads.log`, and `OrganizeOldDownloads.log` in this folder links to it.
