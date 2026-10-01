#!/usr/bin/env python3
"""Commits uncommitted changes in ~/Projects/courses, one commit per changed .tex file.
Local only: never pushes, pulls, amends, or rewrites history.
Triggered daily by the launchd agent com.yourname.courses-autocommit.

Usage: auto_commit_courses.py [--test] [REPO]
  --test  print the commits that would be made without committing anything

Commit messages follow `<COURSE> <ASSIGNMENT>: <Added|Modified|Deleted|Renamed> <file>`,
e.g. `ABC101 HW3: Modified hw3.tex`. Leftover non-.tex changes go into one `REPO:` commit.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import namedtuple
from datetime import datetime

DEFAULT_REPO = os.path.expanduser("~/Projects/courses")
# Leading folders that aren't the course, as in `2026-2027/fall/...`
YEAR_RE = re.compile(r"^\d{4}-\d{4}$")
SEMESTERS = {"fall", "spring"}
MAX_LEN = 72
VERBS = {"A": "Added", "M": "Modified", "D": "Deleted", "R": "Renamed"}


"""
Classes.
"""

# status is one of VERBS' keys; old is the previous path for renames, else None.
Change = namedtuple("Change", "status path old")


class GitError(Exception):
    pass


"""
Helper functions.
"""

def log(msg):
    print(f"{datetime.now():%F %T} {msg}", flush=True)


def git(repo, *args, env=None):
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                            env={**os.environ, **env} if env else None)
    if result.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def preflight(repo):
    """Refuse to run in any state where committing could go wrong."""
    git_dir = git(repo, "rev-parse", "--absolute-git-dir").strip()
    if not git(repo, "branch", "--show-current").strip():
        raise GitError("detached HEAD")
    for marker, state in [("index.lock", "index.lock present"),
                          ("MERGE_HEAD", "merge in progress"),
                          ("CHERRY_PICK_HEAD", "cherry-pick in progress"),
                          ("REVERT_HEAD", "revert in progress"),
                          ("rebase-merge", "rebase in progress"),
                          ("rebase-apply", "rebase/am in progress")]:
        if os.path.exists(os.path.join(git_dir, marker)):
            raise GitError(state)
    return git_dir


def parse_name_status(out):
    """Parses `git diff --name-status -M -z` output into Changes."""
    fields = out.split("\0")
    changes, i = [], 0
    while i < len(fields) and fields[i]:
        code = fields[i][0]
        if code in "RC":
            old, path = fields[i + 1], fields[i + 2]
            changes.append(Change("R", path, old) if code == "R" else Change("A", path, None))
            i += 3
        else:
            changes.append(Change(code if code in VERBS else "M", fields[i + 1], None))
            i += 2
    return changes


def working_changes(repo, git_dir):
    """Everything that differs from HEAD, with renames detected. Stages into a throwaway
    copy of the index so the real one is left alone."""
    fd, tmp_index = tempfile.mkstemp(prefix="autocommit-index-")
    os.close(fd)
    try:
        real_index = os.path.join(git_dir, "index")
        if os.path.exists(real_index):
            shutil.copyfile(real_index, tmp_index)
        env = {"GIT_INDEX_FILE": tmp_index}
        git(repo, "add", "-A", env=env)
        return parse_name_status(
            git(repo, "diff", "--cached", "-M", "-z", "--name-status", "HEAD", env=env))
    finally:
        os.remove(tmp_index)


def scope_for(tex_path):
    """`2026-2027/fall/abc101/hw3/hw3.tex` -> `ABC101 HW3`."""
    dirs = tex_path.split("/")[:-1]
    stem = os.path.splitext(os.path.basename(tex_path))[0]
    if dirs and YEAR_RE.match(dirs[0]):
        dirs = dirs[1:]
    if dirs and dirs[0].lower() in SEMESTERS:
        dirs = dirs[1:]
    course = dirs[0] if dirs else None
    assignment = dirs[1] if len(dirs) > 1 else stem
    parts = [course, assignment] if course else [assignment]
    return " ".join(p.upper().replace(" ", "") for p in parts)


"""
Primary functions.
"""

def message_for(changes):
    """A course commit for a group built around one .tex file, otherwise a REPO commit."""
    tex = [c for c in changes if c.path.endswith(".tex")]
    if len(tex) == 1:
        c = tex[0]
        name = os.path.basename(c.path)
        if c.status == "R" and os.path.basename(c.old) != name:
            name = f"{os.path.basename(c.old)} to {name}"
        return f"{scope_for(c.path)}: {VERBS[c.status]} {name}"[:MAX_LEN]

    statuses = {c.status for c in changes}
    verb = VERBS[statuses.pop()] if len(statuses) == 1 else VERBS["M"]
    names = list(dict.fromkeys(os.path.basename(c.path) for c in changes))
    # `REPO: Verb a, b and c`, falling back to `REPO: Verb N files` when too long.
    joined = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    message = f"REPO: {verb} {joined}"
    if len(names) > 3 or len(message) > MAX_LEN:
        message = f"REPO: {verb} {len(changes)} files"
    return message


def commit(repo, changes, test):
    message = message_for(changes)
    paths = sorted({p for c in changes for p in (c.path, c.old) if p})
    if test:
        log(f"[test] {message}  <- {', '.join(paths)}")
        return
    # Deleted and renamed-away paths may still be on disk (e.g. untracked but now ignored).
    gone = sorted({c.path for c in changes if c.status == "D"} | {c.old for c in changes if c.old})
    present = [p for p in paths if p not in gone]
    # Build the commit in a scratch index starting from HEAD so only these paths change,
    # then sync the real index for them, leaving anything else the user staged alone.
    fd, tmp_index = tempfile.mkstemp(prefix="autocommit-index-")
    os.close(fd)
    try:
        env = {"GIT_INDEX_FILE": tmp_index}
        git(repo, "read-tree", "HEAD", env=env)
        if present:
            git(repo, "add", "-A", "--", *present, env=env)
        if gone:
            git(repo, "rm", "-q", "--cached", "--ignore-unmatch", "--", *gone, env=env)
        git(repo, "commit", "-q", "-m", message, env=env)
    finally:
        os.remove(tmp_index)
    git(repo, "reset", "-q", "--", *paths)
    log(f"Committed: {message}")


def main():
    args = sys.argv[1:]
    test = "--test" in args
    args = [a for a in args if a != "--test"]
    repo = os.path.expanduser(args[0]) if args else DEFAULT_REPO

    try:
        git_dir = preflight(repo)
        head_before = git(repo, "rev-parse", "HEAD").strip()
        changes = working_changes(repo, git_dir)
        if not changes:
            log("No changes")
            return

        remaining = list(changes)
        for tex in sorted((c for c in changes if c.path.endswith(".tex")), key=lambda c: c.path):
            folder = os.path.dirname(tex.path)
            stem = os.path.splitext(os.path.basename(tex.path))[0]
            pdf = os.path.join(folder, stem + ".pdf")
            images = os.path.join(folder, "images") + "/"
            group = [c for c in remaining
                     if c == tex or c.path == pdf or c.path.startswith(images)]
            commit(repo, group, test)
            remaining = [c for c in remaining if c not in group]

        if remaining:
            commit(repo, remaining, test)

        if not test:
            print(git(repo, "log", "--oneline", f"{head_before}..HEAD").rstrip())
        leftovers = git(repo, "status", "--short").rstrip()
        if leftovers:
            print("Left uncommitted:\n" + leftovers)
    except GitError as e:
        log(f"Stopped: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
