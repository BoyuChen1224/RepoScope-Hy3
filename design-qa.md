# Product design QA

## Target and test states

- Reference: `assets/design/tencent-console-concept.png`
- Desktop implementation: `assets/screenshots/tencent-redesign-desktop.png`
- Mobile implementation: `assets/screenshots/tencent-redesign-mobile.png`
- Dark implementation: `assets/screenshots/tencent-redesign-dark.png`
- Verified states: Chinese default, English switch, fixed demo result, dynamic toast translation,
  light/dark theme switch, preference restoration, responsive desktop and mobile layouts.

## Visual comparison

| Check | Initial finding | Resolution | Final severity |
| --- | --- | --- | --- |
| Enterprise console hierarchy | The first pass matched the white console shell, four-step workflow, left input panel, and right result panel. | Kept the target hierarchy and restrained Tencent Cloud-like blue/neutral palette. | None |
| Above-the-fold decision value | The evidence inventory initially pushed the adoption decision too far below the viewport. | Reduced inventory and action spacing so the score, evidence, decision, claims, and risks scan in one compact workspace. | None |
| Bilingual behavior | The first English switch left the active demo toast in Chinese. | Added keyed live-status state and rerendered all demo data, labels, buttons, and notices on language change. | None |
| Dark theme | Dense evidence and evaluation sections required more than a page-level background swap. | Added semantic theme tokens for surfaces, borders, fields, status colors, bars, semantic review, toast, and focus states. | None |
| Responsive behavior | Desktop used a two-column workspace; mobile needed a single-column reading order. | Stacked input before results, retained horizontal workflow scanning, and kept primary controls full-width. | None |
| Asset integrity | No product logo or icon should be approximated with text art. | Used a self-hosted icon font and retained the explicit non-official-project disclaimer. | None |

## Functional checks

- `中 / EN` updates `lang`, page title, navigation, form copy, results, errors/success states, and demo content.
- Chinese is the default when no saved preference exists; a valid saved English preference is restored.
- Light mode is the default when no saved preference exists; dark mode is restored after refresh.
- Core repository inspection, report generation, deterministic evaluation, and semantic review IDs and API paths remain unchanged.
- Keyboard focus styling, reduced-motion handling, semantic regions, labels, and ARIA states are present.

## Final result

final result: passed

No open P0, P1, or P2 visual or interaction findings remain in the tested states.
