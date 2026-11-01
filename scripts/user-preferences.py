#!/usr/bin/env python3
"""Read private preference identities and Markdown evidence; never write state.

Agents use locate before choosing a project's history, index for selective lookup,
and check after their own file edits. Git's common directory joins worktrees;
credential-free origin aliases recover moved projects without merging forks.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Optional
from urllib.parse import urlsplit

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
ENTRY = re.compile(r"^### (\d{4}-\d{2}-\d{2}-[a-z0-9-]+) — (.+)$", re.MULTILINE)
FIELD = re.compile(r"^- \*\*([^*\n]+):\*\*[ \t]*(.*?)(?=^- \*\*[^*\n]+:\*\*|\Z)", re.MULTILINE | re.DOTALL)
KINDS = {"preference", "decision", "rejection", "correction", "delegated"}
REQUIRED_FIELDS = {"Status", "Kind", "Scope", "Source", "User's words", "Meaning"}


def git_read(directory: Path, *arguments: str) -> Optional[str]:
    """Use only read commands; optional locks are disabled even for future callers."""
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(directory), *arguments],
            capture_output=True, text=True, timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def normalized_remote(value: str) -> Optional[str]:
    """Remove credentials, queries and transport differences before saving identity."""
    value = value.strip()
    scp = re.fullmatch(r"[^/@\s]+@([^/:\s]+):(.+)", value)
    if scp:
        host, path = scp.groups()
    else:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https", "ssh", "git"} or not parsed.hostname:
            return None
        host, path = parsed.hostname, parsed.path
    path = path.split("?", 1)[0].split("#", 1)[0].strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    if not path or any(part in {".", "..", ""} for part in path.split("/")):
        return None
    # GitHub's repository identity is case-insensitive; other hosts may differ.
    return host.lower() + "/" + (path.lower() if host.lower() == "github.com" else path)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "project"


def context(directory: Path) -> dict[str, Any]:
    directory = directory.expanduser().resolve()
    if not directory.is_dir():
        raise ValueError("The selected project directory does not exist")
    top = git_read(directory, "rev-parse", "--show-toplevel")
    common = git_read(directory, "rev-parse", "--path-format=absolute", "--git-common-dir") if top else None
    roots = [str(Path(top).resolve())] if top else [str(directory)]
    if common:
        common = str(Path(common).resolve())
        worktrees = git_read(directory, "worktree", "list", "--porcelain", "-z") or ""
        registered = [str(Path(field[9:]).resolve()) for field in worktrees.split("\0")
                      if field.startswith("worktree ") and Path(field[9:]).is_dir()]
        roots = list(dict.fromkeys(registered + roots))
    # Only origin identifies a project: an upstream shared by two forks must not
    # merge their preference histories. Explicit historical aliases stay in JSON.
    origin = git_read(directory, "config", "--get", "remote.origin.url") if top else None
    remote = normalized_remote(origin) if origin else None
    name = Path(roots[0]).name
    identity = {
        "schema_version": 1, "name": name, "roots": roots,
        "git_common_dirs": [common] if common else [],
        "remotes": [remote] if remote else [],
        "skill_name": slug(name)[:44].rstrip("-") + "-user-preferences",
    }
    key = slug(name)[:38].rstrip("-") + "-" + hashlib.sha256((common or roots[0]).encode()).hexdigest()[:12]
    return {"identity": identity, "key": key, "is_git": bool(top), "cwd": str(directory)}


def validate_identity(value: Any, source: Path) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError("Invalid identity schema: " + str(source))
    if not isinstance(value.get("name"), str) or not value["name"].strip():
        raise ValueError("Missing project name: " + str(source))
    skill_name = value.get("skill_name", "")
    if not isinstance(skill_name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", skill_name):
        raise ValueError("Invalid project skill name: " + str(source))
    for key in ("roots", "git_common_dirs", "remotes"):
        items = value.get(key)
        if not isinstance(items, list) or any(not isinstance(item, str) or not item for item in items):
            raise ValueError("Invalid identity field " + key + ": " + str(source))
        if key != "remotes" and any(not Path(item).is_absolute() for item in items):
            raise ValueError("Project identity paths must be absolute: " + str(source))
        if key == "remotes" and any("@" in item or "://" in item or "?" in item or "#" in item for item in items):
            raise ValueError("Remote identities must be normalized without credentials: " + str(source))
    if not value["roots"]:
        raise ValueError("Project identity needs at least one root: " + str(source))
    return value


def profiles(store: Path) -> list[tuple[Path, dict[str, Any]]]:
    result = []
    for source in sorted((store / "projects").glob("*/identity.json")):
        if source.is_symlink() or source.parent.is_symlink():
            raise ValueError("Project identities cannot redirect outside the private store: " + str(source))
        result.append((source.parent, validate_identity(json.loads(source.read_text()), source)))
    return result


def locate(store: Path, directory: Path, explicit_project: bool = False) -> dict[str, Any]:
    observed = context(directory)
    current = observed["identity"]
    known = profiles(store)
    candidates: list[tuple[Path, dict[str, Any]]] = []
    match = "none"
    for field in ("git_common_dirs", "roots", "remotes"):
        values = set(current[field])
        candidates = [(path, data) for path, data in known if values.intersection(data[field])]
        if candidates:
            match = field
            break
    if not candidates and not observed["is_git"]:
        nested = [(path, data, max((len(root) for root in data["roots"]
                   if Path(observed["cwd"]).is_relative_to(Path(root))), default=0)) for path, data in known]
        longest = max((length for _, _, length in nested), default=0)
        candidates = [(path, data) for path, data, length in nested if length == longest and longest]
        if candidates:
            match = "containing_root"
    if len(candidates) > 1:
        raise ValueError("Ambiguous project identity; inspect aliases before choosing a history")
    suggested = store / "projects" / observed["key"]
    if candidates:
        profile, identity = candidates[0]
        scope = "project"
    elif observed["is_git"] or explicit_project:
        profile, identity, scope = suggested, current, "project"
    else:
        profile, identity, scope = store / "general", current, "general"
    return {"store": str(store), "scope": scope, "profile": str(profile),
            "index": str(profile / "user-preferences.md"),
            "project_skill": str(profile / "SKILL.md") if scope == "project" else None,
            "general": str(store / "general" / "user-preferences.md"),
            "exists": bool(candidates) if scope == "project" else (profile / "user-preferences.md").is_file(),
            "match": match, "suggested_profile": str(suggested),
            "skill_name": identity["skill_name"], "identity": identity}


@dataclass
class PreferenceEntry:
    identifier: str
    title: str
    path: Path
    line: int
    fields: dict[str, str]
    text: str
    duplicate_fields: list[str]


def markdown_files(scope: Path) -> list[Path]:
    if not scope.is_dir():
        raise ValueError("The preference scope does not exist")
    return sorted(path for path in scope.rglob("*.md")
                  if not path.is_symlink() and not any(part.startswith(".") for part in path.relative_to(scope).parts))


def entries(scope: Path) -> list[PreferenceEntry]:
    result = []
    for path in markdown_files(scope):
        text = path.read_text(encoding="utf-8")
        headings = list(ENTRY.finditer(text))
        for number, heading in enumerate(headings):
            body = text[heading.end():headings[number + 1].start() if number + 1 < len(headings) else len(text)]
            fields: dict[str, str] = {}
            duplicate_fields = []
            for field in FIELD.finditer(body):
                key, value = field.group(1), field.group(2).strip()
                if key in fields:
                    duplicate_fields.append(key)
                fields[key] = value
            result.append(PreferenceEntry(heading.group(1), heading.group(2), path,
                          text.count("\n", 0, heading.start()) + 1, fields, body, duplicate_fields))
    return result


def check(scope: Path) -> dict[str, Any]:
    records = entries(scope)
    errors = []
    by_id: dict[str, PreferenceEntry] = {}
    for record in records:
        label = str(record.path.relative_to(scope)) + ":" + str(record.line)
        if record.identifier in by_id:
            errors.append(label + ": duplicate entry ID " + record.identifier)
        by_id[record.identifier] = record
        missing = sorted(key for key in REQUIRED_FIELDS if not record.fields.get(key))
        if missing:
            errors.append(label + ": missing fields " + ", ".join(missing))
        if record.duplicate_fields:
            errors.append(label + ": duplicate fields " + ", ".join(record.duplicate_fields))
        if record.fields.get("Kind") not in KINDS:
            errors.append(label + ": invalid Kind")
        status = record.fields.get("Status", "")
        if status not in {"active", "uncertain", "withdrawn by user"} and not re.fullmatch(r"superseded by \d{4}-\d{2}-\d{2}-[a-z0-9-]+", status):
            errors.append(label + ": invalid Status")
        if not re.match(r"^(general|project|area: .+|file: .+|one-off: .+)(?:$|[;, ])", record.fields.get("Scope", "")):
            errors.append(label + ": invalid Scope")
        if not re.search(r"(?m)^\s*>\s*\S", record.fields.get("User's words", "")):
            errors.append(label + ": User's words needs a source quotation")
    for record in records:
        status = record.fields.get("Status", "")
        if status.startswith("superseded by "):
            target = by_id.get(status[len("superseded by "):])
            if not target or record.identifier not in [x.strip() for x in target.fields.get("Supersedes", "").split(",")]:
                errors.append(record.identifier + ": supersession link is missing or not reciprocal")
        for old_id in filter(None, (x.strip() for x in record.fields.get("Supersedes", "").split(","))):
            if old_id not in by_id or by_id[old_id].fields.get("Status") != "superseded by " + record.identifier:
                errors.append(record.identifier + ": Supersedes link is missing or not reciprocal")
        visited = {record.identifier}
        current = record
        while current.fields.get("Status", "").startswith("superseded by "):
            target_id = current.fields["Status"][len("superseded by "):]
            if target_id in visited:
                errors.append(record.identifier + ": cyclic supersession")
                break
            visited.add(target_id)
            if target_id not in by_id:
                break
            current = by_id[target_id]
    preference_files = [path for path in markdown_files(scope) if path.relative_to(scope).parts[0] == "preferences"]
    for path in preference_files:
        if not any(record.path == path for record in records):
            errors.append(str(path.relative_to(scope)) + ": no structured preference entries")
    if (scope / "identity.json").exists():
        try:
            validate_identity(json.loads((scope / "identity.json").read_text()), scope / "identity.json")
        except ValueError as error:
            errors.append(str(error))
    if not (scope / "user-preferences.md").is_file():
        errors.append("Missing root user-preferences.md")
    return {"ok": not errors, "entries": len(records), "files": len(markdown_files(scope)), "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    locating = commands.add_parser("locate")
    locating.add_argument("--cwd", type=Path, default=Path.cwd())
    locating.add_argument("--project-root", type=Path)
    commands.add_parser("inventory")
    indexing = commands.add_parser("index")
    indexing.add_argument("scope", type=Path)
    indexing.add_argument("--query", default="")
    checking = commands.add_parser("check")
    checking.add_argument("scope", type=Path)
    args = parser.parse_args()
    default_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    store = (args.store or Path(os.environ.get("LEARNED_USER_PREFERENCES_HOME", str(default_home / "user-preferences")))).expanduser().resolve()
    if store == PACKAGE_ROOT or PACKAGE_ROOT in store.parents:
        raise ValueError("Keep the private store outside the reusable skill package")
    if args.command == "locate":
        output = locate(store, args.project_root or args.cwd, args.project_root is not None)
    elif args.command == "inventory":
        output = [{"profile": str(path), "name": data["name"], "skill_name": data["skill_name"]} for path, data in profiles(store)]
    elif args.command == "index":
        scope = args.scope.expanduser().resolve()
        terms = args.query.casefold().split()
        output = [{"id": record.identifier, "title": record.title,
                   "status": record.fields.get("Status"), "scope": record.fields.get("Scope"),
                   "file": str(record.path), "line": record.line} for record in entries(scope)
                  if all(term in (str(record.path.relative_to(scope)) + " " + record.title + " " + record.text).casefold() for term in terms)]
    else:
        output = check(args.scope.expanduser().resolve())
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 1 if isinstance(output, dict) and output.get("ok") is False else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        raise SystemExit(2)
