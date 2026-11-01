# Learned User Preferences

A Codex skill for remembering what the user wants, with their words, examples and reasons intact.

The description begins: **“Use whenever you want to learn about the kinds of things the user wants.”** It captures preferences, corrections, rejected options and the choices that narrow a decision. An agent can read a small project root, search a relevant branch and look deeper when useful.

The reusable skill is public. Your actual preference history lives in a separate private store. Each project gets its own preference skill and `user-preferences.md`; Git working copies share the same history. Detailed Markdown files can grow into branches by project aspect or affected file. The live branch map is read from those files, not kept as a second editable list.

## Install

Requires Python 3.9+ for the read-only helper and weekly-update helper. Git is used for repository/worktree identity. No Python packages are needed for normal use.

Clone this repository into a location you own and make the skill available to Codex, for example:

```sh
git clone https://github.com/EthanSK/learned-user-preferences.git ~/.agents/skills/learned-user-preferences
```

If that path already exists, preserve it and inspect it before choosing another installation path. Repository-local skills use `.agents/skills`; Codex also supports [symlinked skill folders](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

Ask the agent to use `$learned-user-preferences` and set up the actual project's profile. The agent follows [project setup](references/project-setup.md), creates/reuses the private history, and adds its locally ignored discovery link. Installing the framework alone does not create project histories or import old chats. To capture future preferences reliably, add a short instruction in your own agent rules to use this skill whenever you express a preference; keep its operating rules in the skill.

## Read-only commands

```sh
python3 scripts/user-preferences.py locate --cwd /path/to/project
python3 scripts/user-preferences.py locate --project-root /path/to/non-git-project
python3 scripts/user-preferences.py inventory
python3 scripts/user-preferences.py index /path/to/private/profile --query preview
python3 scripts/user-preferences.py check /path/to/private/profile
python3 -m unittest discover -s tests -v
```

The helper never creates profiles or edits preferences. The agent makes recording and reconciliation decisions and uses ordinary file tools. Python keeps the same standard-library runtime already needed by the existing public-skill update helper.

The default store is `~/.codex/user-preferences`, respecting `CODEX_HOME`. Set `LEARNED_USER_PREFERENCES_HOME` or pass `--store` for another explicit private location. Keep it outside the installed/public skill. Ensure your existing private backup policy includes the chosen directory.

## How evidence works

- Exact words, their surrounding decision and precise sources remain available.
- Stated reasons, inferred reasons and agent-created examples stay distinguishable.
- Specific, infrequent and one-off preferences are retained with their scope.
- Corrections explicitly supersede earlier entries without erasing them.
- A past approval never grants future permission; an agent suggestion is not a user preference.
- Existing skill learning, technical learnings and decision comments keep their roles. Useful overlap is allowed.

[Read the skill](SKILL.md), [the store structure](user-preferences.md), or [the fictional entry example](references/record-format.md).

## Public updates

On skill use, the agent can check the pinned public source at most weekly. Available updates require explicit approval before installation, preserve local edits and never touch the separate private store. There is no background watcher or transcript logger. Installation does not guarantee automatic invocation or perfect future compliance.

## License

Source-available under Ethan Source-Available No-Sale Terms 1.0. See [LICENSE](LICENSE) and [LICENSING.md](LICENSING.md). This is not an OSI-approved open-source license.
