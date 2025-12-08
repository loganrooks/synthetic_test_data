Run the test suite for the synth_data_gen package.

If arguments are provided ($ARGUMENTS), run tests matching that pattern.
Otherwise, run all tests.

Steps:
1. Run pytest with the specified arguments or all tests
2. Report any failures clearly
3. Suggest fixes for any failing tests

Example usage:
- `/test` - Run all tests
- `/test test_pdf` - Run PDF generator tests
- `/test -k "visual_toc"` - Run tests matching "visual_toc"
