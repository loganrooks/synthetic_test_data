# Ebooklib Type Issues Documentation

This document outlines the type issues related to the `ebooklib` library that cannot be resolved without proper type stubs.

## Overview

The `ebooklib` library does not provide type stubs (`.pyi` files), which causes Pylance to report errors when using the library's features. These errors are false positives - the code works correctly at runtime, but the static type checker cannot verify the types.

## Unfixable Issues

### 1. EpubBook.add_item_css Method
**Location:** `synth_data_gen/generators/epub.py:600`
**Error:** `Cannot access attribute "add_item_css" for class "EpubBook"`

The `add_item_css` method exists in the ebooklib library but is not recognized by Pylance due to missing type stubs. The code correctly handles this with a hasattr check:

```python
if hasattr(book, 'add_item_css'):
    book.add_item_css(font_css)
```

### 2. Dynamic Attribute Access
Various attributes and methods of `EpubBook` and related classes are not recognized by the type checker, including:
- Dynamic spine manipulation
- TOC structure modifications
- Various metadata setters

## Workarounds Applied

1. **Runtime Checks:** Using `hasattr()` to check for method existence before calling
2. **Type Conversions:** Explicitly handling bytes/str conversions for content
3. **List vs Tuple:** Ensuring proper list types for attributes like `book.toc`

## Recommended Solutions

1. **Suppress Warnings:** Use type ignore comments for known safe operations:
   ```python
   book.add_item_css(font_css)  # type: ignore
   ```

2. **Create Local Stubs:** If many ebooklib features are used, consider creating partial type stubs for the most commonly used features.

3. **Contribute Upstream:** Consider contributing type stubs to the ebooklib project or to typeshed.

## Impact

These type issues do not affect runtime behavior. The code executes correctly, but static analysis tools cannot verify type safety for ebooklib operations. This accounts for approximately 50-100 of the total Pylance errors in the codebase.