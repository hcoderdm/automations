#!/usr/bin/env python3
"""
TODO: Add a description of the program.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from typing import Iterator, NamedTuple

DEFAULT_REPO = os.path.expanduser("~/Documents/coursework")
# Leading folders that aren't the course, as in `2026-2027/fall/...`
YEAR_RE = re.compile(r"^\d{4}-\d{4}$")
SEMESTERS = {"fall", "spring"}
MAX_LEN = 72
# What HEAD is compared against before the first commit.
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


# -------------------------------------
# Types
# -------------------------------------

class Status(Enum):
    ADDED = "Added"
    MODIFIED = "Modified"
    DELETED = "Deleted"
    RENAMED = "Renamed"


class Change(NamedTuple):
    status: Status
    path: str
    old: str | None


class Commit(NamedTuple):
    date: datetime
    message: str
    changes: list[Change]


class GitError(Exception):
    pass


def log(msg: object) -> None:
    """Logs msg as one line starting with the date and time."""
    print(f"{datetime.now():%F %T} {' '.join(str(msg).split())}", flush=True)


# -------------------------------------
# git_*
# -------------------------------------

def git(repo: str, *args: str, env: dict[str, str] | None = None) -> str:
    """Runs git in repo and returns stdout, raising GitError on failure."""
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                            env={**os.environ, **env} if env else None)
    if result.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def get_git(repo: str) -> str:
    """Refuses to run in any state where committing could go wrong (detached HEAD, merge,
    rebase, cherry-pick, revert, index.lock). Returns the git dir."""

    # Get the git dir.
    git_dir = git(repo, "rev-parse", "--absolute-git-dir").strip()

    # Check for detached HEAD.
    if not git(repo, "branch", "--show-current").strip():
        raise GitError("detached HEAD")
    
    # Check for other possible commit-blocking states.
    for marker, state in [("index.lock", "index.lock present"),
                          ("MERGE_HEAD", "merge in progress"),
                          ("CHERRY_PICK_HEAD", "cherry-pick in progress"),
                          ("REVERT_HEAD", "revert in progress"),
                          ("rebase-merge", "rebase in progress"),
                          ("rebase-apply", "rebase/am in progress")]:
        # Check for the presence of any of the commit-blocking states.
        if os.path.exists(os.path.join(git_dir, marker)):
            raise GitError(state)
    
    # Return the git dir.
    return git_dir


def git_head(repo: str) -> str | None:
    """HEAD's commit, or None in a repo with no commits yet."""
    try:
        return git(repo, "rev-parse", "--verify", "-q", "HEAD").strip()
    except GitError:
        return None


@contextmanager
def git_scratch_index(copy_from: str | None = None) -> Iterator[dict[str, str]]:
    """Yields an env dict pointing git at a throwaway index, removed afterwards.
    Starts as a copy of copy_from if it exists, otherwise git makes a fresh one."""
    
    # Create a temporary file for the index.
    fd, path = tempfile.mkstemp(prefix="autocommit-index-")
    os.close(fd)

    try:
        # If copy_from exists, copy it to the temporary file.
        if copy_from and os.path.exists(copy_from):
            shutil.copyfile(copy_from, path)
        else:
            # If copy_from doesn't exist, remove the temporary file.
            os.remove(path)
        # Yield the environment dictionary.
        yield {"GIT_INDEX_FILE": path}

    finally:
        # Remove the temporary file.
        if os.path.exists(path):
            os.remove(path)


# -------------------------------------
# parse_args, get_changes
# -------------------------------------

def parse_args() -> argparse.Namespace:
    """Returns the command line arguments."""
    
    # Parse the command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("repo", nargs="?", default=DEFAULT_REPO)
    args = parser.parse_args()
    args.repo = os.path.expanduser(args.repo)
    return args


def get_changes(repo: str, git_dir: str, base: str | None) -> list[Change]:
    """Everything that differs from base, with renames detected. Stages into a
    git_scratch_index copy of the real index so the real one is left alone."""

    # Parse the output of `git diff --name-status -M -z` into Changes.
    def parse(out: str) -> list[Change]:
        """Parses `git diff --name-status -M -z` output into Changes."""
        fields = out.split("\0")
        changes, i = [], 0
        # Iterate over the fields, adding Changes to the list.
        while i < len(fields) and fields[i]:
            code = fields[i][0]
            if code in "RC":
                # Add a Renamed Change, or an Added one for a copy.
                old, path = fields[i + 1], fields[i + 2]
                changes.append(Change(Status.RENAMED, path, old) if code == "R" else Change(Status.ADDED, path, None))
                i += 3
            else:
                # Add an Added or Deleted Change; anything else counts as Modified.
                status = (Status.ADDED if code == "A" else
                          Status.DELETED if code == "D" else
                          Status.MODIFIED)
                changes.append(Change(status, fields[i + 1], None))
                i += 2
        # Return the list of Changes.        
        return changes

    # Stage all changes into a git_scratch_index copy of the real index.
    with git_scratch_index(os.path.join(git_dir, "index")) as env:
        git(repo, "add", "-A", env=env)
        return parse(git(repo, "diff", "--cached", "-M", "-z", "--name-status",
                         base or EMPTY_TREE, env=env))


# -------------------------------------
# plan_*
# -------------------------------------

def plan_commits(repo: str, changes: list[Change]) -> list[Commit]:
    """Turns changes into Commits, oldest work first, so history reads in the order it
    was done."""

    # Plan the commits, oldest work first.
    dated = [(plan_date(repo, g), g) for g in plan_groups(changes)]

    # Sort the commits by date, oldest first.
    return [Commit(date, plan_message(g), g) for date, g in sorted(dated, key=lambda x: x[0])]


def plan_groups(changes: list[Change]) -> list[list[Change]]:
    """One group per .tex file, holding its .pdf and, when no other changed .tex shares the
    folder, its images/. Whatever's left over becomes one final group for a REPO commit."""
    
    groups, remaining = [], list(changes)
    texes = sorted((c for c in changes if c.path.endswith(".tex")), key=lambda c: c.path)
    tex_folders = [os.path.dirname(c.path) for c in texes]
    
    # Iterate over the texes, adding them to the groups.
    for tex in texes:
        folder = os.path.dirname(tex.path)
        stem = os.path.splitext(os.path.basename(tex.path))[0]
        pdf = os.path.join(folder, stem + ".pdf")
        # Get the images folder.
        images = os.path.join(folder, "images") + "/"
        # Check if the folder has only one tex file.
        own_images = tex_folders.count(folder) == 1
        # Add the changes to the group.
        group = [c for c in remaining if c == tex or c.path == pdf or (own_images and c.path.startswith(images))]
        groups.append(group)
        remaining = [c for c in remaining if c not in group]

    # If there are remaining changes, add them to the groups.
    if remaining:
        # Add the remaining changes to the groups.
        groups.append(remaining)

    # Return the groups.
    return groups


def plan_message(group: list[Change]) -> str:
    """A course commit for a group built around one .tex file, otherwise a REPO commit."""

    def scope(tex_path: str) -> str:
        """`2026-2027/fall/abc101/hw3/hw3.tex` -> `ABC101 HW3`."""
        
        dirs = tex_path.split("/")[:-1]
        stem = os.path.splitext(os.path.basename(tex_path))[0]
        # Remove the year and semester from the dirs.
        if dirs and YEAR_RE.match(dirs[0]):
            dirs = dirs[1:]
        # Remove the semester from the dirs.
        if dirs and dirs[0].lower() in SEMESTERS:
            dirs = dirs[1:]
        # Get the course and assignment.
        course = dirs[0] if dirs else None
        assignment = dirs[1] if len(dirs) > 1 else stem
        # Return the course and assignment.
        parts = [course, assignment] if course else [assignment]
        return " ".join(p.upper().replace(" ", "") for p in parts)

    # Get the tex files in the group.
    tex = [c for c in group if c.path.endswith(".tex")]
    # If there is only one tex file, return the course and assignment.
    if len(tex) == 1:
        c = tex[0]
        name = os.path.basename(c.path)
        if c.old and os.path.basename(c.old) != name:
            name = f"{os.path.basename(c.old)} to {name}"
        return f"{scope(c.path)}: {c.status.value} {name}"[:MAX_LEN]

    # Get the statuses of the changes in the group.
    statuses = {c.status for c in group}
    # Get the verb for the commit.
    verb = (statuses.pop() if len(statuses) == 1 else Status.MODIFIED).value
    # Get the names of the changes in the group.
    names = list(dict.fromkeys(os.path.basename(c.path) for c in group))
    # Join the names with commas and an "and" if there are more than one.
    joined = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    # Get the message for the commit.
    message = f"REPO: {verb} {joined}"
    # If the message is too long, return the message for the commit.
    if len(names) > 3 or len(message) > MAX_LEN:
        message = f"REPO: {verb} {len(group)} files"
    return message


def plan_date(repo: str, group: list[Change]) -> datetime:
    """Returns the datetime of the newest file in the group."""

    # Get the mtime of the newest file in the group.
    mtimes = [os.lstat(os.path.join(repo, c.path)).st_mtime
              for c in group
              if c.status != Status.DELETED and os.path.lexists(os.path.join(repo, c.path))]
    
    # Return the datetime of the newest file.
    return datetime.fromtimestamp(max(mtimes) if mtimes else time.time()).astimezone()


# -------------------------------------
# write_*
# -------------------------------------

def write_commit(repo: str, commit: Commit) -> None:
    """Writes a commit to the repo."""

    # Get the changes and paths from the commit.
    changes = commit.changes
    paths = sorted({p for c in changes for p in (c.path, c.old) if p})
    
    # Get the deleted and renamed-away paths.
    gone = sorted({c.path for c in changes if c.status == Status.DELETED}
                  | {c.old for c in changes if c.old})
    present = [p for p in paths if p not in gone]
    
    # Build the commit in a git_scratch_index starting from HEAD.
    with git_scratch_index() as env:
        # Read the tree from HEAD, or start empty before the first commit.
        git(repo, "read-tree", "HEAD" if git_head(repo) else "--empty", env=env)
        # Add the present paths. With no paths, git would add everything.
        if present:
            git(repo, "add", "-A", "--", *present, env=env)
        # Remove the gone paths. With no paths, git refuses to run.
        if gone:
            git(repo, "rm", "-q", "--cached", "--ignore-unmatch", "--", *gone, env=env)
        # Commit the changes.
        git(repo, "commit", "-q", "-m", commit.message, env={**env, "GIT_AUTHOR_DATE": commit.date.isoformat(timespec="seconds")})
    
    # Reset the real index for just those paths.
    git(repo, "reset", "-q", "--", *paths)
    log(f"Committed: {git(repo, 'rev-parse', '--short', 'HEAD').strip()} {commit.message}")


def write_log(repo: str) -> None:
    """Logs one line per change still uncommitted."""
    
    # Log one line per change still uncommitted.
    for line in git(repo, "status", "--short").splitlines():
        log(f"Left uncommitted: {line.strip()}")


# -------------------------------------
# main
# -------------------------------------

def main() -> None:

    # Parse arguments.
    args = parse_args()

    try:
        git_dir = get_git(args.repo)
        changes = get_changes(args.repo, git_dir, git_head(args.repo))
        
        # If there are no changes, log and return.
        if not changes:
            log("No changes")
            return

        # Plan the commits.
        for commit in plan_commits(args.repo, changes):
            if not args.test:
                write_commit(args.repo, commit)

        # If not testing, write the log.
        if not args.test:
            write_log(args.repo)

    # If an exception is raised, log it and exit with status 1.
    except Exception as e:
        log(f"Stopped: {e}" if isinstance(e, GitError) else f"Stopped: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
