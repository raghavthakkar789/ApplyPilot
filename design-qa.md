# Discover workspace design QA

- Reference viewport: approved D-022 fourth-image concept at 1440×1024.
- Implemented viewport: 1440×1024 browser capture from the local production build; the same image subsequently passed Compose build and health validation.
- Visual differences: synthetic employer/job content replaces all reference identity and private data; controls use Lucide outline icons; the evidence cards expand vertically to retain every D-019 state.
- Responsive checks: desktop three-pane at 1440 and 1280; compact sidebar at 1024–1279; master/detail with drawer at 768–1023; single-column list/detail, Back navigation, and expandable filters below 768.
- Accessibility checks: semantic landmarks/headings, visible focus, keyboard controls, 44px touch controls, reduced motion, responsive zoom behavior, and automated axe baseline.
- Interaction checks: selection, search, role/skill/location/source filters, sorting, save/unsave, mobile navigation/filter toggles, Back navigation, and preparation notice.
- Remaining issues: P3 only — the synthetic evidence copy produces slightly taller cards than the reference concept, intentionally preserving all accepted evidence categories without truncation.
- final result: passed

## Resume Storage and Review QA

- Source visual truth path: `design-source-discover-1440.png`, the existing
  approved D-022 ApplyPilot shell and editorial workspace rendered from the
  current production build.
- Implementation screenshot paths: `implementation-resumes-1440.png` and
  `applypilot-resumes-mobile-final.png`.
- Combined comparison evidence: `design-comparison-resumes-1440.png` places the
  source and implementation together at equal CSS density.
- Viewports and normalization: desktop source and implementation are each
  1440×1024 CSS pixels at device scale 1; combined evidence is 2880×1024.
  Mobile is 390×844 CSS pixels at device scale 1. Browser chrome is excluded.
- State: authenticated synthetic resume, current immutable version, successful
  deterministic text extraction, source citation, and no retained real data.
- Full-view comparison: sidebar width, dark/light balance, serif display type,
  Inter UI type, blue eyebrow, border/radius tokens, selection treatment, and
  editorial density remain consistent with the approved shell. Resume-specific
  content intentionally replaces opportunity scoring and evidence cards.
- Focused comparison: no separate crop was needed because desktop controls,
  typography, citations, and state labels remain readable in the equal-density
  combined image. The mobile screenshot separately verifies action wrapping,
  evidence stacking, and touch layout.
- Typography: Source Serif 4 and Inter hierarchy, weights, wrapping, and compact
  UI labels match the existing shell. Colors/tokens retain navy, teal, blue,
  warning, danger, canvas, and border semantics. Lucide icons remain sharp and
  no raster product asset is substituted.
- Interaction checks: resume selection; upload format/limit messaging; review
  candidate dialog; separate Accept and Verify language; trash confirmation;
  source-cited extraction; keyboard-native controls; and desktop/mobile no-
  overflow checks were exercised. The final browser state reported zero console
  errors or warnings.
- Comparison history: the first mobile capture exposed a P2 master/detail issue
  because list and detail were both visible. The implementation now hides the
  list after mobile selection and provides a 44px `Back to resumes` action. The
  post-fix mobile evidence shows the corrected single-column detail state with
  no horizontal overflow. No P0/P1/P2 issue remains.
- Follow-up polish: P3 only — a resume with one short version leaves more open
  list-pane space than dense Discover results; this is an expected content-
  density difference, not missing information.
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

## Job Catalog and Source Registry QA

- Reference viewport: approved D-022 fourth-image composition at 1440×1024.
- Implemented captures: `job-catalog-desktop-final.png`,
  `job-catalog-manual-dialog-final.png`, and
  `job-catalog-mobile-detail-final.png`.
- Synthetic API state included three catalog records, Greenhouse and Remotive
  provenance, a manual-entry label, and a partial Ashby failure notice.
- Desktop checks: authenticated catalog loading, source attribution, search,
  filter toolbar, selection, save state, `Not evaluated` match boundary, and
  manual-job dialog were exercised at 1440×1024. The manual dialog is modal,
  keyboard-focusable, and clearly states that URLs are never fetched.
- Mobile checks: 390×844 single-column detail flow, Back navigation, Remotive
  attribution, preparation-only action, stacked evidence, and zero horizontal
  overflow. A first capture exposed header/filter overflow; wrapping and
  mobile detail padding were corrected before this final capture.
- Accessibility checks: semantic landmarks, visible focus styles, text status
  labels, 44px controls, responsive filters, and keyboard selection were
  exercised. Browser console reported zero errors and zero warnings.
- Remaining issues: P3 only — normalized job fields will gain richer structured
  display when the future matching and eligibility contracts are implemented.
- final result: passed
