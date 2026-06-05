"""GitHub Trending CLI — entry point with all feature flags."""

from __future__ import annotations

import argparse
import os
import sys
import time
import webbrowser
from datetime import datetime, timezone

from rich.console import Console

import github_api
import scraper
import utils

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="🔥 GitHub Trending CLI — Fetch trending repositories.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # --- Filters ---
    parser.add_argument(
        "--duration",
        choices=["day", "week", "month", "year"],
        default="week",
        help="Time range for repository creation.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of repositories to display (1–100).",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Filter by programming language (e.g. python, rust, go).",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Filter by topic (e.g. machine-learning, cli, devops).",
    )
    parser.add_argument(
        "--sort",
        choices=["stars", "forks", "updated"],
        default="stars",
        help="Sort repositories by field.",
    )
    parser.add_argument(
        "--min-stars",
        type=int,
        default=None,
        help="Minimum star count to include.",
    )

    # --- Source ---
    parser.add_argument(
        "--source",
        choices=["api", "trending"],
        default="api",
        help="Data source: 'api' (GitHub Search API) or 'trending' (scrape GitHub Trending page).",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Keyword search in repo names and descriptions.",
    )

    # --- Auth ---
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="GitHub personal-access token (or set GITHUB_TOKEN env var).",
    )

    # --- Cache ---
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass the local results cache.",
    )

    # --- Output ---
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Export results to a file (.json or .csv).",
    )

    # --- Modes ---
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Browse results interactively and open repos in browser.",
    )
    parser.add_argument(
        "--watch",
        type=int,
        default=None,
        metavar="SECONDS",
        help="Re-fetch every N seconds (Ctrl+C to stop).",
    )
    parser.add_argument(
        "--open",
        type=int,
        default=None,
        metavar="N",
        help="Instantly open repo #N in your browser.",
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        help="Show notifications for new trending repos since last check.",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Start the Flask web UI instead of the CLI.",
    )

    args = parser.parse_args()

    # --- Web mode ---
    if args.web:
        _start_web_server(args)
        return

    # --- Validation ---
    if args.limit < 1 or args.limit > 100:
        console.print("[red]Error:[/red] --limit must be between 1 and 100.")
        sys.exit(1)

    if args.watch and args.watch < 10:
        console.print("[red]Error:[/red] --watch interval must be >= 10 seconds.")
        sys.exit(1)

    if args.min_stars is not None and args.min_stars < 0:
        console.print("[red]Error:[/red] --min-stars must be >= 0.")
        sys.exit(1)

    try:
        if args.watch:
            _watch_loop(args)
        else:
            _single_run(args)
    except KeyboardInterrupt:
        console.print("\n[dim]Goodbye![/dim]")
        sys.exit(0)


def _start_web_server(args: argparse.Namespace) -> None:
    """Import and launch the Flask web UI."""
    if args.token:
        os.environ["GITHUB_TOKEN"] = args.token

    console.print("\n[bold bright_magenta]🚀 Starting GitHub Trending Web UI...[/bold bright_magenta]")
    console.print("[dim]Open http://127.0.0.1:5000 in your browser.[/dim]\n")

    import web  # noqa: E402 — lazy import so Flask is optional for CLI

    webbrowser.open("http://127.0.0.1:5000")
    web.run_server()


def _fetch_repos(args: argparse.Namespace) -> list[dict]:
    """Fetch repos from the selected source, using cache unless --no-cache."""
    if args.source == "trending":
        return _fetch_repos_trending(args)

    # Default: GitHub Search API
    if not args.no_cache:
        cached = utils.read_cache(args.source, args.duration, args.limit, args.language)
        if cached is not None:
            console.print("[dim](using cached results)[/dim]")
            return cached

    repos = github_api.fetch_trending_repos(
        duration=args.duration,
        limit=args.limit,
        language=args.language,
        topic=args.topic,
        sort=args.sort,
        min_stars=args.min_stars,
        token=args.token,
        query_keyword=args.query,
    )

    if not args.no_cache:
        utils.write_cache(repos, args.source, args.duration, args.limit, args.language)

    # Apply keyword filter on API results
    if args.query:
        q_lower = args.query.lower()
        repos = [
            r for r in repos
            if q_lower in (r.get("full_name") or "").lower()
            or q_lower in (r.get("description") or "").lower()
        ]

    return repos


def _fetch_repos_trending(args: argparse.Namespace) -> list[dict]:
    """Fetch repos via the GitHub Trending scraper with API fallback."""
    since_map = {
        "day": "daily",
        "week": "weekly",
        "month": "monthly",
        "year": "monthly",
    }
    since = since_map.get(args.duration, "daily")

    if not args.no_cache:
        cached = utils.read_cache(args.source, args.duration, args.limit, args.language)
        if cached is not None:
            console.print("[dim](using cached results)[/dim]")
            return cached

    repos = scraper.fetch_trending_with_fallback(
        since=since,
        language=args.language,
        limit=args.limit,
        query=args.query,
        token=args.token,
        topic=args.topic,
        sort=args.sort,
        min_stars=args.min_stars,
    )

    if not args.no_cache and repos:
        utils.write_cache(repos, args.source, args.duration, args.limit, args.language)

    return repos


def _display_repos(args: argparse.Namespace, repos: list[dict]) -> None:
    """Display repos as a rich table with links."""
    console.print()
    source_label = "Trending Page" if args.source == "trending" else "Search API"
    console.print(utils.build_header_panel(
        args.duration, args.limit, args.language,
        topic=args.topic, sort=args.sort, min_stars=args.min_stars,
        source=source_label, query=args.query,
    ))
    console.print()

    table = utils.build_rich_table(repos)
    console.print(table)

    # Links
    console.print()
    console.print("[bold]🔗 Links:[/bold]")
    for i, repo in enumerate(repos, start=1):
        name = repo.get("full_name", "N/A")
        url = repo.get("html_url", f"https://github.com/{name}")
        stars_today = repo.get("stars_today", 0)
        today_badge = f"  [yellow](+{stars_today} today)[/yellow]" if stars_today else ""
        console.print(f"  [dim]{i:>2}.[/dim] [cyan]{name}[/cyan] → [link={url}]{url}[/link]{today_badge}")
    console.print()


def _single_run(args: argparse.Namespace) -> None:
    """Execute a single fetch-and-display cycle."""
    try:
        repos = _fetch_repos(args)
    except github_api.GitHubAPIError as e:
        console.print(f"\n[red]❌ Error:[/red] {e}", highlight=False)
        sys.exit(1)

    if not repos:
        console.print("[yellow]No trending repositories found for the given criteria.[/yellow]")
        sys.exit(0)

    # Notifications
    if args.notify:
        utils.check_new_repos(repos, console)

    _display_repos(args, repos)

    # Quick open
    if args.open is not None:
        idx = args.open
        if 1 <= idx <= len(repos):
            url = repos[idx - 1].get("html_url", "")
            console.print(f"[dim]Opening {url} in browser...[/dim]")
            webbrowser.open(url)
        else:
            console.print(f"[red]--open: number must be between 1 and {len(repos)}.[/red]")

    # Export
    if args.output:
        try:
            utils.export_results(repos, args.output)
            console.print(f"[green]✅ Exported to {args.output}[/green]")
        except ValueError as e:
            console.print(f"[red]❌ Export error:[/red] {e}")
            sys.exit(1)

    # Interactive mode
    if args.interactive:
        _interactive_browse(repos)


def _interactive_browse(repos: list[dict]) -> None:
    """Let the user pick repos by number and view details or open in browser."""
    console.print("[bold bright_magenta]📊 Interactive Mode[/bold bright_magenta]")
    console.print(
        "[dim]Commands: [bold]<number>[/bold] → details  │  "
        "[bold]o <number>[/bold] → open in browser  │  "
        "[bold]q[/bold] → quit[/dim]\n"
    )

    while True:
        try:
            choice = console.input("[bold]› [/bold]").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice in ("q", "quit", "exit", ""):
            break

        # Open in browser
        if choice.startswith(("o ", "open ")):
            parts = choice.split()
            if len(parts) == 2 and parts[1].isdigit():
                idx = int(parts[1])
                if 1 <= idx <= len(repos):
                    url = repos[idx - 1].get("html_url", "")
                    console.print(f"[dim]Opening {url} ...[/dim]")
                    webbrowser.open(url)
                    continue
            console.print("[red]Usage: o <number>[/red]")
            continue

        # View details
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(repos):
                utils.show_repo_detail(repos[idx - 1], console)
                continue
            console.print(f"[red]Number must be between 1 and {len(repos)}.[/red]")
            continue

        console.print("[dim]Enter a number, 'o N', or 'q'.[/dim]")


def _watch_loop(args: argparse.Namespace) -> None:
    """Re-fetch and display every --watch seconds."""
    interval = args.watch
    args.no_cache = True

    while True:
        os.system("clear" if os.name != "nt" else "cls")
        now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        console.print(
            f"[dim]Last updated: {now}  │  "
            f"Refreshing every {interval}s  │  Ctrl+C to stop[/dim]"
        )

        try:
            repos = _fetch_repos(args)
        except github_api.GitHubAPIError as e:
            console.print(f"\n[red]❌ Error:[/red] {e}", highlight=False)
            console.print(f"[dim]Retrying in {interval}s...[/dim]")
            time.sleep(interval)
            continue

        if repos:
            if args.notify:
                utils.check_new_repos(repos, console)
            _display_repos(args, repos)
        else:
            console.print("[yellow]No results found.[/yellow]")

        time.sleep(interval)


if __name__ == "__main__":
    main()
