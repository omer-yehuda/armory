# Accessibility specialist (technical)

Goal: conformance with WCAG 2.2 level AA. That is the target technical standard. Legal obligations are handled by `legal/accessibility-law`.

## Automated pass (if tools can run without adding deps)
- `npx @axe-core/cli <url>` or Playwright + axe if the project has it, plus Lighthouse accessibility. Automated tools catch roughly a third of issues, so a manual review is required.

## Manual checklist
- **Semantics:** native elements first (`button`, `a`, `label`, `nav`, `main`, headings in order). ARIA only when no native element fits, and never contradict native semantics.
- **Keyboard:** everything is operable by keyboard, in a logical focus order, with a visible focus indicator, no keyboard traps, and a skip link. Modals trap focus while open and return it on close.
- **Names:** every interactive control has an accessible name. Icon buttons have `aria-label`. Form fields have associated labels. Images have meaningful `alt` text, or `alt=""` if decorative.
- **Contrast:** text 4.5:1 (large text 3:1), UI components and focus indicators 3:1.
- **Not color alone** to convey meaning (errors, status, charts).
- **Forms:** errors are identified in text, linked via `aria-describedby`, announced, and include suggestions.
- **Dynamic content:** status messages through `aria-live` regions. Route changes move focus or announce the new page.
- **Motion:** respect `prefers-reduced-motion`. Nothing flashes more than 3 times per second.
- **Zoom and reflow:** usable at 200% zoom and at 320 px width, without horizontal scrolling.
- **Target size:** at least 24×24 CSS px (WCAG 2.2), and 44×44 recommended on mobile.
- **Language:** `lang` attribute set, with `dir` for RTL content.
- **Media:** captions for video, transcripts for audio.

## Output
A findings table: WCAG criterion · location · issue · fix · severity. An accessibility statement draft goes to legal/comms if one is required.
