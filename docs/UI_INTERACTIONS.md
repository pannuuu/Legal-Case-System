# UI Interactions, Navigation & Component States

**Source Reference:** `reference/ui_reference.mp4` (`00:00–01:45`)  
**Scope:** Behavioral specification distinguishing interactions directly observed in the recording from functionality inferred from visible controls.

---

## 1. Chronological Interaction Sequence Demonstrated in the Video

| Timestamp | User Action / Event | Observed UI Response |
| :--- | :--- | :--- |
| **`00:00–00:12`** | Initial page load & vertical scroll check | Lands on `Guidance` view (`Guidance` tab active, `● Connected` indicator green). User scrolls up to show the Hero Banner and educational disclaimer, then scrolls back down to Section `01`. |
| **`00:13–00:28`** | Initial legal problem entry (`01`) | User copies/pastes a multi-sentence unpaid-salary scenario into the composer `<textarea>`. The placeholder disappears and `Send message ↗` switches from muted sage to active dark forest green (`#194030`). |
| **`00:29–00:34`** | Click `Send message ↗` | Button switches to `Sending... ↗` (muted/disabled). User scrolls briefly to show empty `02 Case summary` and `03 Similar judgments` (`Persistent Vector Index`) below. |
| **`00:35–00:37`** | AI first response received | User message bubble (`YOU`) and AI follow-up response (`ASSISTANT`) populate inside the `ChatTranscript`. A highlighted `NEXT QUESTION` callout (`#F3F8E4` with green left border) renders below the transcript asking whether the user is classified as a "workman" under the Industrial Disputes Act, 1947. Composer placeholder updates to `Answer the question or add another important fact...`. |
| **`00:40–00:55`** | Follow-up answer entry | User types `"Yes, I am classified as a workman."` into the composer `<textarea>` and corrects a typo (`workmsn` → `workman`). |
| **`00:56–01:03`** | Click `Send message ↗` | Button enters `Sending... ↗`. Transcript scrolls to bottom showing the user's `YOU` bubble and a dark-green `AI` badge with a three-dot typing indicator (`•••`). |
| **`01:04–01:05`** | Second AI response & summary generation | Typing indicator is replaced by the `ASSISTANT` legal guidance message (noting Indian labor law avenues and non-advice caveat). Section `02 Case summary` simultaneously transitions from empty state to the populated 5-field form with a `Review required` pill. |
| **`01:06–01:13`** | Inspecting Case Summary (`02`) | User scrolls down to Section `02`, scrolls inside the `KEY FACTS` textarea to inspect all generated lines, and hovers over `CLAIMED HARM` without modifying field values. |
| **`01:14–01:25`** | Click `Confirm summary ✓` | `Save revision` changes to `Saving...` (muted) and `Confirm summary ✓` enters a disabled/muted state while `Send message ↗` briefly shows `Sending... ↗` as the backend runs post-confirmation retrieval, prediction, and synthesis. At `01:24`, buttons return to normal enabled appearance. |
| **`01:26–01:29`** | Click `Similar Judgments` in header | Active nav pill switches to `Similar Judgments`. View switches from the two-column Guidance + Sidebar layout to the full-width Results view starting at Section `03` (`Retrieved 5 relevant precedent passages`, `Generation: Verified`). |
| **`01:30–01:36`** | Scroll through Similar Judgments | User scrolls past all 5 Supreme Court judgment cards (`M.R. KRISHNA MURTHI`, `KOTAK MAHINDRA BANK`, `Shreevjita Pattnaik`, `All India Bank Officers' Confederation`, `RAJWATI @ RAJJO`) and the bottom verification note (`01:36`). |
| **`01:36–01:39`** | Scroll into Section `04` (`Appeal outcome prediction`) | Directly below Section `03`, Section `04` displays `Appeal Allowed` (`91.0%`), the green/red probability distribution bar (`Allowed: 91.0%` / `Dismissed: 9.0%`), model architecture metadata, and the `ACADEMIC & LEGAL APPLICABILITY NOTICE`, followed by the global footer. |
| **`01:40`** | Click `Outcome Prediction` in header | Active nav pill switches to `Outcome Prediction` and anchors to Section `04`. |
| **`01:41`** | Click `Similar Judgments` in header | Active nav pill switches back to `Similar Judgments` and scrolls back up to Section `03`. |
| **`01:42–01:45`** | Click `Guidance` in header | Active nav pill switches to `Guidance`, restoring the two-column layout with the `YOUR WORKFLOW` sidebar. Sidebar now reflects updated progress (`02 Confirmed ✓`, `03 5 retrieved`, `04` model/outcome status), and Section `01` shows a newly appended `ASSISTANT` synthesis message summarizing the claim and retrieved corpus relevance. |

---

## 2. Observed vs. Inferred Functionality

### 2.1 Directly Demonstrated in Recording
- Initial problem submission via textarea + `Send message ↗`.
- Single-question follow-up loop with `NEXT QUESTION` callout and updated composer placeholder.
- Automatic population of Section `02 Case summary` once sufficient intake facts are gathered.
- Summary confirmation via `Confirm summary ✓`, triggering retrieval (`03`), outcome prediction (`04`), final assistant synthesis in `01`, and `YOUR WORKFLOW` sidebar status updates.
- Top-bar view/section switching between `Guidance`, `Similar Judgments`, and `Outcome Prediction`.
- Internal scrolling within `ChatTranscript` and `KEY FACTS` textarea, plus full-page vertical scrolling through retrieved judgments and outcome prediction.

### 2.2 Inferred from Visible Interface Controls (Not Clicked in Recording)
- **`Save revision` button (`02`):** Inferred to persist edits made to `PROBLEM TYPE`, `JURISDICTION`, `KEY FACTS`, `CLAIMED HARM`, or `REQUESTED OUTCOME` without triggering final confirmation/retrieval, or to be enabled/dirty-checked when fields are edited.
- **`↻ New case` button (Header):** Inferred to reset the active session, clear chat history, clear case summary/retrieval/prediction state, and return the user to the initial `Guidance` empty state (`What happened?`).
- **Editing Case Summary fields:** All 5 summary fields are standard editable `<input>` / `<textarea>` controls; typing edits was not demonstrated, only scrolling inside `KEY FACTS`.
- **Disconnected / Error State (`● Connected`):** Inferred counterpart state when backend health check fails (e.g., `Disconnected` or offline badge).
- **Direct click on `Outcome Prediction` before summary confirmation:** Not demonstrated; presumably either shows an empty/pending state or keeps the tab disabled/scroll-locked until a summary is confirmed.

---

## 3. Component State Matrix

| Component / Element | Initial / Empty State | Loading / Busy State | Populated / Active State | Completed / Verified State |
| :--- | :--- | :--- | :--- | :--- |
| **`Guidance` / `Similar Judgments` / `Outcome Prediction` Nav Tabs** | `Guidance` highlighted (`#E7EFE5`); others transparent | Remains clickable | Highlighted pill follows user selection | — |
| **`ChatTranscript` (`01`)** | Centered `✦ What happened?` prompt | Appends `AI` avatar + `•••` typing pill | Scrollable `YOU` (`#E9F8B8`) + `ASSISTANT` (`#FFFFFF`) bubbles | Includes post-confirmation synthesis message |
| **`NextQuestionCallout` (`01`)** | Hidden | Hidden or replaced on submit | Visible (`#F3F8E4`, green left bar) when `next_question` exists | Hidden once intake concludes / summary confirmed |
| **`MessageComposer` (`01`)** | Initial example placeholder; `Send message ↗` muted when empty | `Sending... ↗` muted/disabled | Enabled dark `#194030` button when non-empty; follow-up placeholder | Remains available for additional facts |
| **`CaseSummarySection` (`02`)** | Centered `Your summary will appear here` box | `Save revision` shows `Saving...`; `Confirm summary ✓` muted | 5-field editable form + `Review required` amber badge | Sidebar Step `02` updates to `Confirmed ✓` *(Note: in recording at `01:25`, the card badge still read `Review required` immediately after confirmation)* |
| **`SimilarJudgmentsSection` (`03`)** | Card preview with `Persistent Vector Index` badge | — *(not shown mid-load)* | `Retrieved N relevant precedent passages` + `Generation: Verified` + N `JudgmentCard`s | Sidebar Step `03` updates to `5 retrieved` |
| **`OutcomePredictionSection` (`04`)** | Not shown in Guidance column prior to confirmation | — *(not shown mid-load)* | `Appeal Allowed` / `Dismissed` pill, confidence `%`, stacked green/red bar, notice | Sidebar Step `04` updates with model & predicted class (to be **Random Forest** in our build) |
| **`WorkflowSidebar` Steps `01`–`04`** | `01` active lime pill; `02`–`04` neutral pills | — | Active step highlighted | `01`–`04` all show lime-green number pills and updated subtitles |
