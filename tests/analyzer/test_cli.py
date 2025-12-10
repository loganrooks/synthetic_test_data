"""
Tests for the CLI module.
"""

import pytest
import sys
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import io

from synth_data_gen.analyzer.cli import (
    main,
    cmd_discover,
    cmd_add_patterns,
    cmd_validate,
    cmd_coverage,
    cmd_list,
)


class TestMain:
    """Tests for the main CLI entry point."""

    def test_no_command_shows_help(self, capsys):
        """Test that no command shows help and returns 1."""
        result = main([])

        assert result == 1

    def test_help_flag(self, capsys):
        """Test --help flag."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])

        assert exc_info.value.code == 0

    def test_discover_command_routing(self, tmp_path):
        """Test that discover command is properly routed."""
        epub_path = tmp_path / "test.epub"
        epub_path.touch()

        with patch("synth_data_gen.analyzer.cli.cmd_discover") as mock_cmd:
            mock_cmd.return_value = 0
            result = main(["discover", str(epub_path)])

        mock_cmd.assert_called_once()
        assert result == 0

    def test_validate_command_routing(self):
        """Test that validate command is properly routed."""
        with patch("synth_data_gen.analyzer.cli.cmd_validate") as mock_cmd:
            mock_cmd.return_value = 0
            result = main(["validate"])

        mock_cmd.assert_called_once()

    def test_list_command_routing(self):
        """Test that list command is properly routed."""
        with patch("synth_data_gen.analyzer.cli.cmd_list") as mock_cmd:
            mock_cmd.return_value = 0
            result = main(["list"])

        mock_cmd.assert_called_once()


class TestCmdDiscover:
    """Tests for the discover command."""

    @pytest.fixture
    def mock_epub(self, tmp_path):
        """Create a minimal test EPUB."""
        epub_path = tmp_path / "test.epub"

        with zipfile.ZipFile(epub_path, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip")
            zf.writestr(
                "META-INF/container.xml",
                """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>""",
            )
            zf.writestr(
                "content.opf",
                """<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
    <metadata><dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Test</dc:title></metadata>
    <manifest><item id="ch1" href="ch1.xhtml" media-type="application/xhtml+xml"/></manifest>
    <spine><itemref idref="ch1"/></spine>
</package>""",
            )
            zf.writestr(
                "ch1.xhtml",
                """<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body><h1>Test</h1></body>
</html>""",
            )

        return epub_path

    def test_discover_single_file(self, mock_epub, capsys):
        """Test discovering patterns in a single EPUB."""
        import argparse

        args = argparse.Namespace(
            epub_path=mock_epub,
            output=Path("candidates.yaml"),
        )

        result = cmd_discover(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Analyzing:" in captured.out

    def test_discover_directory(self, mock_epub, capsys):
        """Test discovering patterns in a directory."""
        import argparse

        args = argparse.Namespace(
            epub_path=mock_epub.parent,
            output=Path("candidates.yaml"),
        )

        result = cmd_discover(args)

        assert result == 0

    def test_discover_nonexistent_path(self, tmp_path, capsys):
        """Test error handling for non-existent path."""
        import argparse

        args = argparse.Namespace(
            epub_path=tmp_path / "nonexistent.epub",
            output=Path("candidates.yaml"),
        )

        result = cmd_discover(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()


class TestCmdAddPatterns:
    """Tests for the add-patterns command."""

    def test_file_not_found(self, tmp_path, capsys):
        """Test error handling for non-existent candidates file."""
        import argparse

        args = argparse.Namespace(
            candidates_file=tmp_path / "nonexistent.yaml",
            validate=False,
        )

        result = cmd_add_patterns(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()

    def test_empty_candidates(self, tmp_path, capsys):
        """Test handling empty candidates file."""
        import argparse
        import yaml

        candidates_file = tmp_path / "empty.yaml"
        with open(candidates_file, "w") as f:
            yaml.dump({}, f)

        args = argparse.Namespace(
            candidates_file=candidates_file,
            validate=False,
        )

        result = cmd_add_patterns(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "no candidates" in captured.out.lower()

    def test_skip_decision(self, tmp_path, capsys):
        """Test handling skip decision."""
        import argparse
        import yaml

        candidates_file = tmp_path / "candidates.yaml"
        candidates = {
            "candidates": [
                {"id": "test1", "decision": "skip"},
            ]
        }
        with open(candidates_file, "w") as f:
            yaml.dump(candidates, f)

        args = argparse.Namespace(
            candidates_file=candidates_file,
            validate=False,
        )

        result = cmd_add_patterns(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "skipping" in captured.out.lower()

    def test_new_pattern_decision(self, tmp_path, capsys):
        """Test handling new_pattern decision (not implemented)."""
        import argparse
        import yaml

        candidates_file = tmp_path / "candidates.yaml"
        candidates = {
            "candidates": [
                {
                    "id": "test1",
                    "decision": "new_pattern",
                    "pattern_name": "new_toc_style",
                },
            ]
        }
        with open(candidates_file, "w") as f:
            yaml.dump(candidates, f)

        args = argparse.Namespace(
            candidates_file=candidates_file,
            validate=False,
        )

        result = cmd_add_patterns(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "adding new pattern" in captured.out.lower()
        assert "not yet implemented" in captured.out.lower()


class TestCmdValidate:
    """Tests for the validate command."""

    @patch("synth_data_gen.analyzer.cli.validate_all_patterns")
    @patch("synth_data_gen.analyzer.cli.generate_validation_report")
    def test_validate_all(self, mock_report, mock_validate, capsys):
        """Test validating all patterns."""
        import argparse
        from synth_data_gen.analyzer.validation import ValidationResult

        mock_validate.return_value = [
            ValidationResult(pattern_id="test", success=True),
        ]
        mock_report.return_value = "Validation Report"

        args = argparse.Namespace(categories=None, patterns=None)

        result = cmd_validate(args)

        assert result == 0
        mock_validate.assert_called_once()

    @patch("synth_data_gen.analyzer.cli.validate_all_patterns")
    @patch("synth_data_gen.analyzer.cli.generate_validation_report")
    def test_validate_with_failures(self, mock_report, mock_validate, capsys):
        """Test validate command with failures returns non-zero."""
        import argparse
        from synth_data_gen.analyzer.validation import ValidationResult

        mock_validate.return_value = [
            ValidationResult(pattern_id="test", success=False, error="Failed"),
        ]
        mock_report.return_value = "Validation Report"

        args = argparse.Namespace(categories=None, patterns=None)

        result = cmd_validate(args)

        assert result == 1

    @patch("synth_data_gen.analyzer.cli.validate_all_patterns")
    @patch("synth_data_gen.analyzer.cli.generate_validation_report")
    def test_validate_by_category(self, mock_report, mock_validate, capsys):
        """Test validating by category."""
        import argparse
        from synth_data_gen.analyzer.validation import ValidationResult

        mock_validate.return_value = []
        mock_report.return_value = "Report"

        args = argparse.Namespace(categories=["toc_style"], patterns=None)

        cmd_validate(args)

        call_kwargs = mock_validate.call_args[1]
        assert call_kwargs["categories"] == ["toc_style"]


class TestCmdCoverage:
    """Tests for the coverage command."""

    def test_coverage_nonexistent_path(self, tmp_path, capsys):
        """Test error handling for non-existent path."""
        import argparse

        args = argparse.Namespace(epub_path=tmp_path / "nonexistent.epub")

        result = cmd_coverage(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()

    @patch("synth_data_gen.analyzer.cli.EpubAnalyzer")
    def test_coverage_single_file(self, mock_analyzer_class, tmp_path, capsys):
        """Test coverage report for single file."""
        import argparse

        epub_path = tmp_path / "test.epub"
        epub_path.touch()

        mock_analyzer = MagicMock()
        mock_result = MagicMock()
        mock_result.get_matched_pattern_ids.return_value = ["ncx_flat"]
        mock_analyzer.analyze.return_value = mock_result
        mock_analyzer_class.return_value = mock_analyzer

        args = argparse.Namespace(epub_path=epub_path)

        result = cmd_coverage(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "coverage report" in captured.out.lower()


class TestCmdList:
    """Tests for the list command."""

    def test_list_all_patterns(self, capsys):
        """Test listing all patterns."""
        import argparse

        args = argparse.Namespace(category=None)

        result = cmd_list(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "patterns" in captured.out.lower()

    def test_list_by_category(self, capsys):
        """Test listing patterns by category."""
        import argparse

        args = argparse.Namespace(category="toc_style")

        result = cmd_list(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "toc_style" in captured.out.lower()


class TestCLIIntegration:
    """Integration tests for CLI."""

    @pytest.fixture
    def test_epub(self, tmp_path):
        """Create a test EPUB for integration tests."""
        epub_path = tmp_path / "integration_test.epub"

        with zipfile.ZipFile(epub_path, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip")
            zf.writestr(
                "META-INF/container.xml",
                """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>""",
            )
            zf.writestr(
                "content.opf",
                """<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
    <metadata><dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Test</dc:title></metadata>
    <manifest>
        <item id="ch1" href="ch1.xhtml" media-type="application/xhtml+xml"/>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    </manifest>
    <spine toc="ncx"><itemref idref="ch1"/></spine>
</package>""",
            )
            zf.writestr(
                "toc.ncx",
                """<?xml version="1.0"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <navMap>
        <navPoint id="np1" playOrder="1">
            <navLabel><text>Chapter 1</text></navLabel>
            <content src="ch1.xhtml"/>
        </navPoint>
    </navMap>
</ncx>""",
            )
            zf.writestr(
                "ch1.xhtml",
                """<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body><h1>Chapter 1</h1><p>Content</p></body>
</html>""",
            )

        return epub_path

    def test_full_workflow_discover(self, test_epub, capsys):
        """Test full discover workflow."""
        result = main(["discover", str(test_epub)])

        assert result == 0
        captured = capsys.readouterr()
        assert "EPUB Version:" in captured.out

    def test_full_workflow_list(self, capsys):
        """Test full list workflow."""
        result = main(["list"])

        assert result == 0
        captured = capsys.readouterr()
        assert "pattern" in captured.out.lower()
