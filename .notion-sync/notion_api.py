"""
Notion API wrapper for the sync system.

Provides a clean interface to Notion's API with:
- Rate limiting compliance
- Recursive block fetching
- Image downloading
- Error handling
"""

import hashlib
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import requests
from notion_client import Client
from notion_client.errors import APIResponseError
from ratelimit import limits, sleep_and_retry
from rich.console import Console

from config import Config

console = Console()

# Notion API rate limit: 3 requests per second
RATE_LIMIT_CALLS = 3
RATE_LIMIT_PERIOD = 1  # second


@dataclass
class NotionPage:
    """Represents a Notion page with metadata."""
    
    id: str
    title: str
    last_edited_time: datetime
    created_time: datetime
    url: str
    icon: Optional[str] = None
    cover: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, page: dict) -> "NotionPage":
        """Create NotionPage from API response."""
        # Extract title from properties
        title = ""
        if "properties" in page:
            title_prop = page["properties"].get("title", {})
            if "title" in title_prop and title_prop["title"]:
                title = title_prop["title"][0].get("plain_text", "")
        
        # Fallback: try to get from child_page type
        if not title and page.get("type") == "child_page":
            title = page.get("child_page", {}).get("title", "")
        
        # Extract icon
        icon = None
        if page.get("icon"):
            if page["icon"]["type"] == "emoji":
                icon = page["icon"]["emoji"]
            elif page["icon"]["type"] == "external":
                icon = page["icon"]["external"]["url"]
        
        # Extract cover
        cover = None
        if page.get("cover"):
            if page["cover"]["type"] == "external":
                cover = page["cover"]["external"]["url"]
            elif page["cover"]["type"] == "file":
                cover = page["cover"]["file"]["url"]
        
        return cls(
            id=page["id"].replace("-", ""),
            title=title,
            last_edited_time=datetime.fromisoformat(
                page["last_edited_time"].replace("Z", "+00:00")
            ),
            created_time=datetime.fromisoformat(
                page["created_time"].replace("Z", "+00:00")
            ),
            url=page.get("url", ""),
            icon=icon,
            cover=cover,
        )


@dataclass
class NotionBlock:
    """Represents a Notion block."""
    
    id: str
    type: str
    has_children: bool
    content: dict
    children: list["NotionBlock"]
    
    @classmethod
    def from_api_response(cls, block: dict) -> "NotionBlock":
        """Create NotionBlock from API response."""
        block_type = block["type"]
        content = block.get(block_type, {})
        
        return cls(
            id=block["id"].replace("-", ""),
            type=block_type,
            has_children=block.get("has_children", False),
            content=content,
            children=[],
        )


class NotionAPI:
    """
    Wrapper around Notion API with rate limiting and utilities.
    
    Handles:
    - Authentication
    - Rate limiting (3 req/sec)
    - Recursive block fetching
    - Image downloading
    - Error handling with retries
    """
    
    def __init__(self, config: Config):
        """
        Initialize the Notion API client.
        
        Args:
            config: Configuration instance with Notion token.
        """
        self.config = config
        self.client = Client(auth=config.notion_token)
        self._request_count = 0
    
    @sleep_and_retry
    @limits(calls=RATE_LIMIT_CALLS, period=RATE_LIMIT_PERIOD)
    def _rate_limited_call(self, func, *args, **kwargs) -> Any:
        """Execute a rate-limited API call."""
        self._request_count += 1
        return func(*args, **kwargs)
    
    def get_child_pages(self, parent_page_id: str) -> list[NotionPage]:
        """
        Get all child pages of a parent page.
        
        Args:
            parent_page_id: The ID of the parent page.
            
        Returns:
            List of NotionPage objects for child pages.
        """
        pages = []
        has_more = True
        start_cursor = None
        
        # Format page ID with dashes for API
        formatted_id = self._format_page_id(parent_page_id)
        
        while has_more:
            try:
                response = self._rate_limited_call(
                    self.client.blocks.children.list,
                    block_id=formatted_id,
                    start_cursor=start_cursor,
                )
                
                for block in response.get("results", []):
                    if block["type"] == "child_page":
                        # Fetch full page details
                        page_id = block["id"]
                        page_details = self._rate_limited_call(
                            self.client.pages.retrieve,
                            page_id=page_id,
                        )
                        
                        # Merge child_page title with page details
                        page_details["child_page"] = block.get("child_page", {})
                        pages.append(NotionPage.from_api_response(page_details))
                
                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor")
                
            except APIResponseError as e:
                console.print(f"[red]API Error fetching child pages: {e}[/red]")
                raise
        
        return pages
    
    def get_page(self, page_id: str) -> NotionPage:
        """
        Get a single page by ID.
        
        Args:
            page_id: The Notion page ID.
            
        Returns:
            NotionPage object.
        """
        formatted_id = self._format_page_id(page_id)
        
        try:
            response = self._rate_limited_call(
                self.client.pages.retrieve,
                page_id=formatted_id,
            )
            return NotionPage.from_api_response(response)
        except APIResponseError as e:
            console.print(f"[red]API Error fetching page {page_id}: {e}[/red]")
            raise
    
    def get_page_blocks(self, page_id: str, recursive: bool = True) -> list[NotionBlock]:
        """
        Get all blocks from a page.
        
        Args:
            page_id: The Notion page ID.
            recursive: Whether to fetch children recursively.
            
        Returns:
            List of NotionBlock objects (with children populated if recursive).
        """
        return self._fetch_blocks(page_id, recursive)
    
    def _fetch_blocks(self, block_id: str, recursive: bool) -> list[NotionBlock]:
        """Recursively fetch blocks."""
        blocks = []
        has_more = True
        start_cursor = None
        
        formatted_id = self._format_page_id(block_id)
        
        while has_more:
            try:
                response = self._rate_limited_call(
                    self.client.blocks.children.list,
                    block_id=formatted_id,
                    start_cursor=start_cursor,
                )
                
                for block_data in response.get("results", []):
                    block = NotionBlock.from_api_response(block_data)
                    
                    # Recursively fetch children if needed
                    if recursive and block.has_children:
                        block.children = self._fetch_blocks(block.id, recursive)
                    
                    blocks.append(block)
                
                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor")
                
            except APIResponseError as e:
                console.print(f"[red]API Error fetching blocks: {e}[/red]")
                raise
        
        return blocks
    
    def download_image(
        self,
        url: str,
        target_dir: Path,
        filename: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Download an image from a URL to the target directory.
        
        Args:
            url: The image URL (can be Notion-hosted or external).
            target_dir: Directory to save the image.
            filename: Optional filename. If not provided, generates from URL.
            
        Returns:
            Path to downloaded image, or None if download failed.
        """
        try:
            # Generate filename if not provided
            if not filename:
                # Create deterministic filename from URL hash
                url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
                
                # Try to get extension from URL
                parsed = urlparse(url)
                path_ext = Path(parsed.path).suffix
                
                # Default to .png if no extension found
                ext = path_ext if path_ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"] else ".png"
                filename = f"image-{url_hash}{ext}"
            
            target_path = target_dir / filename
            
            # Skip if already downloaded
            if target_path.exists():
                return target_path
            
            # Download with timeout
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Ensure directory exists
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(target_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return target_path
            
        except requests.RequestException as e:
            console.print(f"[yellow]Warning: Failed to download image {url}: {e}[/yellow]")
            return None
        except Exception as e:
            console.print(f"[yellow]Warning: Error saving image: {e}[/yellow]")
            return None
    
    def _format_page_id(self, page_id: str) -> str:
        """
        Format a page ID for API calls.
        
        Notion API sometimes requires dashes, sometimes doesn't.
        This ensures consistent formatting.
        """
        # Remove existing dashes
        clean_id = page_id.replace("-", "")
        
        # Add dashes in standard UUID format
        if len(clean_id) == 32:
            return f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"
        
        return page_id
    
    @property
    def request_count(self) -> int:
        """Number of API requests made."""
        return self._request_count
