#!/usr/bin/env python3
"""Reddit Pain Workflow — scan developer subreddits for pain signals.

Usage:
    python reddit_pain_workflow.py                    # scan default subs
    python reddit_pain_workflow.py --subreddit cursor  # scan specific sub
    python reddit_pain_workflow.py --cron              # cron-friendly output
    python reddit_pain_workflow.py --report markdown   # generate report

No Reddit API key needed — uses public JSON API.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError

# Subreddits known for developer pain discussions
DEFAULT_SUBREDDITS = [
    "programming", "webdev", "cursor", "ClaudeAI", "OpenAI",
    "MachineLearning", "vscode", "python", "devops", "selfhosted"
]

PAIN_KEYWORDS = [
    ("ERROR", r"\b(error|crash|bug|broken|fail|exception)\b"),
    ("UX", r"\b(confus|unclear|hard to use|terrible ui|bad ux)\b"),
    ("PRICE", r"\b(expensive|overpriced|too much|cost|pricing)\b"),
    ("MISSING", r"\b(missing|lack|no way to|can't|cannot|no support)\b"),
    ("DOCS", r"\b(documentation|docs|undocumented|no example|outdated)\b"),
    ("PERF", r"\b(slow|lag|timeout|hangs|stuck|freeze)\b"),
    ("LIMIT", r"\b(limit|rate limit|quota|threshold|cap)\b"),
    ("BREAK", r"\b(broke after|stopped working|regression|downgrade)\b"),
]


def fetch_posts(subreddit: str, limit: int = 25) -> list[dict]:
    """Fetch hot posts from a subreddit using public JSON API."""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    headers = {"User-Agent": "reddit-pain-workflow/1.0 (pain-scanner)"}
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        return data.get("data", {}).get("children", [])
    except URLError:
        return []


def classify_pain(title: str, selftext: str = "", num_comments: int = 0) -> dict | None:
    """Classify a post as pain or not. Returns pain info if painful."""
    text = f"{title} {selftext}".lower()

    # Only posts with engagement (>3 comments) or explicit question marks
    if num_comments < 3 and "?" not in title:
        return None

    matched_categories = []
    all_matches = []
    for category, pattern in PAIN_KEYWORDS:
        matches = re.findall(pattern, text)
        if matches:
            matched_categories.append(category)
            all_matches.extend(matches[:3])

    if not matched_categories:
        return None

    # Score: more categories + more keyword matches = higher pain
    score = len(matched_categories) * 10 + min(len(all_matches) * 2, 20)
    # Boost by comment count
    score += min(num_comments // 5, 15)

    return {
        "categories": matched_categories,
        "score": score,
        "keywords": list(set(all_matches))[:5],
    }


def scan(subreddits: list[str], limit: int = 25) -> dict:
    """Run a full pain scan across subreddits."""
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subreddits_scanned": len(subreddits),
        "total_posts": 0,
        "pain_signals": [],
    }

    for subreddit in subreddits:
        posts = fetch_posts(subreddit, limit)
        results["total_posts"] += len(posts)

        for child in posts:
            post = child["data"]
            title = post.get("title", "")
            selftext = post.get("selftext", "")
            num_comments = post.get("num_comments", 0)
            score = post.get("score", 0)

            pain = classify_pain(title, selftext, num_comments)
            if not pain:
                continue

            results["pain_signals"].append({
                "subreddit": subreddit,
                "title": title[:200],
                "permalink": f"https://reddit.com{post.get('permalink', '')}",
                "comments": num_comments,
                "upvotes": score,
                "pain_score": pain["score"],
                "categories": pain["categories"],
                "keywords": pain["keywords"],
            })

    # Sort by pain score descending
    results["pain_signals"].sort(key=lambda x: (-x["pain_score"], -x["comments"]))
    return results


def format_report(results: dict) -> str:
    """Generate a markdown pain report."""
    signals = results["pain_signals"]
    lines = [
        f"# Reddit Pain Report",
        f"**Generated**: {results['timestamp']}",
        f"**Scanned**: {results['subreddits_scanned']} subreddits, {results['total_posts']} posts",
        f"**Pain Signals**: {len(signals)}",
        "",
        "## 🔥 Top Pain Signals",
        "",
    ]

    # Category breakdown
    cat_counts = {}
    for s in signals:
        for c in s["categories"]:
            cat_counts[c] = cat_counts.get(c, 0) + 1
    lines.append("| Category | Count |")
    lines.append("|---|---|")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {cat} | {count} |")
    lines.append("")

    # Top 10 by pain score
    lines.append("| # | Sub | Title | 💬 | ⬆ | Score | Categories |")
    lines.append("|---|---|---|---|---|---|---|")
    for i, s in enumerate(signals[:10], 1):
        cats = "/".join(s["categories"])
        title_short = s["title"][:50] + ("..." if len(s["title"]) > 50 else "")
        lines.append(
            f"| {i} | r/{s['subreddit']} | {title_short} | {s['comments']} | {s['upvotes']} | {s['pain_score']} | {cats} |"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Reddit Pain Workflow")
    parser.add_argument("--subreddit", help="Scan a specific subreddit")
    parser.add_argument("--cron", action="store_true", help="Cron-friendly output (JSON)")
    parser.add_argument("--report", choices=["markdown", "json"], default="markdown",
                        help="Report format")
    parser.add_argument("--limit", type=int, default=25, help="Posts per subreddit")
    parser.add_argument("--output", help="Save report to file")
    args = parser.parse_args()

    subs = [args.subreddit] if args.subreddit else DEFAULT_SUBREDDITS
    results = scan(subs, args.limit)

    if args.cron:
        print(json.dumps({
            "scan_time": results["timestamp"],
            "signals_found": len(results["pain_signals"]),
            "top_signal": results["pain_signals"][0] if results["pain_signals"] else None,
        }, ensure_ascii=False, indent=2))
    elif args.report == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        report = format_report(results)
        print(report)
        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
