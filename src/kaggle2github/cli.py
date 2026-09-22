"""
Command-line interface for kaggle2github with rich terminal formatting.
"""

import argparse
import os
import sys
from pathlib import Path

# Ensure package root is in sys.path for direct script execution
pkg_root = Path(__file__).resolve().parent.parent
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from kaggle2github import __version__
from kaggle2github.config import (
    DEFAULT_DOWNLOAD_DIR,
    DEFAULT_REPOS_DIR,
    get_github_token,
    get_kaggle_credentials,
)
from kaggle2github.github_client import GitHubClient
from kaggle2github.kaggle_client import KaggleClient
from kaggle2github.packager import RepoPackager

console = Console()

def cmd_scan(args: argparse.Namespace) -> None:
    """Scan and list public Kaggle notebooks."""
    client = KaggleClient(username=args.user)
    target_user = args.user or client.username

    if not target_user:
        console.print("[bold red]Error:[/bold red] Kaggle username must be specified via --user or KAGGLE_USERNAME.")
        sys.exit(1)

    with console.status(f"[bold green]Fetching public kernels for {target_user}..."):
        try:
            kernels = client.list_kernels(user=target_user, page_size=args.page_size)
        except Exception as e:
            console.print(f"[bold red]Failed to fetch kernels:[/bold red] {e}")
            sys.exit(1)

    if not kernels:
        console.print(f"[yellow]No public kernels found for user '{target_user}'.[/yellow]")
        return

    table = Table(title=f"Kaggle Kernels Catalog for @{target_user} ({len(kernels)} total)")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Slug", style="magenta")
    table.add_column("Title", style="bold white")
    table.add_column("Votes", justify="right", style="green")
    table.add_column("Views", justify="right", style="blue")

    for i, k in enumerate(kernels, start=1):
        table.add_row(str(i), k["slug"], k["title"], str(k["votes"]), str(k["views"]))

    console.print(table)
    console.print(f"\n[green]To download these kernels run:[/green] [bold]kaggle2github download --user {target_user}[/bold]")

def cmd_download(args: argparse.Namespace) -> None:
    """Download kernels from Kaggle into staging directory."""
    client = KaggleClient(username=args.user)
    target_user = args.user or client.username

    if not target_user:
        console.print("[bold red]Error:[/bold red] Kaggle username must be specified via --user or KAGGLE_USERNAME.")
        sys.exit(1)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    slugs = args.slugs
    if not slugs:
        with console.status(f"[bold green]Fetching kernel list for {target_user}..."):
            try:
                kernels = client.list_kernels(user=target_user)
                slugs = [k["slug"] for k in kernels]
            except Exception as e:
                console.print(f"[bold red]Failed to list kernels:[/bold red] {e}")
                sys.exit(1)

    console.print(f"[bold cyan]Downloading {len(slugs)} kernel(s) to '{out_dir}'...[/bold cyan]")
    success_count = 0

    for i, slug in enumerate(slugs, start=1):
        console.print(f"[{i}/{len(slugs)}] Downloading [bold]{slug}[/bold]...")
        try:
            client.download_kernel(slug, output_dir=str(out_dir), user=target_user)
            success_count += 1
        except Exception as e:
            console.print(f"  [red]Failed to download {slug}: {e}[/red]")

    console.print(f"\n[bold green]Download complete![/bold green] Successfully retrieved {success_count}/{len(slugs)} kernels.")
    console.print(f"Next step: [bold]kaggle2github build --input-dir {out_dir}[/bold]")

def cmd_build(args: argparse.Namespace) -> None:
    """Transform downloaded notebooks into production multi-repositories."""
    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)

    if not in_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Input directory '{in_dir}' does not exist.")
        sys.exit(1)

    subdirs = [d for d in in_dir.iterdir() if d.is_dir() and list(d.glob("*.ipynb"))]
    if not subdirs:
        console.print(f"[yellow]No notebook folders found in '{in_dir}'.[/yellow]")
        return

    k_user, _ = get_kaggle_credentials()
    kaggle_user = args.kaggle_user or k_user or "kaggle-user"
    github_user = args.github_user or "github-user"
    author = args.author or github_user

    packager = RepoPackager(
        author=author,
        kaggle_user=kaggle_user,
        github_user=github_user,
    )

    console.print(f"[bold cyan]Building {len(subdirs)} repositories into '{out_dir}'...[/bold cyan]")
    built_repos = []

    for d in subdirs:
        try:
            res = packager.build_repository(kernel_dir=d, output_dir=out_dir)
            built_repos.append(res)
            console.print(f"  [green]OK[/green] Built: [bold]{res['repo_name']}[/bold] ({res['code_cells']} code cells)")
        except Exception as e:
            console.print(f"  [red]Error building {d.name}:[/red] {e}")

    table = Table(title=f"Successfully Built Repositories ({len(built_repos)} total)")
    table.add_column("Repository", style="magenta")
    table.add_column("Inferred Dependencies", style="cyan")
    table.add_column("Cells (Code/Total)", justify="right", style="green")

    for r in built_repos:
        deps_summary = ", ".join(r["dependencies"][:4])
        if len(r["dependencies"]) > 4:
            deps_summary += f" (+{len(r['dependencies']) - 4} more)"
        table.add_row(r["repo_name"], deps_summary, f"{r['code_cells']}/{r['total_cells']}")

    console.print(table)
    console.print(f"\n[green]All repositories generated in '{out_dir}'.[/green]")
    console.print(f"To publish to GitHub: [bold]kaggle2github publish --repos-dir {out_dir}[/bold]")

def cmd_publish(args: argparse.Namespace) -> None:
    """Create GitHub repositories and push local code."""
    repos_dir = Path(args.repos_dir)
    if not repos_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Directory '{repos_dir}' does not exist.")
        sys.exit(1)

    token = args.token or get_github_token()
    if not token:
        console.print("[bold red]Error:[/bold red] GitHub token required. Set GITHUB_TOKEN or pass --token.")
        sys.exit(1)

    client = GitHubClient(token=token, github_user=args.user)
    try:
        user = client.get_authenticated_user()
    except Exception as e:
        console.print(f"[bold red]GitHub Authentication Error:[/bold red] {e}")
        sys.exit(1)

    repo_folders = [d for d in repos_dir.iterdir() if d.is_dir() and (d / "README.md").exists()]
    if not repo_folders:
        console.print(f"[yellow]No built repository folders found in '{repos_dir}'.[/yellow]")
        return

    visibility_str = "PUBLIC" if args.public else "PRIVATE"
    console.print(f"[bold cyan]Publishing {len(repo_folders)} repositories to GitHub as {visibility_str}...[/bold cyan]")

    for idx, rpath in enumerate(repo_folders, start=1):
        repo_name = rpath.name
        console.print(f"\n[{idx}/{len(repo_folders)}] Processing [bold]{repo_name}[/bold]...")

        # 1. Ensure repo exists on GitHub
        try:
            client.ensure_repository(
                repo_name=repo_name,
                description="Production-structured machine learning project migrated from Kaggle.",
                private=not args.public,
                topics=["kaggle", "machine-learning", "python", "data-science"],
            )
            console.print(f"  [green]OK[/green] Remote repo verified ({visibility_str})")
        except Exception as e:
            console.print(f"  [red]Failed to verify remote repo:[/red] {e}")
            continue

        # 2. Push code
        success, msg = client.push_repository(
            repo_path=rpath,
            repo_name=repo_name,
            user_name=args.git_name,
            user_email=args.git_email,
        )
        if success:
            console.print(f"  [green]OK[/green] {msg}")
        else:
            console.print(f"  [red]Push failed:[/red] {msg}")

    console.print("\n[bold green]Publishing process completed![/bold green]")

def cmd_run_all(args: argparse.Namespace) -> None:
    """Execute scan, download, build, and publish sequentially."""
    console.print(Panel.fit("[bold cyan]kaggle2github[/bold cyan] - Full Pipeline Execution", border_style="cyan"))
    cmd_download(args)
    cmd_build(args)
    cmd_publish(args)

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="kaggle2github",
        description="Turn Kaggle notebooks into production-ready, recruiter-grade GitHub repositories.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan and list public Kaggle kernels")
    p_scan.add_argument("--user", help="Kaggle username")
    p_scan.add_argument("--page-size", type=int, default=100, help="Number of kernels to list")
    p_scan.set_defaults(func=cmd_scan)

    # download
    p_dl = subparsers.add_parser("download", help="Download Kaggle kernels")
    p_dl.add_argument("--user", help="Kaggle username")
    p_dl.add_argument("--slugs", nargs="*", help="Specific kernel slugs to download")
    p_dl.add_argument("--output-dir", default=DEFAULT_DOWNLOAD_DIR, help="Staging output directory")
    p_dl.set_defaults(func=cmd_download)

    # build
    p_build = subparsers.add_parser("build", help="Build standalone repositories from notebooks")
    p_build.add_argument("--input-dir", default=DEFAULT_DOWNLOAD_DIR, help="Directory containing downloaded kernels")
    p_build.add_argument("--output-dir", default=DEFAULT_REPOS_DIR, help="Output directory for generated repositories")
    p_build.add_argument("--author", help="Author name for LICENSE and README")
    p_build.add_argument("--kaggle-user", help="Kaggle username for links and badges")
    p_build.add_argument("--github-user", help="GitHub username for repository remotes")
    p_build.set_defaults(func=cmd_build)

    # publish
    p_pub = subparsers.add_parser("publish", help="Create GitHub repos and push code")
    p_pub.add_argument("--repos-dir", default=DEFAULT_REPOS_DIR, help="Directory containing generated repositories")
    p_pub.add_argument("--user", help="GitHub username")
    p_pub.add_argument("--token", help="GitHub Personal Access Token (defaults to GITHUB_TOKEN)")
    p_pub.add_argument("--public", action="store_true", help="Publish repositories as public (default: private)")
    p_pub.add_argument("--git-name", help="Git user.name for commits")
    p_pub.add_argument("--git-email", help="Git user.email for commits")
    p_pub.set_defaults(func=cmd_publish)

    # run-all
    p_all = subparsers.add_parser("run-all", help="Download, build, and publish in one command")
    p_all.add_argument("--user", required=True, help="Kaggle username")
    p_all.add_argument("--github-user", required=True, help="GitHub username")
    p_all.add_argument("--slugs", nargs="*", help="Specific kernel slugs (optional)")
    p_all.add_argument("--author", help="Author name")
    p_all.add_argument("--token", help="GitHub token")
    p_all.add_argument("--public", action="store_true", help="Publish as public")
    p_all.add_argument("--input-dir", default=DEFAULT_DOWNLOAD_DIR, help="Staging directory")
    p_all.add_argument("--output-dir", default=DEFAULT_REPOS_DIR, help="Repositories directory")
    p_all.add_argument("--repos-dir", default=DEFAULT_REPOS_DIR, help="Repositories directory")
    p_all.add_argument("--git-name", help="Git user.name")
    p_all.add_argument("--git-email", help="Git user.email")
    p_all.set_defaults(func=cmd_run_all)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
