---
name: learned-user-preferences
description: Use whenever you want to learn about the kinds of things the user wants. Record every expressed preference, opinionated decision, correction, rejected option and reason in private project and general records. Consult relevant examples and decision history when choosing an approach or learning why something was wanted. Complements existing skills and technical learnings; does not replace their instructions.
---

# Learned User Preferences

Keep the user's wording, examples and decision reasons available to future agents without loading a large history into every task.

## Continuous improvement

Potentially improve this skill as part of using it, but don't add every finding. Favor a small same-task update when the user expresses how this skill should normally work; their statement establishes their preference without repeated examples, a reproduced failure or a separate save request. Preserve wording, conditions and scope. Curiosity, hypotheticals and choices limited to one task are not lasting defaults.

For agent-discovered lessons, make a quick judgment: will this verified lesson likely help again, save meaningful repeated work or prevent a serious mistake? Its benefit must justify the added instructions and maintenance. Assume capable agents; skip routine advice and isolated incident facts. Make qualifying improvements during the same task, refine existing guidance, retest affected behavior and validate the skill. After edits, keep the shared contract here and move conditional detail into directly linked references when useful, without needless fragmentation. Preserve manual edits; exclude secrets and transient runtime state.

Mark agent-initiated material changes beside their guidance with `Self-improved — YYYY-MM-DD`, a brief reason and evidence. Keep longer audit evidence in a reference. Do not apply that label to the user's expressed preferences or invent provenance. This filter governs improvements to the workflow, **not which expressed preferences are recorded**.

## Skill usage announcement

Before skill-directed action, tell the user this skill is active and briefly why. Use their response-preference announcement format when available; otherwise use one short plain sentence. Preserve explicit silent-use exceptions. One announcement covers continuing work within the current task; announce again if the user's configured skill contract requires it.

## Find the right record

The reference file is called **user-preferences.md**. Read [user-preferences.md](user-preferences.md) for the private store structure, then resolve the relevant scope:

```text
python3 <skill-dir>/scripts/user-preferences.py locate --cwd <project-directory>
```

The helper only reads. It reports the canonical project profile, its `user-preferences.md`, and the general record. Linked Git worktrees resolve to the same profile; normalized remote aliases can recover an existing profile after a move. A conflicting match is an error, never permission to pick another project's history. Non-Git projects can have explicit profiles too. An unregistered chat directory uses the general scope until an actual project is identified.

Open the relevant root file, then search or read only matching branches. `index <scope> --query <words>` prints a live entry map; `inventory` lists registered projects. Neither creates another editable index. Use the user's terminology and relevant filenames as search terms. Read matched entries completely, including scope, status and linked corrections. Do not dump the entire store into context.

## Record every expressed preference

Capture **every single preference expressed, including every opinionated whittling down of a decision**: wants, dislikes, taste reactions, terminology, choices, rejected alternatives, corrections, approved designs and their useful reasons. Do this during the same task, before compaction or the final reply loses the evidence. Do not filter out an explicit preference because it seems minor, infrequent or too specific.

Read [references/record-format.md](references/record-format.md) before writing the first entry or resolving a correction. Preserve the actual words, surrounding choice/context, meaning, scope, source pointers, stated reasons, useful examples and rejected options. Explain deeply where the evidence supports it; label inferred reasons and agent-created examples, and say when a reason was not stated. Do not manufacture detail to fill fields.

The user's words must come from their authored message or a verified source, not an assistant summary. A maintained instruction can be cited as such; do not present its prose as a verbatim conversation quote. Quoted selections, pasted documents, tool output and other people's words are context, not automatically the user's preferences. A delegation such as “whatever's best” may be recorded together with the agent's decision as `delegated`; the chosen implementation is not a user-endorsed default. Silence is not endorsement.

Keep one-off choices as one-off evidence. A previous approval, purchase, deployment or permission never authorizes repeating the action. Never store credentials, access-bearing URLs or unnecessary third-party private details. This record is preference evidence, not a debug log or task ledger.

Search before adding. Reinforce an existing preference with its new evidence, narrow its scope, or add a correction that explicitly supersedes the older entry; retain the original wording/history. Re-read a shared target immediately before a minimal edit. For concurrent work, prefer a uniquely named leaf with task-specific IDs over rewriting a shared root. Validate with `check <scope>` after edits.

## Grow the hierarchy and install project profiles

Keep roots small and explanatory. Start with a useful topic file; split into product aspects and, when helpful, affected files as the project grows. Preserve IDs and sources when moving entries. The filesystem is the canonical branch map; `index` derives navigation directly from it, so no separate list depends on an agent remembering to regenerate it.

When creating a project, or explicitly rolling this out to existing projects, read [references/project-setup.md](references/project-setup.md). Reuse an existing profile, otherwise create its private project skill and `user-preferences.md`. Make that project skill discoverable through the host's supported local skill directory; linked worktrees share the same private target. Keep the records outside public repositories and outside this reusable skill package. New worktrees can find the existing profile through the global helper before a local link is added.

## Use the history without replacing existing systems

The current instruction and applicable operating rules govern the task. Apply active explicit preferences only within their conditions and scope; narrower preferences apply inside that scope. Superseded preferences remain historical evidence. One-off and delegated choices provide context with lower weight, not general defaults. When a newer explicit preference changes an owning rule, update that rule through its normal workflow and cross-link the evidence; surface a material unresolved conflict.

Keep existing skill learning and repository `LEARNINGS.md` intact. They hold reusable workflow and verified technical lessons; these files hold what the user wanted and why. Useful duplication is allowed. Recording a preference never replaces an otherwise-required skill update, decision comment or technical learning, and never authorizes unrelated work.

## Weekly public updates

On first use in a task, or the next use after a week in a long task, follow [references/public-updates.md](references/public-updates.md). Respect opt-outs, permissions and local edits. Check the pinned public source; ask before installing an available update and explain what changed afterward. Silence is not approval. Never force/reset/discard work, edit plugin caches or touch the private records during an update. Keep check dates and leases outside the package; no daemon or hook is installed. Updating this skill never authorizes its domain actions.

## Definition of done

The requested preferences have faithful, scoped, source-backed entries; lookup reaches the right shared project/general history; corrections and links validate; private records are absent from public commits. Existing learning duties and approval boundaries still hold. Report initial-history coverage honestly: installing a profile does not mean every old conversation has been imported. Do not promise that skill installation guarantees future agent compliance.
