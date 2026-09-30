# Organize Old Downloads

Moves anything in `~/Downloads` older than 30 days into `~/Archive/Old Downloads`, sorted into folders by month (`2026-08`, `2026-09`, and so on). The month comes from when the file was last modified.

It runs every day at 4:00 AM. It also runs at login, so if the Mac was off at 4:00 it catches up then. It only does the cleanup once per day either way.

If a file with the same name is already in the month folder, it leaves the download where it is and notes that in the log.

## Setup

```bash
./install.sh
./uninstall.sh
```

## Running

```bash
./organize_old_downloads.sh
```

If it already ran since the last 4:00 AM it exits without doing anything. Delete `~/.local/state/organize-old-downloads/last_run` to force it.

The log is at `~/Library/Logs/OrganizeOldDownloads.log`, and `OrganizeOldDownloads.log` in this folder links to it.
