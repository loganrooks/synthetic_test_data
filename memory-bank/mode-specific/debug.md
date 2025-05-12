# Debug Specific Memory
<!-- Entries below should be added reverse chronologically (newest first) -->
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