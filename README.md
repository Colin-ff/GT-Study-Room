# G Study Room

A browser-based simulator for computer-delivered IELTS General Training Reading and Writing.

## Use G Study Room

- **Online.** Start practising in your browser with the Cambridge IELTS 14–20 General Training question bank. The site is public and requires no sign-in or installation. [Open the live simulator](https://gstudyroom.space)
- **Local.** Download the repository, build the site with Python, and open it on `localhost`. The included question bank works offline after setup. To get later updates, pull the latest changes and rebuild. [Local setup instructions](#run-locally)

Both versions offer the same Reading and Writing practice features. Each browser stores drafts and progress separately for the live site and `localhost`, so records do not sync between them.

**Access from mainland China.** Some visitors in mainland China have received a Cloudflare block page when opening the site. The block comes from the hosted site's security layer, and the exact rule is unconfirmed. If you encounter it, follow the [local setup instructions](#run-locally) to practise offline.

## Why I built it

When I started preparing for IELTS General Training, I found fewer practice resources for GT than for Academic. It was especially hard to find a single place that combined past-paper practice with an interface that felt like the computer-delivered test.

Listening and Speaking are shared across the two IELTS formats, while Reading and Writing differ. I built G Study Room around those two modules so GT candidates can work through practice sets, get used to the interface and review their attempts in one place.

## Features

- Browse practice collections and select a test and module.
- Read passages and answer questions side by side, highlight text and flag questions to revisit.
- Practise with separate Reading and Writing timers.
- Score Reading automatically on submission and review your answers against the answer key.
- Practise Writing Task 1 and Task 2 with live word counts and automatic draft saving. Writing reference answers appear when included in a question pack.
- Track completion and review attempt history in the same browser. Progress is saved locally and is specific to the browser and site address.

## Run locally

Requires **Python 3.9 or later** and a modern browser. Building the included question bank needs no third-party Python packages.

```sh
git clone https://github.com/Colin-ff/GT-Study-Room.git
cd GT-Study-Room
python3 build.py
python3 -m http.server 8000 --directory dist
```

Open [localhost:8000](http://localhost:8000/). On Windows, use `py -3` in place of `python3` if needed.

## How to practise

1. Open a Cambridge IELTS book or **Original demo**.
2. Select a test, then choose **Reading** or **Writing**.
3. Start the timer when ready. Use the question or task navigation to move through the module.
4. Select **Submit** to finish the attempt. Open **History** to review past submissions.

The question bank contains Cambridge IELTS 14–20 General Training, with four tests per book, 1,120 Reading questions and 56 Writing tasks. The repository also includes a short original demo.

## Project structure

| Path | Purpose |
| --- | --- |
| `frontend/` | Catalog and exam page templates, styling and browser-side logic |
| `bank/` | One JSON file per test with passages, questions, answer keys and available writing references |
| `importers/` | PDF extraction and OCR scripts for the matching Cambridge editions |
| `build.py` | Python builder that turns question-bank JSON into static pages |
| `dist/` | Generated HTML output, served by any static web host |

Scoring, timers and progress run in the browser. The Python builder runs offline before deployment. The app needs no application server, API keys or database.

## Add a question pack

Use [the demo JSON](bank/demo-gt/test-1.json) as a schema example. Put Cambridge-format practice sets you are authorised to use in `bank/cambridge-<number>-gt/test-<number>.json`, then run `python3 build.py` again. Each Cambridge-format set has 40 consecutive Reading question IDs and two Writing tasks. The build adds detected packs to the catalog.

Question packs may contain passages, answers, accepted variants and image assets. Keep existing book and test IDs stable so saved progress remains associated with the right test.

### Import from PDFs

The importers expect the same General Training editions and page order used by this project. They are only needed to regenerate the bank from PDFs. Install [Poppler](https://poppler.freedesktop.org/) and [Tesseract](https://github.com/tesseract-ocr/tesseract) on your system and make sure their commands are on your PATH. Install the Python PDF dependency with `python3 -m pip install PyMuPDF`.

```sh
python3 importers/cambridge14.py sources/cambridge-14-gt.pdf
python3 importers/cambridge15_17.py 15 sources/cambridge-15-gt.pdf
python3 importers/cambridge15_17.py 16 sources/cambridge-16-gt.pdf
python3 importers/cambridge15_17.py 17 sources/cambridge-17-gt.pdf
python3 build.py
```

Review extracted text, blank positions and answer keys before publishing a pack. Git tracks the question-bank JSON. Source PDFs and generated HTML are excluded.

## Deploy

Run `python3 build.py` and publish the contents of `dist/` with a static web host. Keep the same site address across updates to retain access to existing browser progress.
