"""Build Cambridge GT 15–17 bank entries from a supplied book PDF."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import base64
import json
import os
from pathlib import Path
import re
import subprocess

import fitz

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("book", type=int, choices=[15, 16, 17])
parser.add_argument("pdf", type=Path)
parser.add_argument("--ocr-cache", type=Path)
args = parser.parse_args()
book = args.book
root = Path(__file__).resolve().parents[1]
directory = root / "bank" / f"cambridge-{book}-gt"
directory.mkdir(exist_ok=True)
document = fitz.open(args.pdf)
pages = [""] + subprocess.check_output(["pdftotext", "-layout", str(args.pdf), "-"], text=True).split("\f")
LETTERS = "ABCDEFGH"
ROMAN = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"]

# Keys transcribed from the four printed Reading answer-key pages of each book.
KEYS = {
    15: [
        "NOT GIVEN|NOT GIVEN|TRUE|TRUE|FALSE|NOT GIVEN|D|E|B|A|D|B|E|C|3 / three metres / meters|residential building sites|eliminate|(temporary) (work) platforms|safety nets|(maintenance) work|selection|inspection|140.98|unemployed|payslip|doctor’s letter|circumstances|D|C|C|D|C|F|B|A|G|gravel|nuggets|sieve|mercury",
        "FALSE|NOT GIVEN|TRUE|TRUE|FALSE|FALSE|C|A|C|B|C|E|B|D|sewage|poisoning|drowning|gloves|tags|disconnected|objectives|review|calendar|collaboration|distraction|creativity|retention|iv|vi|vii|i|v|iii|A|C|D|B|flexible|land|ball",
        "FALSE|TRUE|NOT GIVEN|TRUE|FALSE|NOT GIVEN|TRUE|B|E|C|D|A|F|C|familiar|abilities|stimulating|potential|promotion|flexible|C|F|C|A|E|B|D|D|A|B|efficient|food|hibernation|blood|temperature|A|D|B|C|A",
        "E|C|B|D|A|C|B|NOT GIVEN|TRUE|TRUE|TRUE|FALSE|NOT GIVEN|FALSE|photo|screens|productivity|mobile|gossip|snacks|skills|commitment|value|panel|potential|organisation / organization|courses|rules|fairness|submissive|biting|forgiveness|E|C|G|D|F|C|D|B",
    ],
    16: [
        "D|B|C|E|A|B|TRUE|TRUE|NOT GIVEN|FALSE|FALSE|FALSE|TRUE|NOT GIVEN|fertiliser / fertilizer|animal|obstacle|aids|bending|gate|proactive|special offers|brand names|negativity|presentation|credit card|rudeness|vi|iv|ii|viii|v|i|iii|D|D|A|family|platform|multi(-)coloured / multi(-)colored",
        "FALSE|TRUE|NOT GIVEN|TRUE|FALSE|TRUE|FALSE|F|H|C|F|A|D|E|festivals|budget|partnerships|diversity|database|accounting|knowledge|regulations|responsibilities|leaflets|statement|contractors|stress|B|A|C|B|D|C|F|B|A|community service|shifting sand|copper|farmers",
        "E|D|C|A|C|TRUE|NOT GIVEN|NOT GIVEN|FALSE|TRUE|TRUE|NOT GIVEN|FALSE|FALSE|correct|conversation|filter|fresh|flavour / flavor|bitter|day|issues|(relevant) information|(meeting) agenda|conflicts|tension|social activity|vii|iii|i|vi|viii|v|B|C|B|C|G|E|B",
        "D|B|A|C|F|C|E|G|FALSE|NOT GIVEN|NOT GIVEN|FALSE|TRUE|FALSE|highlight|details|insights|samples|questionnaire|authentic|routine|dress code|personalities|conversation starters|goals|open mind|improvements|D|C|A|D|C|B|A|D|C|A|grounds|referees|prejudice",
    ],
    17: [
        "C|G|D|F|A|FALSE|TRUE|FALSE|NOT GIVEN|TRUE|eye-catching landmark|cemetery|(unique) (Chinese) architecture|(self-booking) computer terminals / terminals for self-booking|personality|dull|qualities|viewpoints|colleague|clichés / cliches|stationery|photos|locations|labels|requirement|focus|tasks|iv|vi|iii|i|viii|explosion|shaft|sparks|manpower|A|B|D|D",
        "B|E|A|D|C|TRUE|FALSE|NOT GIVEN|TRUE|NOT GIVEN|FALSE|TRUE|NOT GIVEN|FALSE|position|partitions|windows|heat|planning|choice|record|length|steps|feet|cones|sign|blocks|C|G|A|B|C|D|A|B|D|back layout|journalist|river|fish",
        "E|D|A|D|E|C|FALSE|NOT GIVEN|TRUE|FALSE|TRUE|NOT GIVEN|FALSE|NOT GIVEN|informal|manual|solution|colleague|senior|mediation|3 / three|operator|physical|evenings|self-employed|geography|mechanical|vi|vii|ii|i|iv|v|C|B|A|popping|pullers|candle|arm",
        "E|B|D|A|C|B|C|TRUE|TRUE|FALSE|NOT GIVEN|FALSE|NOT GIVEN|FALSE|tools|procedure|strength|rope|footpath|pedestrians|chippings|narrow|cutting chart|tradespeople|(reinforcing) steel|cost-effective|inconvenience|vets|pairs|food|hibernation|D|A|B|B|D|E|A|C|D",
    ],
}
# Passage start/end pages and the number of heading lines on the first page.
PASSAGES = {
    15: [
        [(16,16,1),(18,18,1),(20,20,1),(22,22,1),(24,25,1)],
        [(38,38,1),(40,40,1),(42,42,1),(44,44,2),(47,48,1)],
        [(60,60,1),(62,62,1),(64,64,2),(66,66,1),(68,69,1)],
        [(82,82,1),(84,84,1),(86,86,1),(88,88,1),(90,91,1)],
    ],
    16: [
        [(19,19,2),(21,21,1),(23,23,1),(25,25,1),(28,29,1)],
        [(41,41,1),(43,43,1),(45,45,2),(47,47,1),(49,50,1)],
        [(63,63,2),(65,65,1),(67,67,1),(69,69,1),(72,73,1)],
        [(85,85,1),(87,87,1),(89,89,1),(91,91,1),(93,94,1)],
    ],
    17: [
        [(17,17,1),(19,19,1),(21,21,2),(23,23,1),(25,25,1),(28,29,1)],
        [(41,41,1),(43,43,1),(45,45,2),(47,47,1),(49,50,1)],
        [(63,63,1),(65,65,1),(67,67,1),(69,69,1),(72,73,1)],
        [(85,85,1),(87,87,1),(89,89,1),(91,91,1),(93,94,1)],
    ],
}
# (question page, first, last, passage index, kind, optional number of choices / word limit)
GROUPS = {
    15: [
        [(17,1,6,0,"tf"),(19,7,14,1,"match",5),(21,15,22,2,"notes",5),(23,23,27,3,"sentence",4),(26,28,31,4,"mc"),(27,32,36,4,"match",7),(28,37,40,4,"summary",1)],
        [(39,1,6,0,"tf"),(41,7,14,1,"match",5),(43,15,20,2,"table",1),(45,21,27,3,"notes",1),(46,28,33,4,"head",7),(49,34,37,4,"mc"),(50,38,40,4,"summary",1)],
        [(61,1,7,0,"tf"),(63,8,14,1,"match",6),(65,15,20,2,"sentence",1),(67,21,27,3,"match",7),(70,28,30,4,"mc"),(71,31,35,4,"summary",1),(72,36,40,4,"list",4)],
        [(83,1,7,0,"match",6),(85,8,14,1,"tf"),(87,15,20,2,"sentence",1),(89,21,27,3,"notes",1),(92,28,32,4,"summary",1),(93,33,37,4,"list",7),(94,38,40,4,"mc")],
    ],
    16: [
        [(20,1,6,0,"match",5),(22,7,14,1,"tf"),(24,15,20,2,"table",1),(26,21,27,3,"sentence",2),(27,28,34,4,"head",8),(30,35,37,4,"mc"),(31,38,40,4,"summary",1)],
        [(42,1,7,0,"tf"),(44,8,14,1,"match",8),(46,15,20,2,"notes",1),(48,21,27,3,"sentence",1),(51,28,32,4,"mc"),(52,33,36,4,"list",7),(53,37,40,4,"summary",2)],
        [(64,1,5,0,"match",5),(66,6,14,1,"tf"),(68,15,22,2,"notes",1),(70,23,27,3,"flow",2),(71,28,33,4,"head",8),(74,34,36,4,"mc"),(75,37,40,4,"list",7)],
        [(86,1,8,0,"match",7),(88,9,14,1,"tf"),(90,15,20,2,"sentence",1),(92,21,27,3,"notes",2),(95,28,31,4,"mc"),(96,32,37,4,"list",4),(97,38,40,4,"summary",1)],
    ],
    17: [
        [(18,1,5,0,"list",8),(20,6,10,1,"tf"),(22,11,14,2,"sentence",3),(24,15,20,3,"sentence",1),(26,21,27,4,"notes",1),(27,28,32,5,"head",8),(30,33,36,5,"summary",1),(31,37,40,5,"mc")],
        [(42,1,5,0,"match",5),(44,6,14,1,"tf"),(46,15,20,2,"notes",1),(48,21,27,3,"sentence",1),(51,28,32,4,"match",7),(52,33,36,4,"mc"),(53,37,40,4,"summary",2)],
        [(64,1,6,0,"match",5),(66,7,14,1,"tf"),(68,15,21,2,"flow",0),(70,22,27,3,"sentence",1),(71,28,33,4,"head",7),(74,34,36,4,"mc"),(75,37,40,4,"summary",1)],
        [(86,1,7,0,"match",6),(88,8,14,1,"tf"),(90,15,21,2,"flow",1),(92,22,27,3,"table",2),(95,28,31,4,"summary",1),(96,32,36,4,"mc"),(97,37,40,4,"list",5)],
    ],
}
REFERENCES = {15: [(p,) for p in range(129, 137)],
              16: [(132,), (133,134), (135,), (136,), (137,138), (139,), (140,), (141,)],
              17: [(132,), (133,), (134,), (135,), (136,), (137,138), (139,), (140,141)]}
COMPLETION = {"table":"Table completion","sentence":"Sentence completion","notes":"Note completion",
              "summary":"Summary completion","flow":"Flow-chart completion"}
TRUTH = ["TRUE", "FALSE", "NOT GIVEN"]
WORD_LIMITS = {
    0: "ONE WORD AND/OR A NUMBER",
    1: "ONE WORD ONLY",
    2: "NO MORE THAN TWO WORDS",
    3: "NO MORE THAN THREE WORDS",
    4: "NO MORE THAN TWO WORDS AND/OR A NUMBER",
    5: "NO MORE THAN THREE WORDS AND/OR A NUMBER",
}
WRITING_START = {15: 29, 16: 32, 17: 32}


def original(page, scale=1.55):
    sheet = document[page-1]
    return base64.b64encode(sheet.get_pixmap(matrix=fitz.Matrix(scale,scale),
                            colorspace=fitz.csGRAY).tobytes("jpeg", jpg_quality=81)).decode()


def ocr(page, mode):
    cache = args.ocr_cache / (f"{page}.txt" if mode == 3 else f"{page}-{mode}.txt") if args.ocr_cache else None
    if cache and cache.exists():
        return cache.read_text()
    with fitz.open(args.pdf) as pdf:
        image = pdf[page-1].get_pixmap(dpi=230, colorspace=fitz.csGRAY).tobytes("png")
    value = subprocess.check_output(["tesseract", "stdin", "stdout", "--psm", str(mode),
                                    "-c", "preserve_interword_spaces=1"], input=image,
                                    stderr=subprocess.DEVNULL, env={**os.environ,"OMP_THREAD_LIMIT":"1"}).decode()
    if cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(value)
    return value


def cleaned(value):
    return [line.rstrip() for line in value.splitlines()
            if not re.fullmatch(r"\s*(?:Reading|Writing|Test\s*[1-4lI]|\d+)\s*", line, re.I)
            and not re.search(r"\b[pP][.J-]\s*\d{3}\s*(?:\d{1,2}\s*)?$", line)]


def tidy(text):
    text = " ".join(text.split())
    text = re.sub(r"\s+([,.?!;:])", r"\1", text)
    for old, new in [(" 一 "," – "),(" ,","'"),("you,re","you’re"),("if s","it’s"),("ifs important","it’s important"),
                     ("lace-pedilar","lace-pedlar"),("Fernando's","Ferrando's"),("halfa ","half a "),(" | "," I "),("Introductio n","Introduction")]:
        text = text.replace(old,new)
    return text


def paragraphs(lines):
    blocks, current = [], []
    for line in lines:
        s = line.strip()
        if not s or re.match(r"^(?:[A-H]\s{2,}|[•¢]\s+)", s):
            if current:
                blocks.append(tidy(" ".join(current)))
                current = []
        if s:
            current.append(s.replace("¢ ", "• ", 1) if s.startswith("¢ ") else s)
    if current:
        blocks.append(tidy(" ".join(current)))
    return blocks


# The scanned edition places these letters in the margin. OCR otherwise drops them.
SECTION_STARTS_17 = {
    28: ("A", ("Coal has been used", "The simplest solution", "By about 1810")),
    29: ("D", ("As the leading chemist", "But in fact, the real inventor")),
    41: ("A", ("Aynho Properties", "Danesdale Agency", "Jakesford Properties", "Kasama Letting", "Leftfield Letting")),
    49: ("A", ("On October 20", "At first, when asked", "Fosbury explained that when", "In this way, the Flop")),
    50: ("E", ("What did Fosbury think", "But completing the Flop", "Fosbury explains how he came")),
    63: ("A", ("Grove Mill", "Blackhill Trail", "Fern Way", "Bay Red Valley", "Brownwater Trail")),
    72: ("A", ("In the north of England", "We meet at his farm", "Westwood’s farm produces")),
    73: ("D", ("There are certainly simpler", "In Westwood’s 1920s", "So how was this arcane")),
    85: ("A", ("Perry Forest", "Pugsley Beach", "Marston Hall", "Craven Discovery", "Shelford Family", "Garston Park")),
}


SECTION_STARTS_15 = {
    18: ("A", ("Ezy Rice Cooker", "Family Rice Cooker", "Mini Rice Cooker", "VPN Rice Cooker", "S16 Rice cooker")),
    24: ("A", ("On January 24", "Though Marshall and Sutter", "As news spread")),
    25: ("D", ("How did all these", "Another way was to use", "After 1850", "Though gold mining continued")),
    40: ("A", ("Whittlesey Museum", "Octavia Hill’s Birthplace", "Chatteris Museum", "March and District Museum", "Wisbech and Fenland")),
    47: ("A", ("Humans have been eating", "One major problem", "‘Even with armed guards", "Paso Pacifico’s solution")),
    48: ("E", ("Sea turtles on average", "To date, Paso Pacifico")),
    62: ("A", ("Logitech K120", "Cherry MX 3.0 Keyboard", "Logitech K780", "Microsoft Sculpt Ergonomic", "Microsoft Universal Bluetooth", "Corsair Strafe RGB")),
    66: ("A", ("Make sure you know", "You should expect", "It can be a shock", "All employers", "When | worked", "Don't try to do", "Starting a new job is")),
    82: ("A", ("A new dual-purpose", "Funding for the cycle", "Annie Newcome", "Marshbrook Country Park is", "Although the path", "Further information")),
}


def passage_lines(page, scans):
    lines = cleaned(scans.get((page,3), pages[page]))
    sections = {15: SECTION_STARTS_15, 17: SECTION_STARTS_17}.get(book, {})
    if book == 15:
        lines = [re.sub(r"^\s*[e©¢]\s+(?:[—_]+\s*)?", "• ", line) for line in lines]
        lines = [line.replace("hasnt arrived", "hasn’t arrived").replace("youre self-employed", "you’re self-employed") for line in lines]
    if book == 15 and page == 47:
        lines = [re.sub(r"^([A-D])(?:[ _=]+)(?=\S)", "", line) for line in lines]
    if page in sections:
        first, starts = sections[page]
        labels = dict(zip(starts, LETTERS[LETTERS.index(first):]))
        seen = set()
        corrected = []
        for line in lines:
            text = line.strip()
            if text in LETTERS:
                continue
            for prefix, letter in labels.items():
                if text.startswith(prefix):
                    seen.add(prefix)
                    line = f"{letter}    {text}"
                    break
            corrected.append(line)
        assert seen == set(starts), (page, set(starts) - seen)
        lines = corrected
    return lines


def passage(spec, scans):
    first, last, headings = spec
    lines = passage_lines(first, scans)
    if (book, first) in {(15,47),(16,28),(16,72),(17,28),(17,72)}:
        start = next(i for i, line in enumerate(lines) if line.strip())
    else:
        start = next(i for i, line in enumerate(lines) if re.match(r"\s*Read the text", line, re.I)) + 1
    trimmed = lines[start:]
    header_lines = [i for i, line in enumerate(trimmed) if line.strip()][:headings]
    title = tidy(" ".join(trimmed[i] for i in header_lines))
    body = trimmed[header_lines[-1]+1:]
    for page in range(first+1,last+1):
        body.extend(["", *passage_lines(page, scans)])
    blocks = paragraphs(body)
    if book == 15 and first in {24,90}:
        continuations = ("the most significant", "show many of", "cubs which", "thought to be", "is a clear example",
                         "subjected to", "in their brains", "and understanding")
        merged = []
        for block in blocks:
            if merged and block.startswith(continuations):
                merged[-1] += " " + block
            else:
                merged.append(block)
        blocks = merged
    return {"title":title, "blocks":blocks, "pages":[first,last]}


def accepted(key):
    if key == "3 / three metres / meters":
        return [key, "3", "three", "3 metres", "3 meters", "three metres", "three meters"]
    if key == "doctor’s letter":
        return [key, "doctor's letter"]
    variants = []
    for alternative in key.split(" / "):
        options = [alternative]
        while any("(" in variant for variant in options):
            options = [choice for variant in options for choice in
                       ([re.sub(r"\([^)]*\)\s*", "",variant,count=1),
                         re.sub(r"\(([^)]*)\)",r"\1",variant,count=1)] if "(" in variant else [variant])]
        variants.extend(tidy(variant) for variant in options)
    return list(dict.fromkeys([*variants,key]))


def numbered(lines, first, last, kind):
    items = {}
    current = option = None
    started = False
    options = {}
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if re.match(r"^List\s+of\b", line, re.I) or re.match(r"^List\s*[oO0。]f\b",line):
            current = None
            started = True
            continue
        if match := re.match(r"^(\d{1,2})[.)]?\s+(\S.*)", line):
            n = int(match[1])
            if n == first or (started and n == first+len(items)):
                if n in items:
                    return {}, {}
                current, option, started = n, None, True
                items[n] = {"text":match[2], "options":{}}
                continue
        if not started:
            continue
        if match := re.match(r"^([A-H]|i{1,3}|iv|vi{0,3})[.)]?\s+(\S.*)",line):
            label, text = match.groups()
            if kind == "mc" and current is not None and label in "ABCD" and (re.match(r"^[A-D][.)]?\s{2,}",line) or label == chr(65+len(items[current]["options"]))):
                option = label
                items[current]["options"][label] = text
                continue
            if kind in {"head","list"} and label in (ROMAN if kind == "head" else LETTERS):
                options[label] = text
                current = None
                continue
        if current is not None and not re.search(r"(?:p\.|answer sheet)\s*\d",line,re.I):
            if option:
                items[current]["options"][option] += " " + line
            else:
                items[current]["text"] += " " + line
    return items, options


BLANK = re.compile(r"(?=[.…· ]*[.…·][.…· ]*[.…·][.…· ]*[.…·])[.…· ]+")


def question_group(spec, key, scans):
    page, first, last, passage_id, kind, *arg = spec
    amount = arg[0] if arg else 0
    source = scans.get((page,6),pages[page])
    if book in {15, 17}:
        markers = "_~—=" if book == 15 else "_~—"
        source = re.sub(rf"(?m)^([A-H]|i{{1,3}}|iv|vi{{0,3}})[ ]*[{markers}]+[ {markers}]*", r"\1    ", source)
    if book == 15:
        for old, new in [("areference","a reference"),("amention","a mention"),("acontrast","a contrast"),
                         ("awarning","a warning"),("SectionA","Section A"),("‘It may","It may"),
                         ("B- Arocker","B A rocker"),("B- may","B may"),("Bare heavier","B are heavier"),
                         ("Brun long","B run long"),("Itis in","It is in"),("alot of","a lot of"),
                         ("Itillustrates","It illustrates")]:
            source = source.replace(old, new)
    if book == 17:
        source = source.replace("41 External applicants", "11 External applicants")
        source = source.replace("Bas animal feed.", "B as animal feed.").replace("Ba public who", "B a public who")
        source = source.replace("Acontroversy", "A controversy").replace("Anew danger", "A new danger")
        source = source.replace("Ademand", "A demand").replace("Along-standing", "A long-standing")
        source = source.replace("Anincreasing", "An increasing").replace("€xternal", "External")
        source = source.replace("areference", "a reference").replace("Itled", "It led").replace("Itis", "It is")
        source = source.replace("lan White", "Ian White").replace("howchanges", "how changes").replace("ageneral", "a general")
        source = source.replace("anincrease", "an increase").replace("awillingness", "a willingness")
    lines = cleaned(source)
    instruction = ""
    figure = False
    worksheet = []
    items, labels = numbered(lines,first,last,kind)
    ids = list(range(first,last+1))
    choices = []
    if kind == "tf":
        label, instruction, choices = "True / False / Not Given", "Do the statements agree with the information in the text?", TRUTH
    elif kind == "mc":
        label, instruction, choices = "Multiple choice", "Choose the correct letter, A, B, C or D.", list("ABCD")
    elif kind == "head":
        label, instruction, choices = "Matching headings", "Choose the correct heading for each section or paragraph.", ROMAN[:amount]
    elif kind in {"match","list"}:
        label, instruction, choices = "Matching", f"Choose the correct letter, A–{LETTERS[amount-1]}.", list(LETTERS[:amount])
    else:
        label = COMPLETION[kind]
        instruction = f"Choose {WORD_LIMITS[amount]} from the text for each answer."
    if kind in {"table","flow"}:
        figure = True
    elif kind in {"notes","summary"}:
        if book == 16:
            # Keep the original narrative and inline numbered blanks whenever the text layer supports them.
            start = next((i for i,line in enumerate(lines) if re.search(r"your answer sheet",line,re.I)), -1)
            body = [line.strip() for line in lines[start+1:] if line.strip()]
            if body:
                text = " ".join(body[1:]) if kind == "summary" else "\n".join(body[1:])
                for n in ids:
                    text = re.sub(rf"(?<!\d){n}[ .…·]{{3,}}", f"[[{n}]] ",text)
                text = re.sub(r"(\[\[\d+\]\])\s+(?=[A-Z][a-z]+\s)", r"\1. ", text) if kind == "summary" else text
                if re.findall(r"\[\[(\d+)\]\]",text) == list(map(str,ids)):
                    worksheet = [body[0], *(tidy(block) for block in text.splitlines())]
        figure = not worksheet
    elif list(items) != ids:
        figure = True
    elif kind == "mc" and any(list(item["options"]) != choices for item in items.values()):
        figure = True
    elif kind in {"head","list"} and set(labels) != set(choices):
        figure = True
    elif kind == "sentence":
        for item in items.values():
            value, count = BLANK.subn(" [[blank]] ",item["text"])
            if count != 1:
                figure = True
            item["text"] = value
    if figure:
        items = {}
        labels = {}
    if choices:
        assert all(key[n-1] in choices for n in ids), (book,page,choices,key)
    questions = []
    for n in ids:
        item = items.get(n,{})
        answer = key[n-1]
        questions.append({"id":n,"text":tidy(item.get("text","")),"answer":answer,
                          "accepted":accepted(answer),"leads":[],
                          "options":{k:tidy(v) for k,v in item.get("options",{}).items()}})
    group = {"passage":passage_id,"first":first,"last":last,"page":page,
             "kind":label,"instruction":instruction,"choices":choices,"questions":questions,
             "choiceLabels":labels,"worksheet":worksheet}
    if figure:
        group["sourceImage"] = original(page,1.8)
    return group


def writing(test, scans):
    result = []
    for task in (1,2):
        page = WRITING_START[book] + test*22 + task-1
        source = scans.get((page,3),pages[page])
        lines = cleaned(source)
        start = next(i for i,line in enumerate(lines) if f"WRITING TASK {task}" in line.upper())
        body = lines[start:]
        while body and (not body[-1].strip() or re.match(r"^\s*[^a-zA-Z]*(?:p[. ]?[\dtaJ]+[^a-zA-Z]*)?$", body[-1])):
            body.pop()
        if book == 15:
            if task == 2:
                body = body[:next(i for i,line in enumerate(body) if "Write at least 250 words" in line)+1]
            elif page in {29,73,95}:
                body = body[:next(i for i,line in enumerate(body) if line.startswith("Begin your letter"))+1] + ["", "Dear …,"]
            else:
                body = body[:next(i for i,line in enumerate(body) if line.startswith("Dear Sir"))+1]
            body = [line.replace("HelShe", "He/She").replace("voluntary!", "voluntary/").replace("voluntarylunpaid", "voluntary/unpaid") for line in body]
        if book == 17 and page == 32:
            body = body[:next(i for i,line in enumerate(body) if line.startswith("Begin your letter"))+1] + ["", "Dear …"]
        prompt = "\n".join(re.sub(r"^e (?=[a-z])", "• ", line.strip()) for line in body).strip()
        prompt = re.sub(r"\n{3,}","\n\n",prompt)
        pages_ref = REFERENCES[book][test*2+task-1]
        result.append({"prompt":prompt,"minimum":[150,250][task-1],"page":page,
                       "reference":original(pages_ref[0]),
                       "extraReferences":[original(p) for p in pages_ref[1:]]})
    return result


work = set()
if book in {15, 17}:
    for specs in PASSAGES[book]:
        for first,last,_ in specs:
            work.update((p,3) for p in range(first,last+1))
    for specs in GROUPS[book]:
        work.update((spec[0],6) for spec in specs if spec[4] not in {"table","flow","notes","summary"})
    work.update((WRITING_START[book]+22*t+j,3) for t in range(4) for j in range(2))
else:
    work.update((p,3) for p in (93,94))
with ThreadPoolExecutor(max_workers=6) as pool:
    scans = dict(zip(sorted(work), pool.map(lambda pair: ocr(*pair),sorted(work))))

for index, specs in enumerate(PASSAGES[book]):
    key = KEYS[book][index].split("|")
    assert len(key)==40
    groups = [question_group(spec,key,scans) for spec in GROUPS[book][index]]
    data = {"passages":[passage(spec,scans) for spec in specs],
            "groups":groups,"writing":writing(index,scans)}
    (directory / f"test-{index+1}.json").write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
    print(f"{book} Test {index+1}: original-layout pages {[g['page'] for g in groups if 'sourceImage' in g]}")
