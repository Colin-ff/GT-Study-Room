# G Study Room release QA — 2026-11-28

final result: passed

## Visual truth and captured implementation

- Homepage reference: `/workspace/scratch/1ec37912b271/generated_images/exec-789d952b-cce3-4592-9a87-a950255094c0.png`.
- Bookshelf reference: `/workspace/scratch/1ec37912b271/generated_images/exec-c83d99bd-accc-4c20-af28-0dab81c80663.png`.
- Reference pixels: 1487 × 1058. Browser captures: 1488 × 1056 JPEG, CSS iframe viewport 1488 × 1056, density 1; 15px native vertical scrollbar leaves 1473px content width. References normalized to 1488 × 1056 for comparison.
- Homepage implementation: `/workspace/shared/g-study-room-qa/home-final.jpg`.
- Bookshelf implementation: `/workspace/shared/g-study-room-qa/library-final.jpg`.
- Combined equal-size comparison inputs opened together: `home-comparison.jpg`, `library-comparison.jpg` in that same QA folder.
- Focused card typography, images and scale comparison: `cards-comparison.jpg`.
- Mobile: actual 390 × 844 iframe, 375px content plus native scrollbar; screenshot `mobile-library.jpg`. No horizontal overflow.
- States: homepage with Past paper practice selected; shelf with Cambridge 17 selected. Existing browser records supply actual progress rather than the reference's fabricated 35%.

The earlier preview issue was a host-routing mismatch. The Sites preview CLI's returned `http://127.0.0.1:4173/` now renders normally in the cloud browser. Temporary iframe fixtures provide exact desktop/mobile viewport sizes; they are excluded from deployment.

## Comparison history and fixes

1. [P2, fixed] Inactive card titles were partially covered by the central card. Use short labels on side cards, keep full titles in accessible names and the selected description, and shift side labels outward. The final focused comparison confirms readable AI Speaking / AI Writing labels and five pictured size tiers.
2. [P2, fixed] Selecting volume 14 left excessive blank shelf space on desktop; a desktop clamped display window fills the row while retaining the selection. At mobile widths this clamping clipped the active cover: keep the selected book centered below 600px. Mobile re-capture confirms volume 14 is fully visible; selecting volume 20 also works.
3. [P2, fixed] The homepage's vertical centering placed the headline and glass panel too low relative to the reference. Top-align the desktop layout, retain the smaller user-requested typography, and give the panel a minimum 744px height. Re-capture shows the panel begins near the reference's upper third and the headline stays alongside the carousel.

## Required fidelity surfaces

- Typography: system sans/Arial follows the reference's sans style. Smaller 28–40px introduction, 28px panel title and compact card labels implement the user's request to reduce text. Full tool titles appear when selected; subordinate metadata remains secondary.
- Layout: floating rounded navigation, left introduction/right glass carousel, center/adjacent/outer scale tiers, separate broad bookshelf with selected-book details. Mobile stacks sections, keeps controls reachable and has no horizontal page overflow.
- Colors/tokens: emerald accents, forest-green translucent panels, thin pale borders and white/cream text match the chosen direction. Coming soon is distinct from the available practice action.
- Images: all five modules have actual generated pictures per the user's later request; they intentionally replace the mock's four outline icons. The forest, cozy window backdrop, cover artwork and G/open-book mark share the green/cream art direction. Arrow/close icons are licensed Phosphor assets. No broken image loads.
- Content: G-study-room, Forum, the five requested modules, Cambridge 14–20, four tests per volume and browser-local storage notice are present. Coming soon tools and Forum make no claim of working AI/server behavior.

## Browser and automated verification

- Click side card; select by dots; previous/next wrap; physical mouse drag from center to left changes Past paper practice to AI Writing Feedback; ArrowLeft restores the previous selection.
- Mobile feature selection, Forum dialog opening/closing, and book 14/17/20 selection work. Arrow controls and browser-native scroll remain reachable.
- Homepage → bookshelf → Cambridge 17 → Test 1 Reading works. Existing completed records, 40-question navigation, review controls and vocabulary still appear.
- Book vocabulary opens the existing notebook. Resume points to a saved attempt and progress reads the existing storage keys.
- Browser console inspected: no application errors. Only unrelated Chrome extension metadata messages were present.
- Python static build, JavaScript syntax checks, DOM integration checks, asset/catalog links and preservation of 28 Cambridge test pages pass. Exam HTML source and question bank are unchanged by the redesign.

## Follow-up polish (P3)

- The new original book covers use shared nature artwork with volume-specific palette variation rather than seven unrelated illustrations.
- Side-card metadata scales down intentionally; selecting a card exposes the full readable title and description below.
- Physical phone touch gestures were not tested on hardware; pointer/touch handling is shared and desktop physical dragging is verified.

No actionable P0/P1/P2 findings remain. Publish this verified revision to the existing site without changing its audience or domain. V22 remains the rollback target.

## 2026-11-28 incremental bookshelf check

User reference: `upload/image(20261128-003548).png`, requesting visible book sides. Browser inspection at 1363 × 936 and in a 390 × 844 mobile iframe confirmed separate textured spines, foreshortened covers, thin top page edges and book shadows. Volume 17 is enlarged and rotates more frontally on selection. Initial volume 14 clipping at the left shelf edge was corrected by deriving the display center from actual book width. Rechecked volumes 14, 17 and 20: active books and spines remain visible. Physical drag changed 17 to 18; ArrowLeft returned to 17. The volume 20 destination remains `books/cambridge-20-gt.html`. Mobile content width and scroll width both 375px (native scrollbar included in the 390px frame). All seven spines are present. No application console errors. Existing build and saved-record tests pass.

## Forest-green practice theme — 2026-11-28

- Reading, Writing, test catalog, vocabulary sidebar and history/review surfaces share forest-green navigation and controls, sage borders and warm paper surfaces. Yellow/green annotations and red incorrect-answer feedback retain their meaning.
- Browser verified bookshelf → Cambridge 14 catalog → Reading review → vocabulary/history dialog → Writing; separate 3D spine and top page edge remain visible. Existing saved progress and vocabulary still appear.
- Theme changes are confined to styles: script blocks in exam/catalog are byte-identical to the previous source; bank records and storage keys unchanged. Existing build and homepage integration tests pass.
