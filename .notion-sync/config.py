"""
Configuration management for Notion → GitHub sync.

Loads settings from environment variables and provides
structured configuration for all sync components.
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class PageMapping:
    """Maps a Notion page to a local directory."""
    
    notion_page_id: str
    directory_name: str
    display_name: str
    description: str = ""
    
    @property
    def slug(self) -> str:
        """URL-safe directory name."""
        return self.directory_name


@dataclass
class Config:
    """
    Central configuration for the sync system.
    
    Loads from environment variables and provides defaults.
    All secrets are loaded from env vars - never hardcoded.
    """
    
    # Notion settings
    notion_token: str
    notion_parent_page_id: str
    
    # Git settings
    git_user_name: str
    git_user_email: str
    github_token: Optional[str] = None
    
    # Paths
    repo_root: Path = field(default_factory=lambda: Path.cwd())
    
    # Sync behavior
    debug: bool = False
    dry_run: bool = False
    force_sync: bool = False
    
    # Page mappings (populated after init)
    page_mappings: list[PageMapping] = field(default_factory=list)
    
    # Internal paths
    @property
    def sync_dir(self) -> Path:
        """Path to .notion-sync directory."""
        return self.repo_root / ".notion-sync"
    
    @property
    def state_file(self) -> Path:
        """Path to sync state JSON file."""
        return self.sync_dir / "state.json"
    
    @property
    def images_cache_dir(self) -> Path:
        """Temporary directory for downloading images."""
        return self.sync_dir / ".image-cache"
    
    @classmethod
    def from_env(cls, env_file: Optional[Path] = None) -> "Config":
        """
        Load configuration from environment variables.
        
        Args:
            env_file: Optional path to .env file. If not provided,
                     looks for .env in current directory.
        
        Returns:
            Configured Config instance.
            
        Raises:
            ValueError: If required environment variables are missing.
        """
        # Load .env file if it exists
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Required variables
        notion_token = os.getenv("NOTION_TOKEN")
        if not notion_token:
            raise ValueError(
                "NOTION_TOKEN environment variable is required.\n"
                "Create a Notion integration at https://www.notion.so/my-integrations"
            )
        
        notion_parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
        if not notion_parent_page_id:
            raise ValueError(
                "NOTION_PARENT_PAGE_ID environment variable is required.\n"
                "This should be the ID of your 'Tech Notes' page in Notion."
            )
        
        # Clean up the page ID (remove dashes if present)
        notion_parent_page_id = notion_parent_page_id.replace("-", "")
        
        # Git configuration (required)
        git_user_name = os.getenv("GIT_USER_NAME")
        if not git_user_name:
            raise ValueError(
                "GIT_USER_NAME environment variable is required.\n"
                "Set this to your name for git commits."
            )
        
        git_user_email = os.getenv("GIT_USER_EMAIL")
        if not git_user_email:
            raise ValueError(
                "GIT_USER_EMAIL environment variable is required.\n"
                "Set this to your email for git commits."
            )
        
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError(
                "GITHUB_TOKEN environment variable is required.\n"
                "Create a token at https://github.com/settings/tokens"
            )
        
        # Paths
        repo_root_str = os.getenv("REPO_ROOT")
        repo_root = Path(repo_root_str) if repo_root_str else Path.cwd()
        
        # Sync behavior
        debug = os.getenv("DEBUG", "false").lower() == "true"
        dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        force_sync = os.getenv("FORCE_SYNC", "false").lower() == "true"
        
        return cls(
            notion_token=notion_token,
            notion_parent_page_id=notion_parent_page_id,
            git_user_name=git_user_name,
            git_user_email=git_user_email,
            github_token=github_token,
            repo_root=repo_root,
            debug=debug,
            dry_run=dry_run,
            force_sync=force_sync,
        )
    
    def get_directory_for_page(self, page_title: str) -> str:
        """
        Generate a clean directory name from a Notion page title.
        
        Examples:
            "Linux" -> "linux"
            "SSH – Secure Shell" -> "ssh-secure-shell"
            "Git & GitHub" -> "git-github"
            "AWS – Amazon Web Services" -> "aws"
        
        Args:
            page_title: The Notion page title.
            
        Returns:
            A clean, URL-safe directory name.
        """
        # Special cases for known pages
        title_lower = page_title.lower()
        
        special_mappings = {
            "linux": "linux",
            "ssh": "ssh-secure-shell",
            "ssh – secure shell": "ssh-secure-shell",
            "git": "git-github",
            "git & github": "git-github",
            "aws": "aws",
            "aws – amazon web services": "aws",
            "docker": "docker",
            "kubernetes": "kubernetes",
            "jenkins": "jenkins",
            "spring boot": "spring-boot",
        }
        
        if title_lower in special_mappings:
            return special_mappings[title_lower]
        
        # Generic transformation
        # Remove special characters, replace spaces/dashes with single dash
        slug = re.sub(r'[–—]', '-', page_title)  # En/em dash to hyphen
        slug = re.sub(r'[&]', '-', slug)  # Ampersand to hyphen
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove other special chars
        slug = re.sub(r'[\s_]+', '-', slug)  # Spaces/underscores to hyphens
        slug = re.sub(r'-+', '-', slug)  # Multiple hyphens to single
        slug = slug.strip('-').lower()
        
        return slug
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        # Ensure repo_root is a Path
        if isinstance(self.repo_root, str):
            self.repo_root = Path(self.repo_root)
        
        # Create necessary directories
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        self.images_cache_dir.mkdir(parents=True, exist_ok=True)
