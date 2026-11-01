# Preference evidence format

Use ordinary Markdown. This preserves long quotes, examples and reasons without forcing them into escaped JSON/XML strings. Structured pointers and identities can use JSON, but rich preference evidence stays readable.

Each preference entry has a stable, unique ID: `YYYY-MM-DD-subject-<short-random-suffix>`. Group related entries in the topic file for their subject; when parallel edits would otherwise collide, use a topic-named leaf in the same branch rather than a task-named file. The entry heading is `### <id> — <short title>`. An entry runs until the next `#`, `##` or `###` heading at the start of a line; use `####` for any subheading inside an entry.

Required fields are `Status`, `Kind`, `Scope`, `Source`, `User's words`, and `Meaning`. Write `Meaning` as one self-contained statement of what the user wants, with its conditions: lookup shows it first, before an agent decides whether to read the entry. Keep `Context`, `Reason`, `Alternatives rejected`, `Examples`, `Related` and `Supersedes` whenever they preserve useful evidence, scaled to the decision. Reasons may explicitly say `not stated`; lack of a reason is not a reason to omit the preference.

```markdown
### 2030-01-02-wider-preview-a4f19c — Give the preview more space
- **Status:** active
- **Kind:** preference
- **Scope:** area: editor preview, this project
- **Source:** authored user message, task “Preview layout”, 2030-01-02, message 3
- **User's words:**
  > I'd rather have a wider preview than another row of controls.
- **Context:** The user was choosing between two editor layouts.
- **Meaning:** Prefer a wider preview when it competes with another controls row in this editor.
- **Reason:** not stated. Inferred: the preview may matter more to this workflow; verify before treating that reason as fact.
- **Alternatives rejected:** Another row of controls in the offered layout. This does not reject controls elsewhere.
- **Examples:** Agent-created illustration: keep occasional controls in the existing menu if that preserves preview width. This illustration was not separately approved.
- **Related:** The owning layout code or design specification, with a precise source pointer when available.
```

The example above is fictional. Real records preserve actual words and source locations. If the user chooses “B”, retain the actual B proposal in Context so future agents can understand the decision. Do not paste unrelated conversation material. Keep complete useful context; do not paraphrase inside quotation marks or silently repair dictated words. A deliberate omission inside a quote must be marked and must not change its meaning.

Kinds: `preference`, `decision`, `rejection`, `correction`, `delegated`. Status: `active`, `uncertain`, `withdrawn by user`, or `superseded by <id>`. Scope: `general`, `project`, `area: <aspect>`, `file: <path>`, or `one-off: <task/occasion>`. Conditions can follow the scope. One-off approvals are never standing permission. An agent's delegated choice is clearly identified as the agent's choice.

For a genuine replacement, create the new entry with `- **Supersedes:** <old-id>` and change the old status to `superseded by <new-id>`. Retain the old words and rationale. Reciprocal links must resolve within the same scope. A narrower exception is linked through Related and scoped accordingly; it need not erase a still-valid broader preference. If the user only reinforces a preference, preserve the additional quote/source on the existing entry instead of losing either occurrence.

Source pointers should be useful after the task ends: visible task title plus stable ID and message/date, a canonical prompt path, a repository-relative file and heading/line, or an immutable commit. Clearly distinguish a conversation quote from an existing maintained instruction. Do not invent a source, date or exact quotation from a summary. Private source paths stay private.

Read only the entries a decision needs, using the line ranges `index --query` returns. Run `check` after edits: it checks required fields, allowed kinds/statuses/scopes, unique IDs and reciprocal supersession links. It cannot judge quote fidelity, infer the user's intent or prove that every preference was captured. The agent must compare entries with the real message.
