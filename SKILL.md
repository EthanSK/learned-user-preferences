---
name: learned-user-preferences
description: Use whenever you want to learn about the kinds of things the user wants. Record every expressed preference, opinionated decision, correction, rejected option and reason in private project and general records, with detail proportionate to the decision. Look up only the relevant categorized entries when current instructions don't settle a choice where the user's taste matters, or when the user refers back to an earlier decision or asks why something was chosen. Routine work already settled by current instructions needs no lookup. Complements existing skills and technical learnings; does not replace their instructions.
---

# Learned User Preferences

Keep the user's wording, examples and decision reasons available to future agents without loading a large history into every task.

## Continuous improvement

Potentially improve this skill as part of using it, but don't add every finding. Favor a small same-task update when the user expresses how this skill should normally work; their statement establishes their preference without repeated examples, a reproduced failure or a separate save request. Preserve wording, conditions and scope. Curiosity, hypotheticals and choices limited to one task are not lasting defaults.

For agent-discovered lessons, make a quick judgment: will this verified lesson likely help again, save meaningful repeated work or prevent a serious mistake? Its benefit must justify the added instructions and maintenance. Assume capable agents; skip routine advice and isolated incident facts. Make qualifying improvements during the same task, refine existing guidance, retest affected behavior and validate the skill. After edits, keep the shared contract here and move conditional detail into directly linked references when useful, without needless fragmentation. Preserve manual edits; exclude secrets and transient runtime state.

Mark agent-initiated material changes beside their guidance with `Self-improved — YYYY-MM-DD`, a brief reason and evidence. Keep longer audit evidence in a reference. Do not apply that label to the user's expressed preferences or invent provenance. This filter governs improvements to the workflow, **not which expressed preferences are recorded**.

## Skill usage announcement

Before skill-directed action, tell the user this skill is active and briefly why. Use their response-preference announcement format when available; otherwise use one short plain sentence. Preserve explicit silent-use exceptions. One announcement covers continuing work within the current task; announce again if the user's configured skill contract requires it.

## Look up only what the decision needs

User-requested — 2026-11-01: the history is “categorized and organized so it can efficiently be looked up”; an agent should not go “reading the whole … user preference history, all the files we've collected and everything every single time for unnecessary things”. Find “the correct balance”.

- **Settled work needs no lookup.** When the current request, operating instructions and owning skills already settle the choice (routine fixes and edits, or follow-through on a decided design), proceed without opening the store. Recording a new preference needs only the destination check under **Record every expressed preference**, not a history read.
- **Look up when taste or context is genuinely missing:** an open choice that the user's preferences or past reasons would plausibly change (product or design direction, naming, scope trade-offs, which option to recommend), or the user refers to an earlier decision or asks why something was chosen or rejected.
- **Start narrow and stop when settled.** Resolve the scope once per task and reuse it; read a root or the structure reference only when it is unfamiliar. Query the narrowest likely branch with the user's terms. Widen to a parent branch or the general scope only for a concrete unanswered question, such as a cross-project preference that could apply. Choose entries from their title, status, scope and meaning, then read each selected `line`–`end_line` range completely and follow its supersession links. Stop when more reading would not change what you would do; don't open adjacent branches, every match or whole topic files just in case.
- **Read deeper when it matters.** Give context, rejected options and sources a fuller read when the decision is consequential, entries appear to conflict, or the user asks why. If nothing relevant exists, use judgment, or ask when the unknown is material.

## Find the right record

The reference file is called **user-preferences.md**; read [user-preferences.md](user-preferences.md) when the private store's structure is unfamiliar. Resolve the relevant scope with:

```text
python3 <skill-dir>/scripts/user-preferences.py locate --cwd <project-directory>
```

The helper only reads. It reports the canonical project profile, its `user-preferences.md`, and the general record. Linked Git worktrees resolve to the same profile; normalized remote aliases can recover an existing profile after a move. A conflicting match is an error, never permission to pick another project's history. Non-Git projects can have explicit profiles too. An unregistered chat directory uses the general scope until an actual project is identified.

`index <scope-or-branch>` prints a compact branch map: each Markdown file with its entry count. `index <scope-or-branch> --query <words>` lists entries whose ID, path, title or body contain every term, case-insensitively, with their status, scope, meaning, file and exact inclusive `line`–`end_line` range. `inventory` lists registered projects. None of these creates another editable index. Use the user's terminology and relevant filenames as search terms. Do not dump the entire store into context.

## Record every expressed preference

Capture **every single preference expressed, including every opinionated whittling down of a decision**: wants, dislikes, taste reactions, terminology, choices, rejected alternatives, corrections, approved designs and their useful reasons. Do this during the same task, before compaction or the final reply loses the evidence. Do not filter out an explicit preference because it seems minor, infrequent or too specific.

Read [references/record-format.md](references/record-format.md) before writing the first entry or resolving a correction. Save generously, write proportionately, apply carefully: preserve every expressed preference, with detail proportionate to the decision. A simple preference can be brief; go deep where the surrounding choice, stated reasons, useful examples and rejected options explain the user's judgment. Always preserve the actual words, meaning, scope and source pointers. Label inferred reasons and agent-created examples, say when a reason was not stated, and keep tentative statements `uncertain`. Do not manufacture detail to fill fields. Keep recording light enough to support the actual task.

The user's words must come from their authored message or a verified source, not an assistant summary. A maintained instruction can be cited as such; do not present its prose as a verbatim conversation quote. Quoted selections, pasted documents, tool output and other people's words are context, not automatically the user's preferences. A delegation such as “whatever's best” may be recorded together with the agent's decision as `delegated`; the chosen implementation is not a user-endorsed default. Silence is not endorsement.

Keep one-off choices as one-off evidence. A previous approval, purchase, deployment or permission never authorizes repeating the action. Never store credentials, access-bearing URLs or unnecessary third-party private details. This record is preference evidence, not a debug log or task ledger.

Before adding, query the destination topic's branch directory for the same subject, not the whole history; check the general scope too when the preference may already be recorded there. Reinforce an existing preference with its new evidence, narrow its scope, or add a correction that explicitly supersedes the older entry; retain the original wording/history. Put each entry in the topic file for its subject so lookup by category works. Re-read the target immediately before a minimal insertion. When concurrent edits to that file are likely, a topic-named leaf in the same branch is fine; don't scatter ordinary notes by task. Validate with `check <scope>` after edits.

## Grow the hierarchy and install project profiles

Keep roots small and explanatory. Start with a useful topic file; split into product aspects and, when helpful, affected files as the project grows. Preserve IDs and sources when moving entries. The filesystem is the canonical branch map; `index` derives navigation directly from it, so no separate list depends on an agent remembering to regenerate it.

When creating a project, or explicitly rolling this out to existing projects, read [references/project-setup.md](references/project-setup.md). Reuse an existing profile, otherwise create its private project skill and `user-preferences.md`. Make that project skill discoverable through the host's supported local skill directory; linked worktrees share the same private target. Keep the records outside public repositories and outside this reusable skill package. New worktrees can find the existing profile through the global helper before a local link is added.

## Use the history without replacing existing systems

The current instruction and applicable operating rules govern the task. Apply active explicit preferences only within their conditions and scope; narrower preferences apply inside that scope. Superseded preferences remain historical evidence. One-off and delegated choices provide context with lower weight, not general defaults. For an apparent conflict, read only the entries involved and their context; differing scopes or conditions often mean both still apply. When a newer explicit preference changes an owning rule, update that rule through its normal workflow and cross-link the evidence; surface a material unresolved conflict.

Keep existing skill learning and repository `LEARNINGS.md` intact. They hold reusable workflow and verified technical lessons; these files hold what the user wanted and why. Useful duplication is allowed. Recording a preference never replaces an otherwise-required skill update, decision comment or technical learning, and never authorizes unrelated work.

## Weekly public updates

On first use in a task, or the next use after a week in a long task, follow [references/public-updates.md](references/public-updates.md). Respect opt-outs, permissions and local edits. Check the pinned public source; ask before installing an available update and explain what changed afterward. Silence is not approval. Never force/reset/discard work, edit plugin caches or touch the private records during an update. Keep check dates and leases outside the package; no daemon or hook is installed. Updating this skill never authorizes its domain actions.

## Definition of done

The requested preferences have faithful, scoped, source-backed entries; lookup reaches the right shared project/general history and reads only what the decision needed; corrections and links validate; private records are absent from public commits. Existing learning duties and approval boundaries still hold. Report initial-history coverage honestly: installing a profile does not mean every old conversation has been imported. Do not promise that skill installation guarantees future agent compliance.
