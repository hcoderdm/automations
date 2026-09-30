# Automations

Small scripts that run on their own on this Mac through launchd.

- [auto-commit-courses](auto-commit-courses) commits changes in `~/Projects/courses` every day at 4:00 AM.
- [backup-resume](backup-resume) copies the resume PDF to iCloud Drive whenever it changes.
- [organize-old-downloads](organize-old-downloads) moves downloads older than 30 days into `~/Archive/Old Downloads` every day at 4:00 AM.

Each folder has its script, a launchd plist, `install.sh` and `uninstall.sh`, and a link to its log in `~/Library/Logs`. Run `install.sh` in a folder to turn that one on, and `uninstall.sh` to turn it off. After editing a plist, run `install.sh` again to reload it.

To see what's loaded:

```bash
launchctl list | grep hcoderdm
```
