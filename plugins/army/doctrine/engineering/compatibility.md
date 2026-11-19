# Compatibility checker

Goal: the product looks and works right on the devices, browsers and languages the audience actually uses.

## Checks
- **Browsers:** the project's browserslist target (or the last 2 versions of Chrome, Safari, Firefox and Edge). Watch for Safari quirks (dates, flexbox gap in older versions, `100vh` on iOS, autoplay rules).
- **Devices and viewports:** 320, 375, 768, 1024 and 1440 px widths. Touch versus mouse, the on-screen keyboard covering inputs, safe areas on notched phones.
- **RTL:** layout mirroring, icons, mixed Hebrew/English text, numbers and punctuation, form fields with `dir="auto"` for user input.
- **Feature support:** check APIs with caniuse data before using them. Provide fallbacks or polyfills when the targets need them.
- **Accessibility settings:** 200% zoom, reduced motion, high contrast/forced colors, and dark mode.
- If Playwright is available, run the key pages in Chromium, WebKit and Firefox, in mobile emulation, and capture screenshots.

## Output
A compatibility matrix (page · browser/device · status · issue · fix), with screenshots when available.
