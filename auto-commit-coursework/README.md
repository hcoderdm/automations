# Auto-Commit Coursework

Commits changes in `~/Documents/coursework` once a day, one commit per `.tex` file. It doesn't push.

Each commit is dated by when its files were last modified rather than when the job ran, so work from the evening before shows up at that time, and commits are made oldest first.

Commit messages look like this:

```
STAT110 HW3: Modified hw3.tex
COMPSCI1210 PSET2: Added 2026-cs1210-pset2.tex
STAT110 HW2: Renamed hw2.tex to homework2.tex
REPO: Modified README.md
```

The course and assignment names come from the path, so `2026-2027/fall/stat110/hw3/hw3.tex` is `STAT110 HW3`. A `.tex` commit also picks up its PDF and anything in an `images/` folder next to it, unless another changed `.tex` shares that folder, in which case the images go in the `REPO:` commit. Other changes go in one `REPO:` commit at the end. To keep a file out, add it to the `.gitignore` in the coursework repo.

If a merge or rebase is in progress, or HEAD is detached, it doesn't commit anything and writes the reason to the log.

It's scheduled for 4:00 AM. If the Mac is asleep then, launchd runs it when the Mac wakes.

## Setup

From the top-level folder:

```bash
./install.sh auto-commit-coursework
./uninstall.sh auto-commit-coursework
```

`../install.sh` builds `~/Applications/Automations/AutoCommitCoursework.app` with the script inside it and runs it once so macOS asks for access to `~/Documents`. Click Allow. Only that app gets access, not bash or python. If you edit the script, install it again so the app picks up the change. To check or remove the access later, look under System Settings > Privacy & Security > Files & Folders.

## Running

```bash
./auto_commit_coursework.py
./auto_commit_coursework.py --test
```

`--test` prints the commits it would make without making them. You can pass a different repo path as the last argument.

The log is at `~/Library/Logs/auto-commit-coursework.log`, and `auto-commit-coursework.log` in this folder links to it.
