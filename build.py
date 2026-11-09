"""Build the static IELTS test library from bank/<book>/test-N.json."""
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "dist"
EXAM = (ROOT / "frontend" / "exam.html").read_text(encoding="utf-8")
CATALOG = (ROOT / "frontend" / "catalog.html").read_text(encoding="utf-8")
READING_HEADINGS = json.loads((ROOT / "bank" / "reading-headings.json").read_text(encoding="utf-8"))


# In these legacy passages the letter is already part of the stored text.
LEGACY_LABELLED_PAGES = {
    "cambridge-14-gt": {19, 27, 40, 48, 61, 85},
    "cambridge-15-gt": {18, 24, 40, 47, 62, 66, 82},
    "cambridge-16-gt": {19, 28, 43, 63, 72, 85},
    "cambridge-17-gt": {28, 41, 49, 63, 72, 85},
}


def label_legacy_passage(passage):
    labels = {}
    expected = "A"
    for index, block in enumerate(passage["blocks"]):
        if block.startswith(expected + " "):
            labels[str(index)] = expected
            expected = chr(ord(expected) + 1)
    assert len(labels) >= 2, passage["title"]
    return labels


def catalog(path, title, intro, cards, back=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    html = (CATALOG.replace("__TITLE__", escape(title)).replace("__INTRO__", escape(intro))
            .replace("__BACK__", back).replace("__CARDS__", "\n".join(cards)))
    path.write_text(html, encoding="utf-8")


books = []
for book in sorted((ROOT / "bank").iterdir()):
    if not book.is_dir():
        continue
    if book.name == "demo-gt":
        title = "Original demo"
    elif match := re.fullmatch(r"cambridge-(\d+)-gt", book.name):
        title = f"Cambridge IELTS {match[1]}"
    else:
        continue
    book_url = f"books/{book.name}.html"
    cards = []
    for source in sorted(book.glob("test-*.json")):
        test_number = int(source.stem.removeprefix("test-"))
        test = json.loads(source.read_text(encoding="utf-8"))
        questions = [q for group in test["groups"] for q in group["questions"]]
        question_count = len(questions)
        assert question_count and (book.name == "demo-gt" or question_count == 40), source
        assert [q["id"] for q in questions] == list(range(1, question_count + 1)), source
        assert all(q["answer"] for q in questions), source
        assert test["passages"] and len(test["writing"]) == 2, source
        book_headings = READING_HEADINGS.get(book.name, {})
        for passage in test["passages"]:
            pages = passage.get("pages")
            headings = book_headings.get(str(pages[0]), {}) if pages else {}
            for index, heading in headings.items():
                block = passage["blocks"][int(index)]
                assert block == heading or block.startswith(heading + " "), (source, heading)
            if headings:
                passage["headings"] = headings
            if pages and pages[0] in LEGACY_LABELLED_PAGES.get(book.name, ()):
                passage["labels"] = label_legacy_passage(passage)
            for index, letter in passage.get("labels", {}).items():
                assert passage["blocks"][int(index)].startswith(letter + " "), (source, letter)

        if book.name == "cambridge-14-gt" and test_number == 1:
            explanations = json.loads((ROOT / "bank" / "cambridge-14-test-1-review.json").read_text(encoding="utf-8"))
            assert set(explanations) == {str(q["id"]) for q in questions}, source
            for group in test["groups"]:
                blocks = test["passages"][group["passage"]]["blocks"]
                for question in group["questions"]:
                    entry = explanations[str(question["id"])]
                    evidence = []
                    for block, first, *last in entry.pop("anchors"):
                        text = blocks[block]
                        if first is None:
                            begin = 0
                            excerpt = text
                        else:
                            begin = text.index(first)
                            end = text.index(last[0], begin) + len(last[0])
                            excerpt = text[begin:end]
                            assert end >= begin + len(first) and text.count(excerpt) == 1, (source, question["id"])
                        evidence.append((block, begin, excerpt))
                    entry["evidence"] = [[block, excerpt] for block, _, excerpt in sorted(evidence)]
            test["explanations"] = explanations
        key = f"{book.name}-{source.stem}-v2"
        test["storageKey"] = key
        path = f"tests/{book.name}/{source.stem}.html"
        output = DEST / path
        output.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(test, ensure_ascii=False).replace("<", "\\u003c")
        output.write_text(EXAM.replace("__PAGE_TITLE__", f"G Study Room · {title} · Test {test_number}")
                          .replace("__BOOK_LABEL__", f"{title} · General Training")
                          .replace("__TEST_LABEL__", f"Test {test_number} Practice")
                          .replace("__BOOK_URL__", "../../" + book_url)
                          .replace("__EXAM_DATA__", data), encoding="utf-8")
        links = "".join(
            f'<a href="../{escape(path)}?mode={mode}">{mode.title()}'
            f'<span class="status" data-module="{mode}" lang="zh">未练习</span></a>'
            for mode in ("reading", "writing")
        )
        cards.append(f'<article class="test" data-storage-key="{escape(key)}" data-reading-total="{question_count}">'
                     f'<div class="test-head"><h2>Test {test_number}</h2>'
                     '<span class="progress" data-total lang="zh">未练习</span></div>'
                     f'<p class="description">{question_count} reading questions · 2 writing tasks</p>'
                     f'<div class="modules">{links}</div></article>')
    if cards:
        catalog(DEST / book_url, title, "Choose a test and a module.", cards,
                '<a class="back" href="../">‹ All books</a>')
        books.append(f'<a class="test book-link" href="{escape(book_url)}"><h2>{title}</h2>'
                     f'<p class="description">{len(cards)} tests · Reading &amp; Writing</p>'
                     '<span class="open-book">View tests →</span></a>')
assert books, "No tests found in bank/"
catalog(DEST / "index.html", "Test library", "Choose a practice collection to get started.", books)
