from ebooklib import epub

# --- Corrected Investigation ---

# Test Case: Adding and Retrieving Calibre-style metadata
book = epub.EpubBook()
book.set_identifier('test-id')
book.set_title('Test Book with Calibre Meta')
book.set_language('en')

# Add Calibre-style metadata
# namespace=None, tag_name='meta', tag_value=None, attributes_dict
book.add_metadata(None, 'meta', None, {'name': 'calibre:series', 'content': 'My Awesome Series'})
book.add_metadata(None, 'meta', None, {'name': 'calibre:series_index', 'content': '1'})
book.add_metadata(None, 'meta', None, {'name': 'calibre:timestamp', 'content': '2024-05-14T12:00:00Z'})
book.add_metadata('DC', 'publisher', 'Test Publisher Inc.') # A standard DC element

print("--- Full book.metadata structure ---")
for namespace, meta_dict in book.metadata.items():
    print(f"Namespace: {namespace}")
    for tag_name, items_list in meta_dict.items():
        print(f"  Tag Name: {tag_name}")
        for i, item_tuple in enumerate(items_list):
            print(f"    Item {i}: {item_tuple} (Length: {len(item_tuple)})")
            if len(item_tuple) == 2: # Expected for meta name/content tags
                tag_text, attrs = item_tuple
                print(f"      Unpacked: tag_text='{tag_text}', attrs={attrs}")
            elif len(item_tuple) == 3: # Expected for standard DC like title, publisher
                 # For items like ('title', 'My Test Book', {}), the first element is the tag name itself
                 # but add_metadata for DC elements stores it as (value, attributes_dict) under the tag name key
                 # Let's adjust based on observed behavior for DC elements from add_metadata
                dc_value, dc_attrs = item_tuple[0], item_tuple[1] # This might need adjustment based on actual DC storage
                # Actually, for DC elements added via add_metadata, it's often (value, attrs)
                # For set_title, set_identifier etc, it's (tag_name_again, value, attrs_dict)
                # This part is tricky, let's focus on the None namespace meta tags.
                # The typical structure for DC elements from add_metadata is ('value_of_tag', {attributes})
                # e.g. for publisher: ('Test Publisher Inc.', {})
                # Let's assume for now the primary interest is the None namespace.
                print(f"      DC-like Unpacked (approx): value='{item_tuple[0]}', attrs={item_tuple[1]}")


print("\n--- Corrected Retrieval for Calibre-style 'meta' tags (namespace None) ---")
retrieved_series_content = None
retrieved_series_index = None

if None in book.metadata and 'meta' in book.metadata[None]:
    meta_items_list = book.metadata[None]['meta']
    print(f"Found 'meta' items under None namespace: {meta_items_list}")
    for tag_text, attrs in meta_items_list: # Unpack as 2-tuple
        print(f"  Inspecting item: text='{tag_text}', attrs={attrs}")
        if isinstance(attrs, dict):
            if attrs.get('name') == 'calibre:series':
                retrieved_series_content = attrs.get('content')
                print(f"    Found 'calibre:series', content: '{retrieved_series_content}'")
            elif attrs.get('name') == 'calibre:series_index':
                retrieved_series_index = attrs.get('content')
                print(f"    Found 'calibre:series_index', content: '{retrieved_series_index}'")
else:
    print("  No 'meta' tags found under None namespace or None namespace not present.")

print(f"\nRetrieved calibre:series content: {retrieved_series_content}")
print(f"Retrieved calibre:series_index content: {retrieved_series_index}")

print("\n--- Verifying standard DC metadata (e.g., publisher) ---")
retrieved_publisher = None
if 'DC' in book.metadata and 'publisher' in book.metadata['DC']:
    # Standard DC items are often a list of tuples: (value, attributes_dict)
    # Example: book.metadata['DC']['publisher'] = [('Test Publisher Inc.', {})]
    publisher_list = book.metadata['DC']['publisher']
    if publisher_list:
        # Assuming the first publisher entry
        pub_value, pub_attrs = publisher_list[0]
        retrieved_publisher = pub_value
        print(f"  Found 'DC:publisher', value: '{retrieved_publisher}', attrs: {pub_attrs}")
else:
    print("  DC:publisher not found.")

print(f"\nRetrieved DC:publisher: {retrieved_publisher}")


print("\n--- How set_title, set_identifier are stored ---")
# These are typically stored with their Dublin Core namespace ('DC')
# and the tag name itself is part of the tuple.
# e.g., book.metadata['DC']['title'] = [('title', 'Test Book with Calibre Meta', {})]
# e.g., book.metadata['DC']['identifier'] = [('identifier', 'test-id', {'id': 'id'})]

if 'DC' in book.metadata:
    if 'title' in book.metadata['DC']:
        print(f"DC title entry: {book.metadata['DC']['title']}")
    if 'identifier' in book.metadata['DC']:
        print(f"DC identifier entry: {book.metadata['DC']['identifier']}")
    if 'language' in book.metadata['DC']:
        print(f"DC language entry: {book.metadata['DC']['language']}")


print("-" * 30)
print("Investigation script finished.")