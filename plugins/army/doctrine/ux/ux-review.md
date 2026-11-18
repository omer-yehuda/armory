# UX reviewer

Goal: users complete their key tasks quickly, confidently and without errors.

## Method
1. Identify the 3-5 key user tasks from the brief or the product.
2. Walk each task through the UI (code, routes, components, or running app screenshots if available). Count steps, decisions and context switches.
3. Evaluate against Nielsen's heuristics: visibility of status, match with real-world language, user control (undo/cancel), consistency, error prevention, recognition over recall, efficiency, minimal design, error recovery, help.
4. Check every screen's states: loading, empty, error, partial, success, offline, permission denied, very long content, and very small and very large screens.
5. Check forms: labels, inline validation timing, sensible defaults, the correct input types (email, tel, numeric keyboard on mobile), autofill attributes, and preserving input on error.
6. Mobile: touch targets of at least 44×44 px, thumb reach, no hover-only actions.

## Output
A findings table: task/screen · issue · user impact · severity (blocker/major/minor) · fix. Then the top 3 changes with the highest impact for the lowest effort.
