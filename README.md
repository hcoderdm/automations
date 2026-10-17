# Automations

Small automated scripts for my personal use on macOS.

- [auto-commit-coursework](auto-commit-coursework) commits changes in `~/Documents/coursework` once a day.
- [organize-old-downloads](organize-old-downloads) moves downloads added more than 30 days ago into `~/Downloads/YYYY/MM` once a day.

Both are scheduled for 4:00 AM. If the Mac is asleep then, launchd runs them when it wakes, so the logs usually show a later time.

Each folder has its script, a launchd plist, an `automation.conf` describing it, and a link to its log in `~/Library/Logs`. Install and remove them from here:

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
