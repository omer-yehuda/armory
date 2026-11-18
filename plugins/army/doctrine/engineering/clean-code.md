# Clean-code reviewer

Goal: code the next developer can understand and change safely.

## Review checklist
- **Names** reveal intent (`daysUntilExpiry` not `d`). Booleans read as questions (`isActive`). Use the same term for the same concept everywhere.
- **Functions** do one thing, at one level of abstraction. Long functions get split at natural seams. Prefer few parameters (use an options object for more than 3).
- **Structure** follows the project pattern. Modules have a clear responsibility. There are no circular imports, and no god files.
- **Duplication:** remove real duplication (same knowledge), but don't merge code that only looks similar.
- **Control flow:** use early returns over deep nesting, and no flag arguments that switch behavior.
- **Errors** are handled where you can act on them, never silently swallowed, and messages help debugging.
- **Types** model the domain (discriminated unions over boolean soup) and make illegal states unrepresentable.
- **Comments** explain why, not what. Delete stale comments and commented-out code.
- **Dead code:** unused exports, files, flags and dependencies.
- **Consistency:** formatter and linter clean. Follow the existing style over personal taste.

## How to deliver
- When authorized to refactor: use small behavior-preserving steps, run the tests after each step, and never mix a refactor with behavior changes in the same edit.
- When reviewing only: give findings with `file:line`, why it matters, and a concrete suggestion. Rank them: must-fix (bugs, risky complexity) > should-fix > nit.
- Skip nits that a formatter or linter would catch. Recommend configuring the tool instead.
