"""Click-based CLI for reddit-pain-workflow."""

import json
import sys

import click

from reddit_pain_workflow import (
    DEFAULT_SUBREDDITS,
    scan,
    format_report,
)


@click.command()
@click.option("--subreddit", help="Scan a specific subreddit")
@click.option("--cron", is_flag=True, help="Cron-friendly output (JSON)")
@click.option(
    "--report",
    type=click.Choice(["markdown", "json"]),
    default="markdown",
    help="Report format",
)
@click.option("--limit", type=int, default=25, help="Posts per subreddit")
@click.option("--output", help="Save report to file")
def main(subreddit, cron, report, limit, output):
    """Reddit Pain Workflow — scan developer subreddits for pain signals."""
    subs = [subreddit] if subreddit else DEFAULT_SUBREDDITS
    results = scan(subs, limit)

    if cron:
        click.echo(
            json.dumps(
                {
                    "scan_time": results["timestamp"],
                    "signals_found": len(results["pain_signals"]),
                    "top_signal": (
                        results["pain_signals"][0]
                        if results["pain_signals"]
                        else None
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif report == "json":
        click.echo(
            json.dumps(results, ensure_ascii=False, indent=2)
        )
    else:
        report_text = format_report(results)
        click.echo(report_text)
        if output:
            with open(output, "w") as f:
                f.write(report_text)
            click.echo(f"\nSaved to {output}")
