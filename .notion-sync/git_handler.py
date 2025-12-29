"""
Git operations handler for the sync system.

Handles:
- Change detection
- Semantic commit message generation
- Staging and committing
- Push operations
"""

import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from rich.console import Console

from config import Config

console = Console()


class ChangeType(Enum):
    """Types of changes detected."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class FileChange:
    """Represents a file change."""
    
    path: Path
    change_type: ChangeType
    old_path: Optional[Path] = None  # For renames
    
    @property
    def topic(self) -> Optional[str]:
        """Extract topic name from file path."""
        parts = self.path.parts
        
        # Skip hidden directories and root files
        if not parts or parts[0].startswith("."):
            return None
        
        # First directory is the topic
        return parts[0]


@dataclass
class SyncChanges:
    """Collection of changes from a sync operation."""
    
    files: list[FileChange] = field(default_factory=list)
    
    @property
    def topics_changed(self) -> set[str]:
        """Get unique topics that have changes."""
        return {f.topic for f in self.files if f.topic}
    
    @property
    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return len(self.files) > 0
    
    @property
    def added_count(self) -> int:
        """Count of added files."""
        return sum(1 for f in self.files if f.change_type == ChangeType.ADDED)
    
    @property
    def modified_count(self) -> int:
        """Count of modified files."""
        return sum(1 for f in self.files if f.change_type == ChangeType.MODIFIED)
    
    @property
    def deleted_count(self) -> int:
        """Count of deleted files."""
        return sum(1 for f in self.files if f.change_type == ChangeType.DELETED)
    
    @property
    def images_added(self) -> int:
        """Count of new images."""
        image_exts = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
        return sum(
            1 for f in self.files
            if f.change_type == ChangeType.ADDED
            and f.path.suffix.lower() in image_exts
        )


class GitHandler:
    """
    Handles Git operations for the sync system.
    
    Generates professional, semantic commit messages and
    manages all git interactions.
    """
    
    def __init__(self, config: Config):
        """
        Initialize git handler.
        
        Args:
            config: Configuration instance.
        """
        self.config = config
        self.repo_root = config.repo_root
    
    def _run_git(
        self,
        *args: str,
        capture_output: bool = True,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """Run a git command."""
        cmd = ["git", "-C", str(self.repo_root)] + list(args)
        
        if self.config.debug:
            console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
        
        return subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=check,
        )
    
    def is_git_repo(self) -> bool:
        """Check if repo_root is a git repository."""
        try:
            self._run_git("rev-parse", "--git-dir")
            return True
        except subprocess.CalledProcessError:
            return False
    
    def init_repo(self) -> None:
        """Initialize a new git repository."""
        if not self.is_git_repo():
            self._run_git("init")
            console.print("[green]Initialized new git repository[/green]")
    
    def configure_user(self) -> None:
        """Configure git user for commits."""
        try:
            self._run_git("config", "user.name", self.config.git_user_name)
            self._run_git("config", "user.email", self.config.git_user_email)
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]Warning: Could not configure git user: {e}[/yellow]")
    
    def get_changes(self) -> SyncChanges:
        """
        Detect all changes in the working directory.
        
        Returns:
            SyncChanges object with all detected changes.
        """
        changes = SyncChanges()
        
        # Get status of all files
        try:
            result = self._run_git("status", "--porcelain=v1", "-uall")
        except subprocess.CalledProcessError:
            return changes
        
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            
            # Parse porcelain format: XY path
            status = line[:2]
            path_str = line[3:]
            
            # Handle renames (format: "R  old -> new")
            if " -> " in path_str:
                old_path, new_path = path_str.split(" -> ")
                changes.files.append(FileChange(
                    path=Path(new_path),
                    change_type=ChangeType.RENAMED,
                    old_path=Path(old_path),
                ))
                continue
            
            path = Path(path_str)
            
            # Determine change type
            if status[0] == "?" or status[1] == "?":
                change_type = ChangeType.ADDED
            elif status[0] == "D" or status[1] == "D":
                change_type = ChangeType.DELETED
            elif status[0] == "A":
                change_type = ChangeType.ADDED
            else:
                change_type = ChangeType.MODIFIED
            
            changes.files.append(FileChange(path=path, change_type=change_type))
        
        return changes
    
    def stage_all(self) -> None:
        """Stage all changes."""
        self._run_git("add", "-A")
    
    def stage_files(self, paths: list[Path]) -> None:
        """Stage specific files."""
        for path in paths:
            self._run_git("add", str(path))
    
    def generate_commit_message(
        self,
        changes: SyncChanges,
        synced_pages: list[str],
        is_initial: bool = False,
    ) -> str:
        """
        Generate a semantic commit message based on changes.
        
        Format: docs(<scope>): <action> <details>
        
        Args:
            changes: SyncChanges object with detected changes.
            synced_pages: List of page names that were synced.
            is_initial: Whether this is the initial commit.
            
        Returns:
            Formatted commit message.
        """
        topics = changes.topics_changed
        
        # Initial commit
        if is_initial:
            if len(synced_pages) == 1:
                return f"docs({synced_pages[0]}): initial sync"
            else:
                pages_list = ", ".join(sorted(synced_pages))
                return (
                    f"docs: initial sync of {len(synced_pages)} topics\n\n"
                    f"Topics: {pages_list}"
                )
        
        # Single topic changed
        if len(topics) == 1:
            topic = list(topics)[0]
            action = self._determine_action(changes, topic)
            return f"docs({topic}): {action}"
        
        # Multiple topics changed
        if len(topics) > 1:
            topics_list = ", ".join(sorted(topics))
            return (
                f"docs: sync updates across {len(topics)} topics\n\n"
                f"Updated: {topics_list}"
            )
        
        # Fallback (e.g., only root README changed)
        return "docs: update documentation index"
    
    def _determine_action(self, changes: SyncChanges, topic: str) -> str:
        """Determine the action description for a topic."""
        topic_changes = [f for f in changes.files if f.topic == topic]
        
        # Check for images
        images_added = sum(
            1 for f in topic_changes
            if f.change_type == ChangeType.ADDED
            and f.path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
        )
        
        # Check for README changes
        readme_changed = any(
            f.path.name.lower() == "readme.md"
            for f in topic_changes
        )
        
        # All files are new
        all_new = all(f.change_type == ChangeType.ADDED for f in topic_changes)
        if all_new:
            if images_added > 0:
                return f"initial sync with {images_added} images"
            return "initial sync"
        
        # Determine primary action
        if images_added > 0 and readme_changed:
            return f"update content and add {images_added} image{'s' if images_added > 1 else ''}"
        elif images_added > 0:
            return f"add {images_added} image{'s' if images_added > 1 else ''}"
        elif readme_changed:
            return "update content"
        else:
            return "sync latest changes"
    
    def commit(self, message: str) -> bool:
        """
        Create a commit with the given message.
        
        Args:
            message: Commit message.
            
        Returns:
            True if commit was created, False if nothing to commit.
        """
        if self.config.dry_run:
            console.print(f"[yellow]Dry run - would commit:[/yellow]\n{message}")
            return True
        
        try:
            # Check if there are staged changes
            result = self._run_git("diff", "--cached", "--quiet", check=False)
            if result.returncode == 0:
                console.print("[dim]No changes to commit[/dim]")
                return False
            
            self._run_git("commit", "-m", message)
            console.print(f"[green]Committed:[/green] {message.split(chr(10))[0]}")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Commit failed: {e}[/red]")
            return False
    
    def push(self, remote: str = "origin", branch: str = "main") -> bool:
        """
        Push commits to remote.
        
        Args:
            remote: Remote name.
            branch: Branch name.
            
        Returns:
            True if push succeeded.
        """
        if self.config.dry_run:
            console.print(f"[yellow]Dry run - would push to {remote}/{branch}[/yellow]")
            return True
        
        try:
            # Check if remote exists
            result = self._run_git("remote", "get-url", remote, check=False)
            if result.returncode != 0:
                console.print(f"[yellow]Remote '{remote}' not configured, skipping push[/yellow]")
                return False
            
            self._run_git("push", remote, branch)
            console.print(f"[green]Pushed to {remote}/{branch}[/green]")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Push failed: {e}[/red]")
            return False
    
    def get_remote_url(self, remote: str = "origin") -> Optional[str]:
        """Get the URL of a remote."""
        try:
            result = self._run_git("remote", "get-url", remote)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def set_remote(self, remote: str, url: str) -> None:
        """Set or update a remote URL."""
        try:
            # Try to set-url (updates if exists)
            self._run_git("remote", "set-url", remote, url, check=False)
        except subprocess.CalledProcessError:
            # Add new remote
            self._run_git("remote", "add", remote, url)
    
    def get_current_branch(self) -> str:
        """Get the current branch name."""
        try:
            result = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "main"
    
    def has_commits(self) -> bool:
        """Check if the repository has any commits."""
        try:
            self._run_git("rev-parse", "HEAD")
            return True
        except subprocess.CalledProcessError:
            return False
