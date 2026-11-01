"""Exercise actual Git/worktree lookup, selective evidence and read-only commands.

All histories, remotes and quotations are fictional temporary fixtures. These
checks do not call a model or access the installer's real preference history.
"""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/user-preferences.py"
spec = importlib.util.spec_from_file_location("preference_reader", SCRIPT)
reader = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = reader
spec.loader.exec_module(reader)


def git(root, *arguments):
    result = subprocess.run(["git", "-C", str(root), *arguments], capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout.strip()


def snapshot(root):
    return {str(path.relative_to(root)): (path.lstat().st_mode, path.lstat().st_mtime_ns,
            os.readlink(path) if path.is_symlink() else hashlib.sha256(path.read_bytes()).hexdigest())
            for path in root.rglob("*") if path.is_file() or path.is_symlink()}


def entry(identifier="2030-01-02-preview-abc123", status="active", supersedes=None, scope="project"):
    return (f"### {identifier} — Prefer a wide preview\n"
            f"- **Status:** {status}\n- **Kind:** preference\n- **Scope:** {scope}\n"
            "- **Source:** authored fixture message, 2030-01-02, message 1\n"
            "- **User's words:**\n  > Keep the preview wide.\n"
            "- **Meaning:** Prefer more space for the editor preview.\n"
            "- **Reason:** stated — the preview matters during editing.\n"
            + (f"- **Supersedes:** {supersedes}\n" if supersedes else ""))


TOPICS = {"editor": ("preview", "toolbar", "shortcuts"), "export": ("formats", "naming"), "website": ("landing", "docs")}


def fixture_lines(identifier, title, meaning, status="active", supersedes=None, examples=()):
    lines = [f"### {identifier} — {title}", f"- **Status:** {status}", "- **Kind:** preference",
             "- **Scope:** project", "- **Source:** authored fixture message, 2030-01-02, message 1",
             "- **User's words:**", f"  > {title}.", f"- **Meaning:** {meaning}"]
    if supersedes:
        lines.append(f"- **Supersedes:** {supersedes}")
    if examples:
        lines += ["- **Examples:** Agent-created illustration:", *examples]
    return lines


def write_hierarchy(profile):
    """Write fictional topic files and return each entry's expected file, range, meaning and status."""
    expected = {}
    for aspect, topics in TOPICS.items():
        branch = profile / "preferences" / aspect
        branch.mkdir(parents=True)
        for topic in topics:
            ids = [f"2030-01-02-{aspect}-{topic}-{number}" for number in range(4)]
            lines = [f"# {topic.title()} preferences", ""]
            for number, identifier in enumerate(ids):
                if number == 2:
                    # File-level grouping prose belongs to no entry.
                    lines += ["## Later grouping", "", "Grouping prose outside every entry.", ""]
                status, supersedes, examples = "active", None, ()
                if (aspect, topic) == ("editor", "preview") and number == 0:
                    status = "superseded by " + ids[3]
                if (aspect, topic) == ("editor", "preview") and number == 3:
                    supersedes = ids[0]
                if number == 1:
                    # A column-zero fence containing a heading-like line stays inside its entry.
                    examples = ("```text", "# not a heading", "```")
                meaning = f"Keep {topic} {aspect} choice {number}" + (" with strong contrast." if number == 1 else ".")
                start = len(lines) + 1
                lines += fixture_lines(identifier, f"{aspect} {topic} choice {number}", meaning, status, supersedes, examples)
                expected[identifier] = (branch / f"{topic}.md", start, len(lines), meaning, status)
                lines += ["", ""]
            (branch / f"{topic}.md").write_text("\n".join(lines) + "\n")
    return expected


class PreferenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="preferences-fixture-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.store = self.root / "private"
        self.repo = self.root / "sample-project"
        self.repo.mkdir()
        git(self.repo, "init", "--initial-branch=main")
        git(self.repo, "config", "user.name", "Fixture")
        git(self.repo, "config", "user.email", "fixture@example.invalid")
        git(self.repo, "config", "commit.gpgsign", "false")
        (self.repo / "source.txt").write_text("sample\n")
        git(self.repo, "add", "source.txt")
        git(self.repo, "commit", "-m", "fixture")
        git(self.repo, "remote", "add", "origin", "https://github.com/example/sample-project.git")

    def profile(self, name="sample", identity=None):
        profile = self.store / "projects" / name
        profile.mkdir(parents=True)
        value = identity or reader.context(self.repo)["identity"]
        (profile / "identity.json").write_text(json.dumps(value))
        (profile / "user-preferences.md").write_text("# Scope\n\nFictional project.\n")
        (profile / "preferences").mkdir()
        return profile

    def command(self, *arguments):
        return subprocess.run([sys.executable, str(SCRIPT), "--store", str(self.store), *map(str, arguments)],
                              capture_output=True, text=True)

    def test_linked_worktrees_share_profile(self):
        worktree = self.root / "second-copy"
        git(self.repo, "worktree", "add", "-b", "fixture-branch", str(worktree))
        profile = self.profile()
        first = reader.locate(self.store, self.repo)
        second = reader.locate(self.store, worktree)
        self.assertEqual(first["profile"], str(profile))
        self.assertEqual(first["profile"], second["profile"])
        self.assertEqual(second["match"], "git_common_dirs")

    def test_unregistered_worktrees_suggest_same_profile(self):
        worktree = self.root / "another-name"
        git(self.repo, "worktree", "add", "-b", "new-branch", str(worktree))
        first = reader.locate(self.store, self.repo)
        second = reader.locate(self.store, worktree)
        self.assertEqual(first["suggested_profile"], second["suggested_profile"])
        self.assertFalse(self.store.exists())

    def test_remote_normalization_never_returns_credentials(self):
        expected = "github.com/example/sample-project"
        self.assertEqual(reader.normalized_remote("https://sample:secret@GitHub.com/Example/Sample-Project.git?access=private"), expected)
        self.assertEqual(reader.normalized_remote("git@github.com:Example/Sample-Project.git"), expected)
        self.assertEqual(reader.normalized_remote("ssh://git@github.com/Example/Sample-Project.git"), expected)
        self.assertIsNone(reader.normalized_remote("file:///private/repo.git"))

    def test_relocated_project_matches_origin_alias(self):
        profile = self.profile()
        moved = self.root / "relocated-project"
        self.repo.rename(moved)
        actual = reader.locate(self.store, moved)
        self.assertEqual(actual["profile"], str(profile))
        self.assertEqual(actual["match"], "remotes")

    def test_upstream_does_not_merge_distinct_forks(self):
        self.profile()
        git(self.repo, "remote", "set-url", "origin", "https://github.com/another-owner/another-fork.git")
        git(self.repo, "remote", "add", "upstream", "https://github.com/example/sample-project.git")
        moved = self.root / "another-fork"
        self.repo.rename(moved)
        self.assertFalse(reader.locate(self.store, moved)["exists"])

    def test_ambiguous_alias_is_refused(self):
        identity = reader.context(self.repo)["identity"]
        identity["roots"] = [str(self.root / "gone")]
        identity["git_common_dirs"] = []
        self.profile("first", identity)
        self.profile("second", identity)
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            reader.locate(self.store, self.repo)

    def test_repo_without_remote_uses_common_directory(self):
        git(self.repo, "remote", "remove", "origin")
        profile = self.profile()
        self.assertEqual(reader.locate(self.store, self.repo)["profile"], str(profile))

    def test_non_git_chat_and_explicit_project_have_distinct_scope(self):
        directory = self.root / "non-git-project"
        directory.mkdir()
        self.assertEqual(reader.locate(self.store, directory)["scope"], "general")
        explicit = reader.locate(self.store, directory, explicit_project=True)
        profile = self.profile("non-git", explicit["identity"])
        child = directory / "src"
        child.mkdir()
        result = reader.locate(self.store, child)
        self.assertEqual(result["profile"], str(profile))
        self.assertEqual(result["match"], "containing_root")

    def test_all_commands_preserve_files_and_git_index(self):
        profile = self.profile()
        (profile / "preferences/layout.md").write_text(entry())
        write_hierarchy(profile)
        before = snapshot(self.root)
        for command in (("locate", "--cwd", self.repo), ("inventory",), ("index", profile),
                        ("index", profile, "--query", "preview"), ("check", profile)):
            result = self.command(*command)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(before, snapshot(self.root))

    def test_nested_branch_search_is_live_and_scoped(self):
        profile = self.profile()
        branch = profile / "preferences/editor/preview"
        branch.mkdir(parents=True)
        (branch / "width.md").write_text(entry(scope="one-off: fixture task"))
        result = self.command("index", profile, "--query", "wide")
        found = json.loads(result.stdout)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["scope"], "one-off: fixture task")
        self.assertTrue(found[0]["file"].endswith("width.md"))
        self.assertEqual(json.loads(self.command("index", profile, "--query", "unrelated").stdout), [])

    def test_query_returns_meaning_and_exact_inclusive_ranges(self):
        profile = self.profile()
        expected = write_hierarchy(profile)
        self.assertTrue(reader.check(profile)["ok"], reader.check(profile)["errors"])
        rows = json.loads(self.command("index", profile, "--query", "CONTRAST").stdout)
        self.assertEqual(sorted(row["id"] for row in rows),
                         sorted(identifier for identifier in expected if identifier.endswith("-1")))
        for row in rows:
            path, start, end, meaning, status = expected[row["id"]]
            self.assertEqual((row["file"], row["line"], row["end_line"], row["meaning"], row["status"]),
                             (str(path), start, end, meaning, status))
            ranged = path.read_text().split("\n")[row["line"] - 1:row["end_line"]]
            self.assertTrue(ranged[0].startswith("### " + row["id"] + " — "))
            self.assertIn("# not a heading", ranged)
            self.assertNotIn("## Later grouping", ranged)
        # Grouping prose sits between entries and is not attributed to the entry above it.
        self.assertEqual(json.loads(self.command("index", profile, "--query", "grouping").stdout), [])

    def test_superseded_matches_stay_reachable_by_pointer(self):
        profile = self.profile()
        expected = write_hierarchy(profile)
        old, new = "2030-01-02-editor-preview-0", "2030-01-02-editor-preview-3"
        rows = {row["id"]: row for row in json.loads(self.command("index", profile, "--query", new).stdout)}
        self.assertEqual(set(rows), {old, new})
        self.assertEqual(rows[old]["status"], "superseded by " + new)
        self.assertEqual((rows[old]["line"], rows[old]["end_line"]), expected[old][1:3])

    def test_unqueried_index_is_a_branch_map_not_entries(self):
        profile = self.profile()
        expected = write_hierarchy(profile)
        result = self.command("index", profile)
        branch_map = json.loads(result.stdout)
        self.assertEqual((branch_map["files"], branch_map["entries"]), (8, len(expected)))
        self.assertIn({"path": "preferences/editor/preview.md", "entries": 4}, branch_map["branches"])
        self.assertIn({"path": "user-preferences.md", "entries": 0}, branch_map["branches"])
        self.assertEqual(sum(row["entries"] for row in branch_map["branches"]), len(expected))
        for identifier in expected:
            self.assertNotIn(identifier, result.stdout)
        # More evidence in an existing topic grows the counts, not the map.
        preview = profile / "preferences/editor/preview.md"
        extra = "\n".join(line for number in range(10)
                          for line in fixture_lines(f"2030-02-03-extra-{number}", f"extra {number}", "More evidence.") + [""])
        preview.write_text(preview.read_text() + "\n" + extra + "\n")
        grown = json.loads(self.command("index", profile).stdout)
        self.assertEqual((len(grown["branches"]), grown["entries"]), (8, len(expected) + 10))
        # A branch directory narrows both the map and a query.
        export = profile / "preferences/export"
        self.assertEqual([row["path"] for row in json.loads(self.command("index", export).stdout)["branches"]],
                         ["formats.md", "naming.md"])
        rows = json.loads(self.command("index", export, "--query", "contrast").stdout)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(Path(row["file"]).parent == export for row in rows))

    def test_required_fields_duplicate_ids_and_bad_values_fail(self):
        profile = self.profile()
        (profile / "preferences/a.md").write_text(entry().replace("- **Meaning:** Prefer more space for the editor preview.\n", ""))
        (profile / "preferences/b.md").write_text(entry(status="approved forever"))
        errors = "\n".join(reader.check(profile)["errors"])
        self.assertIn("missing fields Meaning", errors)
        self.assertIn("duplicate entry ID", errors)
        self.assertIn("invalid Status", errors)

    def test_superseded_history_is_retained_and_reciprocal(self):
        profile = self.profile()
        old, new = "2030-01-02-old-abc123", "2030-01-03-new-def456"
        leaf = profile / "preferences/layout.md"
        leaf.write_text(entry(old, "superseded by " + new) + "\n" + entry(new, supersedes=old))
        self.assertTrue(reader.check(profile)["ok"])
        self.assertEqual(len(reader.entries(profile)), 2)
        leaf.write_text(entry(old, "superseded by " + new) + "\n" + entry(new))
        self.assertFalse(reader.check(profile)["ok"])

    def test_dangling_supersession_and_cycles_fail(self):
        profile = self.profile()
        old, new = "2030-01-02-old-abc123", "2030-01-03-new-def456"
        leaf = profile / "preferences/layout.md"
        leaf.write_text(entry(old, "superseded by " + new))
        self.assertFalse(reader.check(profile)["ok"])
        leaf.write_text(entry(old, "superseded by " + new, new) + "\n" + entry(new, "superseded by " + old, old))
        self.assertIn("cyclic supersession", "\n".join(reader.check(profile)["errors"]))

    def test_unstructured_preference_file_is_reported(self):
        profile = self.profile()
        (profile / "preferences/unfinished.md").write_text("# An unfinished capture\n")
        self.assertIn("no structured preference entries", "\n".join(reader.check(profile)["errors"]))

    def test_private_store_inside_public_package_is_refused(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--store", str(SCRIPT.parent / "private"), "inventory"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("outside the reusable skill package", result.stderr)

    def test_symlink_identity_cannot_redirect_to_another_store(self):
        outside = self.root / "other-profile"
        outside.mkdir()
        (outside / "identity.json").write_text(json.dumps(reader.context(self.repo)["identity"]))
        projects = self.store / "projects"
        projects.mkdir(parents=True)
        (projects / "redirect").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "cannot redirect"):
            reader.profiles(self.store)


if __name__ == "__main__":
    unittest.main()
