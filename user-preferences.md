# Where user preferences live

This file explains the structure. Actual user records are private and are not shipped with the public skill.

The store is `$LEARNED_USER_PREFERENCES_HOME` when explicitly configured, otherwise `<Codex home>/user-preferences` (`~/.codex/user-preferences` by default).

```text
user-preferences/
  user-preferences.md                       store explanation; no copied project list
  general/
    user-preferences.md                     general scope and coverage
    preferences/                           broader preferences and per-skill history
      skills/<skill-name>/<topic>.md        grows only when useful
  projects/<project-key>/
    identity.json                          canonical identity and aliases
    SKILL.md                               the project's private preference skill
    user-preferences.md                     project scope, coverage, existing sources
    preferences/<aspect>/<topic>.md         exact words, examples and reasons
    preferences/<aspect>/<file>/<topic>.md  a deeper branch when useful
```

Use the read-only helper's `locate`, `inventory`, `index` and `check` commands. The project root explains its scope and points to its `preferences/` tree; the live index is derived from the actual files, not maintained as a second source. Agents can read just the relevant branch, and can choose to look deeper when deciding what the user would want.

Keep cross-project preferences in `general`. Keep project-specific decisions in that project's profile. For a preference about a particular skill, use the corresponding `general/preferences/skills/<skill-name>/` branch, or that project's branch when the skill is project-specific. Cross-link relevant records instead of copying the entire history.

The public skill's instructions and references can be updated independently of this private tree. Private histories must never be placed inside a public skill checkout, even if a local ignore rule appears to hide them. Follow [references/project-setup.md](references/project-setup.md) when creating a profile and [references/record-format.md](references/record-format.md) when recording evidence.
