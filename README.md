# Automations

Small scripts that run on their own on this Mac through launchd.

- [auto-commit-coursework](auto-commit-coursework) commits changes in `~/Documents/coursework` every day at 4:00 AM.
- [organize-old-downloads](organize-old-downloads) moves downloads older than 30 days into `~/Downloads/YYYY/MM` every day at 4:00 AM.

Each folder has its script, a launchd plist, `install.sh` and `uninstall.sh`, and a link to its log in `~/Library/Logs`. Run `install.sh` in a folder to turn that one on, and `uninstall.sh` to turn it off. After editing a plist, run `install.sh` again to reload it.

Both need Full Disk Access for `/bin/bash` (System Settings > Privacy & Security > Full Disk Access), since launchd jobs can't otherwise read `~/Documents` or `~/Downloads`.

To see what's loaded:

```bash
launchctl list | grep hcoderdm
```
