# Manual Testing Documentation

This document outlines the manual testing procedures for the AI-Powered Quiz & Study Assistant Platform. These tests are intended to complement the automated test suite (`tests/`) and cover areas that are difficult or impossible to automate effectively, such as visual polish, complex accessibility (508) requirements, and the non-deterministic behavior of AI feedback.

---

## 1. Functional Testing

### 1.1 Quiz Creation (JSON Interface)
**Goal:** Verify the robustness of the manual JSON input for quiz creation.
- [ ] **Empty Submission:** Submit with an empty title and/or empty questions field. Verify validation messages.
- [ ] **Invalid JSON:** Paste malformed JSON (e.g., missing commas, trailing commas, unclosed brackets). Verify that the application shows a helpful error message instead of crashing.
- [ ] **Schema Validation:** Submit valid JSON but with incorrect fields (e.g., `ans_idx` instead of `answer_index`). Verify how the system handles missing/extra keys.
- [ ] **Large Payloads:** Test with a quiz containing 50+ questions to ensure the `POST` request and database persistence work as expected.

### 1.2 Quiz Taking Flow
**Goal:** Ensure the user experience of taking a quiz is intuitive.
- [ ] **Partial Completion:** Submit a quiz without answering all questions. Verify that the score reflects the unanswered questions as incorrect.
- [ ] **Navigation During Quiz:** Start a quiz, navigate back to the home page, and then use the browser "Back" button. Ensure the form state or session behaves predictably.
- [ ] **Multiple Submissions:** Rapidly click the "Submit" button to check for duplicate entry creation in the database.

---

## 2. UI/UX & Responsiveness

### 2.1 Cross-Device Layout
**Goal:** Ensure the app is usable on all screen sizes.
- [ ] **Mobile View (iPhone/Android):** Open the app on a mobile device or via Chrome DevTools (Responsive mode). Check if the `container` and `textarea` scale correctly without horizontal scrolling.
- [ ] **Tablet View:** Verify the layout on medium-sized screens.
- [ ] **Text Overflow:** Use extremely long quiz titles and question texts to see if they break the layout or wrap correctly.

### 2.2 Visual Consistency
- [ ] **Hover/Focus States:** Verify that links, buttons, and radio buttons have clear visual changes when hovered or focused.
- [ ] **Color Contrast:** Check that error messages (e.g., "Invalid questions JSON") are clearly visible against the background.

---

## 3. Accessibility (Section 508) Manual Audit

Automated tools like `axe` catch ~30-40% of issues. The following must be verified manually:

### 3.1 Keyboard Navigation
- [ ] **Tab Order:** Use the `Tab` key to navigate through the entire site. The order should be logical (top-to-bottom, left-to-right).
- [ ] **Focus Indicators:** Ensure every interactive element (links, buttons, radio inputs) has a visible focus ring/outline when navigated via keyboard.
- [ ] **Form Submission:** Verify that you can submit the quiz and the quiz creation form using only the `Enter` or `Space` key.

### 3.2 Screen Reader Experience
- [ ] **Result Feedback:** Use a screen reader (VoiceOver, NVDA, or JAWS) on the Results page. Does it clearly announce whether a question was correct or incorrect? (Check if the ✅/❌ icons have `aria-label` or `alt` text).
- [ ] **Error Announcements:** When a form submission fails, does the screen reader announce the error message?
- [ ] **Page Titles:** Ensure the `<title>` tag updates for each page so the screen reader announces the context on page load.

### 3.3 Semantic Structure
- [ ] **Landmarks:** Verify (via browser inspection) that the main content is wrapped in a `<main>` tag and navigation is in a `<nav>` tag (currently uses `div.container`).

---

## 4. AI Feedback Verification

Since AI responses are non-deterministic, manual sampling is required.

### 4.1 Helpful & Accurate
- [ ] **Relevance:** Does the "AI Feedback" actually address the specific questions that were missed?
- [ ] **Tone:** Is the feedback encouraging and educational, as per the product requirements?
- [ ] **Accuracy:** If the AI (even the mock) suggests "fundamentals," does that make sense for the quiz context?

### 4.2 Error Handling
- [ ] **Mock/API Failure:** If the AI service is unreachable, verify that the Results page still loads gracefully with a "Feedback unavailable" message (instead of a 500 error).

---

## 5. Cross-Browser Testing

Verify the application functionality and appearance in:
- [ ] **Chrome** (latest)
- [ ] **Firefox** (latest)
- [ ] **Safari** (macOS and iOS)
- [ ] **Edge** (latest)

---

## 6. How to Document Manual Test Results

When performing manual testing, please record the following in a new test report:
1. **Date of Test:**
2. **Environment:** (e.g., Local, Docker, Production URL)
3. **Browser/OS:**
4. **Test Case ID:** (from the sections above)
5. **Status:** (Pass/Fail)
6. **Notes/Bugs:** If failed, include steps to reproduce and screenshots if possible.
