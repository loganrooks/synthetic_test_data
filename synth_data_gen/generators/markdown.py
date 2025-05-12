import os
import json # For JSON frontmatter
import random
from typing import Any, Dict, List

from ..core.base import BaseGenerator
from ..common.utils import ensure_output_directories # Assuming MD_DIR is handled by output_path

class MarkdownGenerator(BaseGenerator):
    """
    Generator for Markdown files.
    """
    GENERATOR_ID = "markdown"

    def get_default_specific_config(self) -> Dict[str, Any]:
        """
        Returns the default specific configuration for Markdown generation.
        Refer to specifications/synthetic_data_package_specification.md for details.
        """
        return {
            "headings_config": {"count": 5, "max_depth": 3}, # Unified Quantity for count
            "include_emphasis_styles": True,
            "md_list_items_config": {"count": 4, "max_nesting_depth": 2, "include_lists": True}, # Unified Quantity
            "include_links": True, # This might become part of a link_config object
            "md_images_config": {"count": 1, "include_images": True}, # Unified Quantity
            "include_blockquotes": True, # This might become part of a blockquote_config object
            "gfm_features": {
                "md_tables_occurrence_config": {"count": 0}, # Unified Quantity
                "md_footnotes_occurrence_config": {"count": 0}, # Unified Quantity
                "md_task_lists_occurrence_config": {"count": 0}, # Unified Quantity
                "md_code_blocks_config": {"count": 1, "include_code_blocks": True}, # Unified Quantity
            },
            "frontmatter": {
                "include_chance": 1.0,
                "style": "yaml", # yaml, toml, json
                "fields": {
                    "title": True, "author": True, "date": "2025-01-01",
                    "tags": ["synthetic", "test"], "custom_fields": []
                }
            },
            "md_variant": "basic_elements" # To select which content generation logic to use
        }

    def validate_config(self, specific_config: Dict[str, Any], global_config: Dict[str, Any]) -> bool:
        if not super().validate_config(specific_config, global_config):
            return False
        # Add Markdown-specific validation logic here
        if "md_variant" not in specific_config:
            print("Warning: md_variant not specified, using default.")
        return True

    def _generate_frontmatter(self, config: Dict[str, Any], global_config: Dict[str, Any]) -> str:
        fm_config = config.get("frontmatter", {})
        if not fm_config.get("include_chance", 0.0) >= (random.random() if isinstance(fm_config.get("include_chance"), float) else 1.0): # handle exact 1.0 too
            return ""

        style = fm_config.get("style", "yaml")
        fields = fm_config.get("fields", {})
        
        title = fields.get("title")
        if title is True: title = config.get("title", "Synthetic Markdown Document") # Get from main config if True
        elif not isinstance(title, str): title = "Default Title"

        author = fields.get("author")
        if author is True: author = global_config.get("default_author", "Synthetic Author")
        elif not isinstance(author, str): author = "Default Author"
        
        date_val = fields.get("date", "YYYY-MM-DD") # Placeholder
        tags = fields.get("tags", ["test"])
        custom_fields = fields.get("custom_fields", []) # Expects list of {"key": "k", "value": "v"}

        if style == "yaml":
            lines = ["---"]
            if title: lines.append(f"title: {title}")
            if author: lines.append(f"author: {author}")
            if date_val: lines.append(f"date: {date_val}")
            if tags: lines.append(f"tags: {json.dumps(tags)}") # Ensure proper list format
            for cf in custom_fields: lines.append(f"{cf.get('key', 'custom')}: {cf.get('value', 'default')}")
            lines.append("---")
            return "\n".join(lines) + "\n\n"
        elif style == "toml":
            lines = ["+++"]
            if title: lines.append(f'title = "{title}"')
            if author: lines.append(f'author = "{author}"')
            if date_val: lines.append(f'date = "{date_val}"')
            if tags: lines.append(f'tags = {json.dumps(tags)}') # TOML array
            for cf in custom_fields: lines.append(f'{cf.get("key", "custom")} = "{cf.get("value", "default")}"')
            lines.append("+++")
            return "\n".join(lines) + "\n\n"
        elif style == "json":
            fm_obj = {}
            if title: fm_obj["title"] = title
            if author: fm_obj["author"] = author
            if date_val: fm_obj["date"] = date_val
            if tags: fm_obj["tags"] = tags
            for cf in custom_fields: fm_obj[cf.get('key', 'custom')] = cf.get('value', 'default')
            return json.dumps(fm_obj, indent=2) + "\n\n"
        return ""


    def generate(self, specific_config: Dict[str, Any], global_config: Dict[str, Any], output_path: str) -> str:
        """
        Generates a single Markdown file.
        """
        ensure_output_directories(os.path.dirname(output_path))
        
        content = self._generate_frontmatter(specific_config, global_config)
        
        variant = specific_config.get("md_variant", "basic_elements")

        if variant == "basic_elements":
            content += self._create_md_basic_elements_content(specific_config, global_config)
        elif variant == "extended_elements":
            content += self._create_md_extended_elements_content(specific_config, global_config)
        elif variant == "json_frontmatter_variant": # Assuming JSON frontmatter is a variant itself
            # Frontmatter already handled, just need body
            content += "# Document with JSON Frontmatter\n\nThis is the main content."
        elif variant == "error_frontmatter_variant":
            # Frontmatter generation might need a flag to force error for this variant
            content = """---
title: Erroneous Frontmatter
author: Synthetic Data Generator
date: 2025-05-10
tags: [markdown, error
description: This frontmatter has an unclosed list and a missing colon.
another_field value_without_colon
---

# Document with Faulty Frontmatter

The YAML frontmatter above contains intentional syntax errors.
"""
        elif variant == "no_frontmatter_variant":
            content = "# Document Without Frontmatter\n\nThis Markdown document begins directly with content." # No frontmatter
        elif variant == "embedded_html":
            content += self._create_md_with_embedded_html_content(specific_config, global_config)
        elif variant == "with_latex":
            content += self._create_md_with_latex_content(specific_config, global_config)
        else:
            print(f"Warning: Unknown Markdown variant '{variant}'. Generating basic elements.")
            content += self._create_md_basic_elements_content(specific_config, global_config)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Error creating Markdown {output_path}: {e}") # Consider raising GeneratorError
            # Or return an error status/message
        return output_path

    # --- Helper methods for content generation, adapted from original functions ---

    def _create_md_basic_elements_content(self, specific_config: Dict[str, Any], global_config: Dict[str, Any]) -> str:
        headings_config = specific_config.get("headings_config", {"count": 3, "max_depth": 3})
        num_headings_to_generate = self._determine_count(headings_config, "headings")
        max_depth = headings_config.get("max_depth", 3)

        content = ""
        for i in range(num_headings_to_generate):
            current_depth = (i % max_depth) + 1
            content += f"{'#' * current_depth} Header Level {current_depth} - Instance {i+1}\n"
            content += f"This is some content under heading {i+1}.\n\n"

        # Keep other basic elements for now, will be driven by their own configs later
        content += "This document serves as a basic test for Markdown parsing.\n"
        content += "We explore *italicized text* and **bold text**. `inline code`.\n"
        # Config-driven list generation
        list_items_config = specific_config.get("md_list_items_config", {"count": 0, "include_lists": False})
        if list_items_config.get("include_lists", False):
            num_list_items = self._determine_count(list_items_config, "md_list_items")
            if num_list_items > 0:
                content += "\n" # Add a newline before the list
                # Determine list type (e.g., unordered, ordered) based on config if available
                # For now, default to unordered
                list_marker = "- "
                for i in range(num_list_items):
                    # Basic nesting example (not fully config-driven yet for nesting depth)
                    nest_depth = list_items_config.get("max_nesting_depth", 1) # Simplified
                    prefix = "  " * (i % nest_depth if nest_depth > 0 else 0) # Basic indent
                    content += f"{prefix}{list_marker}List item {i+1}\n"
                content += "\n" # Add a newline after the list
        
        content += "A link to a [resource](https://example.com/).\n"

        # Config-driven image generation
        images_config = specific_config.get("md_images_config", {"count": 0, "include_images": False})
        if images_config.get("include_images", False):
            num_images = self._determine_count(images_config, "md_images")
            if num_images > 0:
                content += "\n"
                for i in range(num_images):
                    alt_text = images_config.get("default_alt_text", "Placeholder image")
                    image_path = images_config.get("default_image_path", f"images/placeholder_{i+1}.jpg")
                    content += f"![{alt_text} {i+1}]({image_path})\n"
                content += "\n"
        
        content += "---\n> A blockquote.\n"
        return content

    def _create_md_extended_elements_content(self, specific_config: Dict[str, Any], global_config: Dict[str, Any]) -> str:
        gfm_config = specific_config.get("gfm_features", {})
        
        content = "# Extended Markdown Features\n"

        # Config-driven table generation
        tables_occurrence_config = gfm_config.get("md_tables_occurrence_config", {"count": 0})
        num_tables = self._determine_count(tables_occurrence_config, "md_tables")

        if num_tables > 0:
            content += "\n## Tables\n"
            for _ in range(num_tables):
                # Add a simple placeholder table structure
                content += "| Header 1 | Header 2 | Header 3 |\n"
                content += "|---|---|---|\n"
                content += "| Cell 1.1 | Cell 1.2 | Cell 1.3 |\n"
                content += "| Cell 2.1 | Cell 2.2 | Cell 2.3 |\n\n"
        
        content += "## Footnotes\nHere is text with a footnote.[^1]\n[^1]: This is a footnote.\n"
        content += "## Task Lists\n- [x] Done\n- [ ] To Do\n"
        content += "## Code Blocks\n```python\ndef test():\n  pass\n```\n"
        return content

    def _create_md_with_embedded_html_content(self, specific_config: Dict[str, Any], global_config: Dict[str, Any]) -> str:
        return """# Markdown with Embedded HTML
<div style="color: blue;">This is <b>HTML</b> text.</div>
Markdown text continues here.
"""

    def _create_md_with_latex_content(self, specific_config: Dict[str, Any], global_config: Dict[str, Any]) -> str:
        return """# Markdown with LaTeX
Inline LaTeX: $E = mc^2$.
Display LaTeX:
$$
\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}
$$
"""