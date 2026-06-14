# reddit-pain-workflow

> Daily automated pipeline: scan Reddit for developer pain points → extract signals → produce actionable insights

[![Stars](https://img.shields.io/github/stars/minirr890112-byte/reddit-pain-workflow?style=flat-square&color=f6c242)](https://github.com/minirr890112-byte/reddit-pain-workflow/stargazers)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)](https://python.org)

## Why This Exists

The best startup ideas come from real problems. Instead of guessing what developers struggle with, this pipeline scans Reddit daily across 20+ subreddits, extracts pain signals, and produces a ranked report of the most actionable pain points. Feed the output into pain-to-pip-package to build solutions.

## Install

```bash
pip install git+https://github.com/minirr890112-byte/reddit-pain-workflow.git
```

## Usage

```bash
# One-off scan
python scanner.py --subreddits programming,webdev,devops

# Daily cron mode
python scanner.py --daily --output pain_signals.json

# Targeted scan
python scanner.py --keywords "docker","kubernetes","ci/cd"
```

## Pipeline

```
20+ Subreddits → Pain Comment Detection → Sentiment Scoring → JSON Output
      ↓                    ↓                    ↓               ↓
programming,       NLP classifier        Frustration      Ranked by
webdev, devops     (frustration/lost/    /Anger/Despair   severity
AI, python, etc    stuck patterns)       intensity        score
```

## Features

- Scans 20+ developer subreddits (programming, webdev, devops, AI, etc.)
- NLP pain detection: frustration, lost, stuck patterns
- Sentiment scoring with frustration/anger/despair intensity
- Daily cron-ready output
- CSV and JSON export formats

## Ecosystem

| Tool | Description |
|---|---|
| [pain-to-pip-package](https://github.com/minirr890112-byte/pain-to-pip-package) | Turn pain signals into pip packages |
| [task-cost-estimator](https://github.com/minirr890112-byte/task-cost-estimator) | Estimate cost to build the solution |
| [popular-web-designs](https://github.com/minirr890112-byte/popular-web-designs) | Design your tool with real design systems |

## License

MIT © [HermesMade](https://github.com/minirr890112-byte)
