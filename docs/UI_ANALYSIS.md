# UI Analysis & Visual Design System

**Source Reference:** `reference/ui_reference.mp4` (`1906×902`, `30.00 fps`, `3,179` frames, `105.97 s` total duration)  
**Scope:** Analysis only — no application code or components are modified in this phase.

---

## 1. Executive Summary & Overall Application Layout

The reference application is a light-mode, editorial-style legal guidance web interface built around a numbered, four-stage workflow (`01` through `04`) on a warm sage-tinted off-white canvas (`#F3F5F0`).

### Page Structure & Layout Modes Observed

1. **Sticky Top Header Bar (`86px` height, full viewport width):**
   - Pinned at the top across all views and scroll positions, separated from content by a `1px solid #E2E4DF` bottom border.
   - Left: Brand mark (`§` icon inside rounded dark green square) + title (`AI Legal Guidance`) + subtitle (`Indian legal context`).
   - Center-right: Primary navigation tabs (`Guidance`, `Similar Judgments`, `Outcome Prediction`).
   - Far right: Utility action (`↻ New case`) + live connection indicator (`● Connected`).

2. **Guidance View (`Guidance` nav tab active, `00:00–01:26` & `01:42–01:45`):**
   - Centered content container spanning approximately `1384px` (`x=248` to `x=1632` at `1906px` viewport width).
   - **Hero / Intro Banner (above the two-column grid):**
     - Left block: Eyebrow label (`ACADEMIC LEGAL TECHNOLOGY PROTOTYPE`), two-line headline (`Understand your case.` / *`Explore what comes next.`*), and a three-line descriptive paragraph.
     - Right block (aligned beside the hero text): Rounded muted-sage disclaimer card (`For educational purposes only. Not a substitute for professional legal advice.`) with an info circle icon (`ⓘ`).
   - **Two-Column Content Grid (`28px` column gap):**
     - **Left Main Column (`~1022px` wide):** Vertically stacked numbered step cards:
       - `01 / UNDERSTAND YOUR SITUATION` — **Start with your legal concern** (Conversational intake chat + follow-up question callout + composer).
       - `02 / REVIEW THE FACTS` — **Case summary** (Structured editable form with 5 fields + `Save revision` / `Confirm summary ✓` actions).
       - `03 / EXPLORE REFERENCES` — **Similar judgments** (Preview/empty placeholder card visible below `02` before confirmation at `00:30`).
     - **Right Sidebar (`~334px` wide):**
       - **Workflow Tracker Card (`YOUR WORKFLOW`):** Vertical list of steps `01`–`04` with numbered status pills, step titles, and dynamic status subtitles.
       - **Advisory Card (`Stay informed`):** Light sage-tinted card with scales-of-justice icon and two-sentence legal disclaimer.

3. **Precedents & Prediction Focused View (`Similar Judgments` / `Outcome Prediction` nav tabs active, `01:27–01:42`):**
   - Clicking `Similar Judgments` transitions out of the two-column Guidance + Sidebar view into a single-column centered results view (`~1384px` content width without the right workflow sidebar).
   - Displays **Section `03 / EXPLORE REFERENCES` — Similar judgments** (list of retrieved Supreme Court judgment cards + verification footer note) followed vertically by **Section `04 / EXPERIMENTAL RESEARCH` — Appeal outcome prediction** (prediction summary card + applicability notice) and the **Global Page Footer**.
   - Clicking `Outcome Prediction` scrolls/focuses directly to Section `04` within this results view; clicking `Similar Judgments` scrolls back to Section `03`; clicking `Guidance` returns to the two-column Guidance + Sidebar view.

> **Important Project Adaptation Note:** In the reference recording (`01:36–01:45`), Section `04` and Sidebar Step `04` reference `InLegalBERT` (`BertForSequenceClassification`). Per project specifications, our implementation will **not** introduce InLegalBERT and will adapt those model label/metadata slots to reflect the **Experiment 3 Random Forest** model when implemented in later phases.

---

## 2. Screen-by-Screen / Section-by-Section Analysis

### 2.1 Top Navigation Header & Brand Identity
- **Height & Surface:** `86px` tall, solid `#F3F5F0` / subtle translucent match with `#E2E4DF` bottom border.
- **Left Brand Block:**
  - Icon container: Rounded square (`~38×38px`, `border-radius: ~10px`), dark forest green fill (`#224939` / `#194030`), containing a crisp white section-sign symbol (`§`).
  - Title: `AI Legal Guidance` (semibold dark text, ~`15–16px`).
  - Subtitle: `Indian legal context` (muted olive-grey text, ~`12px`).
- **Center-Right Navigation Tabs:**
  - Three horizontal items: `Guidance`, `Similar Judgments`, `Outcome Prediction`.
  - **Active tab state:** Soft sage-tinted pill (`#E7EFE5`), subtle rounded corners (`~10px`), dark forest text, medium weight.
  - **Inactive tab state:** Transparent background, muted charcoal/grey text (`#555C56`).
- **Far-Right Controls:**
  - `↻ New case` button: Rounded pill/button (`#EBF1E8` fill, `~10px` radius), refresh-counterclockwise icon + `New case` label.
  - Connection status indicator: Small circular green dot (`#82B24E`, `~8px`) + `Connected` text in muted grey-green (`~13px`).

### 2.2 Hero Banner & Educational Notice (Guidance View Top)
- **Eyebrow:** `ACADEMIC LEGAL TECHNOLOGY PROTOTYPE` — uppercase, wide letter-spacing (`~0.08em`), small muted olive-grey (`~11px`).
- **Display Headline:**
  - Line 1: `Understand your case.` — Bold geometric sans-serif (`~52–56px`), deep forest green (`#143D2D`).
  - Line 2: *`Explore what comes next.`* — Italic high-contrast serif (`~52–56px`), fresh leaf-green (`#77AC48`).
- **Subtitle Paragraph:**
  - `A structured starting point for understanding legal concerns in the Indian context — with transparent limitations, persistent precedent retrieval, and experimental outcome modeling.` (`~16px`, muted grey-green `#5C655E`, max width `~620px`).
- **Right Hero Callout (`For educational purposes only.`):**
  - Soft sage-grey rounded rectangle (`#E9EFE6`, `1px solid #DCE3D9`, `~14px` radius, padding `~18px 22px`), positioned on the right side of the hero row.
  - Left-aligned info icon (`ⓘ`) beside two-line muted body text (`~13px`): `For educational purposes only. Not a substitute for professional legal advice.`

### 2.3 Right Sidebar (`YOUR WORKFLOW` & `Stay informed`)
- **Width:** `~334px`, sticky or aligned alongside Sections `01`–`02` (`00:00–00:34`, `01:00`, `01:43–01:45`).
- **Card 1 — Workflow Stepper (`YOUR WORKFLOW`):**
  - White rounded card (`#FFFFFF`, `1px solid #E2E4DF`, `16px` radius, `~24px` padding).
  - Header: `YOUR WORKFLOW` (uppercase tracked label, `~11px`, muted grey).
  - Four vertical rows separated by thin `1px` horizontal dividers:
    1. `01` — **Share your concern** / Subtitle: `Conversational guidance`
    2. `02` — **Review your summary** / Subtitle: `Review key facts` (updates to `Confirmed ✓` after confirmation)
    3. `03` — **Explore references** / Subtitle: `Persistent index` (updates to `5 retrieved` after retrieval)
    4. `04` — **Experimental prediction** / Subtitle: `FIRAC-compatible inputs` (updates after prediction; shows model/outcome label in recording, to be adapted to Random Forest)
  - **Step Badge (`01`–`04`):** Rounded square (`~28×28px`, `~8px` radius). Active/completed steps use soft lime-green (`#E9F8B8`) with dark green text; pending steps use neutral light grey border/background (`#F4F6F1`).
- **Card 2 — Advisory Notice (`Stay informed`):**
  - Soft sage-tinted card (`#E9EFE6` / `#EFF3EC`, `1px solid #DCE3D9`, `16px` radius, `~20px` padding).
  - Scales-of-justice icon (green) + bold title `Stay informed` (`~14px`).
  - Muted body text (`~12.5px`): `AI-generated guidance can be incomplete. Always consult a qualified legal professional for advice.`

### 2.4 Section `01 / UNDERSTAND YOUR SITUATION` — Conversational Case Intake
- **Outer Card:** White (`#FFFFFF`), `1px solid #E2E4DF`, `~20px` radius, `~32px` padding.
- **Card Header Row:**
  - Left: Eyebrow `01 / UNDERSTAND YOUR SITUATION` (uppercase, tracked monospace/sans) + Title `Start with your legal concern` (`~22px` bold `#143D2D`).
  - Right: Status pill `Guidance` (lime-green `#E9F8B8` fill, `#194030` text, `~8px` radius).
- **Intro Copy:** `Share the facts in your own words. The assistant will ask one follow-up question at a time to build a reviewable case summary.`
- **Chat Transcript Container:**
  - Rounded inner panel (`border-radius: ~14px`, light tinted `#F6F8F4` / `#F3F5F0` background, `1px solid #E5E8E2`).
  - **Empty / Initial State (`00:00–00:29`):** Centered four-point sparkle icon (`✦` in leaf green), bold prompt `What happened?`, and helper text `Describe the legal issue you would like to understand.`
  - **Populated Scrollable State (`00:34–01:05`, `01:43–01:45`):** Internal vertical scrollbar on the right (`~420–460px` max height) displaying alternating messages:
    - **User Message Bubble:** Right-aligned, soft lime-green fill (`#E9F8B8`), `~14px` rounded corners, `YOU` uppercase micro-label above message text, paired with a small square `You` avatar badge (`#DCE7D5` / `#E9EFE6`) on the far right.
    - **AI Assistant Message Bubble:** Left-aligned, paired with a dark forest-green square `AI` avatar badge (`#194030`, white `AI` text, `~32×32px`, `~8px` radius) on the far left; white card surface (`#FFFFFF`, `1px solid #E2E4DF`, `~14px` radius) with `ASSISTANT` uppercase micro-label and multi-line response text.
    - **Typing / Loading Indicator (`00:59–01:02`):** Dark green `AI` avatar badge next to a compact white pill containing three animated/muted dots (`•••`).
- **Follow-Up Question Callout (`NEXT QUESTION`, `00:35–00:56`):**
  - Appears directly between the chat transcript box and the message composer whenever the AI provides a follow-up question.
  - Background: Soft lime-cream (`#F3F8E4`), `4px solid #9FC259` left accent border, rounded corners (`~10px`), padding `~14px 18px`.
  - Header: `NEXT QUESTION` (uppercase, small olive-green `#6F8F3D`), followed by the single question text in dark charcoal (`#2C2C2C`, `~14px`).
- **Message Composer & Submit Row:**
  - Full-width resizable `<textarea>` (`~88–100px` height, `#FFFFFF` fill, `1px solid #D9DDD6`, `~12px` radius).
  - Placeholder (initial): `For example: My employer has not paid my salary for three months...`
  - Placeholder (after first message): `Answer the question or add another important fact...`
  - Bottom-right primary action button: `Send message ↗` (solid `#194030` when enabled with text; muted sage `#92A096` when empty/disabled; displays `Sending... ↗` while awaiting API response).

### 2.5 Section `02 / REVIEW THE FACTS` — Case Summary Form
- **Outer Card:** White (`#FFFFFF`), `1px solid #E2E4DF`, `~20px` radius, `~32px` padding.
- **Header Row:**
  - Left: Eyebrow `02 / REVIEW THE FACTS` + Title `Case summary` (`~22px` bold `#143D2D`).
  - Right (once populated): Status pill `Review required` (warm cream/amber tint `#FBF0D9` with dark brown-amber text, `~8px` radius).
- **Empty State (`00:24–01:02`):**
  - Centered square outline icon, bold heading `Your summary will appear here`, and helper line `Send a message to begin collecting the key details.`
- **Populated Form State (`01:04–01:26`):**
  - Helper text: `This is a preliminary placeholder summary. Review the fields and correct anything before confirming.`
  - **2-Column Grid + Full-Width Middle Field:**
    1. `PROBLEM TYPE` (top-left text input, e.g., `Unpaid salary recovery`)
    2. `JURISDICTION` (top-right text input, e.g., `Bengaluru, India`)
    3. `KEY FACTS` (full-width scrollable `<textarea>`, multi-line bullet/line summary)
    4. `CLAIMED HARM` (bottom-left text input, e.g., `Unpaid salary for three months totalling 120000`)
    5. `REQUESTED OUTCOME` (bottom-right text input, e.g., `Recovery of unpaid salary`)
  - **Action Footer (bottom-right aligned):**
    - Secondary button: `Save revision` (light neutral `#EBF1E8` fill, dark green/charcoal text; switches to `Saving...` during confirmation/save).
    - Primary button: `Confirm summary ✓` (deep forest green `#194030` fill, white bold text; muted `#8A9B91` when processing).

### 2.6 Section `03 / EXPLORE REFERENCES` — Similar Judgments
- **Initial Preview State (in Guidance view at `00:30–00:33`):**
  - Card header: `03 / EXPLORE REFERENCES`, title `Similar judgments`, right pill `Persistent Vector Index` (light neutral/sage border pill).
  - Subtitle: `Authentic Supreme Court of India precedents retrieved by semantic similarity to your confirmed case summary.`
- **Populated Results View (`01:27–01:36`, `01:41–01:42`):**
  - **Section Header & Metadata Bar:**
    - Title `Similar judgments`, subtitle, and metadata row: left text `Retrieved 5 relevant precedent passages` + right status pill `Generation: Verified` (soft green `#E8F0E4` fill with subtle border).
  - **Stacked Precedent Result Cards (5 cards separated by `~20px` vertical gap):**
    - White card (`#FFFFFF`, `1px solid #E2E4DF`, `~16px` radius, `~28px` padding).
    - **Card Top Metadata Row:**
      - Left: Uppercase court label `SUPREME COURT OF INDIA` (`~11px` muted grey).
      - Right: Similarity badge (e.g., `43.5% match`, `40.4% match`, `38.1% match`, `38.0% match`, `37.8% match`) in `#E9F8B8` pill with `#194030` bold text + ISO date beside it (e.g., `2019-03-05`) in muted monospace/grey.
    - **Case Citation & Number:**
      - Bold uppercase case title (`~16–17px`, `#143D2D`, e.g., `M.R. KRISHNA MURTHI v. THE NEW INDIA ASSURANCE CO. LTD. & OTHERS`).
      - Subtitle (`~13px` monospace/grey): e.g., `Case: Civil Appeal Nos. 2476-2477 of 2019`.
    - **Excerpt Container:**
      - Light background (`#FAFBF9`), `1px solid #E5E8E2` border, **`3px solid #74B451` left accent border**, rounded right/overall corners (`~10px`), padding `~16px 20px`.
      - Header row inside box: `VERBATIM PASSAGE EXCERPT` (left, uppercase `~11px`) and `Offsets: [29192 : 33645]` (right, monospace `~12px`).
      - Body: Verbatim quoted judgment text (`~13.5px`, dark `#2C2C2C`, `line-height: ~1.65`).
    - **Card Footer Line:** `Context: Precedent on Motor accident compensation.` (`Context:` bold, category text muted).
  - **Section Footer Note:**
    - Centered muted line below the 5th card (`01:36`): `Note: Retrieved from persistent index of authentic Supreme Court judgments. Passages are verified verbatim excerpts.`

### 2.7 Section `04 / EXPERIMENTAL RESEARCH` — Outcome Prediction
- **Observed Header & Framing (`01:36–01:41`):**
  - Eyebrow: `04 / EXPERIMENTAL RESEARCH` (left) + right-aligned model badge pill (observed in recording as `InLegalBERT Model (Fine-tuned)`; **to be replaced with Random Forest Experiment 3 label** per project constraints).
  - Title: `Appeal outcome prediction` (`~22px` bold `#143D2D`).
  - Subtitle (observed in recording): Two-line explanation of outcome probability estimation on Supreme Court of India appellate judgments structured in FIRAC format (to be worded for Experiment 3 Random Forest).
- **Prediction Result Inner Card:**
  - Rounded white card (`1px solid #E2E4DF`, `~14px` radius, `~24px` padding).
  - Row 1: `PREDICTED OUTCOME` (uppercase label, left) + large status pill `Appeal Allowed` (`#E5F6DC` fill, `#194030` bold text, `~10px` radius, right).
  - Row 2: `Model Confidence` (left) + bold monospace percentage `91.0%` (right).
  - Row 3 (`PROBABILITY DISTRIBUTION`):
    - Horizontal stacked progress bar (`~12px` height, fully rounded `999px` pill ends): left segment leaf-green (`#74B451`) proportional to `Allowed`, right segment muted crimson (`#C25656`) proportional to `Dismissed`.
    - Labels directly below bar: `Allowed: 91.0%` (left, green) and `Dismissed: 9.0%` (right, dark red/charcoal).
  - Row 4 (Model Metadata Footer): Two inline metadata pairs separated horizontally (`Architecture: ...` and `Classes: 2 (Binary Appellate Classification)`).
- **Applicability Notice Box:**
  - Warm cream-tinted inner card (`#FBFCF4`, `1px solid #EAE7DC`, `~12px` radius, `~18px 22px` padding).
  - Uppercase header: `ACADEMIC & LEGAL APPLICABILITY NOTICE` (`#7A5D2E` / muted brown).
  - Three bullet points explaining academic/statistical nature, historical appellate distribution basis, and non-legal-advice disclaimer.

### 2.8 Global Page Footer (`01:37–01:41`)
- Separated by a subtle full-width `1px solid #E2E4DF` top divider.
- Horizontal flex bar at bottom of results view:
  - Left: `AI Legal Guidance  ·  Academic project`
  - Right: `Indian legal context  ·  Grounded Supreme Court precedents`
- Styled in small muted monospace/sans text (`~12px`, `#6E7770`).

---

## 3. Extracted Visual Design System

All colors and layout metrics below were sampled directly from full-resolution (`1906×902`) frames of `reference/ui_reference.mp4`.

### 3.1 Color Palette

| Token / Role | Observed Hex | Usage |
| :--- | :--- | :--- |
| `--bg-canvas` | `#F3F5F0` | Main viewport background & sticky header background |
| `--bg-surface` | `#FFFFFF` / `#FCFCFC` | Primary section cards, sidebar stepper card, assistant bubbles, inputs |
| `--bg-surface-muted` | `#F6F8F4` / `#FAFBF9` | Chat transcript inner container, verbatim excerpt box |
| `--bg-sage-soft` | `#E9EFE6` / `#EBF1E8` | Hero notice box, `Stay informed` card, `New case` & `Save revision` buttons |
| `--bg-nav-active` | `#E7EFE5` | Active top navigation tab pill |
| `--bg-lime-accent` | `#E9F8B8` | User chat bubble, `Guidance` badge, `% match` badges, active step number pills |
| `--bg-next-question` | `#F3F8E4` | `NEXT QUESTION` callout background |
| `--bg-allowed-pill` | `#E5F6DC` | `Appeal Allowed` prediction badge background |
| `--bg-verified-pill` | `#E8F0E4` | `Generation: Verified` status badge |
| `--bg-review-pill` | `#FBF0D9` *(approx. warm cream)* | `Review required` status pill |
| `--bg-notice-warm` | `#FBFCF4` | `ACADEMIC & LEGAL APPLICABILITY NOTICE` box |
| `--color-brand-dark` | `#143D2D` / `#194030` / `#224939` | Logo tile, `AI` avatar badge, primary CTA buttons (`Send message`, `Confirm summary`), primary headings |
| `--color-accent-green` | `#77AC48` | Hero serif headline accent (*`Explore what comes next.`*) |
| `--color-status-green` | `#74B451` / `#82B24E` | `Allowed` probability bar, excerpt left accent border, `Connected` status dot |
| `--color-next-border` | `#9FC259` | `NEXT QUESTION` left accent border (`4px`) |
| `--color-status-red` | `#C25656` *(muted crimson)* | `Dismissed` probability bar segment |
| `--color-btn-disabled` | `#8A9B91` / `#92A096` | Disabled/loading state for primary dark green buttons |
| `--text-primary` | `#2C2C2C` | Body copy, input text, chat messages, judgment excerpts |
| `--text-muted` | `#5C655E` / `#6E7770` | Subtitles, placeholders, eyebrow labels, footer text |
| `--border-subtle` | `#E2E4DF` / `#DCE3D9` | Card borders, header/footer hairlines, form input borders, dividers |

### 3.2 Typography & Hierarchy

> **Note:** Exact font-family CSS declarations cannot be read from video pixels alone; classifications below describe the observed typefaces.

| Element | Classification | Estimated Size & Weight | Style Notes |
| :--- | :--- | :--- | :--- |
| Hero Headline (Line 1) | Geometric / Humanist Sans-serif | `~52–56px`, Bold (`700`) | Tight line-height (`~1.08`), `#143D2D` |
| Hero Headline (Line 2) | High-contrast Editorial Serif | `~52–56px`, Italic (`400–600`) | `#77AC48`, tight tracking |
| Section Titles (`Start with...`, `Case summary`, etc.) | Sans-serif | `~22–24px`, Semibold/Bold (`600–700`) | `#143D2D` |
| Judgment Case Title | Sans-serif | `~16–17px`, Bold (`700`), Uppercase | `#143D2D` |
| Eyebrows (`01 / ...`, `YOUR WORKFLOW`, `PROBLEM TYPE`) | Monospace / Tracked Sans | `~11px`, Medium (`500–600`), Uppercase | Letter-spacing `~0.06–0.08em`, muted grey |
| Body / Chat / Excerpts | Sans-serif | `~14px`, Regular (`400`) | Line-height `~1.55–1.65`, `#2C2C2C` |
| Metadata / Offsets / Percentages / Footer | Monospace / Tabular | `~12–13px`, Regular–Bold | Used for `91.0%`, `Offsets: [...]`, dates, footer |

### 3.3 Spacing, Radii, Shadows & Control Dimensions
- **Container Max Width:** `~1384px` centered on `1906px` viewport (`~248px` horizontal side margins at `1906px`).
- **Grid Split (Guidance View):** Left column `~1022px` (`minmax(0, 1fr)`), right sidebar `~334px`, column gap `28px`, vertical card gap `~24px`.
- **Header Height:** `86px`.
- **Border Radius:**
  - Large section cards: `~16–20px`
  - Inner callouts / chat box / form inputs / excerpt cards: `~10–14px`
  - Buttons & nav pills: `~8–10px`
  - Status badges (`Guidance`, `43.5% match`, `Review required`): `~6–8px`
  - Progress bar: `999px` (pill ends)
- **Shadows:** Very soft, minimal elevation on main white cards (`0 1px 3px rgba(20, 61, 45, 0.04)` or flat `1px solid #E2E4DF` border-first design — no heavy drop shadows).
- **Buttons:**
  - `Send message ↗`: Height `~42px`, horizontal padding `~18–20px`, `border-radius: ~10px`.
  - `Save revision` / `Confirm summary ✓`: Height `~42px`, horizontal padding `~18–22px`, `border-radius: ~10px`.
  - `New case`: Height `~38px`, horizontal padding `~14px`.
- **Inputs & Textareas:**
  - Single-line inputs (`PROBLEM TYPE`, `JURISDICTION`, `CLAIMED HARM`, `REQUESTED OUTCOME`): Height `~44px`, `1px solid #D9DDD6`, `border-radius: ~10px`, horizontal padding `~14px`, white `#FFFFFF` background.
  - Multi-line textareas (`KEY FACTS`, chat composer): Min-height `~90–110px`, vertical resize handle visible in bottom-right corner (`resize: vertical`).

### 3.4 Icons & Visual Indicators
- **Brand Mark:** White section sign `§` on `#224939` rounded square.
- **Info Icon:** Outline circle `ⓘ` in hero disclaimer.
- **Scales Icon:** Balance scale icon in `Stay informed` card.
- **Empty-State Icons:** Four-point sparkle `✦` (chat intake), rounded square outline (case summary).
- **Button Icons:** Diagonal arrow `↗` (`Send message`), checkmark `✓` (`Confirm summary`), counterclockwise arrow `↻` (`New case`).
- **Connection Indicator:** Solid `~8px` `#82B24E` circle beside `Connected`.
- **Avatars:** Rounded square `AI` (`#194030` fill, white text) and `You` (`#DCE7D5` fill, dark text).
