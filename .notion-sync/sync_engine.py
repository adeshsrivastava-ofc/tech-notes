"""
Main sync engine for Notion → GitHub synchronization.

Orchestrates:
- Page discovery from Notion
- Change detection
- Content conversion
- File writing
- Git operations
- State management
"""

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from config import Config
from git_handler import GitHandler
from markdown_converter import MarkdownConverter
from notion_api import NotionAPI, NotionPage

console = Console()


@dataclass
class PageState:
    """State of a synced page."""
    
    page_id: str
    title: str
    directory: str
    last_edited_time: str
    last_synced_time: str
    content_hash: Optional[str] = None


@dataclass
class SyncState:
    """Overall sync state."""
    
    pages: dict[str, PageState] = field(default_factory=dict)
    last_sync_time: Optional[str] = None
    version: str = "1.0"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "last_sync_time": self.last_sync_time,
            "pages": {
                page_id: {
                    "page_id": state.page_id,
                    "title": state.title,
                    "directory": state.directory,
                    "last_edited_time": state.last_edited_time,
                    "last_synced_time": state.last_synced_time,
                    "content_hash": state.content_hash,
                }
                for page_id, state in self.pages.items()
            },
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SyncState":
        """Create from dictionary."""
        state = cls(
            version=data.get("version", "1.0"),
            last_sync_time=data.get("last_sync_time"),
        )
        
        for page_id, page_data in data.get("pages", {}).items():
            state.pages[page_id] = PageState(
                page_id=page_data["page_id"],
                title=page_data["title"],
                directory=page_data["directory"],
                last_edited_time=page_data["last_edited_time"],
                last_synced_time=page_data["last_synced_time"],
                content_hash=page_data.get("content_hash"),
            )
        
        return state


@dataclass
class SyncResult:
    """Result of a sync operation."""
    
    pages_synced: list[str] = field(default_factory=list)
    pages_skipped: list[str] = field(default_factory=list)
    pages_failed: list[str] = field(default_factory=list)
    images_downloaded: int = 0
    commit_created: bool = False
    pushed: bool = False
    
    @property
    def success(self) -> bool:
        """Check if sync was successful."""
        return len(self.pages_failed) == 0


class SyncEngine:
    """
    Main orchestrator for Notion → GitHub synchronization.
    
    Coordinates all components to perform the sync:
    1. Discover pages in Notion
    2. Detect which pages have changed
    3. Convert changed pages to Markdown
    4. Write files and download images
    5. Generate index README
    6. Commit and push changes
    """
    
    def __init__(self, config: Config):
        """
        Initialize sync engine.
        
        Args:
            config: Configuration instance.
        """
        self.config = config
        self.notion_api = NotionAPI(config)
        self.markdown_converter = MarkdownConverter(self.notion_api)
        self.git_handler = GitHandler(config)
        self.state = self._load_state()
    
    def _load_state(self) -> SyncState:
        """Load sync state from file."""
        if self.config.state_file.exists():
            try:
                with open(self.config.state_file) as f:
                    data = json.load(f)
                return SyncState.from_dict(data)
            except (json.JSONDecodeError, KeyError) as e:
                console.print(f"[yellow]Warning: Could not load state file: {e}[/yellow]")
        
        return SyncState()
    
    def _save_state(self) -> None:
        """Save sync state to file."""
        self.config.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config.state_file, "w") as f:
            json.dump(self.state.to_dict(), f, indent=2)
    
    def sync(self, push: bool = True) -> SyncResult:
        """
        Perform full synchronization.
        
        Args:
            push: Whether to push changes to remote.
            
        Returns:
            SyncResult with details of the operation.
        """
        result = SyncResult()
        
        console.print("\n[bold blue]🔄 Starting Notion → GitHub Sync[/bold blue]\n")
        
        # Initialize git repo if needed
        self.git_handler.init_repo()
        self.git_handler.configure_user()
        
        is_initial = not self.git_handler.has_commits()
        
        # Discover pages
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Discovering pages in Notion...", total=None)
            
            try:
                pages = self.notion_api.get_child_pages(
                    self.config.notion_parent_page_id
                )
                progress.update(task, description=f"Found {len(pages)} pages")
            except Exception as e:
                console.print(f"[red]Failed to fetch pages: {e}[/red]")
                result.pages_failed.append("(page discovery)")
                return result
        
        if not pages:
            console.print("[yellow]No pages found under the parent page.[/yellow]")
            console.print("[dim]Make sure the integration has access to the pages.[/dim]")
            return result
        
        # Process each page
        for page in pages:
            try:
                synced = self._sync_page(page, result)
                if synced:
                    result.pages_synced.append(page.title)
                else:
                    result.pages_skipped.append(page.title)
            except Exception as e:
                console.print(f"[red]Failed to sync '{page.title}': {e}[/red]")
                result.pages_failed.append(page.title)
        
        # Generate index README
        self._generate_index(pages)
        
        # Git operations
        changes = self.git_handler.get_changes()
        
        if changes.has_changes:
            self.git_handler.stage_all()
            
            commit_msg = self.git_handler.generate_commit_message(
                changes,
                synced_pages=[self.config.get_directory_for_page(p) for p in result.pages_synced],
                is_initial=is_initial,
            )
            
            result.commit_created = self.git_handler.commit(commit_msg)
            
            if push and result.commit_created:
                result.pushed = self.git_handler.push()
        else:
            console.print("[dim]No changes to commit[/dim]")
        
        # Update state
        self.state.last_sync_time = datetime.now(timezone.utc).isoformat()
        self._save_state()
        
        # Print summary
        self._print_summary(result)
        
        return result
    
    def _sync_page(self, page: NotionPage, result: SyncResult) -> bool:
        """
        Sync a single page.
        
        Args:
            page: NotionPage to sync.
            result: SyncResult to update.
            
        Returns:
            True if page was synced, False if skipped.
        """
        directory_name = self.config.get_directory_for_page(page.title)
        
        # Check if page has changed
        if not self._should_sync_page(page):
            console.print(f"[dim]Skipping {page.title} (unchanged)[/dim]")
            return False
        
        console.print(f"[cyan]Syncing:[/cyan] {page.title}")
        
        # Create directory
        page_dir = self.config.repo_root / directory_name
        images_dir = page_dir / "images"
        page_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # Fetch blocks
        blocks = self.notion_api.get_page_blocks(page.id)
        
        # Convert to markdown
        markdown_content, downloaded_images = self.markdown_converter.convert(
            blocks,
            images_dir=images_dir,
            relative_images_path="images",
        )
        
        # Add page header
        full_content = self._create_page_content(page, markdown_content)
        
        # Write README.md
        readme_path = page_dir / "README.md"
        with open(readme_path, "w") as f:
            f.write(full_content)
        
        result.images_downloaded += len(downloaded_images)
        
        # Update state
        self.state.pages[page.id] = PageState(
            page_id=page.id,
            title=page.title,
            directory=directory_name,
            last_edited_time=page.last_edited_time.isoformat(),
            last_synced_time=datetime.now(timezone.utc).isoformat(),
        )
        
        return True
    
    def _should_sync_page(self, page: NotionPage) -> bool:
        """Check if a page should be synced."""
        if self.config.force_sync:
            return True
        
        # Check if we have state for this page
        if page.id not in self.state.pages:
            return True
        
        stored_state = self.state.pages[page.id]
        
        # Compare last_edited_time
        stored_time = datetime.fromisoformat(stored_state.last_edited_time)
        
        return page.last_edited_time > stored_time
    
    def _create_page_content(self, page: NotionPage, body: str) -> str:
        """Create full page content with header."""
        lines = []
        
        # Title with optional icon
        if page.icon:
            lines.append(f"# {page.icon} {page.title}")
        else:
            lines.append(f"# {page.title}")
        
        lines.append("")
        
        # Metadata
        lines.append(f"> 📅 Last updated: {page.last_edited_time.strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append(f"> 🔗 [View in Notion]({page.url})")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Body content
        lines.append(body)
        
        return "\n".join(lines)
    
    def _generate_index(self, pages: list[NotionPage]) -> None:
        """Generate the root README.md index."""
        lines = []
        
        lines.append("# 📚 Tech Notes")
        lines.append("")
        lines.append("A collection of technical notes and documentation.")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Topics")
        lines.append("")
        
        # Sort pages alphabetically
        sorted_pages = sorted(pages, key=lambda p: p.title.lower())
        
        for page in sorted_pages:
            directory = self.config.get_directory_for_page(page.title)
            icon = page.icon if page.icon else "📄"
            lines.append(f"- [{icon} {page.title}](./{directory}/)")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## About")
        lines.append("")
        lines.append("These notes are automatically synced from [Notion](https://notion.so) using a custom sync system.")
        lines.append("")
        lines.append(f"*Last sync: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*")
        lines.append("")
        
        # Write file
        readme_path = self.config.repo_root / "README.md"
        with open(readme_path, "w") as f:
            f.write("\n".join(lines))
    
    def _print_summary(self, result: SyncResult) -> None:
        """Print sync summary."""
        console.print("\n" + "=" * 50)
        console.print("[bold]Sync Summary[/bold]")
        console.print("=" * 50)
        
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Pages synced", str(len(result.pages_synced)))
        table.add_row("Pages skipped", str(len(result.pages_skipped)))
        table.add_row("Pages failed", str(len(result.pages_failed)))
        table.add_row("Images downloaded", str(result.images_downloaded))
        table.add_row("Commit created", "✓" if result.commit_created else "✗")
        table.add_row("Pushed to remote", "✓" if result.pushed else "✗")
        table.add_row("API requests", str(self.notion_api.request_count))
        
        console.print(table)
        
        if result.pages_synced:
            console.print(f"\n[green]Synced:[/green] {', '.join(result.pages_synced)}")
        
        if result.pages_failed:
            console.print(f"\n[red]Failed:[/red] {', '.join(result.pages_failed)}")
        
        console.print("")
    
    def status(self) -> None:
        """Print current sync status."""
        console.print("\n[bold]Sync Status[/bold]\n")
        
        if not self.state.pages:
            console.print("[yellow]No pages have been synced yet.[/yellow]")
            console.print("Run 'python sync.py' to perform initial sync.")
            return
        
        table = Table(title="Synced Pages")
        table.add_column("Page", style="cyan")
        table.add_column("Directory", style="green")
        table.add_column("Last Edited", style="yellow")
        table.add_column("Last Synced", style="blue")
        
        for page_state in sorted(self.state.pages.values(), key=lambda p: p.title):
            edited = datetime.fromisoformat(page_state.last_edited_time)
            synced = datetime.fromisoformat(page_state.last_synced_time)
            
            table.add_row(
                page_state.title,
                page_state.directory,
                edited.strftime("%Y-%m-%d %H:%M"),
                synced.strftime("%Y-%m-%d %H:%M"),
            )
        
        console.print(table)
        
        if self.state.last_sync_time:
            last_sync = datetime.fromisoformat(self.state.last_sync_time)
            console.print(f"\nLast sync: {last_sync.strftime('%Y-%m-%d %H:%M UTC')}")
    
    def clean(self, confirm: bool = False) -> None:
        """
        Clean all synced content and reset state.
        
        Args:
            confirm: Whether to proceed without confirmation.
        """
        if not confirm:
            console.print("[yellow]This will delete all synced content and reset state.[/yellow]")
            response = input("Are you sure? (yes/no): ")
            if response.lower() != "yes":
                console.print("Aborted.")
                return
        
        # Remove synced directories
        for page_state in self.state.pages.values():
            page_dir = self.config.repo_root / page_state.directory
            if page_dir.exists():
                shutil.rmtree(page_dir)
                console.print(f"Removed: {page_dir}")
        
        # Remove root README
        readme = self.config.repo_root / "README.md"
        if readme.exists():
            readme.unlink()
            console.print(f"Removed: {readme}")
        
        # Reset state
        self.state = SyncState()
        self._save_state()
        
        console.print("[green]Clean complete.[/green]")
