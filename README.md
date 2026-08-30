# Python Web Scraping & Testing (Selenium + pytest)

[![CI](https://github.com/nupolovykh/QA-web-labprojects-python/actions/workflows/ci.yml/badge.svg)](https://github.com/nupolovykh/QA-web-labprojects-python/actions/workflows/ci.yml)

> ⏹️ **Archived Coursework** — Selenium & pytest labs from a university software-testing course

A progression of labs on web-scraping and automated testing in Python: Selenium
basics and page interactions, pytest fundamentals (asserts, parametrization,
fixtures, class-based tests), CI/CD integration, FastAPI + pytest API testing,
HTML test reporting, Locust load testing, and the Page Object Model pattern.

**Tech stack:** Python, Selenium, pytest, FastAPI, Uvicorn, Locust

## Labs

| Lab | Topic | Location | Status | Preview |
|---|---|---|---|---|
| 1-3 | Selenium basics: scraping python.org | [`lab01-03/`](lab01-03) | ✅ working | [sample output](#lab01-03-sample-output) |
| 4 | Scraping VK video listings | [`lab04/`](lab04) | ❌ broken upstream | [old sample](#lab04-sample-output) (site has since moved) |
| 5 | Scraping ci.nsu.ru news with a date filter | [`lab05/`](lab05) | ✅ working | [sample output](#lab05-sample-output) |
| 6 | Context menus and file upload | [`lab06/`](lab06) | ✅ working | <img src="lab06/docs/screenshot.png" width="240" alt="lab06 screenshot"> |
| 7 | Multi-tab/window handling | [`lab07/`](lab07) | ✅ working | [sample output](#lab07-sample-output) |
| 8 | Explicit waits + Google Translate automation | [`lab08/`](lab08) | ⚠️ target unreachable | see [notes](#lab08-notes) |
| 9 | pytest basics: plain asserts | [`lab09/`](lab09) | ✅ working | |
| 10 | pytest parametrize + fixtures | [`lab10/`](lab10) | ✅ working | |
| 11 | pytest + CI (GitHub Actions & Jenkins) | [`lab11/`](lab11) | ✅ working | |
| 12 | FastAPI + Uvicorn API, tested with pytest | [`lab12/`](lab12) | ✅ working | |
| 13 | pytest-html reporting & Locust load testing | [`lab13/`](lab13) | ✅ working | |
| 14 | Page Object Model with Selenium + pytest | [`lab14/`](lab14) | ✅ working | [sample output](#lab14-sample-output) |

Statuses last verified running each lab live inside `.devcontainer/` (real
Chrome + Xvfb, real network) — see commit history for what each fix
addressed. `lab08` and `lab04` depend on external sites this network
couldn't reach or that have since redesigned; that's tracked below per lab,
not treated as a bug in this repo's code.

### lab01-03 sample output

`python-parsing.py` prints what it scrapes from python.org; a real run looks like:

```
<img> src => https://www.python.org/static/img/python-logo.png

<a> href => https://www.python.org/about/
<a> href => https://www.python.org/about/apps/
<a> href => https://www.python.org/about/quotes/
<a> href => https://www.python.org/about/gettingstarted/
<a> href => https://www.python.org/about/help/
...
```

### lab04 sample output

The live site (`vk.com/video`) has since been rebuilt on a different domain
(`vkvideo.ru`) as a client-side-routed SPA with no plain `<a href>` menu
links to scrape, so the script no longer collects anything. This is what
`video_data.csv` looked like from an earlier run, before that migration —
kept as-is rather than regenerated:

| Title | Views | Likes | Creation Date | Channel Name | Subscribers |
|---|---|---|---|---|---|
| КСТАТИ #49 – Отар Кушанашвили, XOLIDAYBOY, ... | 29M views | 39.3K | 1 month ago | VK Видео | 1.1M followers |
| Уезжай, если сможешь. 1 серия | 5.2M views | 4.6K | 20 days ago | Winline | 133K followers |
| Большое шоу 8 сезон. Расширенная версия. | 17.5M views | 22.9K | 3 months ago | Азамат Мусагалиев | 1.4M followers |

### lab05 sample output

`vki-parsing.py` writes every matching news card to `result.txt`; a real run
(940 lines, ~230 news items) starts like:

```
Date: 25.09.2024
Title: О проведении социально-психологического тестирования
Link: https://ci.nsu.ru/news/social-and-psychological-testing/
Image URL: https://ci.nsu.ru/upload/resize_cache/iblock/6c3/.../3036.jpg

Date: 19.09.2024
Title: Опрос для студентов и родителей в рамках независимой оценки качества образования
Link: https://ci.nsu.ru/news/survey-for-students-and-parents/
Image URL: https://ci.nsu.ru/upload/iblock/890/.../Kartinka.png
```

### lab07 sample output

`loading-to-browser.py` joins the titles of 10 randomly-opened Wikipedia
pages, then round-trips that string through base64encode.org. Since the
pages are random, the exact text differs every run — one real run:

```
Легенда об Уленшпигеле Проханов, Ярослав Иванович Королевские казармы Языки
Комор Кернер, Давид Борисович Patrick Beurard-Valdoye Suzanne de Court
Izawa Soul on Ice Robert B. Brewer

0JvQtdCz0LXQvdC00LAg0L7QsSDQo9C70LXQvdGI0L/QuNCz0LXQu9C1INCf0YDQvtGF0LDQvdC+0LIs...
```

### lab08 notes

`work-with-latency.py` targets `culture.ru` (poems) and `translate.google.com`.
`culture.ru` timed out at the TCP level from inside this devcontainer's
network — not a Selenium or markup issue, so there's no output to preview
from here. Worth re-testing from a different network before assuming the
site itself is down.

### lab14 sample output

`ai-tests.py` exercises the same `ci.nsu.ru` news page as `lab05` through a
Page Object Model, asserting on title text and date ranges rather than
writing a file:

```
6 passed in 231.91s (0:03:51)
```

## Install & run

```bash
pip install -r requirements.txt
```

ChromeDriver is managed automatically by [`webdriver-manager`](https://pypi.org/project/webdriver-manager/) —
no manual driver download or path setup needed. In `.devcontainer/`, Xvfb +
a window manager are already running by the time the container starts (see
[`.devcontainer/README.md`](.devcontainer/README.md)), so Selenium labs run
with a plain `python ...` — no `--headless` or extra wrapper needed.

### Selenium scripts

Run directly from the repo root:

```bash
python lab01-03/python-parsing.py   # ✅ working
python lab04/vk-parsing.py          # ❌ target site was rebuilt on a different domain, see lab04 notes above
python lab05/vki-parsing.py         # ✅ working, writes lab05/result.txt
python lab06/loading-to-browser.py  # ✅ working, writes lab06/docs/screenshot.png
python lab07/loading-to-browser.py  # ✅ working
python lab08/work-with-latency.py   # ⚠️ culture.ru unreachable from this devcontainer's network, see lab08 notes above
```

### Plain pytest labs

Test files aren't named to pytest's default discovery pattern
(`test_*.py`), so pass the filename explicitly. Runs fine from the repo root:

```bash
pytest lab09/tests.py -v
pytest lab10/classes.py -v
pytest lab11/tests.py -v
```

### lab12 — FastAPI + pytest (needs the app running first)

```bash
cd lab12
uvicorn main:app --host 0.0.0.0 --port 8000 &
pytest api_tests.py -v
kill %1
```

### lab13 — two independent halves

```bash
# plain pytest + html report
cd lab13/casual_funcs
pytest tests.py -v          # report.html is (re)generated here

# Locust load test
cd lab13/fastapi_funcs
uvicorn main:app --host 0.0.0.0 --port 8000 &
locust -f locustfile.py --headless -u 5 -r 5 --run-time 30s --host http://localhost:8000
kill %1
```

404s on `GET`/`DELETE /user/1` in the Locust report are expected — virtual
users racing each other for the same resource, not a bug.

### lab14 — Page Object Model (must run from its own directory)

`ai-tests.py` imports the local `ci_nsu.py` module, so run it from inside
`lab14/`, not by path from the repo root:

```bash
cd lab14
pytest ai-tests.py -v   # ✅ working, 6 tests, ~4 min (recreates the driver per test)
```

`tests.py` in the same folder is dead code — a class with an `__init__`
constructor and methods not prefixed `test_`, so pytest collects 0 tests
from it. `ai-tests.py` is its working replacement.

Some labs (`lab11`, `lab12`) also ship their own `requirements.txt` for a
minimal, lab-scoped install.

## Documentation

- [Selenium for Python docs](https://selenium-python.readthedocs.io/)
- [pytest docs](https://docs.pytest.org/en/stable/getting-started.html)
- [Selenium + Python questions on Stack Overflow](https://stackoverflow.com/search?q=%5Bpython%5D+and+%5Bselenium%5D)
