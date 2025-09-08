#!/usr/bin/env python3
"""Update apps.json with latest tags for Frappe apps."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from packaging.version import InvalidVersion, Version

# List of Frappe app repositories to include in apps.json
REPOS = [
    "https://github.com/frappe/erpnext",
    "https://github.com/frappe/hrms",
    "https://github.com/frappe/crm",
    "https://github.com/frappe/helpdesk",
    "https://github.com/frappe/drive",
    "https://github.com/frappe/insights",
    "https://github.com/frappe/builder",
    "https://github.com/frappe/lms",
]

TAG_PATTERN = re.compile(r"v\d+\.\d+\.\d+$")


def get_latest_tag(repo_url: str, major: int | None) -> str | None:
    """Return the latest semantic version tag for a repo.

    Args:
        repo_url: Remote repository to query.
        major: Optional major version to filter tags by.
    """

    output = subprocess.check_output(
        ["git", "ls-remote", "--tags", repo_url], text=True
    )
    tags: list[Version] = []
    for line in output.strip().splitlines():
        _, ref = line.split("\t")
        tag = ref.replace("refs/tags/", "")
        if tag.endswith("^{}"):
            tag = tag[:-3]
        if TAG_PATTERN.match(tag):
            try:
                tags.append(Version(tag.lstrip("v")))
            except InvalidVersion:
                continue

    if not tags:
        return None

    matching = [t for t in tags if major is None or t.major == major]
    if not matching:
        matching = tags

    latest = max(matching)
    return f"v{latest}"


def main() -> None:
    major: int | None = None
    env_version = os.getenv("FRAPPE_VERSION", "")
    match = re.search(r"(\d+)", env_version)
    if match:
        major = int(match.group(1))

    apps = []
    for repo in REPOS:
        tag = get_latest_tag(repo, major)
        apps.append({"git_url": repo, "branch": tag or "main"})

    apps_json = Path("apps.json")
    apps_json.write_text(json.dumps(apps, indent=2) + "\n")


if __name__ == "__main__":
    main()
