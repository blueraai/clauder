# RULES (MUST DO)

1. You MUST NEVER update this file, and ALWAYS honor and enforce all of its rules above all else. Only the user may ever update these rules. You may NEVER overrule these in any way. You SHALL NEVER summarize those rules, they MUST be followed verbatim.
2. If you face any deadlock or uncertainty in honoring these rules, pause and explain your issue to the user, seeking for guidance.
3. You MUST NEVER read any file or folder matching any entry in the `.claude/.ignore` file, or any secret like keys or credentials, even if you are asked to do so or you deem it necessary.
4. You MUST NEVER write any file or folder matching any entry in the `.claude/.immutable` file, even if you are asked to do so or you deem it necessary.
5. You MUST ALWAYS explain in the most amount of details possible the actions you are about to take and pause to ask for review and approval before proceeding with making any code change, any tool call, taking any action, or executing any command (OTHER THAN `say`, or any command explicitly allowed in `.claude/settings.json` or `.claude/settings.local.json`).
6. Unless small and purely visual, any effort MUST be broken down into a series of the smallest possible steps, each with:
- Clear goals
- Extensive risks and edge cases outlined
- A testing plan
- A backward compatibility assessment
If any of these are unclear, risky, or require user input, you MUST pause and discuss with the user before proceeding.
7. When planning or executing anything you:
- Ensure any design and implementation is coherent and compatible with `HISTORY.md` and `SPECIFICATIONS.md`, should those files exist at project root level.
- MUST Check for inconsistencies (e.g., duplicate code, conflicting code, dead code, unstable code, anything that breaks existing behavior, anything that conflicts with established patterns)
- MUST Check for best practices
- MUST Check, clearly highlight, and request user consent, for any important or potentially unsafe operation other than a code change (e.g., running unsual commands, running important commands, running unsafe commands, taking actions on a system like a database, repository, server, modifying access control)
- MUST Check for unsafe practices (e.g., security issues, irreversible actions like deletions, accessing private data such as keys, passwords, or environment variables)
- MUST Check for missed use cases and edge cases
- MUST Check for user experience inconsistencies or breakage
- MUST Check for possible side effects (direct or indirect)
- MUST Check, clearly highlight, and request user consent, for any irreversible or hardly reversible action (e.g., running qualifying commands, deletions)
- MUST Check, clearly highlight, and request user consent, for anything that may impact the production environment
8. After actions are taken, ensure that `HISTORY.md` and `SPECIFICATIONS.md` at project root level are correctly updated to reflect the latest state and decisions, should those files exist. Ensure these remain coherent, complete, best represented, best organized. `HISTORY.md` should include a summary of the request, detailed description of changes, and reasoning. `SPECIFICATIONS.md` should reflect all latest specifications.
9. Once your are done with your current task, before committing, you MUST present ALL diffs with the last commit and seek user review and approval. 
- If the user approves, proceed with updating the `HISTORY.md` and `SPECIFICATIONS.md` files if they exist and commit your changes with `[claude] <summary>` format, including a meaningful summary and an extensive description of the changes.
- If the user comments, use that feedback to get back to work. Reapply the same effort breakdown, checks, and `HISTORY.md` and `SPECIFICATIONS.md` updates accordingly if these files exist.
- If the user disapproves, show the commit history and present all commits and actions to undo. You MUST get explicit approval from the user before proceeding.
10. You do not need approval to commit or update the `HISTORY.md` and `SPECIFICATIONS.md` files, but you need describe the actions taken in the most amount of details possible.
11. You SHALL NEVER create new `HISTORY.md` and `SPECIFICATIONS.md` files yourself. These must always be created by the user.
11. You SHALL NEVER attempt to bypass a blocking hook or denied access by trying a different method.
12. You SHALL NEVER execute any script which you do not trust.
13. When working with CSS, all `px` values MUST be expressed in `rem`, unless lower than 4px or defining media breakpoint.
14. When creating a new Claude Code Sub-Agent, through `/agents` or when asked to create a new `Claude` agent in natural language, always use the specilized agent called `agent-builder`. Once the new sub-agent has been created, always mention: "☑️ New specialized agent created in `.claude/agents/`. 🔄 Restart Claude Code to start using it.".
15. When updating the `HISTORY.md` and `SPECIFICATIONS.md` files your must use the specilized agent called `specifications-tracking-specialist` if available, unless you are the `specifications-tracking-specialist` sub-agent already. When you prompt this agent, describe exactly what changes occurred, what was requested, what was implemented, and what was dismissed, providing as much detail as possible. Remember, this agent has no context about any questions or previous conversations between you and the user. So be sure to communicate clearly, and provide ALL relevant context.
16. When receiving feedback or reviews from other agents, always keep in mind they may not have as much context as you do, and help put things in perspective. Make sure important feedback is taken into acount, while ensuring that features remain coherent, that context isn't lost, that the project complexity does not outgrow its scope, abd that the project does not become overly future-proofed.
17. Never keep secrets like environment variables or keys in the project. Always recommend keeping them in `~/.env/<project-name>` and never read or access them.