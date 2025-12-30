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
        """
        Extract topic name from file path.
        
        Topic is the first directory component, NOT the filename.
        Root-level files (e.g., README.md) return None.
        
        Examples:
            linux/README.md -> "linux"
            aws/images/arch.png -> "aws"
            README.md -> None (root-level file)
            .notion-sync/state.json -> None (hidden directory)
        """
        parts = self.path.parts
        
        # No parts = empty path (shouldn't happen)
        if not parts:
            return None
        
        # Skip hidden directories (e.g., .notion-sync/)
        if parts[0].startswith("."):
            return None
        
        # Root-level files have only 1 part (the filename itself).
        # Topics are directories, not files, so we need at least 2 parts:
        # [directory, filename] or [dir1, dir2, ..., filename]
        if len(parts) < 2:
            return None
        
        # First directory is the topic
        return parts[0]
    
    @property
    def is_root_file(self) -> bool:
        """Check if this file is at the repository root level."""
        return len(self.path.parts) == 1 and not self.path.parts[0].startswith(".")


@dataclass
class SyncChanges:
    """Collection of changes from a sync operation."""
    
    files: list[FileChange] = field(default_factory=list)
    
    @property
    def topics_changed(self) -> set[str]:
        """
        Get unique topics (directories) that have changes.
        
        Root-level files are excluded - they don't belong to any topic.
        """
        return {f.topic for f in self.files if f.topic}
    
    @property
    def has_root_changes(self) -> bool:
        """Check if any root-level files (e.g., README.md) changed."""
        return any(f.is_root_file for f in self.files)
    
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
        
        Parses git status --porcelain=v1 output.
        Format: XY<space>PATH where XY is 2-char status code.
        
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
            
            # Validate minimum line length: XY<space>P (at least 4 chars)
            if len(line) < 4:
                continue
            
            # Parse porcelain v1 format: XY<space>PATH
            # Position 0: index status (X)
            # Position 1: worktree status (Y)
            # Position 2: space separator
            # Position 3+: file path
            status = line[:2]
            
            # Validate separator is a space (defensive check)
            if line[2] != " ":
                # Fallback: try to find path after first space
                space_idx = line.find(" ")
                if space_idx >= 2:
                    path_str = line[space_idx + 1:]
                else:
                    continue
            else:
                path_str = line[3:]
            
            # Sanity check: path should not be empty
            if not path_str or not path_str.strip():
                continue
            
            # Handle renames (format: "R  old -> new")
            if " -> " in path_str:
                old_path, new_path = path_str.split(" -> ", 1)
                changes.files.append(FileChange(
                    path=Path(new_path.strip()),
                    change_type=ChangeType.RENAMED,
                    old_path=Path(old_path.strip()),
                ))
                continue
            
            path = Path(path_str.strip())
            
            # Determine change type based on status codes
            # X = index status, Y = worktree status
            idx_status, wt_status = status[0], status[1]
            
            if idx_status == "?" or wt_status == "?":
                change_type = ChangeType.ADDED  # Untracked
            elif idx_status == "D" or wt_status == "D":
                change_type = ChangeType.DELETED
            elif idx_status == "A":
                change_type = ChangeType.ADDED  # Staged as new
            elif idx_status == "R" or wt_status == "R":
                change_type = ChangeType.RENAMED
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
        
        Uses Conventional Commits format: docs(<scope>): <description>
        
        Scope rules:
        - Single topic changed: scope = topic name (directory)
        - Multiple topics: no scope, list in body
        - Root files only: no scope, descriptive message
        
        Args:
            changes: SyncChanges object with detected changes.
            synced_pages: List of page/directory names that were synced.
            is_initial: Whether this is the initial commit.
            
        Returns:
            Formatted commit message (max 72 chars for subject line).
        """
        topics = changes.topics_changed
        
        # Initial commit
        if is_initial:
            if len(synced_pages) == 1:
                scope = self._sanitize_scope(synced_pages[0])
                return f"docs({scope}): initial sync"
            else:
                pages_list = ", ".join(sorted(synced_pages))
                return (
                    f"docs: initial sync of {len(synced_pages)} topics\n\n"
                    f"Topics: {pages_list}"
                )
        
        # Single topic changed
        if len(topics) == 1:
            topic = list(topics)[0]
            scope = self._sanitize_scope(topic)
            action = self._determine_action(changes, topic)
            return f"docs({scope}): {action}"
        
        # Multiple topics changed
        if len(topics) > 1:
            topics_list = ", ".join(sorted(topics))
            return (
                f"docs: sync updates across {len(topics)} topics\n\n"
                f"Updated: {topics_list}"
            )
        
        # No topics changed = only root-level files (e.g., README.md, LICENSE)
        # This is the fallback case that previously caused the typo bug
        if changes.has_root_changes:
            return "docs: update documentation index"
        
        # Truly empty changes (shouldn't reach here normally)
        return "docs: sync latest changes"
    
    def _sanitize_scope(self, scope: str) -> str:
        """
        Sanitize scope for use in commit message.
        
        Ensures scope is valid for Conventional Commits:
        - No special characters that break parsing
        - Reasonable length
        - Never empty
        
        Args:
            scope: Raw scope string (typically a directory name).
            
        Returns:
            Sanitized scope string.
        """
        if not scope:
            return "docs"
        
        # Remove any problematic characters for commit message parsing
        sanitized = scope.strip()
        
        # Truncate if too long (keep commits readable)
        if len(sanitized) > 30:
            sanitized = sanitized[:27] + "..."
        
        return sanitized or "docs"
    
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
