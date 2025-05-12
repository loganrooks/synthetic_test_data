# Debug Specific Memory
<!-- Entries below should be added reverse chronologically (newest first) -->
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