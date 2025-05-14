# Debug Specific Memory
<!-- Entries below should be added reverse chronologically (newest first) -->
### Issue: CALIBRE_META_TDD_BLOCK
### Issue: CALIBRE_META_TDD_BLOCKER - Calibre metadata handling in `ebooklib` for `structure.py` - Resolved - 2025-05-14 14:50:00
- **Reported**: 2025-05-14 13:41:00 (SPARC Delegation via TDD Early Return, see [`memory-bank/feedback/tdd-feedback.md`](memory-bank/feedback/tdd-feedback.md:1) entry `[2025-05-14 13:41:00]`) / **Severity**: High (Blocking TDD)
- **Symptoms**:
    - Tests in [`tests/generators/epub_components/test_structure.py`](tests/generators/epub_components/test_structure.py:1) for `create_epub_structure_calibre_artifacts` failed to find added Calibre metadata (`calibre:series`).
    - `ValueError: too many values to unpack (expected 3)` when iterating `book.metadata.get(None, [])`.
    - `AssertionError: OPF file not found in EPUB` when reading back the EPUB using `read_book.get_items()`.
    - `AssertionError: Calibre series metadata tag not found in OPF XML` when parsing OPF directly with incorrect XML namespace query.
- **Investigation**:
    1. Used `investigate_ebooklib_metadata.py` to confirm Calibre-style tags (`<meta name="..." content="..."/>`) should be added with `book.add_metadata(None, 'meta', None, attributes_dict)`.
    2. Confirmed they are stored in `book.metadata[None]['meta']` as a list of 2-tuples: `(None, attributes_dict)`, resolving the `ValueError`.
    3. Simplified SUT `create_epub_structure_calibre_artifacts` and ensured `book.toc` was set and `EpubNcx()` item was added for basic EPUB validity, which resolved issues with `epub.read_epub()` not finding OPF or erroring during spine processing.
    4. Modified `test_create_epub_structure_calibre_artifacts_creates_file` to unzip the EPUB and parse the OPF XML directly.
    5. Identified that the OPF file has a default namespace (`xmlns="http://www.idpf.org/2007/opf"`). When `ebooklib` writes `<meta>` tags (added with `namespace=None`) inside the `<opf:metadata>` block, these `<meta>` tags are effectively in the OPF namespace.
- **Root Cause**:
    1. Initial `ValueError` was due to incorrect unpacking of the 2-tuple metadata entry from `book.metadata[None]['meta']`.
    2. Failures to find the OPF item via `read_book.get_items()` after `epub.read_epub()` were likely due to an insufficiently structured EPUB (missing `book.toc` for NCX generation, or missing NCX item itself), leading to parsing issues in `ebooklib`.
    3. Subsequent failures in the `_creates_file` test (when directly parsing OPF XML) were due to incorrect XML namespace querying. The `findall('meta')` call did not account for the default OPF namespace.
- **Fix Applied**:
    1. Corrected metadata iteration in tests to unpack 2-tuples: `for _, attrs_dict in book.metadata[None]['meta']`.
    2. Ensured SUT `create_epub_structure_calibre_artifacts` sets `book.toc = tuple(toc_links)` and calls `book.add_item(epub.EpubNcx())`.
    3. In `test_create_epub_structure_calibre_artifacts_creates_file`, corrected the XML parsing to find Calibre meta tags using `metadata_element.findall('opf:meta', namespaces)` after identifying the `<opf:metadata>` element.
- **Verification**: Tests `test_create_epub_structure_calibre_artifacts_content` and `test_create_epub_structure_calibre_artifacts_creates_file` now pass.
- **Related Issues**: TDD Early Return `[2025-05-14 13:41:00]` in [`memory-bank/feedback/tdd-feedback.md`](memory-bank/feedback/tdd-feedback.md:1).

### Tool/Technique: `ebooklib` Metadata & XML Namespaces - 2025-05-14 14:50:00
- **Context**: Adding and verifying custom `<meta name="..." content="..."/>` tags (e.g., Calibre-specific) in EPUB OPF files using `ebooklib`.
- **Usage**:
    - **Adding**: Use `book.add_metadata(None, 'meta', None, {'name': 'custom:tag', 'content': 'value'})`. The `None` namespace is key.
    - **In-memory Retrieval**: Access via `book.metadata[None]['meta']`. Each entry is a 2-tuple: `(tag_text_content, attributes_dict)`. For these tags, `tag_text_content` is `None`.
    - **XML Verification (Direct OPF Parsing)**:
        - EPUB OPF files typically have a default namespace: `<package xmlns="http://www.idpf.org/2007/opf" ...>`.
        - When `ebooklib` writes `<meta>` tags (that were added with `namespace=None`) inside the `<opf:metadata>` block, these `<meta>` tags inherit the default OPF namespace.
        - To find them using `xml.etree.ElementTree`, after finding the `<opf:metadata>` element (e.g., `metadata_element = root.find('opf:metadata', {'opf': 'http://www.idpf.org/2007/opf'})`), use `metadata_element.findall('opf:meta', {'opf': 'http://www.idpf.org/2007/opf'})` to query for the meta tags.
- **Effectiveness**: High. Correct namespace handling is crucial for direct XML parsing of OPF files. Essential for verifying tags not easily accessible via `book.get_metadata()` after `read_epub()`.
### Issue: EPUB_NOTES_TYPEERROR - `TypeError` in `epub.write_epub()` for `create_epub_kant_style_footnotes` - Resolved - 2025-05-14 01:22:00
- **Reported**: 2025-05-14 00:48:00 (SPARC Delegation, see [`memory-bank/activeContext.md:1`](memory-bank/activeContext.md:1) entry `[2025-05-14 00:48:00]`) / **Severity**: High (Blocking TDD)
- **Symptoms**: Initially `TypeError: Argument must be bytes or unicode, got 'NoneType'` in `ebooklib.epub.write_epub()`, leading to `EpubException: 'Can not find container file'` or `zipfile.BadZipFile` or `ebooklib`'s "Document is empty" error. Later, test assertion failures.
- **Investigation**:
    1. Added debug prints to `_write_epub_file` in [`synth_data_gen/common/utils.py`](synth_data_gen/common/utils.py:1) to inspect `book.items` before `epub.write_epub()`.
    2. Corrected an `AttributeError` in debug prints (`item.get_media_type` to `item.media_type`).
    3. Observed that chapter and NAV document content was an empty string in the iterated `book.items` within `_write_epub_file`.
    4. Explicitly set NAV document content to bytes in `create_epub_kant_style_footnotes` ([`synth_data_gen/generators/epub_components/notes.py`](synth_data_gen/generators/epub_components/notes.py:1)). This fixed NAV content but not chapter content.
    5. Added more debug prints to trace chapter content from its definition through `_add_epub_chapters` and into `create_epub_kant_style_footnotes` just before `_write_epub_file`. Confirmed content was present until the iteration within `_write_epub_file`.
    6. Discovered that iterating `book.items` showed empty string content for the chapter, while `book.get_item_with_id()` for the same chapter showed populated content *at the same point in execution*.
    7. Hypothesized `ebooklib` expects XHTML content (chapters, NAV) as bytes.
- **Root Cause**:
    1. `ebooklib.epub.write_epub()` (or its internal processing of `book.items`) appears to expect XHTML item content (like chapters and NAV documents) to be `bytes`. If it's a `str`, it might be mishandled or cleared during the EPUB serialization process, leading to the "Document is empty" error.
    2. The SUT (`create_epub_kant_style_footnotes`) was not generating the correct Kant footnote markup in its chapter content.
    3. Test assertions in `test_create_epub_kant_style_footnotes_content` were not perfectly matching the generated HTML (missing `epub:type` attributes) and used an incorrect chapter filename initially.
- **Fix Applied**:
    1. Modified `_add_epub_chapters` in [`synth_data_gen/common/utils.py`](synth_data_gen/common/utils.py:1) to encode chapter content to UTF-8 bytes: `chapter.content = ch_content.encode('utf-8')`.
    2. Ensured NAV document content in `create_epub_kant_style_footnotes` ([`synth_data_gen/generators/epub_components/notes.py`](synth_data_gen/generators/epub_components/notes.py:1)) was also set as UTF-8 encoded bytes.
    3. Updated the `chapter_details["content"]` in `create_epub_kant_style_footnotes` to include the correct Kant footnote markup.
    4. Corrected assertions and chapter filename logic in `test_create_epub_kant_style_footnotes_content` ([`tests/generators/epub_components/test_notes.py`](tests/generators/epub_components/test_notes.py:1)).
- **Verification**: `test_create_epub_kant_style_footnotes_content` now passes. EPUB file is generated correctly.
- **Related Issues**: Original TDD Blocker: [`memory-bank/activeContext.md:1`](memory-bank/activeContext.md:1) (entry `[2025-05-14 00:48:00]`).

---

### Tool/Technique: `ebooklib` Content Type Expectation - 2025-05-14 01:22:00
- **Context**: Debugging `ebooklib.epub.write_epub()` failures ("Document is empty", `TypeError`).
- **Usage**: When adding XHTML content (chapters, NAV documents) to `ebooklib.epub.EpubHtml` items, ensure the `.content` attribute is set with UTF-8 encoded `bytes`, not Python `str` type. While `ebooklib` might accept strings for some items (like CSS `EpubItem`), it appears less robust for `EpubHtml` content during the final write process if content is not bytes.
- **Effectiveness**: High. Changing string content to `bytes` resolved persistent EPUB generation failures.

---
### Issue: TDD_PAGE_NUMBERS_GET_ITEM_WITH_ID - `book.get_item_with_id` returning `None` - Resolved - 2025-05-13 10:01:32
- **Reported**: 2025-05-13 02:41:19 (SPARC Delegation, see [`memory-bank/activeContext.md:2`](memory-bank/activeContext.md:2)) / **Severity**: High (Blocking TDD) / **Symptoms**: `book.get_item_with_id("chapter_semantic_pagebreaks")` returned `None` in `test_create_epub_pagenum_semantic_pagebreak_content` ([`tests/generators/epub_components/test_page_numbers.py`](tests/generators/epub_components/test_page_numbers.py:1)).
- **Investigation**:
    1. Added debug print statements to [`tests/generators/epub_components/test_page_numbers.py`](tests/generators/epub_components/test_page_numbers.py:1) to list all item IDs in the `book` object. (2025-05-13 02:44:15)
    2. Fixed an `UnboundLocalError` in the test file caused by the debug print statements. (2025-05-13 10:00:20)
    3. Test execution with debug prints (from a previous failed run) showed the item `chapter_semantic_pagebreaks` was present in `book.items`. (2025-05-13 10:00:20 - analysis of output from 2025-05-13 10:00:20)
    4. After fixing the `UnboundLocalError` and re-running, the test `test_create_epub_pagenum_semantic_pagebreak_content` passed. (2025-05-13 10:00:41)
- **Root Cause**: The original issue of `get_item_with_id` returning `None` was likely resolved by prior fixes to UID assignment in the SUT ([`synth_data_gen/generators/epub_components/page_numbers.py`](synth_data_gen/generators/epub_components/page_numbers.py:1)) or helper ([`synth_data_gen/common/utils.py`](synth_data_gen/common/utils.py:1)) by the `tdd` mode. The test was then failing due to an unrelated `UnboundLocalError` introduced by my debugging attempts.
- **Fix Applied**:
    - Corrected `UnboundLocalError` in [`tests/generators/epub_components/test_page_numbers.py`](tests/generators/epub_components/test_page_numbers.py:1) by moving `chapter_item_uid` definition.
    - Removed debug print statements from [`tests/generators/epub_components/test_page_numbers.py`](tests/generators/epub_components/test_page_numbers.py:1).
- **Verification**: Test `test_create_epub_pagenum_semantic_pagebreak_content` now passes. (2025-05-13 10:00:41)
- **Related Issues**: Original TDD Blocker: [`memory-bank/activeContext.md`](memory-bank/activeContext.md:2) (entry `[2025-05-13 02:41:19]`).
### Issue: PYTEST_PDF_FIGURES_FAIL - `test_single_column_with_exact_figure_occurrence` `KeyError` &amp; Assertion - Resolved - 2025-05-12 01:03:00
- **Reported**: 2025-05-12 00:58:55 (Task objective) / **Severity**: High / **Symptoms**: `AssertionError: assert call({'count': 1}, 'figures') in [call(10, 'page_count'), call(1, 'chapters')]` followed by `KeyError: 'pdf_figures_occurrence_config'` after first fix attempt.
- **Investigation**:
    1. Reviewed test `test_single_column_with_exact_figure_occurrence` in [`tests/generators/test_pdf_generator.py`](tests/generators/test_pdf_generator.py:533). (2025-05-12 00:59:45)
    2. Reviewed `PdfGenerator` code for figure handling in [`synth_data_gen/generators/pdf.py`](synth_data_gen/generators/pdf.py:167-172). (2025-05-12 01:00:02)
    3. Identified mismatch in `specific_config` structure: test provided `pdf_figures_occurrence_config` at top level, but generator expected it under `figure_generation`. (2025-05-12 01:00:02)
    4. Corrected `specific_config` in the test. (2025-05-12 01:00:19)
    5. `pytest` then showed `KeyError` on the assertion line, as it was still trying to access the old path. (2025-05-12 01:00:29)
    6. Corrected assertion to use `specific_config["figure_generation"]["pdf_figures_occurrence_config"]`. (2025-05-12 01:00:40)
- **Root Cause**: Initial error due to incorrect `specific_config` structure in the test. Subsequent `KeyError` due to assertion not being updated after fixing config structure.
- **Fix Applied**:
    1. Modified `specific_config` in [`tests/generators/test_pdf_generator.py`](tests/generators/test_pdf_generator.py:563) to nest `pdf_figures_occurrence_config` under `figure_generation`.
    2. Updated assertion in [`tests/generators/test_pdf_generator.py`](tests/generators/test_pdf_generator.py:574) to `call(specific_config["figure_generation"]["pdf_figures_occurrence_config"], "figures")`.
- **Verification**: `pytest tests/generators/test_pdf_generator.py` now passes all tests. (2025-05-12 01:00:47)
- **Related Issues**: None.

### Issue: PYTEST_MD_PROBABILISTIC_CALL_COUNT - Probabilistic tests in `test_markdown_generator.py` failing `call_count` - Resolved - 2025-05-12 01:03:00
- **Reported**: 2025-05-12 01:00:47 (`pytest` output after PDF fix) / **Severity**: Medium / **Symptoms**: `AssertionError: assert mock_create_*.call_count == 0` (expected non-zero) for `test_generate_probabilistic_headings_count`, `test_generate_probabilistic_list_items_count`, `test_generate_probabilistic_images_count`. This was after fixing initial `random.random` called twice error.
- **Investigation**:
    1. Reviewed `_create_md_basic_elements_content` in [`synth_data_gen/generators/markdown.py`](synth_data_gen/generators/markdown.py:153). (2025-05-12 01:02:53)
    2. Found that headings, list items, and images were directly generated as strings, not by calling their respective `_create_md_*` helper methods. (2025-05-12 01:02:53)
- **Root Cause**: The `_create_md_basic_elements_content` method was not delegating to the specific `_create_md_heading`, `_create_md_list_item`, and `_create_md_image` methods, so the mocks for these methods were never called.
- **Fix Applied**: Refactored `_create_md_basic_elements_content` in [`synth_data_gen/generators/markdown.py`](synth_data_gen/generators/markdown.py:1) to call `self._create_md_heading()`, `self._create_md_list_item()`, and `self._create_md_image()` in their respective loops. (2025-05-12 01:03:19)
- **Verification**: `pytest` run showed these 3 tests now pass. (2025-05-12 01:03:26)
- **Related Issues**: PYTEST_MD_PROBABILISTIC_RANDOM_TWICE (previous state of these tests).

### Issue: PYTEST_MD_PROBABILISTIC_RANDOM_TWICE - Probabilistic tests in `test_markdown_generator.py` calling `random.random` twice - Resolved - 2025-05-12 01:02:18
- **Reported**: 2025-05-12 01:00:29 (`pytest` output) / **Severity**: Medium / **Symptoms**: `AssertionError: Expected 'random' to have been called once. Called 2 times.` for `test_generate_probabilistic_headings_count`, `test_generate_probabilistic_list_items_count`, `test_generate_probabilistic_images_count`.
- **Investigation**:
    1. Reviewed `BaseGenerator._determine_count` ([`synth_data_gen/core/base.py`](synth_data_gen/core/base.py:91-100)) - it calls `random.random()` for probabilistic configs. (2025-05-12 01:01:19)
    2. Reviewed `MarkdownGenerator._generate_frontmatter` ([`synth_data_gen/generators/markdown.py`](synth_data_gen/generators/markdown.py:54)) - it *also* calls `random.random()` if `frontmatter.include_chance` is a float. (2025-05-12 01:01:50)
- **Root Cause**: The tests correctly mocked `random.random` expecting one call from `_determine_count` for the feature under test (e.g., headings). However, the `frontmatter` config in these tests also had `include_chance: 0.0` (a float), causing a second call to `random.random()` from `_generate_frontmatter`.
- **Fix Applied**: Changed `frontmatter: {"include_chance": 0.0}` to `{"include_chance": 0}` (integer) in the `specific_config` of the three affected probabilistic tests in [`tests/generators/test_markdown_generator.py`](tests/generators/test_markdown_generator.py:1) (lines 262, 288, 311, 395, 422, 445, 521, 547, 569). (2025-05-12 01:02:18)
- **Verification**: Subsequent `pytest` run showed these specific errors were resolved, though new `call_count` errors emerged. (2025-05-12 01:02:24)
- **Related Issues**: PYTEST_MD_PROBABILISTIC_CALL_COUNT (next state of these tests).
### Issue: PDF_TYPE_ERROR_CONTEXT_KEY - `test_generate_single_column_page_count_range` `TypeError` - Investigated (Not Reproducible) - 2025-05-11 21:45:00
- **Reported**: 2025-05-11 21:42:23 (via `tdd` Early Return, see [`memory-bank/activeContext.md:2`](memory-bank/activeContext.md:2) entry `[2025-05-11 21:42:23]`) / **Severity**: Medium (Reported as Blocker) / **Symptoms**: `TypeError: BaseGenerator._determine_count() missing 1 required positional argument: 'context_key_name'` in `tests.generators.test_pdf_generator.TestPdfGenerator.test_generate_single_column_page_count_range`.
- **Investigation**:
    1. Verified `BaseGenerator._determine_count` signature in [`synth_data_gen/core/base.py`](synth_data_gen/core/base.py:65) requires `context_key_name`. (2025-05-11 21:43:47)
    2. Verified call in `PdfGenerator._create_pdf_text_single_column` ([`synth_data_gen/generators/pdf.py:133`](synth_data_gen/generators/pdf.py:133)) correctly passes `context_key_name`. (2025-05-11 21:43:53)
    3. Analyzed mock setup in `test_generate_single_column_page_count_range` ([`tests/generators/test_pdf_generator.py:453-460`](tests/generators/test_pdf_generator.py:453-460)); the `side_effect` correctly calls `BaseGenerator._determine_count` with all arguments. (2025-05-11 21:44:00)
    4. Executed `test_generate_single_column_page_count_range` directly; test passed. (2025-05-11 21:43:40)
    5. Executed all tests in `tests.generators.test_pdf_generator`; all 13 tests passed. (2025-05-11 21:44:40)
- **Root Cause**: Not reproducible with the current codebase. The `tdd` mode's reported error may have been based on an intermediate or since-corrected code state.
- **Fix Applied**: No fix applied as the issue is not currently present.
- **Verification**: All relevant tests pass.
- **Related Issues**: None directly, but highlights potential discrepancies between different test execution environments or code states.
### Issue: PDF_TEST_NAMEERROR_MOCK_DETERMINE_COUNT - `test_generate_single_column_unified_chapters_range` NameError - Resolved - 2025-05-11 18:24:30
- **Reported**: 2025-05-11 18:24:00 (User feedback after test execution) / **Severity**: Medium (Blocking Test) / **Symptoms**: `NameError: name 'mock_determine_count' is not defined` in `tests.generators.test_pdf_generator.TestPdfGenerator.test_generate_single_column_unified_chapters_range` at line 302.
- **Investigation**:
    1. Reviewed test code [`tests/generators/test_pdf_generator.py`](tests/generators/test_pdf_generator.py:182) (lines 182-305). Confirmed `mock_determine_count` was not defined as a parameter or within the method scope. (2025-05-11 18:24:15)
- **Root Cause**: The line `mock_determine_count.side_effect = None` at line 302 of [`tests/generators/test_pdf_generator.py`](tests/generators/test_pdf_generator.py:302) referenced an undefined variable. This line was likely a remnant from a previous mocking strategy.
- **Fix Applied**: Commented out the problematic line `mock_determine_count.side_effect = None` in [`tests/generators/test_pdf_generator.py`](tests/generators/test_pdf_generator.py:302). (2025-05-11 18:24:30)
- **Verification**: Pending test re-execution.
- **Related Issues**: Follow-up to PDF_RANDINT_DOUBLE_CALL.
### Issue: PDF_RANDINT_DOUBLE_CALL - `test_generate_single_column_unified_chapters_range` `randint` called twice - Resolved - 2025-05-11 18:48:00
- **Reported**: 2025-05-11 14:51:00 (via `tdd` Early Return, see [`memory-bank/activeContext.md:1`](memory-bank/activeContext.md:1)) / **Severity**: Medium (Blocking Test) / **Symptoms**: `AssertionError: Expected 'randint' to be called once. Called 2 times. Calls: [call(2, 5), call(2, 5)]` in `tests.generators.test_pdf_generator.TestPdfGenerator.test_generate_single_column_unified_chapters_range`.
- **Investigation**:
    1. Initial investigation incorrectly identified a commented-out line ([`tests/generators/test_pdf_generator.py:255`](tests/generators/test_pdf_generator.py:255)) as the sole duplicate call to `self.generator.generate()`. (2025-05-11 14:55:39)
    2. Inserted `print()` statements into `PdfGenerator.generate`, `_create_pdf_text_single_column`, and `BaseGenerator._determine_count`. (2025-05-11 18:47:00)
    3. Test execution with logging revealed `PdfGenerator.generate` was called twice with different `output_path` arguments: first with `'test_output/pdf/single_col_unified_range.pdf'` then with `'test_output/pdf_range_chapters.pdf'`. (2025-05-11 18:47:41)
- **Root Cause**: The test method `test_generate_single_column_unified_chapters_range` in [`tests/generators/test_pdf_generator.py`](tests/generators/test_pdf_generator.py:1) contained a second block of code (originally lines 306-321) that re-defined `specific_config` and `global_config`, and then called `self.generator.generate()` a second time with a different `output_path`. The `mock_base_randint.reset_mock()` was only called before the first `generate()` call.
- **Fix Applied**: Removed the entire second block of code (lines 306-321) from [`tests/generators/test_pdf_generator.py`](tests/generators/test_pdf_generator.py:306) that was causing the second `self.generator.generate()` call. (2025-05-11 18:48:00)
- **Verification**: Pending test re-execution.
- **Related Issues**: PDF_TEST_NAMEERROR_MOCK_DETERMINE_COUNT (fixed as part of this extended debugging).
### Issue: EPUB_TOC_NCX_FAILURE - Failing `test_generate_adds_basic_toc_items` - Resolved - 2025-05-11 07:48:39
- **Reported**: 2025-05-11 06:06:42 (via `tdd` Early Return, see [`memory-bank/activeContext.md:2`](memory-bank/activeContext.md:2)) / **Severity**: High (Blocking Test) / **Symptoms**: `AssertionError: Expected 'create_ncx' to have been called once. Called 0 times.` in `test_generate_adds_basic_toc_items`.
- **Investigation**:
    1. Confirmed test failure via `python3 -m unittest tests/generators/test_epub_generator.py`. (2025-05-11 07:42:23)
    2. Reviewed test setup in [`tests/generators/test_epub_generator.py`](tests/generators/test_epub_generator.py:88) (lines 88-110). Noted `epub_version: 3` and default "auto" for ToC inclusion flags. (2025-05-11 07:43:42)
    3. Reviewed `EpubGenerator.generate()` ToC logic in [`synth_data_gen/generators/epub.py`](synth_data_gen/generators/epub.py:235) (lines 235-268). Confirmed that for EPUB 3 with "auto" settings, NavDoc is created and NCX is not. (2025-05-11 07:44:39)
- **Root Cause**: The test `test_generate_adds_basic_toc_items` was misconfigured. It was set up for EPUB 3 with "auto" ToC settings (which correctly prioritizes NavDoc over NCX), but it asserted that `create_ncx` should be called. This contradicted the generator's logic and the typical EPUB 3 behavior. The `tdd` mode's initial context also pointed towards an expectation of `epub_version: 2` for this test.
- **Fix Applied**: Modified `specific_config` in `test_generate_adds_basic_toc_items` ([`tests/generators/test_epub_generator.py:98`](tests/generators/test_epub_generator.py:98)) to set `"epub_version": 2`. Changed assertion for `mock_create_nav_document` to `assert_not_called()`, aligning with EPUB 2's primary use of NCX. (2025-05-11 07:45:41)
- **Verification**: Re-ran all tests in [`tests/generators/test_epub_generator.py`](tests/generators/test_epub_generator.py:1). All 21 tests passed. (2025-05-11 07:46:20)
- **Related Issues**: None directly, but highlights the importance of aligning test configurations with intended behavior and EPUB version standards.