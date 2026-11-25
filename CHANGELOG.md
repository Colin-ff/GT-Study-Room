# Changelog

## 2026-11-25 — Cambridge 16–17 Reading review

### Added

- Add source evidence and Chinese explanations for all 320 Reading questions in Cambridge 16 and 17 GT, Tests 1–4 in each book.
- Highlight exact source sentences, including evidence spanning multiple stored text blocks. NOT GIVEN questions label the excerpt as related text rather than confirmation of the claim.
- Explain English paraphrases, blank-adjacent wording and required word forms; discuss distractors and distinguish FALSE from NOT GIVEN.
- Add summaries and shared vocabulary notes for all 41 passages. Use the existing wrong/unanswered filters, evidence location and explanation dialogue after submission and in History.

### Fixed and checked

- Correct the OCR text “pack layout” to “back layout” in Cambridge 17 Test 2, matching the term required by Q37.
- Verify complete question coverage, valid block references, unique exact evidence matches and generated JavaScript syntax across all eight tests.
- Preserve existing test IDs and browser-local answers, history, highlights, vocabulary and writing drafts. No storage migration is required.

Explanations and follow-up replies remain bundled notes and rules, not real-time AI.

## 2026-11-25 — Cambridge 15 Reading review

### Added

- Add source evidence and Chinese explanations for all 160 Reading questions across Cambridge 15 GT Tests 1–4.
- Explain key English wording and paraphrases between each question and its evidence. Completion explanations focus on the blank and word form; choice questions explain distractors; FALSE and NOT GIVEN are distinguished explicitly.
- Include summaries and context-specific vocabulary for all 20 passages. Questions can share the vocabulary notes for their passage.
- Enable the existing wrong/unanswered filters, **Locate evidence** and explanation dialogue for these tests after submission and in History.

### Build and validation

- Discover review files at `bank/reviews/<book-id>/test-N.json` instead of hard-coding a single supported test. Unannotated tests remain usable without review controls.
- Validate full question coverage, non-empty explanations, evidence block bounds and unique exact evidence matches at build time.
- Preserve Cambridge 14 Test 1 reviews and existing browser storage keys, drafts, answers, highlights and vocabulary.
- Make the vocabulary shortcut return shared passage notes when a question has no separate term list.

The explanation dialogue still uses bundled notes and rules. Real-time AI inference is not included in this update.

## 2026-11-25 — Sync live versions 18–19 to GitHub

These changes were published on the live site on 19 November 2026 and synchronised to this repository on 25 November 2026.

### Reading and review

- Keep the shared yellow/green highlight control available after submission and while reviewing historical attempts.
- Allow highlighting and clearing highlights in article titles as well as passage body text and questions.
- Save annotation changes to the matching submitted attempt and history record without unlocking answers or changing the score.
- Allow selected words and phrases from questions to be added to the current passage vocabulary notebook.

### Vocabulary

- Add an **Add word** button beside the selection-based vocabulary button, so no selection is needed to create an entry.
- Add a manual-entry form with a word/phrase field, notes field, **Save** and **Add word** controls.
- Keep manually added words and notes in browser-local storage and include them in the book vocabulary summary.

### Question-bank presentation

- Restore separate lines for opening times, charges and additional notes in Cambridge IELTS 14 GT, Test 3, “Your guide to entertainment in Westhaven”.
- Display **Open**, **Charges** and **other times** labels in bold.
- Store presentation offsets separately from passage text to preserve existing highlight positions.
- Update the Cambridge 14 PDF importer to retain this formatting when regenerating the question bank.

### Validation and compatibility

- Preserve the existing repository directory structure, original demo and build support.
- Keep existing book/test IDs and browser storage keys unchanged.
- Validate the full static build and generated JavaScript syntax before synchronisation.

### Deployment note

The live site is published through ChatGPT Sites. Its source repository and this GitHub repository are separate; publishing to Sites does not automatically synchronise GitHub. This entry records the manual sync of live source commit `506104e70f723dc7bb9b74689d82f9edbff3631e`.
