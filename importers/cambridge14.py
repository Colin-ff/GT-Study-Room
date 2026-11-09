"""Extract Cambridge IELTS 14 General Training from the supplied PDF edition."""
import argparse
import base64
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("pdf", type=Path)
parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "bank/cambridge-14-gt")
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
pages = [""] + subprocess.check_output(["pdftotext", "-layout", str(args.pdf), "-"], text=True).split("\f")

TRUE_FALSE = ["TRUE", "FALSE", "NOT GIVEN"]
LETTERS = list("ABCDEFG")
MC = list("ABCD")
ROMAN = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"]
HEADINGS = [
    "Solving the puzzle of a papyrus document",
    "The importance of written records and different ways of recording them",
    "The use of papyrus for a range of purposes",
    "Suggestions for future possibilities for papyrus",
    "How papyrus was cultivated and different manufacturing methods",
    "The decline of papyrus use",
    "The preservation and destruction of papyrus documents",
    "The process of papyrus production",
]
RESEARCHERS = ["James Wood", "Ken Fening", "John Carr", "Theresa Manful", "Mark Carrington"]
# First body line and optional page continuation for each passage.
PASSAGES = {
    1: [
        (17, 17, "Transition care for the elderly", "What is transition care?"),
        (19, 19, "Cabin bags for air travel", "If you want a small bag"),
        (21, 22, "College car parking policy - staff", "Parking permits and tickets"),
        (24, 24, "Maternity benefits", "If you are expecting a baby"),
        (27, 28, "Papyrus", "Used by the ancient Egyptians"),
    ],
    3: [
        (61, 62, "Your guide to entertainment in Westhaven", "A    TRAX"),
        (64, 64, "Do you have a music project in mind that might benefit from funding?", "Music is wonderfully therapeutic"),
        (66, 66, "Guide to employees on workplace monitoring", "What is workplace monitoring?"),
        (68, 68, "International Experience Canada: application process", "If you want to travel"),
        (70, 71, "Research on improving agricultural yields in Africa", "Three programmes are investigating"),
    ],
    4: [
        (85, 85, "The best travel wallets", "Keep all your bank cards"),
        (87, 87, "UK rail services - how do I claim for my delayed train?", "Generally, if you have been delayed"),
        (89, 89, "Vacancy for food preparation assistant", "Durrant House"),
        (91, 91, "Setting up a business partnership in the UK", "Two or more people"),
        (93, 94, "The role of the Swiss postbus", "Switzerland's postbuses"),
    ],
}
# Question source page, first and last number, passage index, and interaction.
GROUPS = {
    1: [(18, 1, 6, 0, "tf"), (20, 7, 14, 1, "match5"),
        (23, 15, 20, 2, "short3"), (25, 21, 27, 3, "short2"),
        (26, 28, 32, 4, "headings"), (29, 33, 37, 4, "mc"),
        (30, 38, 40, 4, "summary")],
    3: [(63, 1, 7, 0, "match5"), (65, 8, 14, 1, "tf"),
        (67, 15, 21, 2, "notes2"), (69, 22, 27, 3, "flow"),
        (72, 28, 32, 4, "mc"), (73, 33, 36, 4, "researchers"),
        (74, 37, 40, 4, "summary2")],
    4: [(86, 1, 8, 0, "match7"), (88, 9, 14, 1, "tf"),
        (90, 15, 19, 2, "notes"), (92, 20, 27, 3, "sentence"),
        (95, 28, 32, 4, "mc"), (96, 33, 40, 4, "tf")],
}
TYPES = {
    "tf": ("True / False / Not Given", "Do the following statements agree with the information in the text?", TRUE_FALSE),
    "match5": ("Matching", "Choose the letter A–E that matches each statement. You may use any letter more than once.", LETTERS[:5]),
    "match7": ("Matching", "Choose the letter A–G that matches each statement. You may use any letter more than once.", LETTERS),
    "short3": ("Short answer", "Choose NO MORE THAN THREE WORDS AND/OR A NUMBER from the text for each answer.", []),
    "short2": ("Short answer", "Choose NO MORE THAN TWO WORDS AND/OR A NUMBER from the text for each answer.", []),
    "headings": ("Matching headings", "Choose the correct heading, i–viii, for each section.", ROMAN),
    "mc": ("Multiple choice", "Choose the correct letter, A, B, C or D.", MC),
    "summary": ("Summary completion", "Choose ONE WORD ONLY from the text for each answer.", []),
    "summary2": ("Summary completion", "Choose NO MORE THAN TWO WORDS from the text for each answer.", []),
    "notes": ("Note completion", "Choose ONE WORD ONLY from the text for each answer.", []),
    "notes2": ("Note completion", "Choose NO MORE THAN TWO WORDS from the text for each answer.", []),
    "flow": ("Flow-chart completion", "Choose ONE WORD AND/OR A NUMBER ONLY from the text for each answer.", []),
    "researchers": ("Matching researchers", "Match each statement with the correct researcher, A–E. You may use any letter more than once.", LETTERS[:5]),
    "sentence": ("Sentence completion", "Choose ONE WORD ONLY from the text for each answer.", []),
}
WORKSHEET_START = {30: "How papyrus documents have survived", 67: "Guide to employees on workplace monitoring",
                   69: "Applying to International Experience Canada", 74: "Trypanosomiasis",
                   90: "Vacancy for food preparation assistant"}
PARAGRAPH_STARTS = {
    17: ("What is transition care?", "Transition care is for", "Who provides", "Transition care is often",
         "Where do I receive", "Transition care is provided", "What if", "If you're already"),
    21: ("Enforcement", "The nominated contractor", "Visitors", "The College welcomes", "Short-term drop-off", "There will be"),
    24: ("You are entitled", "You may be entitled", "Maternity Allowance (MA) is available", "If you’re on", "If you get benefits"),
    68: ("To apply", "If you are sent", "For International", "Once you have received", "Your application will"),
    70: ("Ethiopia, for", "Wood leads", "The impact that", "Recently, however", "But farmers"),
}

def clean(page):
    # This running source credit repeats at the bottom of both Papyrus pages.
    page = re.sub(
        r"(?m)^ *From Stephen Harris, What have Plants Ever Done for Us\?, "
        r"Bodleian Library Publishing 2015\. Reprinted by kind permission of Bodleian"
        r"\s+Library Publishing\. *$",
        "",
        page,
    )
    return [line.rstrip() for line in page.splitlines()
            if not re.fullmatch(r"\s*(?:Reading|Writing|READING|WRITING|Test\s*[1-4lI]|\d+|\.)\s*", line)]

def normalize(value):
    value = " ".join(value.split())
    value = re.sub(r"\s+([,.?!;:)])", r"\1", value)
    return re.sub(r"(?<=\d), (?=\d{3}\b)", ",", value)

def from_marker(lines, marker):
    return lines[next(i for i, line in enumerate(lines) if line.lstrip().startswith(marker)):]

def grouped(lines, starts=()):
    blocks, current = [], []
    for line in lines:
        line = line.strip()
        if not line or line.startswith(("•", *starts)) or re.match(r"^[A-G]\s{2,}", line):
            if current:
                blocks.append(normalize(" ".join(current)))
                current = []
        if line:
            current.append(line)
    if current:
        blocks.append(normalize(" ".join(current)))
    return blocks

def split_postbus():
    # The left text and right text must be read separately on each printed page.
    columns = []
    for page, marker in [(93, "The Swiss PostBus Limited"), (94, "fuel-cell models")]:
        rows = from_marker(clean(pages[page]), marker)
        left, right = [], []
        for row in rows:
            left.append(row[:55].rstrip())
            right.append(row[55:].strip())
        columns.extend([left, right])
    for index in (1, 2, 3):
        while columns[index] and not columns[index][0].strip():
            columns[index].pop(0)
        while columns[index - 1] and not columns[index - 1][-1].strip():
            columns[index - 1].pop()
    return sum(columns, [])

def passage_data(spec):
    first, last, title, start = spec
    lines = from_marker(clean(pages[first]), start)
    for page in range(first + 1, last + 1):
        while lines and not lines[-1].strip():
            lines.pop()
        continuation = clean(pages[page])
        while continuation and not continuation[0].strip():
            continuation.pop(0)
        lines.extend(continuation)
    if first == 93:
        lines = ["Switzerland's postbuses are much more than just a means of public transportation.", "", *split_postbus()]
    repairs = {"maximum often minutes": "maximum of ten minutes",
               ") net the college": ") not the college", "Durrant House pic": "Durrant House plc",
               "self employed individuals": "self-employed individuals",
               "three- tone post horns": "three-tone post horns",
               "‘language started": "‘language’ started",
               "used to Talk’ to": "used to ‘talk’ to",
               "‘departure of post’, arrival of post’, arrival of special post’": "‘departure of post’, ‘arrival of post’, ‘arrival of special post’",
               "mountain passes an eight-hour": "mountain passes – an eight-hour",
               "and one — of the highest": "and one of the highest",
               "pre arranged permits": "pre-arranged permits", "£3. 50": "£3.50", "£2. 50": "£2.50",
               "4. 30 pm": "4.30 pm", "ultra -lightweight": "ultra-lightweight",
               "simmons. j@durrant-house. com": "simmons.j@durrant-house.com"}
    blocks = grouped(lines, PARAGRAPH_STARTS.get(first, ()))
    for i, block in enumerate(blocks):
        for old, new in repairs.items():
            block = block.replace(old, new)
        blocks[i] = block
    if first == 93 and blocks[-1].startswith("importance."):
        blocks[-2:] = [" ".join(blocks[-2:])]
    return {"title": title, "blocks": blocks, "pages": [first, last]}

def read_key(test):
    answers = {}
    for row in pages[121 + test * 2].split("If you score", 1)[0].splitlines():
        for cell in re.split(r"\s{12,}", row.strip()):
            if match := re.fullmatch(r"(\d{1,2})\s+(.+)", cell):
                number, answer = int(match[1]), match[2].strip()
                assert number not in answers
                answers[number] = answer.upper() if re.fullmatch(r"[A-Ga-g]", answer) else answer
    assert sorted(answers) == list(range(1, 41)), answers
    return answers

def alternatives(answer):
    if answer.startswith("("):
        optional, rest = answer[1:].split(") ", 1)
        return [rest, f"{optional} {rest}"]
    if answer == "1(st) October":
        return ["1(st) October", "1 October", "1st October", "October 1", "October 1st", "the first of October", "first October", "first of October"]
    if answer == "six weeks":
        return ["six weeks", "6 weeks"]
    if answer == "26 weeks":
        return ["26 weeks", "twenty-six weeks", "twenty six weeks"]
    if answer == "39 weeks":
        return ["39 weeks", "thirty-nine weeks", "thirty nine weeks"]
    if answer == "10 days":
        return ["10 days", "ten days"]
    if answer == "£112.75":
        return ["£112.75", "112.75", "112.75 pounds", "£ 112.75"]
    return [answer]

def numbered(lines, first, last, kind):
    items = {}
    current = option = None
    for raw in lines:
        if m := re.match(r"\s*(\d{1,2})\s+(\S.*)", raw):
            number = int(m[1])
            if first <= number <= last:
                current = {"text": m[2], "options": {}}
                items[number] = current
                option = None
            continue
        if current is None or not raw.strip():
            continue
        if kind == "mc" and (m := re.match(r"\s*([A-D])\s{2,}(.+)", raw)):
            option = m[1]
            current["options"][option] = m[2]
            continue
        if kind == "researchers" and "List of Researchers" in raw:
            break
        if option:
            current["options"][option] += " " + raw.strip()
        else:
            content = raw.strip()
            if kind == "sentence":
                if len(raw) - len(raw.lstrip()) >= 15 and current["text"].find("[[blank]]") < 0:
                    content = "[[blank]] " + content
                current["text"] = re.sub(r"\s{5,}", " [[blank]] ", current["text"])
            current["text"] += " " + content
    if kind == "sentence":
        for n, q in items.items():
            q["text"] = re.sub(r"\s{5,}", " [[blank]] ", q["text"])
            q["text"] = q["text"].replace("on . and", "on [[blank]] and").replace("your . for", "your [[blank]], for")
            if "[[blank]]" not in q["text"]:
                q["text"] += " [[blank]]."
    return items

def make_group(spec, answers):
    page, first, last, passage, kind = spec
    label, instruction, choices = TYPES[kind]
    lines = clean(pages[page])
    if page == 18:
        lines = [re.sub(r"^6(?=\s+Transition care may be given)", "5", line) for line in lines]
    worksheet = []
    if page in WORKSHEET_START:
        lines = from_marker(lines, WORKSHEET_START[page])
        pattern = re.compile(r"(?<!\d)(" + "|".join(map(str, range(first, last + 1))) + r")(?!\d)\s*(?=\s{2,}|$)")
        # In summaries all answer positions appear in one paragraph. The first line is the title.
        tagged = [lines[0], *[pattern.sub(lambda m: f"[[{m[1]}]] ", line) for line in lines[1:]]]
        if kind.startswith("summary"):
            worksheet = [tagged[0].strip(), normalize(" ".join(tagged[1:]))]
            if page == 74:
                worksheet[1] = worksheet[1].replace("[[37]] The", "[[37]]. The")
        elif kind == "flow":
            worksheet = [line.replace("[[24]] You", "[[24]]. You") for line in grouped(tagged)]
        else:
            worksheet = [normalize(line) for line in tagged if line.strip()]
            if page == 67:
                line = next(i for i, text in enumerate(worksheet) if "known as [[16]]" in text)
                worksheet[line - 1:line + 2] = [" ".join(worksheet[line - 1:line + 2])]
        assert re.findall(r"\[\[(\d+)\]\]", " ".join(worksheet)) == list(map(str, range(first, last + 1))), (page, worksheet)
        items = {n: {"text": "", "options": {}} for n in range(first, last + 1)}
    else:
        items = numbered(lines, first, last, kind)
    questions = []
    for n in range(first, last + 1):
        item = items[n]
        answer = answers[n]
        if choices:
            assert answer in choices, (page, n, answer)
        if kind == "mc":
            assert list(item["options"]) == MC
        q = {"id": n, "text": normalize(item["text"]), "answer": answer,
             "accepted": alternatives(answer), "leads": [],
             "options": {letter: normalize(text) for letter, text in item["options"].items()}}
        questions.append(q)
    choice_labels = HEADINGS if kind == "headings" else RESEARCHERS if kind == "researchers" else []
    return {"passage": passage, "first": first, "last": last, "page": page, "kind": label,
            "instruction": instruction, "choices": choices, "questions": questions,
            "choiceLabels": dict(zip(choices, choice_labels)), "worksheet": worksheet}

def writing_data(test, first):
    tasks = []
    with tempfile.TemporaryDirectory() as directory:
        for index in range(2):
            page = first + index
            prompt = "\n".join(line.strip() for line in clean(pages[page])).strip()
            prompt = re.sub(r"\n{3,}", "\n\n", prompt)
            reference_page = 128 + test * 2 + index
            image = Path(directory) / "reference.jpg"
            subprocess.run(["pdftoppm", "-f", str(reference_page), "-l", str(reference_page),
                            "-singlefile", "-scale-to", "1500", "-jpeg", str(args.pdf), str(image.with_suffix(""))], check=True)
            tasks.append({"prompt": prompt, "minimum": (150, 250)[index], "page": page,
                          "model": "MODEL ANSWER" in pages[reference_page],
                          "reference": base64.b64encode(image.read_bytes()).decode()})
    return tasks

for test, writing_first in [(1, 31), (2, 52), (3, 75), (4, 97)]:
    output = args.output / f"test-{test}.json"
    if test == 2:
        subprocess.run([sys.executable, str(Path(__file__).with_name("build.py")), str(args.pdf), str(output)], check=True)
        data = json.loads(output.read_text())
        data["writing"][0]["model"] = True
    else:
        answers = read_key(test)
        data = {"passages": [passage_data(spec) for spec in PASSAGES[test]],
                "groups": [make_group(spec, answers) for spec in GROUPS[test]],
                "writing": writing_data(test, writing_first)}
    output.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
