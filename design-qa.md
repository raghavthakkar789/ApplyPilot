# Discover workspace design QA

- Reference viewport: approved D-022 fourth-image concept at 1440×1024.
- Implemented viewport: 1440×1024 browser capture from the local production build; the same image subsequently passed Compose build and health validation.
- Visual differences: synthetic employer/job content replaces all reference identity and private data; controls use Lucide outline icons; the evidence cards expand vertically to retain every D-019 state.
- Responsive checks: desktop three-pane at 1440 and 1280; compact sidebar at 1024–1279; master/detail with drawer at 768–1023; single-column list/detail, Back navigation, and expandable filters below 768.
- Accessibility checks: semantic landmarks/headings, visible focus, keyboard controls, 44px touch controls, reduced motion, responsive zoom behavior, and automated axe baseline.
- Interaction checks: selection, search, role/skill/location/source filters, sorting, save/unsave, mobile navigation/filter toggles, Back navigation, and preparation notice.
- Remaining issues: P3 only — the synthetic evidence copy produces slightly taller cards than the reference concept, intentionally preserving all accepted evidence categories without truncation.
- final result: passed
