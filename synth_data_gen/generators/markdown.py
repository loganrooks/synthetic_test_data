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
            "headings_config": 5,
            "max_heading_depth": 3,
            "include_emphasis_styles": True,
            "include_lists": True,
            "md_list_items_config": 4,
            "list_max_nesting_depth": 2,
            "include_links": True,
            "include_images": True,
            "md_images_config": 1,
            "include_blockquotes": True,
            "gfm_features": {
                "md_tables_occurrence_config": 0,
                "md_footnotes_occurrence_config": 0,
                "md_task_lists_occurrence_config": 0,
                "include_code_blocks": True,
                "md_code_blocks_config": 1,
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
        # Use specific_config to customize content, e.g., number of list items, heading depth
        num_headings = specific_config.get("headings_config", 3) # Simplified
        if isinstance(num_headings, dict): num_headings = num_headings.get("min", 3)

        content = f"# Header 1: The Nature of Synthesis (Configurable: {num_headings} headings planned)\n"
        content += "This document serves as a basic test for Markdown parsing.\n"
        content += "## Header 2: Elements of Style\n"
        content += "We explore *italicized text* and **bold text**. `inline code`.\n"
        content += "### Header 3: Lists\n"
        content += "- Item Alpha\n  - Nested Alpha.1\n- Item Beta\n"
        content += "1. First step\n   1. Sub-step 1.1\n2. Second step\n"
        content += "A link to a [resource](https://example.com/).\n"
        content += "![Placeholder image](images/placeholder.jpg)\n"
        content += "---\n> A blockquote.\n"
        return content

    def _create_md_extended_elements_content(self, specific_config: Dict[str, Any], global_config: Dict[str, Any]) -> str:
        gfm_config = specific_config.get("gfm_features", {})
        tables_config = gfm_config.get("md_tables_occurrence_config", 0)
        if isinstance(tables_config, dict): tables_config = tables_config.get("min", 0)
        
        content = "# Extended Markdown Features\n"
        if tables_config > 0:
            content += "## Tables\n"
            content += "| Header 1 | Header 2 |\n|---|---|\n| Cell 1 | Cell 2 |\n"
        
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