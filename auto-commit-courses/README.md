# Auto-Commit Courses

Commits changes in `~/Projects/courses` every day at 4:00 AM, one commit per `.tex` file. It doesn't push.

Commit messages look like this:

```
STAT110 HW3: Modified hw3.tex
COMPSCI1210 PSET2: Added 2026-cs1210-pset2.tex
STAT110 HW2: Renamed hw2.tex to homework2.tex
REPO: Modified README.md
```

The course and assignment names come from the path, so `2026-2027/fall/stat110/hw3/hw3.tex` is `STAT110 HW3`. A `.tex` commit also picks up its PDF and anything in an `images/` folder next to it. Other changes go in one `REPO:` commit at the end. To keep a file out, add it to the `.gitignore` in the courses repo.

If a merge or rebase is in progress, or HEAD is detached, it doesn't commit anything and writes the reason to the log.

## Setup

```bash
./install.sh
./uninstall.sh
```

## Running

```bash
./auto_commit_courses.py
./auto_commit_courses.py --test
```

`--test` prints the commits it would make without making them. You can pass a different repo path as the last argument.

The log is at `~/Library/Logs/courses-autocommit.log`, and `courses-autocommit.log` in this folder links to it.
