# GT Study Room

A browser-based simulator for computer-delivered IELTS General Training Reading and Writing.

## Why I built it

When I started preparing for IELTS General Training, I found fewer practice resources for GT than for Academic. It was especially hard to find a single place that combined past-paper practice with an interface that felt like the computer-delivered test.

Listening and Speaking are shared across the two IELTS formats, while Reading and Writing differ. I built GT Study Room around those two modules so GT candidates can work through practice sets, get used to the interface and review their attempts in one place.

## Features

- Browse practice collections and select a test and module.
- Read passages and answer questions side by side, highlight text and flag questions to revisit.
- Practise with separate Reading and Writing timers.
- Score Reading automatically on submission and review your answers against the answer key.
- Practise Writing Task 1 and Task 2 with live word counts and automatic draft saving. Writing reference answers appear when included in a question pack.
- Track completion and review attempt history in the same browser. Progress is saved locally and is specific to the browser and site address.

## Run locally

Requires **Python 3.9 or later** and a modern browser. The demo needs no third-party Python packages.

```sh
git clone https://github.com/Colin-ff/GT-Study-Room.git
cd GT-Study-Room
python3 build.py
python3 -m http.server 8000 --directory dist
```

Open [localhost:8000](http://localhost:8000/). On Windows, use `py -3` in place of `python3` if needed.

## How to practise

1. Open **Original demo** or a collection you have added locally.
2. Select a test, then choose **Reading** or **Writing**.
3. Start the timer when ready. Use the question or task navigation to move through the module.
4. Select **Submit** to finish the attempt. Open **History** to review past submissions.

The included demo contains original questions and two writing prompts. The separate private practice deployment contains the Cambridge IELTS 14–17 General Training sets.

## Project structure

| Path | Purpose |
| --- | --- |
| `frontend/` | Catalog and exam page templates, styling and browser-side logic |
| `bank/demo-gt/` | Original demo content and an example question-bank format |
| `build.py` | Python builder that turns question-bank JSON into static pages |
| `dist/` | Generated HTML output, served by any static web host |

Scoring, timers and progress run in the browser. The Python builder runs offline before deployment. The app needs no application server, API keys or database.

## Add a local question pack

Use [the demo JSON](bank/demo-gt/test-1.json) as a schema example. Put Cambridge-format practice sets you are authorised to use in `bank/cambridge-<number>-gt/test-<number>.json`, then run `python3 build.py` again. Each Cambridge-format set has 40 consecutive Reading question IDs and two Writing tasks. The build adds detected packs to the catalog.

Question packs may contain passages, answers, accepted variants and image assets. The public checkout includes the original demo. Local Cambridge packs, source PDFs and generated HTML are ignored by Git.
