# Reusable React Component Breakdown

**Source Reference:** `reference/ui_reference.mp4`  
**Scope:** Component architecture specification for Phase 3 implementation — no React files are created in this phase.

---

## 1. Component Architecture Overview

The interface separates cleanly into layout shell components, workflow step sections, shared UI primitives, and view-specific cards.

```text
App
├── Header
│   ├── BrandLogo
│   ├── NavTabs
│   └── ConnectionStatus
├── HeroBanner (shown in Guidance view)
│   └── DisclaimerBanner
├── MainLayout
│   ├── GuidanceView (2-column grid)
│   │   ├── LeftColumn
│   │   │   ├── CaseIntakeSection (01)
│   │   │   │   ├── ChatTranscript
│   │   │   │   │   ├── ChatMessageBubble (User / AI)
│   │   │   │   │   └── TypingIndicator
│   │   │   │   ├── NextQuestionCallout
│   │   │   │   └── MessageComposer
│   │   │   ├── CaseSummarySection (02)
│   │   │   │   └── CaseSummaryForm
│   │   │   └── SimilarJudgmentsPreview (03, pre-retrieval placeholder)
│   │   └── WorkflowSidebar
│   │       ├── WorkflowStepper
│   │       └── AdvisoryNoticeCard
│   └── ResultsView (single-column full-width view for Similar Judgments / Outcome Prediction)
│       ├── SimilarJudgmentsSection (03)
│       │   └── JudgmentCard (x N)
│       ├── OutcomePredictionSection (04)
│       │   ├── ProbabilityDistributionBar
│       │   └── ApplicabilityNotice
│       └── Footer
└── Shared Primitives
    ├── SectionCard
    ├── StatusBadge
    └── EmptyStateBox
```

---

## 2. Detailed Component Specifications

### 2.1 Layout & Navigation Components

| Component | Location (Planned) | Responsibilities & Props |
| :--- | :--- | :--- |
| **`Header`** | `src/components/Header.jsx` | Renders the sticky `86px` top navigation bar. Houses brand identity (`§` icon + `AI Legal Guidance` / `Indian legal context`), navigation tabs (`Guidance`, `Similar Judgments`, `Outcome Prediction`), the `New case` reset button, and the `Connected` status dot indicator. Accepts `activeTab`, `onSelectTab`, `onNewCase`, and `isConnected`. |
| **`HeroBanner`** | `src/components/HeroBanner.jsx` | Renders the top editorial header in the Guidance view: `ACADEMIC LEGAL TECHNOLOGY PROTOTYPE` eyebrow, two-tone display title (`Understand your case.` + italic serif *`Explore what comes next.`*), intro description, and the right-aligned educational disclaimer card. |
| **`WorkflowSidebar`** | `src/components/WorkflowSidebar.jsx` | Renders the right-hand `~334px` column containing `WorkflowStepper` (`YOUR WORKFLOW` steps `01`–`04` with live status badges/subtitles) and the `Stay informed` advisory card. |
| **`Footer`** | `src/components/Footer.jsx` | Renders the bottom horizontal metadata bar (`AI Legal Guidance · Academic project` on left; `Indian legal context · Grounded Supreme Court precedents` on right). |

---

### 2.2 Section `01` — Conversational Case Intake Components

| Component | Location (Planned) | Responsibilities & Props |
| :--- | :--- | :--- |
| **`CaseIntakeSection`** | `src/components/CaseIntakeSection.jsx` | Container card for `01 / UNDERSTAND YOUR SITUATION` (`Start with your legal concern`) with `Guidance` status badge, helper copy, `ChatTranscript`, optional `NextQuestionCallout`, and `MessageComposer`. |
| **`ChatTranscript`** | `src/components/ChatTranscript.jsx` | Scrollable transcript area (`#F6F8F4` surface). Displays the `What happened?` empty state before any messages exist, or renders chronological `ChatMessageBubble` items and `TypingIndicator` when loading. |
| **`ChatMessageBubble`** | `src/components/ChatMessageBubble.jsx` | Renders either a right-aligned user message (lime-green `#E9F8B8` bubble + `YOU` label + `You` square badge) or a left-aligned assistant message (dark forest `#194030` `AI` square badge + white bordered card + `ASSISTANT` label). |
| **`NextQuestionCallout`** | `src/components/NextQuestionCallout.jsx` | Highlighted `#F3F8E4` callout box with `4px solid #9FC259` left border displaying `NEXT QUESTION` and the current AI follow-up question between the transcript and composer. |
| **`MessageComposer`** | `src/components/MessageComposer.jsx` | Resizable `<textarea>` with context-sensitive placeholder text (initial example vs follow-up prompt) and `Send message ↗` / `Sending... ↗` submit button. Disables submission when empty or busy. |

---

### 2.3 Section `02` — Case Summary Components

| Component | Location (Planned) | Responsibilities & Props |
| :--- | :--- | :--- |
| **`CaseSummarySection`** | `src/components/CaseSummarySection.jsx` | Container card for `02 / REVIEW THE FACTS` (`Case summary`) with dynamic `Review required` / `Confirmed` status badge. Shows `EmptyStateBox` (`Your summary will appear here`) until intake produces summary fields, then renders `CaseSummaryForm`. |
| **`CaseSummaryForm`** | `src/components/CaseSummaryForm.jsx` | Controlled 5-field form in a 2-column + full-width layout: `PROBLEM TYPE` (input), `JURISDICTION` (input), `KEY FACTS` (scrollable textarea), `CLAIMED HARM` (input), `REQUESTED OUTCOME` (input). Includes `Save revision` (`Saving...`) and `Confirm summary ✓` action buttons. |

---

### 2.4 Section `03` — Similar Judgments Components

| Component | Location (Planned) | Responsibilities & Props |
| :--- | :--- | :--- |
| **`SimilarJudgmentsSection`** | `src/components/SimilarJudgmentsSection.jsx` | Container for `03 / EXPLORE REFERENCES` (`Similar judgments`). Renders the `Persistent Vector Index` preview state prior to retrieval, or the populated list with retrieval count (`Retrieved N relevant precedent passages`), `Generation: Verified` pill, stacked `JudgmentCard` items, and verification footer note. |
| **`JudgmentCard`** | `src/components/JudgmentCard.jsx` | Displays a single retrieved Supreme Court judgment: court eyebrow (`SUPREME COURT OF INDIA`), similarity percentage badge (`43.5% match` in `#E9F8B8`), judgment date, bold case title, case number, `VERBATIM PASSAGE EXCERPT` box with `3px solid #74B451` left border and `Offsets: [start : end]`, and bottom `Context:` line. |

---

### 2.5 Section `04` — Outcome Prediction Components

| Component | Location (Planned) | Responsibilities & Props |
| :--- | :--- | :--- |
| **`OutcomePredictionSection`** | `src/components/OutcomePredictionSection.jsx` | Container for `04 / EXPERIMENTAL RESEARCH` (`Appeal outcome prediction`). Displays model badge (to be labeled for Experiment 3 **Random Forest**), predicted outcome pill (e.g., `Appeal Allowed`), `Model Confidence` percentage, `ProbabilityDistributionBar`, model architecture/class metadata, and `ApplicabilityNotice`. |
| **`ProbabilityDistributionBar`** | `src/components/ProbabilityDistributionBar.jsx` | Two-segment rounded horizontal bar visualizing class probabilities (`Allowed` in `#74B451` green vs `Dismissed` in `#C25656` crimson) with aligned percentage labels underneath. |
| **`ApplicabilityNotice`** | `src/components/ApplicabilityNotice.jsx` | Warm cream-tinted notice card (`#FBFCF4`) listing the three academic and legal applicability caveats for statistical predictions. |

---

### 2.6 Shared UI Primitives & Page Containers

| Component / Page | Location (Planned) | Responsibilities |
| :--- | :--- | :--- |
| **`StatusBadge`** | `src/components/StatusBadge.jsx` | Reusable pill badge supporting variants observed in the UI: `lime` (`Guidance`, `% match`), `amber` (`Review required`), `green` (`Appeal Allowed`), `sage` (`Generation: Verified`), and `neutral` (`Persistent Vector Index`). |
| **`SectionCard`** | `src/components/SectionCard.jsx` | Standardized white rounded card wrapper with section eyebrow (`01 / ...`), title, optional top-right badge, and subtitle. |
| **`EmptyStateBox`** | `src/components/EmptyStateBox.jsx` | Centered placeholder panel for empty chat and empty summary states with icon, title, and helper copy. |
| **`LegalGuidancePage`** | `src/pages/LegalGuidancePage.jsx` | Top-level page orchestrator coordinating session state, view/tab switching (`Guidance`, `Similar Judgments`, `Outcome Prediction`), scroll targeting, and API service calls (to be wired in later phases). |
