#!/usr/bin/env python3
"""
Notion → GitHub Sync CLI

Usage:
    python sync.py              # Run full sync
    python sync.py --no-push    # Sync without pushing
    python sync.py --force      # Force sync all pages
    python sync.py --dry-run    # Preview changes without committing
    python sync.py status       # Show sync status
    python sync.py clean        # Remove all synced content
"""

import sys
from pathlib import Path

import click
from rich.console import Console

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

console = Console()


@click.group(invoke_without_command=True)
@click.option("--no-push", is_flag=True, help="Don't push changes to remote")
@click.option("--force", is_flag=True, help="Force sync all pages regardless of changes")
@click.option("--dry-run", is_flag=True, help="Preview changes without committing")
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.pass_context
def cli(ctx, no_push: bool, force: bool, dry_run: bool, debug: bool):
    """
    Notion → GitHub Sync
    
    Synchronizes Notion pages to a GitHub repository as Markdown files.
    """
    ctx.ensure_object(dict)
    ctx.obj["no_push"] = no_push
    ctx.obj["force"] = force
    ctx.obj["dry_run"] = dry_run
    ctx.obj["debug"] = debug
    
    # If no subcommand, run sync
    if ctx.invoked_subcommand is None:
        ctx.invoke(sync)


@cli.command()
@click.pass_context
def sync(ctx):
    """Run synchronization from Notion to GitHub."""
    # Load environment
    load_dotenv()
    
    # Import here to ensure env is loaded first
    from importlib import import_module
    config_module = import_module(".notion-sync.config")
    engine_module = import_module(".notion-sync.sync_engine")
    
    Config = config_module.Config
    SyncEngine = engine_module.SyncEngine
    
    try:
        # Load configuration
        config = Config.from_env()
        
        # Apply CLI overrides
        if ctx.obj.get("force"):
            config.force_sync = True
        if ctx.obj.get("dry_run"):
            config.dry_run = True
        if ctx.obj.get("debug"):
            config.debug = True
        
        # Run sync
        engine = SyncEngine(config)
        result = engine.sync(push=not ctx.obj.get("no_push", False))
        
        # Exit with error code if sync failed
        if not result.success:
            sys.exit(1)
            
    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Sync cancelled.[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if ctx.obj.get("debug"):
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
def status():
    """Show current sync status."""
    load_dotenv()
    
    from importlib import import_module
    config_module = import_module(".notion-sync.config")
    engine_module = import_module(".notion-sync.sync_engine")
    
    Config = config_module.Config
    SyncEngine = engine_module.SyncEngine
    
    try:
        config = Config.from_env()
        engine = SyncEngine(config)
        engine.status()
    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def clean(yes: bool):
    """Remove all synced content and reset state."""
    load_dotenv()
    
    from importlib import import_module
    config_module = import_module(".notion-sync.config")
    engine_module = import_module(".notion-sync.sync_engine")
    
    Config = config_module.Config
    SyncEngine = engine_module.SyncEngine
    
    try:
        config = Config.from_env()
        engine = SyncEngine(config)
        engine.clean(confirm=yes)
    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    from importlib import import_module
    init_module = import_module(".notion-sync")
    console.print(f"Notion → GitHub Sync v{init_module.__version__}")


# Alternative entry point that doesn't use module imports
# This is more reliable for the initial run
def main():
    """Main entry point."""
    import os
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Load environment
    load_dotenv()
    
    # Parse simple arguments
    args = sys.argv[1:]
    
    no_push = "--no-push" in args
    force = "--force" in args
    dry_run = "--dry-run" in args
    debug = "--debug" in args
    
    # Remove flags from args
    args = [a for a in args if not a.startswith("--")]
    
    command = args[0] if args else "sync"
    
    if command == "version":
        console.print("Notion → GitHub Sync v1.0.0")
        return
    
    if command == "status":
        run_status()
        return
    
    if command == "clean":
        run_clean("--yes" in sys.argv)
        return
    
    # Default: run sync
    run_sync(
        push=not no_push,
        force=force,
        dry_run=dry_run,
        debug=debug,
    )


def run_sync(push: bool = True, force: bool = False, dry_run: bool = False, debug: bool = False):
    """Run synchronization."""
    # Import from .notion-sync package
    sys.path.insert(0, str(Path(__file__).parent / ".notion-sync"))
    
    from config import Config
    from sync_engine import SyncEngine
    
    try:
        config = Config.from_env()
        config.force_sync = force
        config.dry_run = dry_run
        config.debug = debug
        
        engine = SyncEngine(config)
        result = engine.sync(push=push)
        
        if not result.success:
            sys.exit(1)
            
    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        console.print("\n[dim]Make sure you have created a .env file with your credentials.[/dim]")
        console.print("[dim]See .env.example for the required variables.[/dim]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Sync cancelled.[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_status():
    """Show sync status."""
    sys.path.insert(0, str(Path(__file__).parent / ".notion-sync"))
    
    from config import Config
    from sync_engine import SyncEngine
    
    try:
        config = Config.from_env()
        engine = SyncEngine(config)
        engine.status()
    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        sys.exit(1)


def run_clean(confirm: bool = False):
    """Clean synced content."""
    sys.path.insert(0, str(Path(__file__).parent / ".notion-sync"))
    
    from config import Config
    from sync_engine import SyncEngine
    
    try:
        config = Config.from_env()
        engine = SyncEngine(config)
        engine.clean(confirm=confirm)
    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
