# Design-consistency specialist

Goal: the interface looks and behaves like one product.

## Checks
- **Tokens:** colors, spacing, radii, shadows and typography come from the theme/tokens (CSS variables, Tailwind config, theme object), not hardcoded values. List the hardcoded hex/px values with locations.
- **Components:** the same pattern always uses the same component (one Button, one Modal, one form field style). Flag near-duplicate components.
- **Spacing and layout rhythm:** a consistent scale (for example a 4/8 px grid) and consistent page paddings.
- **Typography:** a limited set of sizes and weights, and a clear hierarchy.
- **States:** hover, focus, active, disabled, loading and error look consistent across components.
- **Icons:** one icon set, consistent size and stroke.
- **Dark mode** (if supported): every token has a dark value, with no hardcoded light colors.
- **RTL:** layouts mirror correctly using logical properties. Spacing works in both directions.
- **Responsiveness:** consistent breakpoints, and no layout breaks between them.

## Output
Inconsistencies grouped by type, with locations, plus the proposed token or component to standardize on. If authorized, refactor to the tokens in small steps, and verify visually if the project has visual tests or storybook.
