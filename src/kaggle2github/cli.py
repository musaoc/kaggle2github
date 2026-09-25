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
    find_downloaded_kaggle_json,
    get_github_token,
    get_kaggle_credentials,
    install_kaggle_json,
    save_env_credentials,
    save_kaggle_credentials,
)
from kaggle2github.github_client import GitHubClient
from kaggle2github.kaggle_client import KaggleClient
from kaggle2github.packager import RepoPackager

console = Console()

def cmd_setup(args: argparse.Namespace) -> None:
    """Interactive setup wizard to configure Kaggle and GitHub credentials."""
    reconfigure = getattr(args, "reconfigure", False)

    console.print(Panel.fit(
        "[bold cyan]kaggle2github Setup Wizard[/bold cyan]\n"
        "Configure Kaggle and GitHub authentication in under 1 minute.",
        border_style="cyan"
    ))

    # --- 1. Kaggle Setup ---
    console.print("\n[bold yellow]Step 1: Kaggle API Authentication[/bold yellow]")
    kaggle_user, kaggle_key = get_kaggle_credentials()
    kaggle_ok = False

    if kaggle_user and kaggle_key and not reconfigure:
        try:
            client = KaggleClient(username=kaggle_user, key=kaggle_key)
            client._get_api()
            console.print(f"  [green]✔ Found existing Kaggle credentials for @{kaggle_user}[/green]")
            keep = console.input(f"  Keep using account @{kaggle_user}? [Y/n]: ").strip().lower()
            if keep in ("", "y", "yes"):
                kaggle_ok = True
            else:
                console.print("  [cyan]Switching to a different Kaggle account...[/cyan]")
        except Exception:
            console.print(f"  [yellow]Existing Kaggle credentials for @{kaggle_user} failed verification.[/yellow]")

    if not kaggle_ok:
        # Check Downloads folder for recently downloaded kaggle.json
        dl_json = find_downloaded_kaggle_json()
        if dl_json:
            console.print(f"  [cyan]Found 'kaggle.json' in your Downloads directory:[/cyan] {dl_json}")
            use_dl = console.input("  Install this file to ~/.kaggle/kaggle.json? [Y/n]: ").strip().lower()
            if use_dl in ("", "y", "yes"):
                try:
                    installed = install_kaggle_json(dl_json)
                    client = KaggleClient()
                    client._get_api()
                    k_user, _ = get_kaggle_credentials()
                    console.print(f"  [green]✔ Successfully installed and verified @{k_user}![/green] (Saved to {installed})")
                    kaggle_user = k_user
                    kaggle_ok = True
                except Exception as e:
                    console.print(f"  [red]Failed to verify downloaded token:[/red] {e}")

    if not kaggle_ok:
        console.print("\n  [bold]How to get your Kaggle token:[/bold]")
        console.print("  1. Go to [link=https://www.kaggle.com/settings]https://www.kaggle.com/settings[/link]")
        console.print("  2. Scroll down to the [bold]API[/bold] section")
        console.print("  3. Click [bold]'Create New Token'[/bold] to download [cyan]kaggle.json[/cyan]\n")

        token_path = console.input("  Enter path to your downloaded kaggle.json (or press Enter to enter key manually): ").strip().strip('"\'')
        if token_path and Path(token_path).is_file():
            try:
                installed = install_kaggle_json(Path(token_path))
                client = KaggleClient()
                client._get_api()
                k_user, _ = get_kaggle_credentials()
                console.print(f"  [green]✔ Verified and installed for @{k_user}![/green] (Saved to {installed})")
                kaggle_user = k_user
                kaggle_ok = True
            except Exception as e:
                console.print(f"  [red]Error installing {token_path}:[/red] {e}")

        if not kaggle_ok:
            user_input = console.input("  Enter your Kaggle Username: ").strip()
            key_input = console.input("  Enter your Kaggle API Key: ").strip()
            if user_input and key_input:
                try:
                    installed = save_kaggle_credentials(user_input, key_input)
                    client = KaggleClient(username=user_input, key=key_input)
                    client._get_api()
                    console.print(f"  [green]✔ Credentials saved to {installed} and verified![/green]")
                    kaggle_user = user_input
                    kaggle_ok = True
                except Exception as e:
                    console.print(f"  [red]Verification failed:[/red] {e}")

    # --- 2. GitHub Setup ---
    console.print("\n[bold yellow]Step 2: GitHub Personal Access Token[/bold yellow]")
    gh_token = get_github_token()
    gh_user = None

    if gh_token and not reconfigure:
        try:
            client = GitHubClient(token=gh_token)
            gh_user = client.get_authenticated_user()
            console.print(f"  [green]✔ Found valid GitHub token for @{gh_user}[/green]")
            keep_gh = console.input(f"  Keep using GitHub account @{gh_user}? [Y/n]: ").strip().lower()
            if keep_gh in ("", "y", "yes"):
                pass
            else:
                console.print("  [cyan]Switching to a different GitHub account / token...[/cyan]")
                gh_user = None
                gh_token = None
        except Exception:
            console.print("  [yellow]Existing GitHub token failed verification.[/yellow]")

    if not gh_user:
        console.print("\n  [bold]How to generate your GitHub token:[/bold]")
        console.print("  1. Visit: [link=https://github.com/settings/tokens/new?scopes=repo&description=kaggle2github]https://github.com/settings/tokens/new?scopes=repo&description=kaggle2github[/link]")
        console.print("  2. Select scope: [bold]repo[/bold] (allows creating and pushing to public/private repositories)")
        console.print("  3. Click [bold]'Generate token'[/bold] and copy the string.\n")

        token_input = console.input("  Paste your GitHub Token: ").strip()
        if token_input:
            try:
                client = GitHubClient(token=token_input)
                gh_user = client.get_authenticated_user()
                gh_token = token_input
                os.environ["GITHUB_TOKEN"] = token_input
                console.print(f"  [green]✔ GitHub account verified: @{gh_user}[/green]")
            except Exception as e:
                console.print(f"  [red]GitHub verification failed:[/red] {e}")

    # --- 3. Save to .env ---
    if kaggle_ok or gh_user:
        console.print("\n[bold yellow]Step 3: Save to .env File[/bold yellow]")
        save_env = console.input("  Save/update credentials in a local .env file? [Y/n]: ").strip().lower()
        if save_env in ("", "y", "yes"):
            k_u, k_k = get_kaggle_credentials()
            env_file = save_env_credentials(
                kaggle_username=k_u if kaggle_ok else None,
                kaggle_key=k_k if kaggle_ok else None,
                github_token=gh_token if gh_user else None,
            )
            console.print(f"  [green]✔ Credentials saved to {env_file.resolve()}[/green]")
            console.print("  [dim](Tip: .env is automatically gitignored to protect your secrets)[/dim]")

    # --- Summary ---
    console.print("\n" + "=" * 60)
    if kaggle_ok and gh_user:
        console.print(Panel(
            f"[bold green]Authentication Complete! 🎉[/bold green]\n\n"
            f"• Kaggle: [bold cyan]@{kaggle_user}[/bold cyan] (Ready to fetch public work)\n"
            f"• GitHub: [bold cyan]@{gh_user}[/bold cyan] (Ready to publish public repositories)\n\n"
            f"Tip: You can edit [bold cyan].env[/bold cyan] directly or run [bold cyan]kaggle2github setup --reconfigure[/bold cyan] anytime to switch accounts.\n\n"
            f"Run the complete migration in one command:\n"
            f"[bold]kaggle2github run-all --user {kaggle_user} --github-user {gh_user}[/bold]",
            title="Setup Summary",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"• Kaggle: {'[green]Connected[/green]' if kaggle_ok else '[red]Not configured[/red]'}\n"
            f"• GitHub: {'[green]Connected[/green]' if gh_user else '[yellow]Not set (required only for publishing)[/yellow]'}\n\n"
            f"Tip: Edit [bold cyan].env[/bold cyan] or run [bold cyan]kaggle2github setup[/bold cyan] anytime to update settings.",
            title="Setup Status",
            border_style="yellow",
        ))

def cmd_scan(args: argparse.Namespace) -> None:
    """Scan and list public Kaggle notebooks."""
    client = KaggleClient(username=args.user)
    target_user = args.user or client.username

    if not target_user:
        console.print("[bold red]Error:[/bold red] Kaggle username must be specified via --user or KAGGLE_USERNAME.")
        console.print("Tip: Run [bold cyan]kaggle2github setup[/bold cyan] to configure authentication.")
        sys.exit(1)

    include_private = getattr(args, "include_private", False)
    privacy_label = "all (including private)" if include_private else "public"
    with console.status(f"[bold green]Fetching {privacy_label} kernels for @{target_user}..."):
        try:
            kernels = client.list_kernels(
                user=target_user,
                page_size=args.page_size,
                include_private=include_private,
            )
        except Exception as e:
            console.print(f"[bold red]Failed to fetch kernels:[/bold red] {e}")
            console.print("Tip: Run [bold cyan]kaggle2github setup[/bold cyan] to verify your Kaggle credentials.")
            sys.exit(1)

    if not kernels:
        console.print(f"[yellow]No {privacy_label} kernels found for user '@{target_user}'.[/yellow]")
        return

    table = Table(title=f"Kaggle Kernels ({privacy_label.title()}) for @{target_user} ({len(kernels)} total)")
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
        console.print("Tip: Run [bold cyan]kaggle2github setup[/bold cyan] to configure authentication.")
        sys.exit(1)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    include_private = getattr(args, "include_private", False)
    slugs = args.slugs
    if not slugs:
        privacy_label = "all (including private)" if include_private else "public"
        with console.status(f"[bold green]Fetching {privacy_label} kernels for @{target_user}..."):
            try:
                kernels = client.list_kernels(user=target_user, include_private=include_private)
                slugs = [k["slug"] for k in kernels]
            except Exception as e:
                console.print(f"[bold red]Failed to list kernels:[/bold red] {e}")
                console.print("Tip: Run [bold cyan]kaggle2github setup[/bold cyan] to verify your credentials.")
                sys.exit(1)

    console.print(f"[bold cyan]Downloading {len(slugs)} kernel(s) to '{out_dir}'...[/bold cyan]")
    success_count = 0

    for i, slug in enumerate(slugs, start=1):
        console.print(f"[{i}/{len(slugs)}] Downloading [bold]{slug}[/bold]...")
        try:
            res = client.download_kernel(slug, output_dir=str(out_dir), user=target_user, include_private=include_private)
            if res:
                success_count += 1
            else:
                console.print(f"  [yellow]Skipped {slug} (private kernel)[/yellow]")
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
    console.print(f"To publish to GitHub (Public by default): [bold]kaggle2github publish --repos-dir {out_dir}[/bold]")

def cmd_publish(args: argparse.Namespace) -> None:
    """Create GitHub repositories and push local code (Public by default)."""
    repos_dir = Path(args.repos_dir)
    if not repos_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Directory '{repos_dir}' does not exist.")
        sys.exit(1)

    token = getattr(args, "token", None) or get_github_token()
    if not token:
        console.print("[bold red]Error:[/bold red] GitHub token required. Run [bold cyan]kaggle2github setup[/bold cyan] or set GITHUB_TOKEN.")
        sys.exit(1)

    client = GitHubClient(token=token, github_user=args.user)
    try:
        user = client.get_authenticated_user()
    except Exception as e:
        console.print(f"[bold red]GitHub Authentication Error:[/bold red] {e}")
        console.print("Tip: Run [bold cyan]kaggle2github setup[/bold cyan] to verify your token.")
        sys.exit(1)

    repo_folders = [d for d in repos_dir.iterdir() if d.is_dir() and (d / "README.md").exists()]
    if not repo_folders:
        console.print(f"[yellow]No built repository folders found in '{repos_dir}'.[/yellow]")
        return

    is_private = getattr(args, "private", False)
    visibility_str = "PRIVATE" if is_private else "PUBLIC"
    console.print(f"[bold cyan]Publishing {len(repo_folders)} repositories to GitHub as {visibility_str}...[/bold cyan]")

    for idx, rpath in enumerate(repo_folders, start=1):
        repo_name = rpath.name
        console.print(f"\n[{idx}/{len(repo_folders)}] Processing [bold]{repo_name}[/bold]...")

        # 1. Ensure repo exists on GitHub
        try:
            client.ensure_repository(
                repo_name=repo_name,
                description="Production-structured machine learning project migrated from Kaggle.",
                private=is_private,
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
    """Execute download, build, and publish sequentially."""
    console.print(Panel.fit("[bold cyan]kaggle2github[/bold cyan] - Full Pipeline Execution", border_style="cyan"))

    # Credential check warning
    k_user, k_key = get_kaggle_credentials()
    if not (k_user and k_key) and not getattr(args, "user", None):
        console.print("[yellow]Warning: Kaggle credentials not found in environment or ~/.kaggle/kaggle.json.[/yellow]")
        console.print("Run [bold cyan]kaggle2github setup[/bold cyan] first if downloads fail.")

    staging_dir = getattr(args, "staging_dir", None) or getattr(args, "input_dir", DEFAULT_DOWNLOAD_DIR)
    repos_dir = getattr(args, "repos_dir", None) or getattr(args, "output_dir", DEFAULT_REPOS_DIR)

    # 1. Download into staging_dir
    dl_args = argparse.Namespace(
        user=args.user,
        slugs=args.slugs,
        output_dir=staging_dir,
        include_private=getattr(args, "include_private", False),
    )
    cmd_download(dl_args)

    # 2. Build from staging_dir into repos_dir
    build_args = argparse.Namespace(
        input_dir=staging_dir,
        output_dir=repos_dir,
        author=getattr(args, "author", None),
        kaggle_user=args.user,
        github_user=args.github_user,
    )
    cmd_build(build_args)

    # 3. Publish to GitHub
    pub_args = argparse.Namespace(
        repos_dir=repos_dir,
        user=args.github_user,
        token=getattr(args, "token", None),
        private=getattr(args, "private", False),
        git_name=getattr(args, "git_name", None),
        git_email=getattr(args, "git_email", None),
    )
    cmd_publish(pub_args)

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="kaggle2github",
        description="Turn Kaggle notebooks into production-ready, recruiter-grade GitHub repositories.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # setup
    p_setup = subparsers.add_parser("setup", help="Interactive setup wizard for Kaggle & GitHub authentication")
    p_setup.add_argument("--reconfigure", "--force", action="store_true", help="Reconfigure credentials or switch connected accounts")
    p_setup.set_defaults(func=cmd_setup)

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan and list public Kaggle kernels")
    p_scan.add_argument("--user", help="Kaggle username")
    p_scan.add_argument("--page-size", type=int, default=100, help="Number of kernels to list")
    p_scan.add_argument("--include-private", action="store_true", help="Include private kernels (default: public kernels only)")
    p_scan.set_defaults(func=cmd_scan)

    # download
    p_dl = subparsers.add_parser("download", help="Download Kaggle kernels (public only by default)")
    p_dl.add_argument("--user", help="Kaggle username")
    p_dl.add_argument("--slugs", nargs="*", help="Specific kernel slugs to download")
    p_dl.add_argument("--include-private", action="store_true", help="Include private kernels (default: public kernels only)")
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
    p_pub = subparsers.add_parser("publish", help="Create GitHub repos and push code (Public by default)")
    p_pub.add_argument("--repos-dir", default=DEFAULT_REPOS_DIR, help="Directory containing generated repositories")
    p_pub.add_argument("--user", help="GitHub username")
    p_pub.add_argument("--token", help="GitHub Personal Access Token (defaults to GITHUB_TOKEN)")
    p_pub.add_argument("--private", action="store_true", help="Publish repositories as private (default: public)")
    p_pub.add_argument("--public", action="store_true", help=argparse.SUPPRESS)
    p_pub.add_argument("--git-name", help="Git user.name for commits")
    p_pub.add_argument("--git-email", help="Git user.email for commits")
    p_pub.set_defaults(func=cmd_publish)

    # run-all
    p_all = subparsers.add_parser("run-all", help="Download, build, and publish public notebooks in one command")
    p_all.add_argument("--user", required=True, help="Kaggle username")
    p_all.add_argument("--github-user", required=True, help="GitHub username")
    p_all.add_argument("--slugs", nargs="*", help="Specific kernel slugs (optional)")
    p_all.add_argument("--include-private", action="store_true", help="Include private kernels (default: public kernels only)")
    p_all.add_argument("--author", help="Author name")
    p_all.add_argument("--token", help="GitHub token")
    p_all.add_argument("--private", action="store_true", help="Publish repositories as private (default: public)")
    p_all.add_argument("--public", action="store_true", help=argparse.SUPPRESS)
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
