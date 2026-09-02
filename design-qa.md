# Discover workspace design QA

- Reference viewport: approved D-022 fourth-image concept at 1440×1024.
- Implemented viewport: 1440×1024 browser capture from the local production build; the same image subsequently passed Compose build and health validation.
- Visual differences: synthetic employer/job content replaces all reference identity and private data; controls use Lucide outline icons; the evidence cards expand vertically to retain every D-019 state.
- Responsive checks: desktop three-pane at 1440 and 1280; compact sidebar at 1024–1279; master/detail with drawer at 768–1023; single-column list/detail, Back navigation, and expandable filters below 768.
- Accessibility checks: semantic landmarks/headings, visible focus, keyboard controls, 44px touch controls, reduced motion, responsive zoom behavior, and automated axe baseline.
- Interaction checks: selection, search, role/skill/location/source filters, sorting, save/unsave, mobile navigation/filter toggles, Back navigation, and preparation notice.
- Remaining issues: P3 only — the synthetic evidence copy produces slightly taller cards than the reference concept, intentionally preserving all accepted evidence categories without truncation.
- final result: passed

## Candidate Profile and Evidence QA

- Reference viewport: D-022 editorial workspace and sidebar contract.
- Implemented viewports: desktop 1440×1024 and mobile 390×844.
- Workflows: protected Profile editing; Evidence list/detail; unverified fact
  entry; explicit verification; immutable-version edit warning; reconfirmation;
  reason-required revocation; conflict inspection and explicit resolution.
- Accessibility: semantic main/sections/dialogs, text lifecycle labels, visible
  focus, keyboard-operable controls, minimum touch targets, and automated axe
  coverage for the profile editor.
- Privacy: synthetic records only; no demographic collection form; private and
  eligibility values are suppressed from broad list responses.
- Browser verification: production build inspected with synthetic API responses
  at 1440×1024 and 390×844. Profile and Evidence rendered without horizontal
  overflow; fact selection, verification confirmation, and competing-value
  conflict dialog were exercised. Browser console reported zero errors or
  warnings after the verified navigation.
- Remaining issues: P3 only — mobile uses a stacked evidence list/detail rather
  than animated master/detail transitions; no information is removed.
- final result: passed
