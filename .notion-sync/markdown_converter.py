"""
Notion blocks to Markdown converter.

Converts Notion's block structure to clean, readable Markdown.
Handles all common block types including:
- Text blocks (paragraphs, headings, quotes)
- Lists (bulleted, numbered, to-do, toggle)
- Code blocks (with language detection)
- Media (images, videos, embeds)
- Tables
- Callouts
- And more...
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from notion_api import NotionAPI, NotionBlock


@dataclass
class ConversionContext:
    """Context passed during markdown conversion."""
    
    # For image handling
    notion_api: NotionAPI
    images_dir: Path
    relative_images_path: str = "images"
    
    # Track downloaded images
    downloaded_images: list[Path] = field(default_factory=list)
    
    # Indentation level (for nested blocks)
    indent_level: int = 0
    
    # List tracking
    in_numbered_list: bool = False
    numbered_list_counter: int = 0


class MarkdownConverter:
    """
    Converts Notion blocks to Markdown.
    
    Handles recursive block structures and maintains proper formatting.
    """
    
    def __init__(self, notion_api: NotionAPI):
        """
        Initialize converter.
        
        Args:
            notion_api: NotionAPI instance for downloading images.
        """
        self.notion_api = notion_api
        
        # Block type handlers
        self._handlers: dict[str, Callable[[NotionBlock, ConversionContext], str]] = {
            "paragraph": self._convert_paragraph,
            "heading_1": self._convert_heading_1,
            "heading_2": self._convert_heading_2,
            "heading_3": self._convert_heading_3,
            "bulleted_list_item": self._convert_bulleted_list_item,
            "numbered_list_item": self._convert_numbered_list_item,
            "to_do": self._convert_todo,
            "toggle": self._convert_toggle,
            "code": self._convert_code,
            "quote": self._convert_quote,
            "callout": self._convert_callout,
            "divider": self._convert_divider,
            "image": self._convert_image,
            "video": self._convert_video,
            "embed": self._convert_embed,
            "bookmark": self._convert_bookmark,
            "link_preview": self._convert_link_preview,
            "table": self._convert_table,
            "table_row": self._convert_table_row,
            "column_list": self._convert_column_list,
            "column": self._convert_column,
            "child_page": self._convert_child_page,
            "child_database": self._convert_child_database,
            "synced_block": self._convert_synced_block,
            "template": self._convert_template,
            "equation": self._convert_equation,
            "breadcrumb": self._convert_breadcrumb,
            "table_of_contents": self._convert_toc,
            "file": self._convert_file,
            "pdf": self._convert_pdf,
            "audio": self._convert_audio,
        }
    
    def convert(
        self,
        blocks: list[NotionBlock],
        images_dir: Path,
        relative_images_path: str = "images",
    ) -> tuple[str, list[Path]]:
        """
        Convert a list of Notion blocks to Markdown.
        
        Args:
            blocks: List of NotionBlock objects.
            images_dir: Directory to save downloaded images.
            relative_images_path: Relative path for image references in markdown.
            
        Returns:
            Tuple of (markdown_content, list_of_downloaded_images).
        """
        context = ConversionContext(
            notion_api=self.notion_api,
            images_dir=images_dir,
            relative_images_path=relative_images_path,
        )
        
        lines = []
        prev_block_type = None
        
        for block in blocks:
            # Add spacing between different block types
            if prev_block_type and self._needs_spacing(prev_block_type, block.type):
                lines.append("")
            
            # Reset numbered list counter if not in a numbered list
            if block.type != "numbered_list_item":
                context.numbered_list_counter = 0
            
            # Convert block
            markdown = self._convert_block(block, context)
            if markdown is not None:
                lines.append(markdown)
            
            prev_block_type = block.type
        
        # Clean up output
        content = "\n".join(lines)
        content = self._normalize_whitespace(content)
        
        return content, context.downloaded_images
    
    def _convert_block(self, block: NotionBlock, context: ConversionContext) -> Optional[str]:
        """Convert a single block to markdown."""
        handler = self._handlers.get(block.type)
        
        if handler:
            return handler(block, context)
        else:
            # Unknown block type - add a comment
            return f"<!-- Unsupported block type: {block.type} -->"
    
    def _convert_children(
        self,
        blocks: list[NotionBlock],
        context: ConversionContext,
        indent: bool = True,
    ) -> str:
        """Convert child blocks with proper indentation."""
        if not blocks:
            return ""
        
        # Increase indent level
        if indent:
            context.indent_level += 1
        
        lines = []
        for block in blocks:
            markdown = self._convert_block(block, context)
            if markdown is not None:
                if indent:
                    # Add indentation
                    indented = self._indent_text(markdown, context.indent_level)
                    lines.append(indented)
                else:
                    lines.append(markdown)
        
        if indent:
            context.indent_level -= 1
        
        return "\n".join(lines)
    
    # =========================================================================
    # Rich text handling
    # =========================================================================
    
    def _rich_text_to_markdown(self, rich_text: list[dict]) -> str:
        """Convert Notion rich text array to markdown string."""
        if not rich_text:
            return ""
        
        parts = []
        for text_obj in rich_text:
            content = text_obj.get("plain_text", "")
            annotations = text_obj.get("annotations", {})
            href = text_obj.get("href")
            
            # Apply formatting
            if annotations.get("code"):
                content = f"`{content}`"
            if annotations.get("bold"):
                content = f"**{content}**"
            if annotations.get("italic"):
                content = f"*{content}*"
            if annotations.get("strikethrough"):
                content = f"~~{content}~~"
            if annotations.get("underline"):
                # Markdown doesn't have underline, use HTML
                content = f"<u>{content}</u>"
            
            # Apply link
            if href:
                content = f"[{content}]({href})"
            
            parts.append(content)
        
        return "".join(parts)
    
    # =========================================================================
    # Block type handlers
    # =========================================================================
    
    def _convert_paragraph(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert paragraph block."""
        text = self._rich_text_to_markdown(block.content.get("rich_text", []))
        
        # Handle children (rare but possible)
        if block.children:
            children = self._convert_children(block.children, context)
            return f"{text}\n{children}"
        
        return text
    
    def _convert_heading_1(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert heading 1 block."""
        text = self._rich_text_to_markdown(block.content.get("rich_text", []))
        return f"# {text}"
    
    def _convert_heading_2(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert heading 2 block."""
        text = self._rich_text_to_markdown(block.content.get("rich_text", []))
        return f"## {text}"
    
    def _convert_heading_3(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert heading 3 block."""
        text = self._rich_text_to_markdown(block.content.get("rich_text", []))
        return f"### {text}"
    
    def _convert_bulleted_list_item(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert bulleted list item."""
        text = self._rich_text_to_markdown(block.content.get("rich_text", []))
        result = f"- {text}"
        
        if block.children:
            children = self._convert_children(block.children, context)
            result = f"{result}\n{children}"
        
        return result
    
    def _convert_numbered_list_item(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert numbered list item."""
        context.numbered_list_counter += 1
        text = self._rich_text_to_markdown(block.content.get("rich_text", []))
        result = f"{context.numbered_list_counter}. {text}"
        
        if block.children:
            children = self._convert_children(block.children, context)
            result = f"{result}\n{children}"
        
        return result
    
    def _convert_todo(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert to-do block."""
        text = self._rich_text_to_markdown(block.content.get("rich_text", []))
        checked = block.content.get("checked", False)
        checkbox = "[x]" if checked else "[ ]"
        result = f"- {checkbox} {text}"
        
        if block.children:
            children = self._convert_children(block.children, context)
            result = f"{result}\n{children}"
        
        return result
    
    def _convert_toggle(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert toggle block to details/summary HTML."""
        text = self._rich_text_to_markdown(block.content.get("rich_text", []))
        
        result = f"<details>\n<summary>{text}</summary>\n"
        
        if block.children:
            children = self._convert_children(block.children, context, indent=False)
            result += f"\n{children}\n"
        
        result += "</details>"
        return result
    
    def _convert_code(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert code block."""
        code = self._rich_text_to_markdown(block.content.get("rich_text", []))
        language = block.content.get("language", "").lower()
        
        # Map Notion language names to markdown
        language_map = {
            "plain text": "",
            "javascript": "javascript",
            "typescript": "typescript",
            "python": "python",
            "java": "java",
            "c++": "cpp",
            "c#": "csharp",
            "ruby": "ruby",
            "go": "go",
            "rust": "rust",
            "shell": "bash",
            "bash": "bash",
            "sql": "sql",
            "json": "json",
            "yaml": "yaml",
            "xml": "xml",
            "html": "html",
            "css": "css",
            "markdown": "markdown",
            "dockerfile": "dockerfile",
        }
        
        lang = language_map.get(language, language)
        
        # Handle caption
        caption = self._rich_text_to_markdown(block.content.get("caption", []))
        
        result = f"```{lang}\n{code}\n```"
        
        if caption:
            result += f"\n*{caption}*"
        
        return result
    
    def _convert_quote(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert quote block."""
        text = self._rich_text_to_markdown(block.content.get("rich_text", []))
        
        # Split by lines and add > prefix
        lines = text.split("\n")
        quoted = "\n".join(f"> {line}" for line in lines)
        
        if block.children:
            children = self._convert_children(block.children, context, indent=False)
            # Quote children too
            children_lines = children.split("\n")
            quoted_children = "\n".join(f"> {line}" for line in children_lines)
            quoted = f"{quoted}\n{quoted_children}"
        
        return quoted
    
    def _convert_callout(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert callout block to blockquote with emoji."""
        text = self._rich_text_to_markdown(block.content.get("rich_text", []))
        
        # Get icon
        icon = ""
        icon_data = block.content.get("icon", {})
        if icon_data.get("type") == "emoji":
            icon = icon_data.get("emoji", "")
        
        # Format as blockquote with icon
        prefix = f"> {icon} " if icon else "> "
        
        lines = text.split("\n")
        result = "\n".join(f"{prefix}{line}" if i == 0 else f"> {line}" 
                         for i, line in enumerate(lines))
        
        if block.children:
            children = self._convert_children(block.children, context, indent=False)
            children_lines = children.split("\n")
            quoted_children = "\n".join(f"> {line}" for line in children_lines)
            result = f"{result}\n{quoted_children}"
        
        return result
    
    def _convert_divider(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert divider block."""
        return "---"
    
    def _convert_image(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert image block, downloading if needed."""
        image_data = block.content
        
        # Get image URL
        url = None
        if image_data.get("type") == "external":
            url = image_data.get("external", {}).get("url")
        elif image_data.get("type") == "file":
            url = image_data.get("file", {}).get("url")
        
        if not url:
            return "<!-- Image URL not found -->"
        
        # Download image
        downloaded_path = context.notion_api.download_image(
            url, context.images_dir
        )
        
        if downloaded_path:
            context.downloaded_images.append(downloaded_path)
            relative_path = f"{context.relative_images_path}/{downloaded_path.name}"
        else:
            # Fallback to original URL
            relative_path = url
        
        # Get caption
        caption = self._rich_text_to_markdown(image_data.get("caption", []))
        alt_text = caption if caption else "Image"
        
        result = f"![{alt_text}]({relative_path})"
        
        if caption:
            result += f"\n*{caption}*"
        
        return result
    
    def _convert_video(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert video block."""
        video_data = block.content
        
        url = None
        if video_data.get("type") == "external":
            url = video_data.get("external", {}).get("url")
        elif video_data.get("type") == "file":
            url = video_data.get("file", {}).get("url")
        
        if not url:
            return "<!-- Video URL not found -->"
        
        caption = self._rich_text_to_markdown(video_data.get("caption", []))
        
        # Check for YouTube/Vimeo for embedding
        if "youtube.com" in url or "youtu.be" in url:
            result = f"[![Video]({url})]({url})"
        else:
            result = f"[Video]({url})"
        
        if caption:
            result += f"\n*{caption}*"
        
        return result
    
    def _convert_embed(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert embed block."""
        url = block.content.get("url", "")
        caption = self._rich_text_to_markdown(block.content.get("caption", []))
        
        result = f"[Embedded content]({url})"
        
        if caption:
            result += f"\n*{caption}*"
        
        return result
    
    def _convert_bookmark(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert bookmark block."""
        url = block.content.get("url", "")
        caption = self._rich_text_to_markdown(block.content.get("caption", []))
        
        title = caption if caption else url
        return f"🔗 [{title}]({url})"
    
    def _convert_link_preview(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert link preview block."""
        url = block.content.get("url", "")
        return f"[{url}]({url})"
    
    def _convert_table(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert table block."""
        if not block.children:
            return "<!-- Empty table -->"
        
        has_header = block.content.get("has_column_header", False)
        rows = []
        
        for i, row_block in enumerate(block.children):
            if row_block.type != "table_row":
                continue
            
            cells = row_block.content.get("cells", [])
            row_text = " | ".join(
                self._rich_text_to_markdown(cell) for cell in cells
            )
            rows.append(f"| {row_text} |")
            
            # Add header separator after first row
            if i == 0 and has_header:
                separator = " | ".join("---" for _ in cells)
                rows.append(f"| {separator} |")
        
        return "\n".join(rows)
    
    def _convert_table_row(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert table row (handled by table parent)."""
        return ""
    
    def _convert_column_list(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert column list (multi-column layout)."""
        # Flatten columns into sequential content
        if not block.children:
            return ""
        
        parts = []
        for col_block in block.children:
            if col_block.children:
                col_content = self._convert_children(col_block.children, context, indent=False)
                parts.append(col_content)
        
        return "\n\n".join(parts)
    
    def _convert_column(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert column (handled by column_list parent)."""
        return ""
    
    def _convert_child_page(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert child page reference."""
        title = block.content.get("title", "Untitled")
        return f"📄 **{title}** (subpage)"
    
    def _convert_child_database(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert child database reference."""
        title = block.content.get("title", "Untitled Database")
        return f"🗃️ **{title}** (database)"
    
    def _convert_synced_block(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert synced block."""
        if block.children:
            return self._convert_children(block.children, context, indent=False)
        return ""
    
    def _convert_template(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert template block."""
        text = self._rich_text_to_markdown(block.content.get("rich_text", []))
        return f"📋 Template: {text}"
    
    def _convert_equation(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert equation block (LaTeX)."""
        expression = block.content.get("expression", "")
        return f"$$\n{expression}\n$$"
    
    def _convert_breadcrumb(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert breadcrumb (not meaningful in static export)."""
        return ""
    
    def _convert_toc(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert table of contents (auto-generated, skip)."""
        return "<!-- Table of Contents (auto-generated in Notion) -->"
    
    def _convert_file(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert file attachment block."""
        file_data = block.content
        
        url = None
        name = "File"
        
        if file_data.get("type") == "external":
            url = file_data.get("external", {}).get("url")
        elif file_data.get("type") == "file":
            url = file_data.get("file", {}).get("url")
            name = file_data.get("name", "File")
        
        if url:
            return f"📎 [{name}]({url})"
        return "<!-- File not found -->"
    
    def _convert_pdf(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert PDF block."""
        pdf_data = block.content
        
        url = None
        if pdf_data.get("type") == "external":
            url = pdf_data.get("external", {}).get("url")
        elif pdf_data.get("type") == "file":
            url = pdf_data.get("file", {}).get("url")
        
        caption = self._rich_text_to_markdown(pdf_data.get("caption", []))
        
        if url:
            result = f"📄 [PDF Document]({url})"
            if caption:
                result += f"\n*{caption}*"
            return result
        return "<!-- PDF not found -->"
    
    def _convert_audio(self, block: NotionBlock, context: ConversionContext) -> str:
        """Convert audio block."""
        audio_data = block.content
        
        url = None
        if audio_data.get("type") == "external":
            url = audio_data.get("external", {}).get("url")
        elif audio_data.get("type") == "file":
            url = audio_data.get("file", {}).get("url")
        
        if url:
            return f"🎵 [Audio]({url})"
        return "<!-- Audio not found -->"
    
    # =========================================================================
    # Utilities
    # =========================================================================
    
    def _needs_spacing(self, prev_type: str, curr_type: str) -> bool:
        """Determine if spacing is needed between block types."""
        # Always add space before headings
        if curr_type.startswith("heading_"):
            return True
        
        # Add space after headings
        if prev_type.startswith("heading_"):
            return True
        
        # Add space between different list types
        list_types = {"bulleted_list_item", "numbered_list_item", "to_do"}
        if prev_type in list_types and curr_type not in list_types:
            return True
        if prev_type not in list_types and curr_type in list_types:
            return True
        
        # Add space around code blocks
        if prev_type == "code" or curr_type == "code":
            return True
        
        # Add space around dividers
        if prev_type == "divider" or curr_type == "divider":
            return True
        
        return False
    
    def _indent_text(self, text: str, level: int) -> str:
        """Add indentation to text."""
        indent = "  " * level  # 2 spaces per level
        lines = text.split("\n")
        return "\n".join(f"{indent}{line}" for line in lines)
    
    def _normalize_whitespace(self, content: str) -> str:
        """Normalize whitespace in the output."""
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in content.split("\n")]
        
        # Remove excessive blank lines (more than 2 consecutive)
        result = []
        blank_count = 0
        
        for line in lines:
            if not line:
                blank_count += 1
                if blank_count <= 2:
                    result.append(line)
            else:
                blank_count = 0
                result.append(line)
        
        # Ensure single trailing newline
        content = "\n".join(result).strip() + "\n"
        
        return content
