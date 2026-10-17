# Auto-Commit Coursework

Commits changes in `~/Documents/coursework` once a day, one commit per `.tex` file. It doesn't push.

Each commit is dated by when its files were last modified rather than when the job ran, so work from the evening before shows up at that time, and commits are made oldest first.

Commit messages look like this:

```
ABC101 HW3: Modified hw3.tex
XYZ200 PSET2: Added 2026-xyz200-pset2.tex
ABC101 HW2: Renamed hw2.tex to homework2.tex
REPO: Modified README.md
```

The course and assignment names come from the path, so `2026-2027/fall/abc101/hw3/hw3.tex` is `ABC101 HW3`. A `.tex` commit also picks up its PDF and anything in an `images/` folder next to it, unless another changed `.tex` shares that folder, in which case the images go in the `REPO:` commit. Other changes go in one `REPO:` commit at the end. To keep a file out, add it to the `.gitignore` in the coursework repo.

If a merge or rebase is in progress, or HEAD is detached, it doesn't commit anything and writes the reason to the log.

It's scheduled for 4:00 AM. If the Mac is asleep then, launchd runs it when the Mac wakes.

## Setup

```bash
./install.sh
./uninstall.sh
```

launchd needs permission to read `~/Documents`: in System Settings > Privacy & Security > Full Disk Access, add `/bin/bash` (press Cmd+Shift+G in the file picker and type the path). Without it the log shows `Operation not permitted`.

## Running

```bash
./auto_commit_coursework.py
./auto_commit_coursework.py --test
```

`--test` prints the commits it would make without making them. You can pass a different repo path as the last argument.

The log is at `~/Library/Logs/coursework-autocommit.log`, and `coursework-autocommit.log` in this folder links to it.
