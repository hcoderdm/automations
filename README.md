# Automations

Small automations for my personal use. Both scripts that run on my Mac, and Claude routines that run on claude.ai.

Mac Scripts:

- [auto-commit-coursework](auto-commit-coursework) commits changes in `~/Documents/coursework` once a day.
- [organize-old-downloads](organize-old-downloads) moves downloads added more than 30 days ago into `~/Downloads/YYYY/MM` once a day.

Claude routines:

- [check-pool-hours](check-pool-hours) warns me if a pool won't be open for one of my swims in the next 3 days.
- [scan-for-event-invites](scan-for-event-invites) finds events in my email, scores them, and adds the ones I pick to my calendar.

The scripts are scheduled for 4:00 AM. If the Mac is asleep then, launchd runs them when it wakes, so the logs usually show a later time. The routines run on claude.ai on a schedule, not on this Mac. Each routine's folder has a copy of its prompt in `prompt.md` and its response formats in `template.md`. Editing them doesn't change the routine.

Each script's folder has the script, a launchd plist, an `automation.conf` describing it, and a link to its log in `~/Library/Logs`. Install and remove them from here:

```bash
# For all automations
./install.sh
./uninstall.sh
# For a particular automation
./install.sh organize-old-downloads
./uninstall.sh organize-old-downloads
```

After editing a script or plist, run `./install.sh` for it again.

macOS won't let a launchd job read `~/Documents` or `~/Downloads` without permission, so `install.sh` wraps each script in its own small app in `~/Applications/Automations` and asks macOS for access to just that job's folder. Please click Allow when it asks. Note that nothing needs Full Disk Access. The script is sealed inside the app, so editing it means reinstalling to rebuild the app, and macOS may ask for access again.

To see what's loaded:

```bash
launchctl list | grep hcoderdm
```
