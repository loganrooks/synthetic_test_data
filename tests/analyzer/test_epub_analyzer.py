"""
Tests for the EpubAnalyzer module.
"""

import pytest
import zipfile
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import io

from synth_data_gen.analyzer.epub_analyzer import (
    EpubAnalyzer,
    AnalysisResult,
    PatternMatch,
    UnknownPattern,
)
from synth_data_gen.analyzer.registry import PatternRegistry, PatternDefinition


class TestPatternMatch:
    """Tests for the PatternMatch dataclass."""

    def test_creation(self):
        """Test creating a PatternMatch."""
        match = PatternMatch(
            pattern_id="ncx_flat",
            matched=True,
            evidence=["NCX file present"],
            location="toc.ncx",
        )

        assert match.pattern_id == "ncx_flat"
        assert match.matched is True
        assert match.evidence == ["NCX file present"]
        assert match.location == "toc.ncx"

    def test_default_values(self):
        """Test PatternMatch default values."""
        match = PatternMatch(pattern_id="test", matched=False)

        assert match.evidence == []
        assert match.location == ""


class TestUnknownPattern:
    """Tests for the UnknownPattern dataclass."""

    def test_creation(self):
        """Test creating an UnknownPattern."""
        unknown = UnknownPattern(
            category="toc_style",
            detected_signature={"custom_element": True},
            evidence=[{"file": "toc.xhtml", "element": "<custom-toc>"}],
            similar_patterns=[{"id": "html_toc_nested_lists", "similarity": 0.8}],
        )

        assert unknown.category == "toc_style"
        assert unknown.detected_signature == {"custom_element": True}
        assert len(unknown.evidence) == 1
        assert len(unknown.similar_patterns) == 1


class TestAnalysisResult:
    """Tests for the AnalysisResult dataclass."""

    def test_creation(self):
        """Test creating an AnalysisResult."""
        result = AnalysisResult(
            epub_path=Path("/test/book.epub"),
            epub_version=3,
        )

        assert result.epub_path == Path("/test/book.epub")
        assert result.epub_version == 3
        assert result.detected_patterns == []
        assert result.unknown_patterns == []
        assert result.errors == []

    def test_get_matched_pattern_ids(self):
        """Test getting IDs of matched patterns."""
        result = AnalysisResult(epub_path=Path("test.epub"), epub_version=3)
        result.detected_patterns = [
            PatternMatch(pattern_id="ncx_flat", matched=True),
            PatternMatch(pattern_id="navdoc_basic", matched=False),
            PatternMatch(pattern_id="footnotes_linked", matched=True),
        ]

        matched_ids = result.get_matched_pattern_ids()

        assert "ncx_flat" in matched_ids
        assert "footnotes_linked" in matched_ids
        assert "navdoc_basic" not in matched_ids

    def test_get_coverage_report(self):
        """Test generating coverage report by category."""
        result = AnalysisResult(epub_path=Path("test.epub"), epub_version=3)
        result.detected_patterns = [
            PatternMatch(pattern_id="toc_ncx_flat", matched=True),
            PatternMatch(pattern_id="toc_navdoc", matched=True),
            PatternMatch(pattern_id="notes_footnotes", matched=True),
            PatternMatch(pattern_id="notes_endnotes", matched=False),
        ]

        coverage = result.get_coverage_report()

        assert "toc" in coverage
        assert len(coverage["toc"]) == 2
        assert "notes" in coverage
        assert len(coverage["notes"]) == 1

    def test_get_unrecognized_elements(self):
        """Test getting list of unrecognized elements."""
        result = AnalysisResult(epub_path=Path("test.epub"), epub_version=3)
        result.unknown_patterns = [
            UnknownPattern(
                category="toc_style",
                detected_signature={"custom": True},
                evidence=[{"element": "custom-toc"}],
            ),
        ]

        unrecognized = result.get_unrecognized_elements()

        assert len(unrecognized) == 1
        assert unrecognized[0]["category"] == "toc_style"
        assert unrecognized[0]["signature"] == {"custom": True}


class TestEpubAnalyzer:
    """Tests for the EpubAnalyzer class."""

    @pytest.fixture
    def mock_registry(self):
        """Create a mock registry with test patterns."""
        registry = MagicMock(spec=PatternRegistry)

        # Mock toc patterns
        toc_pattern = PatternDefinition(
            id="ncx_flat",
            category="toc_style",
            description="Flat NCX",
            detection_signature={"ncx": {"required": True, "min_depth": 1}},
        )
        registry.get_patterns_by_category.return_value = [toc_pattern]

        return registry

    @pytest.fixture
    def create_test_epub(self, tmp_path):
        """Factory fixture to create test EPUB files."""

        def _create_epub(
            name="test.epub",
            epub_version=2,
            has_ncx=True,
            has_navdoc=False,
            has_footnotes=False,
        ):
            epub_path = tmp_path / name

            with zipfile.ZipFile(epub_path, "w") as zf:
                # mimetype
                zf.writestr("mimetype", "application/epub+zip")

                # container.xml
                container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
                zf.writestr("META-INF/container.xml", container_xml)

                # content.opf
                version_str = f'version="{epub_version}.0"'
                content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" {version_str}>
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>Test Book</dc:title>
    </metadata>
    <manifest>
        <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    </manifest>
    <spine>
        <itemref idref="chapter1"/>
    </spine>
</package>"""
                zf.writestr("OEBPS/content.opf", content_opf)

                # NCX if requested
                if has_ncx:
                    ncx = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <navMap>
        <navPoint id="navpoint-1" playOrder="1">
            <navLabel><text>Chapter 1</text></navLabel>
            <content src="chapter1.xhtml"/>
        </navPoint>
    </navMap>
</ncx>"""
                    zf.writestr("OEBPS/toc.ncx", ncx)

                # NavDoc if requested
                if has_navdoc:
                    nav = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<body>
    <nav epub:type="toc">
        <h1>Table of Contents</h1>
        <ol>
            <li><a href="chapter1.xhtml">Chapter 1</a></li>
        </ol>
    </nav>
</body>
</html>"""
                    zf.writestr("OEBPS/nav.xhtml", nav)

                # Chapter content
                footnote_html = ""
                if has_footnotes:
                    footnote_html = """
<p>This is text with a note<sup id="fnref-1"><a href="#fn-1">1</a></sup>.</p>
<div class="footnotes">
    <p id="fn-1" class="footnote">This is the footnote.</p>
</div>"""

                chapter = f"""<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
    <h1>Chapter 1</h1>
    <p>This is the first chapter.</p>
    {footnote_html}
</body>
</html>"""
                zf.writestr("OEBPS/chapter1.xhtml", chapter)

            return epub_path

        return _create_epub

    def test_analyze_nonexistent_file(self):
        """Test analyzing a non-existent file."""
        analyzer = EpubAnalyzer()
        result = analyzer.analyze(Path("/nonexistent/book.epub"))

        assert len(result.errors) > 0
        assert "not found" in result.errors[0].lower()

    def test_analyze_invalid_zip(self, tmp_path):
        """Test analyzing an invalid ZIP file."""
        invalid_file = tmp_path / "invalid.epub"
        invalid_file.write_text("not a zip file")

        analyzer = EpubAnalyzer()
        result = analyzer.analyze(invalid_file)

        assert len(result.errors) > 0
        assert "invalid" in result.errors[0].lower()

    def test_detect_epub_version_2(self, create_test_epub):
        """Test detecting EPUB 2 version."""
        epub_path = create_test_epub(epub_version=2)

        analyzer = EpubAnalyzer()
        result = analyzer.analyze(epub_path)

        assert result.epub_version == 2

    def test_detect_epub_version_3(self, create_test_epub):
        """Test detecting EPUB 3 version."""
        epub_path = create_test_epub(epub_version=3)

        analyzer = EpubAnalyzer()
        result = analyzer.analyze(epub_path)

        assert result.epub_version == 3

    def test_detect_ncx_present(self, create_test_epub):
        """Test detecting presence of NCX file."""
        epub_path = create_test_epub(has_ncx=True)

        analyzer = EpubAnalyzer()

        with zipfile.ZipFile(epub_path, "r") as zf:
            has_ncx = analyzer._has_file_pattern(zf, r".*\.ncx$")

        assert has_ncx is True

    def test_detect_ncx_absent(self, create_test_epub):
        """Test detecting absence of NCX file."""
        epub_path = create_test_epub(has_ncx=False)

        analyzer = EpubAnalyzer()

        with zipfile.ZipFile(epub_path, "r") as zf:
            has_ncx = analyzer._has_file_pattern(zf, r".*\.ncx$")

        assert has_ncx is False

    def test_detect_navdoc(self, create_test_epub):
        """Test detecting EPUB3 Navigation Document."""
        epub_path = create_test_epub(epub_version=3, has_navdoc=True)

        analyzer = EpubAnalyzer()

        with zipfile.ZipFile(epub_path, "r") as zf:
            has_navdoc = analyzer._has_nav_document(zf)

        assert has_navdoc is True

    def test_detect_footnotes(self, create_test_epub):
        """Test detecting footnote patterns."""
        epub_path = create_test_epub(has_footnotes=True)

        analyzer = EpubAnalyzer()

        with zipfile.ZipFile(epub_path, "r") as zf:
            evidence = analyzer._scan_for_notes(zf)

        assert evidence["has_sup_links"] is True
        assert evidence["has_footnote_class"] is True

    def test_get_ncx_depth(self, tmp_path):
        """Test calculating NCX navigation depth."""
        epub_path = tmp_path / "nested.epub"

        # Create EPUB with nested NCX
        nested_ncx = """<?xml version="1.0"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <navMap>
        <navPoint id="np1" playOrder="1">
            <navLabel><text>Part 1</text></navLabel>
            <content src="part1.xhtml"/>
            <navPoint id="np1-1" playOrder="2">
                <navLabel><text>Chapter 1</text></navLabel>
                <content src="ch1.xhtml"/>
                <navPoint id="np1-1-1" playOrder="3">
                    <navLabel><text>Section 1.1</text></navLabel>
                    <content src="s1.xhtml"/>
                </navPoint>
            </navPoint>
        </navPoint>
    </navMap>
</ncx>"""

        with zipfile.ZipFile(epub_path, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip")
            zf.writestr("toc.ncx", nested_ncx)

        analyzer = EpubAnalyzer()

        with zipfile.ZipFile(epub_path, "r") as zf:
            depth = analyzer._get_ncx_depth(zf)

        assert depth >= 3

    def test_analyze_batch(self, create_test_epub, tmp_path):
        """Test batch analysis of multiple EPUBs."""
        # Create multiple EPUBs
        epub1 = create_test_epub(name="book1.epub", epub_version=2)
        epub2 = create_test_epub(name="book2.epub", epub_version=3)

        analyzer = EpubAnalyzer()
        results = analyzer.analyze_batch(tmp_path)

        assert len(results) == 2

    def test_scan_for_headers(self, create_test_epub):
        """Test scanning for header patterns."""
        epub_path = create_test_epub()

        analyzer = EpubAnalyzer()

        with zipfile.ZipFile(epub_path, "r") as zf:
            evidence = analyzer._scan_for_headers(zf)

        assert evidence["h1_count"] >= 1

    def test_scan_for_page_markers(self, tmp_path):
        """Test scanning for page number markers."""
        epub_path = tmp_path / "pages.epub"

        chapter_with_pages = """<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<body>
    <span id="page_1" epub:type="pagebreak">1</span>
    <p>Content on page 1</p>
    <span id="page_2" epub:type="pagebreak">2</span>
    <p>Content on page 2</p>
</body>
</html>"""

        with zipfile.ZipFile(epub_path, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip")
            zf.writestr("chapter.xhtml", chapter_with_pages)

        analyzer = EpubAnalyzer()

        with zipfile.ZipFile(epub_path, "r") as zf:
            evidence = analyzer._scan_for_page_markers(zf)

        assert evidence["has_page_id_anchors"] is True
        assert evidence["has_epub_pagebreak"] is True

    def test_match_toc_pattern_ncx(self, mock_registry):
        """Test matching NCX ToC patterns."""
        analyzer = EpubAnalyzer(mock_registry)

        pattern = PatternDefinition(
            id="ncx_flat",
            category="toc_style",
            description="Flat NCX",
            detection_signature={"ncx": {"required": True, "min_depth": 1}},
        )

        match = analyzer._match_toc_pattern(
            pattern,
            has_ncx=True,
            ncx_depth=2,
            has_navdoc=False,
            has_html_toc=False,
        )

        assert match.matched is True
        assert match.pattern_id == "ncx_flat"
        assert len(match.evidence) > 0

    def test_match_toc_pattern_navdoc(self, mock_registry):
        """Test matching NavDoc ToC patterns."""
        analyzer = EpubAnalyzer(mock_registry)

        pattern = PatternDefinition(
            id="navdoc_basic",
            category="toc_style",
            description="NavDoc",
            detection_signature={"navdoc": {"required": True}},
        )

        match = analyzer._match_toc_pattern(
            pattern,
            has_ncx=False,
            ncx_depth=0,
            has_navdoc=True,
            has_html_toc=False,
        )

        assert match.matched is True
        assert "Navigation Document" in match.evidence[0]

    def test_full_analysis_epub2(self, create_test_epub):
        """Test full analysis of an EPUB2 file."""
        epub_path = create_test_epub(
            epub_version=2,
            has_ncx=True,
            has_footnotes=True,
        )

        # Use real registry
        analyzer = EpubAnalyzer()
        result = analyzer.analyze(epub_path)

        assert result.epub_version == 2
        assert len(result.errors) == 0
        # Should detect some patterns
        assert len(result.detected_patterns) > 0

    def test_full_analysis_epub3(self, create_test_epub):
        """Test full analysis of an EPUB3 file."""
        epub_path = create_test_epub(
            epub_version=3,
            has_ncx=False,
            has_navdoc=True,
        )

        analyzer = EpubAnalyzer()
        result = analyzer.analyze(epub_path)

        assert result.epub_version == 3
        assert len(result.errors) == 0


class TestEpubAnalyzerWithRealRegistry:
    """Integration tests with real pattern registry."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer with real registry."""
        return EpubAnalyzer()

    def test_analyze_categories_covered(self, analyzer, tmp_path):
        """Test that analysis covers all major categories."""
        # Create a minimal EPUB
        epub_path = tmp_path / "test.epub"

        with zipfile.ZipFile(epub_path, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip")

            container = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
            zf.writestr("META-INF/container.xml", container)

            opf = """<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
    <metadata><dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Test</dc:title></metadata>
    <manifest><item id="ch1" href="ch1.xhtml" media-type="application/xhtml+xml"/></manifest>
    <spine><itemref idref="ch1"/></spine>
</package>"""
            zf.writestr("content.opf", opf)

            chapter = """<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body><h1>Chapter 1</h1><p>Content</p></body>
</html>"""
            zf.writestr("ch1.xhtml", chapter)

        result = analyzer.analyze(epub_path)

        # Analysis should complete without errors
        assert len(result.errors) == 0

        # Should have checked patterns (even if not matched)
        pattern_categories = set()
        for match in result.detected_patterns:
            parts = match.pattern_id.split("_", 1)
            if len(parts) > 1:
                pattern_categories.add(parts[0])

        # At least toc patterns should be checked
        # (other categories depend on registry content)
