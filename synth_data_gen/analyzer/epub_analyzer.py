"""
EPUB Analyzer for detecting formatting patterns.

Parses EPUB files and identifies which patterns from the registry they use.
"""

import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree as ET

from .registry import PatternDefinition, PatternRegistry


@dataclass
class PatternMatch:
    """A detected pattern match in an EPUB."""

    pattern_id: str
    matched: bool
    evidence: List[str] = field(default_factory=list)  # Specific elements that matched
    location: str = ""  # File path within EPUB


@dataclass
class UnknownPattern:
    """An unrecognized pattern found during analysis."""

    category: str
    detected_signature: Dict[str, Any]
    evidence: List[Dict[str, str]]
    similar_patterns: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Complete analysis of an EPUB file."""

    epub_path: Path
    epub_version: int
    detected_patterns: List[PatternMatch] = field(default_factory=list)
    unknown_patterns: List[UnknownPattern] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def get_matched_pattern_ids(self) -> List[str]:
        """Get IDs of all matched patterns."""
        return [m.pattern_id for m in self.detected_patterns if m.matched]

    def get_coverage_report(self) -> Dict[str, List[str]]:
        """
        Returns coverage by category: {category: [matched_pattern_ids]}
        """
        coverage: Dict[str, List[str]] = {}
        for match in self.detected_patterns:
            if match.matched:
                # Extract category from pattern_id (e.g., "toc_" prefix)
                parts = match.pattern_id.split("_", 1)
                category = parts[0] if len(parts) > 1 else "other"
                if category not in coverage:
                    coverage[category] = []
                coverage[category].append(match.pattern_id)
        return coverage

    def get_unrecognized_elements(self) -> List[Dict]:
        """Returns elements that didn't match any known pattern."""
        return [
            {
                "category": up.category,
                "signature": up.detected_signature,
                "evidence": up.evidence,
            }
            for up in self.unknown_patterns
        ]


class EpubAnalyzer:
    """
    Analyzes EPUB files to detect formatting patterns.

    Uses the PatternRegistry to identify known patterns and flag
    unknown patterns for human review.
    """

    # Common EPUB namespaces
    NAMESPACES = {
        "opf": "http://www.idpf.org/2007/opf",
        "dc": "http://purl.org/dc/elements/1.1/",
        "ncx": "http://www.daisy.org/z3986/2005/ncx/",
        "xhtml": "http://www.w3.org/1999/xhtml",
        "epub": "http://www.idpf.org/2007/ops",
    }

    def __init__(self, registry: Optional[PatternRegistry] = None):
        """Initialize analyzer with a pattern registry."""
        self.registry = registry or PatternRegistry()

    def analyze(self, epub_path: Path) -> AnalysisResult:
        """
        Analyze an EPUB file and return detected patterns.

        Args:
            epub_path: Path to the EPUB file.

        Returns:
            AnalysisResult with detected patterns and unknown patterns.
        """
        result = AnalysisResult(epub_path=epub_path, epub_version=2)

        if not epub_path.exists():
            result.errors.append(f"File not found: {epub_path}")
            return result

        try:
            with zipfile.ZipFile(epub_path, "r") as zf:
                # Detect EPUB version
                result.epub_version = self._detect_epub_version(zf)

                # Analyze different pattern categories
                self._analyze_toc_patterns(zf, result)
                self._analyze_notes_patterns(zf, result)
                self._analyze_header_patterns(zf, result)
                self._analyze_page_markers(zf, result)

        except zipfile.BadZipFile:
            result.errors.append(f"Invalid EPUB file: {epub_path}")
        except Exception as e:
            result.errors.append(f"Analysis error: {str(e)}")

        return result

    def analyze_batch(self, epub_dir: Path) -> List[AnalysisResult]:
        """Analyze all EPUB files in a directory."""
        results = []
        for epub_file in epub_dir.glob("**/*.epub"):
            results.append(self.analyze(epub_file))
        return results

    def _detect_epub_version(self, zf: zipfile.ZipFile) -> int:
        """Detect EPUB version from container.xml and content.opf."""
        try:
            # Read container.xml
            container_xml = zf.read("META-INF/container.xml").decode("utf-8")
            root = ET.fromstring(container_xml)

            # Find rootfile path
            for rootfile in root.iter():
                if rootfile.tag.endswith("rootfile"):
                    opf_path = rootfile.get("full-path", "")
                    if opf_path:
                        opf_content = zf.read(opf_path).decode("utf-8")
                        # Check for version attribute
                        if 'version="3' in opf_content:
                            return 3
                        elif 'version="2' in opf_content:
                            return 2
        except (KeyError, ET.ParseError):
            pass

        return 2  # Default to EPUB 2

    def _analyze_toc_patterns(
        self, zf: zipfile.ZipFile, result: AnalysisResult
    ) -> None:
        """Analyze Table of Contents patterns."""
        toc_patterns = self.registry.get_patterns_by_category("toc_style")

        # Check for NCX
        has_ncx = self._has_file_pattern(zf, r".*\.ncx$")
        ncx_depth = 0
        if has_ncx:
            ncx_depth = self._get_ncx_depth(zf)

        # Check for NavDoc (EPUB3)
        has_navdoc = self._has_nav_document(zf)

        # Check for HTML ToC
        has_html_toc = self._has_html_toc(zf)

        # Match against known patterns
        for pattern in toc_patterns:
            match = self._match_toc_pattern(
                pattern, has_ncx, ncx_depth, has_navdoc, has_html_toc
            )
            result.detected_patterns.append(match)

    def _analyze_notes_patterns(
        self, zf: zipfile.ZipFile, result: AnalysisResult
    ) -> None:
        """Analyze footnote/endnote patterns."""
        notes_patterns = self.registry.get_patterns_by_category("notes_system")

        # Scan HTML content files for note patterns
        note_evidence = self._scan_for_notes(zf)

        for pattern in notes_patterns:
            match = self._match_notes_pattern(pattern, note_evidence)
            result.detected_patterns.append(match)

    def _analyze_header_patterns(
        self, zf: zipfile.ZipFile, result: AnalysisResult
    ) -> None:
        """Analyze header/title patterns."""
        header_patterns = self.registry.get_patterns_by_category("header_pattern")

        # Scan for header elements
        header_evidence = self._scan_for_headers(zf)

        for pattern in header_patterns:
            match = self._match_header_pattern(pattern, header_evidence)
            result.detected_patterns.append(match)

    def _analyze_page_markers(
        self, zf: zipfile.ZipFile, result: AnalysisResult
    ) -> None:
        """Analyze page number marker patterns."""
        marker_patterns = self.registry.get_patterns_by_category("page_marker")

        # Scan for page markers
        marker_evidence = self._scan_for_page_markers(zf)

        for pattern in marker_patterns:
            match = self._match_page_marker_pattern(pattern, marker_evidence)
            result.detected_patterns.append(match)

    # Helper methods

    def _has_file_pattern(self, zf: zipfile.ZipFile, pattern: str) -> bool:
        """Check if any file in the EPUB matches the given pattern."""
        regex = re.compile(pattern, re.IGNORECASE)
        return any(regex.match(name) for name in zf.namelist())

    def _get_ncx_depth(self, zf: zipfile.ZipFile) -> int:
        """Get the maximum depth of the NCX navigation."""
        for name in zf.namelist():
            if name.lower().endswith(".ncx"):
                try:
                    ncx_content = zf.read(name).decode("utf-8")
                    # Count nested navPoint levels
                    depth = ncx_content.count("<navPoint")
                    if depth > 0:
                        # Estimate depth by nesting
                        max_depth = 1
                        for match in re.finditer(r"<navPoint[^>]*>", ncx_content):
                            pos = match.start()
                            # Count preceding unclosed navPoints
                            preceding = ncx_content[:pos]
                            opens = preceding.count("<navPoint")
                            closes = preceding.count("</navPoint>")
                            current_depth = opens - closes + 1
                            max_depth = max(max_depth, current_depth)
                        return max_depth
                except (KeyError, UnicodeDecodeError):
                    pass
        return 0

    def _has_nav_document(self, zf: zipfile.ZipFile) -> bool:
        """Check for EPUB3 Navigation Document."""
        for name in zf.namelist():
            if name.lower().endswith((".xhtml", ".html")):
                try:
                    content = zf.read(name).decode("utf-8")
                    if 'epub:type="toc"' in content or "epub:type='toc'" in content:
                        return True
                except (KeyError, UnicodeDecodeError):
                    pass
        return False

    def _has_html_toc(self, zf: zipfile.ZipFile) -> bool:
        """Check for HTML-based ToC (not NavDoc)."""
        toc_patterns = [
            r'class=["\']toc["\']',
            r'class=["\']contents["\']',
            r"<h[12][^>]*>.*(?:Table of Contents|Contents).*</h[12]>",
        ]
        for name in zf.namelist():
            if name.lower().endswith((".xhtml", ".html")):
                try:
                    content = zf.read(name).decode("utf-8")
                    for pattern in toc_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            return True
                except (KeyError, UnicodeDecodeError):
                    pass
        return False

    def _scan_for_notes(self, zf: zipfile.ZipFile) -> Dict[str, Any]:
        """Scan EPUB for footnote/endnote patterns."""
        evidence: Dict[str, Any] = {
            "has_sup_links": False,
            "has_footnote_class": False,
            "has_endnotes_file": False,
            "has_epub_noteref": False,
            "has_unlinked_sup": False,
            "samples": [],
        }

        for name in zf.namelist():
            if name.lower().endswith((".xhtml", ".html")):
                try:
                    content = zf.read(name).decode("utf-8")

                    # Check for superscript links
                    if re.search(r"<sup[^>]*>.*<a[^>]*>", content):
                        evidence["has_sup_links"] = True

                    # Check for footnote class
                    if re.search(r'class=["\'][^"\']*footnote', content):
                        evidence["has_footnote_class"] = True

                    # Check for EPUB3 noteref
                    if 'epub:type="noteref"' in content:
                        evidence["has_epub_noteref"] = True

                    # Check for unlinked superscript
                    if re.search(r"<sup[^>]*>\d+</sup>", content):
                        if not re.search(r"<sup[^>]*>.*<a", content):
                            evidence["has_unlinked_sup"] = True

                    # Check if this looks like an endnotes file
                    if "notes" in name.lower() or "endnotes" in name.lower():
                        evidence["has_endnotes_file"] = True

                except (KeyError, UnicodeDecodeError):
                    pass

        return evidence

    def _scan_for_headers(self, zf: zipfile.ZipFile) -> Dict[str, Any]:
        """Scan EPUB for header patterns."""
        evidence: Dict[str, Any] = {
            "h1_count": 0,
            "h2_count": 0,
            "h3_count": 0,
            "has_styled_p_headers": False,
            "has_div_headers": False,
            "header_classes": set(),
        }

        for name in zf.namelist():
            if name.lower().endswith((".xhtml", ".html")):
                try:
                    content = zf.read(name).decode("utf-8")

                    evidence["h1_count"] += len(re.findall(r"<h1[^>]*>", content))
                    evidence["h2_count"] += len(re.findall(r"<h2[^>]*>", content))
                    evidence["h3_count"] += len(re.findall(r"<h3[^>]*>", content))

                    # Check for styled p headers
                    if re.search(r'<p[^>]*class=["\'][^"\']*head', content):
                        evidence["has_styled_p_headers"] = True

                    # Check for div headers
                    if re.search(r'<div[^>]*class=["\'][^"\']*title', content):
                        evidence["has_div_headers"] = True

                    # Collect header classes
                    for match in re.finditer(r'<h\d[^>]*class=["\']([^"\']+)', content):
                        evidence["header_classes"].add(match.group(1))

                except (KeyError, UnicodeDecodeError):
                    pass

        return evidence

    def _scan_for_page_markers(self, zf: zipfile.ZipFile) -> Dict[str, Any]:
        """Scan EPUB for page number markers."""
        evidence: Dict[str, Any] = {
            "has_page_id_anchors": False,
            "has_epub_pagebreak": False,
            "has_pagenum_class": False,
            "samples": [],
        }

        for name in zf.namelist():
            if name.lower().endswith((".xhtml", ".html")):
                try:
                    content = zf.read(name).decode("utf-8")

                    # Check for page_X id anchors
                    if re.search(r'id=["\']page_?\d+["\']', content):
                        evidence["has_page_id_anchors"] = True

                    # Check for EPUB3 pagebreak
                    if 'epub:type="pagebreak"' in content:
                        evidence["has_epub_pagebreak"] = True

                    # Check for pagenum class
                    if re.search(r'class=["\'][^"\']*page[-_]?num', content):
                        evidence["has_pagenum_class"] = True

                except (KeyError, UnicodeDecodeError):
                    pass

        return evidence

    def _match_toc_pattern(
        self,
        pattern: PatternDefinition,
        has_ncx: bool,
        ncx_depth: int,
        has_navdoc: bool,
        has_html_toc: bool,
    ) -> PatternMatch:
        """Match a ToC pattern against evidence."""
        sig = pattern.detection_signature
        evidence = []
        matched = False

        # Check signature requirements
        if "ncx" in sig:
            if sig["ncx"].get("required") and has_ncx:
                evidence.append("NCX file present")
                min_depth = sig["ncx"].get("min_depth", 1)
                if ncx_depth >= min_depth:
                    evidence.append(f"NCX depth: {ncx_depth} >= {min_depth}")
                    matched = True

        if "navdoc" in sig:
            if sig["navdoc"].get("required") and has_navdoc:
                evidence.append("Navigation Document present")
                matched = True

        if "html_toc" in sig:
            if sig["html_toc"].get("required") and has_html_toc:
                evidence.append("HTML ToC present")
                matched = True

        return PatternMatch(
            pattern_id=pattern.id,
            matched=matched,
            evidence=evidence,
        )

    def _match_notes_pattern(
        self, pattern: PatternDefinition, evidence: Dict[str, Any]
    ) -> PatternMatch:
        """Match a notes pattern against evidence."""
        sig = pattern.detection_signature
        match_evidence = []
        matched = False

        # Check various note patterns
        if "reference" in sig:
            ref_sig = sig["reference"]
            if ref_sig.get("type") == "sup_link" and evidence["has_sup_links"]:
                match_evidence.append("Superscript links found")
                matched = True
            elif ref_sig.get("type") == "unlinked" and evidence["has_unlinked_sup"]:
                match_evidence.append("Unlinked superscripts found")
                matched = True
            elif ref_sig.get("type") == "epub_noteref" and evidence["has_epub_noteref"]:
                match_evidence.append("EPUB3 noteref found")
                matched = True

        if "note_text" in sig:
            note_sig = sig["note_text"]
            if note_sig.get("location") == "same_file" and evidence["has_footnote_class"]:
                match_evidence.append("Footnote class in same file")
                if matched:  # Both reference and note location match
                    matched = True
            elif note_sig.get("location") == "separate_file" and evidence["has_endnotes_file"]:
                match_evidence.append("Separate endnotes file found")
                if matched:
                    matched = True

        return PatternMatch(
            pattern_id=pattern.id,
            matched=matched,
            evidence=match_evidence,
        )

    def _match_header_pattern(
        self, pattern: PatternDefinition, evidence: Dict[str, Any]
    ) -> PatternMatch:
        """Match a header pattern against evidence."""
        sig = pattern.detection_signature
        match_evidence = []
        matched = False

        if "standard_headers" in sig:
            if evidence["h1_count"] > 0 or evidence["h2_count"] > 0:
                match_evidence.append(
                    f"Standard headers: h1={evidence['h1_count']}, h2={evidence['h2_count']}"
                )
                matched = True

        if "styled_p" in sig and evidence["has_styled_p_headers"]:
            match_evidence.append("Styled p headers found")
            matched = True

        if "div_headers" in sig and evidence["has_div_headers"]:
            match_evidence.append("Div-based headers found")
            matched = True

        return PatternMatch(
            pattern_id=pattern.id,
            matched=matched,
            evidence=match_evidence,
        )

    def _match_page_marker_pattern(
        self, pattern: PatternDefinition, evidence: Dict[str, Any]
    ) -> PatternMatch:
        """Match a page marker pattern against evidence."""
        sig = pattern.detection_signature
        match_evidence = []
        matched = False

        if "anchor_id" in sig and evidence["has_page_id_anchors"]:
            match_evidence.append("Page ID anchors found")
            matched = True

        if "epub_pagebreak" in sig and evidence["has_epub_pagebreak"]:
            match_evidence.append("EPUB3 pagebreak found")
            matched = True

        if "pagenum_class" in sig and evidence["has_pagenum_class"]:
            match_evidence.append("Page number class found")
            matched = True

        return PatternMatch(
            pattern_id=pattern.id,
            matched=matched,
            evidence=match_evidence,
        )
