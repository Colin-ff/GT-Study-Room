"""Build the self-contained Cambridge 14 GT Test 2 practice page."""
import argparse
import base64
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("pdf", type=Path)
parser.add_argument("output", type=Path, nargs="?", default=ROOT / "test-2.json")
args = parser.parse_args()


def extract(first, last):
    return subprocess.check_output(
        ["pdftotext", "-layout", "-f", str(first), "-l", str(last), str(args.pdf), "-"],
        text=True,
    ).split("\f")


def clean_page(page):
    return [
        line for line in page.splitlines()
        if not re.fullmatch(r"\s*(?:Reading|Writing|READING|WRITING|Test 2|\d+|\.)\s*", line)
    ]


def normalize(text):
    return re.sub(r"\s+([,.?!])", r"\1", " ".join(text.split()))


pages = dict(zip(range(40, 54), extract(40, 53)))
passage_specs = [
    (40, 40, "Five reviews of the Wellington Hotel", ()),
    (42, 42, "Come and play walking football or walking netball", (
        "Walking football was invented", "The two games", "Many players", "The local council",
    )),
    (44, 44, "Dress regulations at work", (
        "Protective clothing and equipment", "Your employer can tell you",
        "You are required to:", "Of course", "Don’t be put off", "The obligation",
        "Jewellery", "Banning employees", "Likewise",
    )),
    (46, 46, "How to achieve a better work-life balance", ()),
    (48, 49, "San Francisco’s Golden Gate Bridge", (
        "Despite the economic benefits", "However, the District",
        "The attempt to build", "The roadway was completed",
    )),
]
passages = []
for first, last, title, paragraph_starts in passage_specs:
    raw = "\n".join("\n".join(clean_page(pages[p])) for p in range(first, last + 1))
    raw = raw.split(title, 1)[1]
    raw = raw.replace("dress smartly ,", "dress ‘smartly’,").replace("'smart ,  5", "‘smart’,")
    raw = re.sub(r"‘smart’,\s+you", "‘smart’,\nyou", raw)
    raw = raw.replace("cept sterile.", "kept sterile.")
    raw = raw.replace("24 /7", "24/7").replace("If s easy", "It’s easy")
    raw = raw.replace("say no’", "say ‘no’").replace("use no’", "use ‘no’")
    raw = raw.replace("of me time’", "of ‘me time’")
    raw = raw.replace("Since then , tens of thousands of people\nmostly", "Since then, tens of thousands of people –\nmostly")
    raw = raw.replace("proceedings This", "proceedings. This")
    raw = raw.replace("orange '", "orange'").replace("out- of- work", "out-of-work")
    raw = re.sub(
        r"opened to\s+opening via White House telegraph\.\s+"
        r"pedestrians the following month\. The next day President Roosevelt announced its",
        "opened to pedestrians the following month. The next day President Roosevelt announced its opening via White House telegraph.",
        raw,
    )
    blocks, lines = [], []
    for line in raw.splitlines():
        line = line.strip()
        if not line or re.match(r"^[A-G]\s{2,}|^•", line) or any(
            line.startswith(start) for start in paragraph_starts
        ):
            if lines:
                blocks.append(normalize(" ".join(lines)))
                lines = []
        if line:
            lines.append(line)
    if lines:
        blocks.append(normalize(" ".join(lines)))
    passages.append({"title": title, "blocks": blocks, "pages": [first, last]})

notes = {
    21: "Make a complete [[blank]] of things that are not helpful and reduce involvement in them",
    22: "Refuse some requests as this can be a useful [[blank]] in gaining a better work-life balance",
    23: "can increase [[blank]] significantly",
    24: "avoid focusing on [[blank]] in the lead-up to bedtime",
    25: "Those who see other people’s [[blank]] as more important than their own will suffer",
    26: "If the working day is too long, get [[blank]] to shorten it occasionally",
    27: "People should learn to recognise their own [[blank]]",
}
note_leads = {
    21: ["How to begin"],
    23: ["Things that can help", "Regular exercise"],
    24: ["Sleep", "• insufficient sleep can make people ill"],
    25: ["Issues that require attention"],
}
specs = [
    (0, 1, 7, 41, "Matching", "Which review mentions the following? You may use any letter more than once.", list("ABCDE")),
    (1, 8, 14, 43, "True / False / Not Given", "Do the following statements agree with the information given in the text?", ["TRUE", "FALSE", "NOT GIVEN"]),
    (2, 15, 20, 45, "Sentence completion", "Complete the sentences. Choose ONE WORD ONLY from the text for each answer.", []),
    (3, 21, 27, 47, "Note completion", "Complete the notes. Choose ONE WORD ONLY from the text for each answer.", []),
    (4, 28, 35, 50, "Matching", "Which section mentions the following? You may use any letter more than once.", list("ABCDEFG")),
    (4, 36, 40, 51, "Sentence completion", "Complete the sentences. Choose ONE WORD ONLY from the text for each answer.", []),
]
answers = {}
for line in extract(125, 125)[0].split("If you score", 1)[0].splitlines():
    for cell in re.split(r"\s{5,}", line.strip()):
        match = re.fullmatch(r"(\d{1,2})\s+(.+)", cell)
        if match:
            number = int(match[1])
            value = match[2].strip()
            answers[number] = value.upper() if len(value) == 1 else value
assert sorted(answers) == list(range(1, 41)), "Incomplete answer key"

groups = []
for passage, first, last, page, kind, instruction, choices in specs:
    texts = {}
    if first == 21:
        texts = notes
    else:
        current = None
        for line in clean_page(pages[page]):
            if match := re.match(r"\s*(\d{1,2})\s+(\S.*)", line):
                number = int(match[1])
                if first <= number <= last:
                    current = number
                    texts[current] = match[2]
            elif current and line.strip():
                content = line.strip()
                if kind == "Sentence completion" and re.match(r"^\s{15,}", line) and "[[blank]]" not in texts[current]:
                    content = "[[blank]] " + content
                texts[current] += " " + content
            if current and kind == "Sentence completion":
                texts[current] = re.sub(r"\s{5,}", " [[blank]] ", texts[current])
        if first in (15, 36):
            for number in range(first, last + 1):
                if "[[blank]]" not in texts[number]:
                    texts[number] += " [[blank]]"
    questions = [
        {"id": n, "text": normalize(texts[n]), "answer": answers[n], "leads": note_leads.get(n, [])}
        for n in range(first, last + 1)
    ]
    for question in questions:
        if choices:
            assert question["answer"] in choices
        else:
            assert question["text"].count("[[blank]]") == 1
    groups.append({
        "passage": passage, "first": first, "last": last, "page": page,
        "kind": kind, "instruction": instruction, "choices": choices, "questions": questions,
    })

writing = []
with tempfile.TemporaryDirectory() as temp:
    for i, page in enumerate((52, 53), 1):
        prompt = "\n".join(line.strip() for line in clean_page(pages[page])).strip()
        prompt = re.sub(r"\n{3,}", "\n\n", prompt)
        ref = Path(temp) / f"writing-{i}"
        subprocess.run([
            "pdftoppm", "-f", str(131 + i), "-l", str(131 + i),
            "-singlefile", "-scale-to", "1500", "-jpeg", str(args.pdf), str(ref),
        ], check=True)
        writing.append({
            "prompt": prompt, "minimum": 150 if i == 1 else 250, "page": page,
            "reference": base64.b64encode(ref.with_suffix(".jpg").read_bytes()).decode(),
        })

data = json.dumps({"passages": passages, "groups": groups, "writing": writing}, ensure_ascii=False)
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(data, encoding='utf-8')
