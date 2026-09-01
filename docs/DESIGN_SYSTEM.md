# ApplyPilot Design System

## 1. Status and authority

This document records the owner-approved visual direction for ApplyPilot and is
the implementation contract for the Milestone 1 web interface. The approved
reference is the fourth design selected on 2026-09-02: a dark structured sidebar
paired with a light editorial workspace and an evidence-rich job detail view.

The reference image defines visual hierarchy and composition, not product truth.
Its people, jobs, companies, dates, percentages, locations, eligibility claims,
and source records are synthetic examples. Implementation must obtain displayed
values from typed domain data and must obey `PRODUCT_REQUIREMENTS.md`, D-015,
D-018, D-019, D-020, and D-021.

## 2. Product experience

ApplyPilot should feel like a calm professional research cockpit for one
technical candidate. It is desktop-first because the primary task compares a
ranked opportunity list with dense, cited match evidence. The interface should
feel precise and editorial rather than promotional, gamified, or AI-themed.

Design principles:

1. **Evidence before confidence.** Scores never appear without their evidence
   coverage, eligibility state, and an expansion path to source citations.
2. **Dense, not cramped.** Serious job research benefits from visible context,
   but grouping, whitespace, and typography must preserve scanability.
3. **State is explicit.** Selected, saved, stale, loading, empty, uncertain,
   blocked, and error states must not rely on colour alone.
4. **Actions say what happens.** Preparation actions cannot imply submission.
   Final Apply is absent until its later milestone and accepted policies exist.
5. **Synthetic fixtures stay synthetic.** No owner identity, resume content,
   authorization status, or real application detail enters committed fixtures.

## 3. Desktop shell

The canonical desktop viewport is 1440 by 1024 CSS pixels. The layout has three
primary regions:

| Region | Width | Purpose |
| --- | ---: | --- |
| Sidebar | 192 px | Persistent product navigation and owner menu |
| Opportunity pane | 528 px | Search, filters, ranking, and job selection |
| Detail pane | Remaining width, minimum 640 px | Job facts, match evidence, and preparation action |

At widths of 1280 px and above, all three regions remain visible. The sidebar
is fixed to the left; the opportunity and detail panes scroll independently
below the shared workspace header. Dividers are one-pixel neutral borders.

The browser-visible application origin remains `http://127.0.0.1:3000`. Layout
decisions do not change the same-origin API, session, CSRF, or network policies.

## 4. Responsive behavior

| Breakpoint | Behavior |
| --- | --- |
| `>= 1280 px` | Full sidebar, opportunity pane, and detail pane |
| `1024–1279 px` | Compact 72 px icon sidebar; list and detail remain split |
| `768–1023 px` | Sidebar becomes a labelled drawer; list and detail use a two-view master/detail pattern |
| `< 768 px` | Single-column flow; search and filters open sheets; selecting a job opens its detail view with a persistent Back control |

No information is removed solely because the viewport is smaller. Match
sections become stacked disclosure panels in the same semantic order. Primary
actions remain reachable without covering evidence. Horizontal scrolling is
prohibited for ordinary page content.

## 5. Colour system

Colours are semantic tokens; components must not use untracked literal colours.
Initial light-theme tokens:

| Token | Value | Use |
| --- | --- | --- |
| `--nav-bg` | `#061D33` | Sidebar base |
| `--nav-bg-active` | `#102D47` | Active navigation row |
| `--nav-text` | `#F5FAFF` | Primary sidebar text |
| `--nav-muted` | `#A9BED0` | Secondary sidebar text |
| `--accent` | `#19D4C5` | Brand accent and active edge |
| `--canvas` | `#F8F7F4` | Application background |
| `--surface` | `#FFFFFF` | Panels and controls |
| `--surface-selected` | `#EDF4FC` | Selected opportunity |
| `--text-strong` | `#071C35` | Headings and primary content |
| `--text` | `#213A55` | Body content |
| `--text-muted` | `#64758A` | Supporting metadata |
| `--border` | `#D9E0E7` | Standard separators |
| `--border-strong` | `#BBC7D3` | Control outlines |
| `--link` | `#0759C7` | Links and blue actions |
| `--success` | `#07866F` | Verified/compatible/full match |
| `--warning` | `#D97706` | Partial/unclear/review required |
| `--danger` | `#C93632` | Verified gap/blocked/destructive |
| `--focus` | `#1769E0` | Keyboard focus ring |

Every text/background pairing must meet WCAG 2.2 AA. Status uses an icon and
label in addition to colour. A dark content theme is deferred; the sidebar is
dark in M1, while the workspace follows the approved light direction.

## 6. Typography

Use freely distributable local or bundled web fonts with no runtime tracking or
third-party font request.

- Display and job-title face: **Source Serif 4**, fallback `Georgia, serif`.
- Interface and data face: **Inter**, fallback `system-ui, sans-serif`.
- Base size: 16 px; compact metadata may use 12–14 px but never below 12 px.
- Body line height: 1.5. Dense UI labels use at least 1.3.
- Page title: 44/48 px desktop, 34/40 px compact, weight 600.
- Job detail title: 36/42 px desktop, 28/34 px compact, weight 600.
- Section heading: 16/22 px, weight 650.
- Control and navigation labels: 14–16 px, weight 500–600.
- Numeric scores use tabular numerals.

## 7. Spacing and shape

Use a four-pixel base scale: `4, 8, 12, 16, 20, 24, 32, 40, 48, 64`.

- Workspace outer padding: 24 px desktop, 20 px tablet, 16 px mobile.
- Dense row padding: 16 px vertically and 20 px horizontally.
- Control height: 40 px compact, 44 px primary/mobile.
- Border radius: 4 px for compact controls, 6 px for buttons and panels,
  pill radius only for counts or explicit status chips.
- Shadows are subtle and reserved for overlays, drawers, menus, and sticky
  elevation. Persistent panes rely on borders instead of card shadows.
- Motion duration: 120–200 ms with reduced-motion support.

## 8. Navigation

The sidebar order is:

1. Discover
2. Saved
3. Applications
4. Evidence
5. Profile
6. Preferences
7. Settings

The ApplyPilot wordmark appears at the top. The active destination has a teal
left edge, darker active background, icon, label, and `aria-current="page"`.
The bottom owner control uses a synthetic/local display label from owner data;
the reference name must not be hardcoded. The menu provides session management
and sign out. There is no account switching, team switcher, invitation, billing,
or public registration UI.

Use a maintained outline icon library with consistent 1.5–2 px strokes. Icons
must have accessible names when they are the sole label. Do not use emoji,
handcrafted SVG, or text glyphs as interface icons.

## 9. Discover workspace

### Header and controls

The header contains the `Global opportunities` title, a factual subtitle, the
current date formatted in the owner's locale, and a compact menu button. Below
it, the toolbar contains:

- Keyword search across roles, skills, employers, and normalized job text.
- Role, skill, location, source, and advanced-filter controls.
- An active-filter count.
- Sort selection, defaulting to the accepted ranking derivation rather than an
  unexplained `Best fit` label.

Search is debounced, keyboard accessible, and labelled. Filter controls expose
selected values, clear actions, and applied state. Unknown data must remain
unknown; filters cannot manufacture eligibility or location facts.

### Opportunity list

Rows are grouped by retrieval/publication date when available. Each row may show:

- Ranking position.
- Freshness/status indicator with text alternative.
- Job title and employer.
- Structured location, work mode, and employment type.
- Approved source attribution.
- Capability alignment and evidence coverage when displayable.
- Eligibility state when relevant.
- Relative freshness with an exact timestamp available to assistive technology.
- Save toggle.

The selected row uses a blue leading edge, selected surface, and programmatic
selected state. Under 40% capability evidence coverage, the row displays
`Insufficient evidence`; it must not show a precise combined percentage.
Unknown, verified gap, possible relevance, and confirmed blocker remain distinct.

Required list states: loading skeleton, no sources configured, no jobs retrieved,
no filter results, stale data, partial adapter failure, pagination/loading more,
and recoverable error.

## 10. Job detail workspace

### Job identity

The detail header shows source attribution, supplied posting/update time, save
state, overflow actions, title, employer, structured location, work mode, and
employment type. Links open the preserved source or canonical employer URL and
retain the attribution required by D-018.

### Match summary

The summary displays these outputs separately:

1. Capability alignment.
2. Preference compatibility.
3. Eligibility: `compatible`, `unclear`, or `blocked`.
4. Evidence coverage.
5. Extraction confidence.

If shown, combined alignment must be labelled as a derived alignment—not an
`overall fit`, hiring probability, interview probability, recruiter interest,
candidate-quality judgment, or performance prediction. Ranking adjustment and
coverage remain inspectable. Score adjectives such as `Excellent fit` are not
used as celebratory or discouraging judgments.

### Evidence sections

The reference grid becomes six semantic sections:

1. Capability alignment by accepted dimensions.
2. Preference compatibility by accepted dimensions.
3. Eligibility requirements, uncertainties, and confirmed blockers.
4. Evidence coverage: covered, partial, and missing.
5. Verified matches and partial matches.
6. Missing evidence, verified gaps, owner actions, and possible relevance.

Every contribution expands to cited job text, source location, exact eligible
verified fact version, scoring-rule version, and weight-set version. Inferred
signals appear only under `Possible relevance`; they never satisfy requirements,
score, clear blockers, or enter application content. Owner corrections create
audited new match versions.

### Role information and actions

Below match evidence, show the sanitized role description and structured facts
such as seniority, team, reporting line, compensation, languages, and working
hours only when present. Missing values are labelled unknown rather than omitted
in a way that implies a negative fact.

Persistent actions:

- `Save for later` / `Saved`.
- `Prepare application`, which opens Application Studio and does not submit,
  send email, create a candidate, or contact an employer.

Supporting microcopy states: `Preparation does not submit an application.`
Final Apply controls are outside M1 and must not be mocked as active behavior.

## 11. Component inventory

Initial reusable frontend components:

- `AppShell`, `SidebarNav`, `OwnerMenu`, `WorkspaceHeader`.
- `OpportunityToolbar`, `SearchField`, `FilterMenu`, `ActiveFilterSummary`,
  `SortMenu`.
- `OpportunityList`, `OpportunityGroup`, `OpportunityRow`, `SaveJobButton`.
- `JobDetailHeader`, `SourceAttribution`, `StructuredJobFacts`.
- `MatchSummary`, `AlignmentMetric`, `EligibilityStatus`, `CoverageMetric`,
  `ConfidenceStatus`.
- `EvidenceSection`, `RequirementRow`, `EvidenceCitation`, `FactorList`,
  `OwnerActionList`.
- `PreparationActionBar`, `EmptyState`, `ErrorState`, `LoadingSkeleton`,
  `StaleDataNotice`, `AdapterHealthNotice`.

Components consume generated API types. They do not implement authentication,
fact verification, score calculation, eligibility, blocker, provenance,
approval, or audit rules independently.

## 12. Interaction and accessibility contract

- All workflows are operable by keyboard alone with logical focus order.
- Focus is never removed and uses a visible two-pixel ring with sufficient
  contrast.
- Split panes use landmarks and labelled regions; headings follow a logical
  hierarchy.
- Selecting a row announces the new detail context without unexpectedly moving
  focus on desktop. Master/detail navigation manages focus explicitly on mobile.
- Menus, sheets, disclosures, and dialogs follow WAI-ARIA authoring patterns,
  trap focus only when modal, and restore focus on close.
- Touch targets are at least 44 by 44 px on touch layouts.
- Status, charts, and progress bars expose equivalent text and values.
- Loading changes use restrained live regions; errors identify recovery actions.
- Content remains usable at 200% zoom and with reduced motion.
- Automated axe checks and Playwright keyboard tests are release gates, not
  substitutes for manual review.

## 13. M1 implementation slice

The first coded vertical slice is intentionally narrow:

1. Authenticated application shell.
2. Discover workspace with synthetic typed opportunities.
3. Search, filter, sort, save, and selection interactions.
4. Responsive job detail with D-019-compliant synthetic match evidence.
5. Preparation-only action that opens a non-submitting placeholder boundary.
6. Loading, empty, uncertain, blocked, insufficient-evidence, and error states.

The slice proves that the owner can sign in, inspect opportunities, select one,
understand why it is ranked, and begin preparation without implying external
submission. It does not add provider AI, external adapters, persistence beyond
the approved scaffold, direct submission, email sending, public hosting, or
unresolved later-milestone behavior.

## 14. Visual verification

Implementation is not complete until the reference and rendered desktop view
are compared at the same 1440 by 1024 viewport. Design QA must verify layout,
typography, spacing, colours, responsive states, keyboard operation, contrast,
and the semantic corrections in this document. P0–P2 differences are fixed
before handoff; remaining P3 polish is recorded.

The approved image may be retained outside Git as design evidence. If a copy is
ever committed, it must contain only synthetic content and use an intentional
asset path and provenance note.
