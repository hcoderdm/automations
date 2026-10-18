#!/usr/bin/env python3
"""Commits uncommitted changes in ~/Documents/coursework, one commit per changed .tex file.
Local only: never pushes, pulls, amends, or rewrites history.
Triggered daily by the launchd agent com.yourname.auto-commit-coursework.

Usage: auto_commit_coursework.py [--test] [REPO]
  --test  print the commits that would be made without committing anything

Commit messages follow `<COURSE> <ASSIGNMENT>: <Added|Modified|Deleted|Renamed> <file>`,
e.g. `ABC101 HW3: Modified hw3.tex`. Leftover non-.tex changes go into one `REPO:` commit.
Each commit's author date is when its files were last modified, not when this ran, and the
commits are made oldest first.

Every function is named `<phase>_<what>`, and the file reads top to bottom in run order:
  git_*    talk to git (plumbing shared by the phases below)
  read_*   find out what changed; touches nothing
  plan_*   decide which commits to make; touches nothing
  write_*  make the commits and report
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime

DEFAULT_REPO = os.path.expanduser("~/Documents/coursework")
# Leading folders that aren't the course, as in `2026-2027/fall/...`
YEAR_RE = re.compile(r"^\d{4}-\d{4}$")
SEMESTERS = {"fall", "spring"}
MAX_LEN = 72
VERBS = {"A": "Added", "M": "Modified", "D": "Deleted", "R": "Renamed"}
# What HEAD is compared against before the first commit.
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


# -------------------------------------
# Types
# -------------------------------------

# status is one of VERBS' keys; old is the previous path for renames, else None.
Change = namedtuple("Change", "status path old")
# One commit to make: when the work was done, its message, and the Changes it holds.
Commit = namedtuple("Commit", "date message changes")


class GitError(Exception):
    pass


def log(msg):
    """Logs msg as one line starting with the date and time."""
    print(f"{datetime.now():%F %T} {' '.join(str(msg).split())}", flush=True)


# -------------------------------------
# git_*
# -------------------------------------

def git(repo, *args, env=None):
    """Runs git in repo and returns stdout, raising GitError on failure."""
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                            env={**os.environ, **env} if env else None)
    if result.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def git_head(repo):
    """HEAD's commit, or None in a repo with no commits yet."""
    try:
        return git(repo, "rev-parse", "--verify", "-q", "HEAD").strip()
    except GitError:
        return None


def git_check(repo):
    """Refuses to run in any state where committing could go wrong (detached HEAD, merge,
    rebase, cherry-pick, revert, index.lock). Returns the git dir."""
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


@contextmanager
def git_scratch_index(copy_from=None):
    """Yields an env dict pointing git at a throwaway index, removed afterwards.
    Starts as a copy of copy_from if it exists, otherwise git makes a fresh one."""
    fd, path = tempfile.mkstemp(prefix="autocommit-index-")
    os.close(fd)
    try:
        if copy_from and os.path.exists(copy_from):
            shutil.copyfile(copy_from, path)
        else:
            os.remove(path)  # git rejects an empty file but makes a fresh index itself
        yield {"GIT_INDEX_FILE": path}
    finally:
        if os.path.exists(path):
            os.remove(path)


# -------------------------------------
# read_*
# -------------------------------------

def read_args(argv):
    """Returns (repo, test) from the command line."""
    parser = argparse.ArgumentParser(description="Commit coursework changes, one per .tex file.")
    parser.add_argument("--test", action="store_true",
                        help="print the commits that would be made without committing anything")
    parser.add_argument("repo", nargs="?", default=DEFAULT_REPO)
    args = parser.parse_args(argv)
    return os.path.expanduser(args.repo), args.test


def read_changes(repo, git_dir, base):
    """Everything that differs from base, with renames detected. Stages into a
    git_scratch_index copy of the real index so the real one is left alone."""

    def parse(out):
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

    with git_scratch_index(os.path.join(git_dir, "index")) as env:
        git(repo, "add", "-A", env=env)
        return parse(git(repo, "diff", "--cached", "-M", "-z", "--name-status",
                         base or EMPTY_TREE, env=env))


# -------------------------------------
# plan_*
# -------------------------------------

def plan_commits(repo, changes):
    """Turns changes into Commits, oldest work first, so history reads in the order it
    was done."""
    dated = [(plan_date(repo, g), g) for g in plan_groups(changes)]
    return [Commit(date, plan_message(g), g) for date, g in sorted(dated, key=lambda x: x[0])]


def plan_groups(changes):
    """One group per .tex file, holding its .pdf and, when no other changed .tex shares the
    folder, its images/. Whatever's left over becomes one final group for a REPO commit."""
    groups, remaining = [], list(changes)
    texes = sorted((c for c in changes if c.path.endswith(".tex")), key=lambda c: c.path)
    tex_folders = [os.path.dirname(c.path) for c in texes]
    for tex in texes:
        folder = os.path.dirname(tex.path)
        stem = os.path.splitext(os.path.basename(tex.path))[0]
        pdf = os.path.join(folder, stem + ".pdf")
        # A shared images/ folder only goes with its .tex when that's the only changed one
        # there; otherwise there's no telling which it belongs to, so it's left for REPO.
        images = os.path.join(folder, "images") + "/"
        own_images = tex_folders.count(folder) == 1
        group = [c for c in remaining
                 if c == tex or c.path == pdf or (own_images and c.path.startswith(images))]
        groups.append(group)
        remaining = [c for c in remaining if c not in group]
    if remaining:
        groups.append(remaining)
    return groups


def plan_message(group):
    """A course commit for a group built around one .tex file, otherwise a REPO commit."""

    def scope(tex_path):
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

    tex = [c for c in group if c.path.endswith(".tex")]
    if len(tex) == 1:
        c = tex[0]
        name = os.path.basename(c.path)
        if c.status == "R" and os.path.basename(c.old) != name:
            name = f"{os.path.basename(c.old)} to {name}"
        return f"{scope(c.path)}: {VERBS[c.status]} {name}"[:MAX_LEN]

    statuses = {c.status for c in group}
    verb = VERBS[statuses.pop()] if len(statuses) == 1 else VERBS["M"]
    names = list(dict.fromkeys(os.path.basename(c.path) for c in group))
    # `REPO: Verb a, b and c`, falling back to `REPO: Verb N files` when too long.
    joined = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    message = f"REPO: {verb} {joined}"
    if len(names) > 3 or len(message) > MAX_LEN:
        message = f"REPO: {verb} {len(group)} files"
    return message


def plan_date(repo, group):
    """When the work in a group was done: the newest mtime among its files still on disk."""
    # lstat so a broken symlink counts as itself instead of raising.
    mtimes = [os.lstat(os.path.join(repo, c.path)).st_mtime
              for c in group if c.status != "D" and os.path.lexists(os.path.join(repo, c.path))]
    return datetime.fromtimestamp(max(mtimes) if mtimes else time.time()).astimezone()


# -------------------------------------
# write_*
# -------------------------------------

def write_commit(repo, commit):
    """Makes one commit holding only commit.changes, dated commit.date. Builds it in a
    git_scratch_index starting from HEAD, then resets the real index for just those paths,
    leaving anything else the user staged alone."""
    changes = commit.changes
    paths = sorted({p for c in changes for p in (c.path, c.old) if p})
    # Deleted and renamed-away paths may still be on disk (e.g. untracked but now ignored).
    gone = sorted({c.path for c in changes if c.status == "D"} | {c.old for c in changes if c.old})
    present = [p for p in paths if p not in gone]
    with git_scratch_index() as env:
        if git_head(repo):
            git(repo, "read-tree", "HEAD", env=env)
        else:
            git(repo, "read-tree", "--empty", env=env)
        if present:
            git(repo, "add", "-A", "--", *present, env=env)
        if gone:
            git(repo, "rm", "-q", "--cached", "--ignore-unmatch", "--", *gone, env=env)
        git(repo, "commit", "-q", "-m", commit.message,
            env={**env, "GIT_AUTHOR_DATE": commit.date.isoformat(timespec="seconds")})
    git(repo, "reset", "-q", "--", *paths)
    log(f"Committed: {git(repo, 'rev-parse', '--short', 'HEAD').strip()} {commit.message}")


def write_report(repo):
    """Logs one line per change still uncommitted."""
    for line in git(repo, "status", "--short").splitlines():
        log(f"Left uncommitted: {line.strip()}")


# -------------------------------------
# main
# -------------------------------------

def main():
    repo, test = read_args(sys.argv[1:])
    try:
        git_dir = git_check(repo)
        changes = read_changes(repo, git_dir, git_head(repo))
        if not changes:
            log("No changes")
            return

        for commit in plan_commits(repo, changes):
            if test:
                paths = sorted({p for c in commit.changes for p in (c.path, c.old) if p})
                log(f"[test] {commit.date:%F %T} {commit.message}  <- {', '.join(paths)}")
            else:
                write_commit(repo, commit)

        if not test:
            write_report(repo)
    except Exception as e:
        # One line per error, so the log never gets a multi-line traceback.
        log(f"Stopped: {e}" if isinstance(e, GitError) else f"Stopped: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
