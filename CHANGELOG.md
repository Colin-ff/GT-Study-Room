# Changelog

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
