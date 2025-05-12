import unittest
import os
from unittest.mock import patch, MagicMock, call
from synth_data_gen.generators.markdown import MarkdownGenerator
from synth_data_gen.core.base import BaseGenerator

class TestMarkdownGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = MarkdownGenerator()
        self.output_dir = "test_output_markdown"
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        # Clean up created files and directory
        if os.path.exists(self.output_dir):
            for item in os.listdir(self.output_dir):
                os.remove(os.path.join(self.output_dir, item))
            os.rmdir(self.output_dir)

    def test_get_default_specific_config(self):
        """Test that get_default_specific_config for Markdown returns the expected structure."""
        defaults = self.generator.get_default_specific_config()
        
        self.assertIsInstance(defaults, dict)
        self.assertIn("headings_config", defaults)
        self.assertIsInstance(defaults["headings_config"], dict)
        self.assertIn("max_depth", defaults["headings_config"])
        self.assertEqual(defaults["headings_config"]["max_depth"], 3)
        
        self.assertIn("md_list_items_config", defaults)
        self.assertIsInstance(defaults["md_list_items_config"], dict)
        
        self.assertIn("md_images_config", defaults)
        self.assertIsInstance(defaults["md_images_config"], dict)

        self.assertIn("gfm_features", defaults)
        self.assertIsInstance(defaults["gfm_features"], dict)
        self.assertTrue(defaults["gfm_features"]["md_tables_occurrence_config"]) # Example check

        self.assertIn("frontmatter", defaults)
        self.assertIsInstance(defaults["frontmatter"], dict)

    @patch('synth_data_gen.generators.markdown.ensure_output_directories')
    @patch.object(MarkdownGenerator, '_determine_count')
    # Removed mock for _create_md_basic_elements_content to let it run
    def test_generate_exact_headings_count(
        self, mock_determine_count, mock_ensure_dirs # mock_create_content removed
    ):
        """Test that generate respects headings_config.count for exact heading generation."""
        exact_heading_count = 2
        
        # Mock _determine_count to return specific values based on context
        def determine_count_side_effect(config_value, context_key):
            if context_key == "headings":
                return exact_heading_count
            # Return default/simple values for other expected calls by _create_md_basic_elements_content
            elif context_key == "md_list_items":
                # Ensure the config_value is a dict before .get()
                return config_value.get("count", 0) if isinstance(config_value, dict) else 0
            elif context_key == "md_images":
                return config_value.get("count", 0) if isinstance(config_value, dict) else 0
            # Add other GFM features if _create_md_basic_elements_content calls them
            elif context_key == "md_tables": # This context key might not be used by basic_elements
                 return config_value.get("count", 0) if isinstance(config_value, dict) else 0
            elif context_key == "md_code_blocks": # This context key might not be used by basic_elements
                 return config_value.get("count", 0) if isinstance(config_value, dict) else 0
            return 1 # Default for other potential calls
        mock_determine_count.side_effect = determine_count_side_effect
        
        specific_config = {
            "headings_config": {"count": exact_heading_count, "max_depth": 2},
            "md_list_items_config": {"count": 0}, # Simplify other elements
            "md_images_config": {"count": 0},
            "gfm_features": {"md_tables_occurrence_config": {"count": 0}, "md_code_blocks_config": {"count": 0}},
            "frontmatter": {"include_chance": 0.0}, # No frontmatter for simplicity
            "md_variant": "basic_elements"
        }
        global_config = {"default_language": "en"}
        output_path = os.path.join(self.output_dir, "test_exact_headings.md")

        self.generator.generate(specific_config, global_config, output_path)

        mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
        
        # Assert that _determine_count was called with the headings_config and "headings"
        self.assertIn(
            call(specific_config["headings_config"], "headings"),
            mock_determine_count.call_args_list
        )
        
        # Since _create_md_basic_elements_content is no longer mocked, we can't assert its call count directly here.
        # The primary check is that _determine_count was called correctly for headings.
        # We can also check the output file content if necessary for a more integrated test.
        # For now, focusing on the _determine_count call.

    @patch('synth_data_gen.generators.markdown.ensure_output_directories')
    @patch.object(MarkdownGenerator, '_determine_count')
    def test_generate_exact_list_items_count(
        self, mock_determine_count, mock_ensure_dirs
    ):
        """Test that generate respects md_list_items_config.count for exact list item generation."""
        exact_list_item_count = 3
        
        def determine_count_side_effect(config_value, context_key):
            if context_key == "headings": # From previous test logic in _create_md_basic_elements_content
                return config_value.get("count", 1) if isinstance(config_value, dict) else 1
            elif context_key == "md_list_items":
                return exact_list_item_count
            # Default for other potential calls from _create_md_basic_elements_content
            elif context_key == "md_images":
                return config_value.get("count", 0) if isinstance(config_value, dict) else 0
            return 1
        mock_determine_count.side_effect = determine_count_side_effect

        specific_config = {
            "headings_config": {"count": 1, "max_depth": 1}, # Minimal headings
            "md_list_items_config": {"count": exact_list_item_count, "max_nesting_depth": 1, "include_lists": True},
            "md_images_config": {"count": 0},
            "gfm_features": {"md_tables_occurrence_config": {"count": 0}, "md_code_blocks_config": {"count": 0}},
            "frontmatter": {"include_chance": 0.0},
            "md_variant": "basic_elements"
        }
        global_config = {"default_language": "en"}
        output_path = os.path.join(self.output_dir, "test_exact_list_items.md")

        self.generator.generate(specific_config, global_config, output_path)

        mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
        
        self.assertIn(
            call(specific_config["md_list_items_config"], "md_list_items"),
            mock_determine_count.call_args_list
        )
        # Further checks could involve reading the file and verifying list item count if needed,
        # once _create_md_basic_elements_content is more fully implemented.

    @patch('synth_data_gen.generators.markdown.ensure_output_directories')
    @patch.object(MarkdownGenerator, '_determine_count')
    def test_generate_exact_images_count(
        self, mock_determine_count, mock_ensure_dirs
    ):
        """Test that generate respects md_images_config.count for exact image generation."""
        exact_image_count = 2
        
        def determine_count_side_effect(config_value, context_key):
            if context_key == "headings":
                return config_value.get("count", 1) if isinstance(config_value, dict) else 1
            elif context_key == "md_list_items":
                return config_value.get("count", 0) if isinstance(config_value, dict) else 0
            elif context_key == "md_images":
                return exact_image_count
            return 1
        mock_determine_count.side_effect = determine_count_side_effect

        specific_config = {
            "headings_config": {"count": 1, "max_depth": 1},
            "md_list_items_config": {"count": 0, "include_lists": False},
            "md_images_config": {"count": exact_image_count, "include_images": True},
            "gfm_features": {"md_tables_occurrence_config": {"count": 0}, "md_code_blocks_config": {"count": 0}},
            "frontmatter": {"include_chance": 0.0},
            "md_variant": "basic_elements"
        }
        global_config = {"default_language": "en"}
        output_path = os.path.join(self.output_dir, "test_exact_images.md")

        self.generator.generate(specific_config, global_config, output_path)

        mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
        
        self.assertIn(
            call(specific_config["md_images_config"], "md_images"),
            mock_determine_count.call_args_list
        )

        # For now, focusing on the _determine_count call.

    @patch('synth_data_gen.generators.markdown.ensure_output_directories')
    @patch.object(MarkdownGenerator, '_determine_count')
    def test_generate_exact_gfm_tables_count(
        self, mock_determine_count, mock_ensure_dirs
    ):
        """Test that generate respects gfm_features.md_tables_occurrence_config.count."""
        exact_table_count = 1
        
        def determine_count_side_effect(config_value, context_key):
            if context_key == "md_tables":
                return exact_table_count
            # Provide defaults for other GFM features that might be checked by _create_md_extended_elements_content
            elif context_key == "md_footnotes": # Assuming extended_elements might call this
                return config_value.get("count", 0) if isinstance(config_value, dict) else 0
            elif context_key == "md_task_lists": # Assuming extended_elements might call this
                return config_value.get("count", 0) if isinstance(config_value, dict) else 0
            elif context_key == "md_code_blocks": # Assuming extended_elements might call this
                return config_value.get("count", 0) if isinstance(config_value, dict) else 0
            return 0 # Default for any other calls like headings, lists, images from other content parts
        mock_determine_count.side_effect = determine_count_side_effect

        specific_config = {
            "headings_config": {"count": 0},
            "md_list_items_config": {"count": 0, "include_lists": False},
            "md_images_config": {"count": 0, "include_images": False},
            "gfm_features": {
                "md_tables_occurrence_config": {"count": exact_table_count}, # Target this
                "md_footnotes_occurrence_config": {"count": 0},
                "md_task_lists_occurrence_config": {"count": 0},
                "md_code_blocks_config": {"count": 0, "include_code_blocks": False},
            },
            "frontmatter": {"include_chance": 0.0},
            "md_variant": "extended_elements" # Target the variant that handles GFM features
        }
        global_config = {"default_language": "en"}
        output_path = os.path.join(self.output_dir, "test_exact_tables.md")

        self.generator.generate(specific_config, global_config, output_path)

        mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
        
        self.assertIn(
            call(specific_config["gfm_features"]["md_tables_occurrence_config"], "md_tables"),
            mock_determine_count.call_args_list
        )
@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
@patch('synth_data_gen.core.base.random.randint') # Patch randint in BaseGenerator's context
def test_generate_range_headings_count(
    self, mock_randint, mock_determine_count, mock_ensure_dirs
):
    """Test that generate respects headings_config for range-based heading generation."""
    min_headings = 2
    max_headings = 5
    expected_headings_from_range = 3 # Assume randint will return this
    mock_randint.return_value = expected_headings_from_range

    # Let _determine_count run its actual logic by wrapping the original method
    # This is important because _determine_count itself calls the mocked randint
    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(self_instance, config_value, context_key):
        # Call the original _determine_count from BaseGenerator
        # Ensure 'self_instance' is the generator instance
        return original_determine_count(self_instance, config_value, context_key)
    
    mock_determine_count.side_effect = determine_count_side_effect

    specific_config = {
        "headings_config": {"min": min_headings, "max": max_headings, "max_depth": 2},
        "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0},
        "gfm_features": {"md_tables_occurrence_config": {"count": 0}, "md_code_blocks_config": {"count": 0}},
        "frontmatter": {"include_chance": 0.0},
        "md_variant": "basic_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(self.output_dir, "test_range_headings.md")

    # Patch _create_md_basic_elements_content to check its call count for headings
    with patch.object(self.generator, '_create_md_heading', return_value="") as mock_create_heading:
        self.generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
    
    # Check that _determine_count was called for headings
    self.assertIn(
        call(self.generator, specific_config["headings_config"], "headings"), # Pass generator instance
        mock_determine_count.call_args_list
    )
    # Check that randint was called by _determine_count
    mock_randint.assert_called_once_with(min_headings, max_headings)
    
    # Check that _create_md_heading was called the number of times randint returned
    self.assertEqual(mock_create_heading.call_count, expected_headings_from_range)
@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
@patch('synth_data_gen.core.base.random.random') # Patch random.random for probability
@patch('synth_data_gen.core.base.random.randint') # Patch randint for if_true/if_false
def test_generate_probabilistic_headings_count(
    self, mock_randint, mock_random_random, mock_determine_count, mock_ensure_dirs
):
    """Test that generate respects headings_config for probabilistic heading generation."""
    # Scenario 1: Probability check passes, if_true is an exact count
    mock_random_random.return_value = 0.05 # Lower than chance, so it should pass
    expected_headings_from_prob_exact = 3
    
    # Let _determine_count run its actual logic
    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(self_instance, config_value, context_key):
        return original_determine_count(self_instance, config_value, context_key)
    mock_determine_count.side_effect = determine_count_side_effect

    headings_prob_config_exact = {
        "chance": 0.1,
        "if_true": expected_headings_from_prob_exact, # Exact count
        "if_false": 0,
        "max_depth": 2
    }
    specific_config_exact = {
        "headings_config": headings_prob_config_exact,
        "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0},
        "gfm_features": {"md_tables_occurrence_config": {"count": 0}, "md_code_blocks_config": {"count": 0}},
        "frontmatter": {"include_chance": 0.0},
        "md_variant": "basic_elements"
    }
    global_config = {"default_language": "en"}
    output_path_exact = os.path.join(self.output_dir, "test_prob_headings_exact.md")

    with patch.object(self.generator, '_create_md_heading', return_value="") as mock_create_heading_exact:
        self.generator.generate(specific_config_exact, global_config, output_path_exact)

    mock_ensure_dirs.assert_any_call(os.path.dirname(output_path_exact))
    self.assertIn(
        call(self.generator, headings_prob_config_exact, "headings"),
        mock_determine_count.call_args_list
    )
    mock_random_random.assert_called_once() # Ensure probability was checked
    self.assertEqual(mock_create_heading_exact.call_count, expected_headings_from_prob_exact)

    # Reset mocks for Scenario 2
    mock_random_random.reset_mock()
    mock_randint.reset_mock()
    mock_determine_count.reset_mock() # Reset all calls to _determine_count
    mock_determine_count.side_effect = determine_count_side_effect # Re-apply side effect
    
    # Scenario 2: Probability check passes, if_true is a range
    mock_random_random.return_value = 0.03 # Lower than chance
    min_headings_range = 2
    max_headings_range = 4
    expected_headings_from_prob_range = 3
    mock_randint.return_value = expected_headings_from_prob_range

    headings_prob_config_range = {
        "chance": 0.05,
        "if_true": {"min": min_headings_range, "max": max_headings_range}, # Range count
        "if_false": {"count": 0}, # Using object form for if_false
        "max_depth": 2
    }
    specific_config_range = {
        "headings_config": headings_prob_config_range,
        "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0},
        "gfm_features": {"md_tables_occurrence_config": {"count": 0}, "md_code_blocks_config": {"count": 0}},
        "frontmatter": {"include_chance": 0.0},
        "md_variant": "basic_elements"
    }
    output_path_range = os.path.join(self.output_dir, "test_prob_headings_range.md")

    with patch.object(self.generator, '_create_md_heading', return_value="") as mock_create_heading_range:
        self.generator.generate(specific_config_range, global_config, output_path_range)
    
    self.assertIn(
        call(self.generator, headings_prob_config_range, "headings"),
        mock_determine_count.call_args_list
    )
    mock_random_random.assert_called_once()
    mock_randint.assert_called_once_with(min_headings_range, max_headings_range)
    self.assertEqual(mock_create_heading_range.call_count, expected_headings_from_prob_range)

    # Scenario 3: Probability check fails
    mock_random_random.reset_mock()
    mock_randint.reset_mock()
    mock_determine_count.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect

    mock_random_random.return_value = 0.5 # Higher than chance
    expected_headings_if_false = 1 # if_false is an exact count

    headings_prob_config_fail = {
        "chance": 0.1,
        "if_true": {"count": 5},
        "if_false": expected_headings_if_false, # Exact count for if_false
        "max_depth": 2
    }
    specific_config_fail = {
        "headings_config": headings_prob_config_fail,
        # ... other configs ...
        "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0},
        "gfm_features": {"md_tables_occurrence_config": {"count": 0}, "md_code_blocks_config": {"count": 0}},
        "frontmatter": {"include_chance": 0.0},
        "md_variant": "basic_elements"
    }
    output_path_fail = os.path.join(self.output_dir, "test_prob_headings_fail.md")

    with patch.object(self.generator, '_create_md_heading', return_value="") as mock_create_heading_fail:
        self.generator.generate(specific_config_fail, global_config, output_path_fail)

    self.assertIn(
        call(self.generator, headings_prob_config_fail, "headings"),
        mock_determine_count.call_args_list
    )
    mock_random_random.assert_called_once()
    mock_randint.assert_not_called() # Should not be called if probability fails and if_false is exact
    self.assertEqual(mock_create_heading_fail.call_count, expected_headings_if_false)
@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
@patch('synth_data_gen.core.base.random.randint')
def test_generate_range_list_items_count(
    self, mock_randint, mock_determine_count, mock_ensure_dirs
):
    """Test that generate respects md_list_items_config for range-based list item generation."""
    min_list_items = 2
    max_list_items = 5
    expected_list_items_from_range = 4
    mock_randint.return_value = expected_list_items_from_range

    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(self_instance, config_value, context_key):
        # For md_list_items, we want the original logic to run to hit randint
        if context_key == "md_list_items":
            return original_determine_count(self_instance, config_value, context_key)
        # For other calls (like headings), return a simple default to avoid interference
        elif context_key == "headings":
             return config_value.get("count", 1) if isinstance(config_value, dict) else 1
        elif context_key == "md_images":
             return config_value.get("count", 0) if isinstance(config_value, dict) else 0
        return 1 # Default for other potential calls
    mock_determine_count.side_effect = determine_count_side_effect
    
    specific_config = {
        "headings_config": {"count": 1, "max_depth": 1}, # Minimal headings
        "md_list_items_config": {
            "min": min_list_items,
            "max": max_list_items,
            "max_nesting_depth": 1,
            "include_lists": True
        },
        "md_images_config": {"count": 0},
        "gfm_features": {"md_tables_occurrence_config": {"count": 0}, "md_code_blocks_config": {"count": 0}},
        "frontmatter": {"include_chance": 0.0},
        "md_variant": "basic_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(self.output_dir, "test_range_list_items.md")

    # We need to check how many times list item creation is called.
    # Assuming _create_md_list_item is the method responsible for generating a single list item.
    with patch.object(self.generator, '_create_md_list_item', return_value="- item\n") as mock_create_list_item:
        self.generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_any_call(os.path.dirname(output_path))
    
    # Check that _determine_count was called for md_list_items
    # The call to _determine_count for md_list_items will be made with the generator instance
    self.assertIn(
        call(self.generator, specific_config["md_list_items_config"], "md_list_items"),
        mock_determine_count.call_args_list
    )
    # Check that randint was called by _determine_count for md_list_items
    mock_randint.assert_called_once_with(min_list_items, max_list_items)
    
    # Check that _create_md_list_item was called the number of times randint returned
    self.assertEqual(mock_create_list_item.call_count, expected_list_items_from_range)
@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
@patch('synth_data_gen.core.base.random.random')  # For probability check
@patch('synth_data_gen.core.base.random.randint')  # For range within probabilistic
def test_generate_probabilistic_list_items_count(
    self, mock_randint, mock_random_random, mock_determine_count, mock_ensure_dirs
):
    """Test probabilistic md_list_items_config for list item generation."""
    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(self_instance, config_value, context_key):
        if context_key == "md_list_items": # Target this call
            return original_determine_count(self_instance, config_value, context_key)
        # Simplified defaults for other calls within _create_md_basic_elements_content
        elif context_key == "headings":
            return 1
        elif context_key == "md_images":
            return 0
        return 0 # Default for any other unexpected calls
    mock_determine_count.side_effect = determine_count_side_effect

    # Scenario 1: Probability passes, if_true is exact
    mock_random_random.return_value = 0.05 # Pass
    expected_items_scenario1 = 2
    list_items_config_s1 = {
        "chance": 0.1, "if_true": expected_items_scenario1, "if_false": 0,
        "max_nesting_depth": 1, "include_lists": True
    }
    specific_config_s1 = {
        "headings_config": {"count": 0},
        "md_list_items_config": list_items_config_s1,
        "md_images_config": {"count": 0},
        "gfm_features": {}, "frontmatter": {"include_chance": 0.0}, "md_variant": "basic_elements"
    }
    output_path_s1 = os.path.join(self.output_dir, "test_prob_list_items_s1.md")
    with patch.object(self.generator, '_create_md_list_item', return_value="- item\n") as mock_create_item_s1:
        self.generator.generate(specific_config_s1, {"default_language": "en"}, output_path_s1)
    
    self.assertIn(call(self.generator, list_items_config_s1, "md_list_items"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    self.assertEqual(mock_create_item_s1.call_count, expected_items_scenario1)

    # Reset mocks for Scenario 2
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect

    # Scenario 2: Probability passes, if_true is a range
    mock_random_random.return_value = 0.02 # Pass
    min_items_s2, max_items_s2 = 1, 3
    expected_items_scenario2 = 2 # Assume randint returns this
    mock_randint.return_value = expected_items_scenario2
    list_items_config_s2 = {
        "chance": 0.1, "if_true": {"min": min_items_s2, "max": max_items_s2}, "if_false": 0,
        "max_nesting_depth": 1, "include_lists": True
    }
    specific_config_s2 = {
        "headings_config": {"count": 0},
        "md_list_items_config": list_items_config_s2,
        "md_images_config": {"count": 0},
        "gfm_features": {}, "frontmatter": {"include_chance": 0.0}, "md_variant": "basic_elements"
    }
    output_path_s2 = os.path.join(self.output_dir, "test_prob_list_items_s2.md")
    with patch.object(self.generator, '_create_md_list_item', return_value="- item\n") as mock_create_item_s2:
        self.generator.generate(specific_config_s2, {"default_language": "en"}, output_path_s2)

    self.assertIn(call(self.generator, list_items_config_s2, "md_list_items"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    mock_randint.assert_called_once_with(min_items_s2, max_items_s2)
    self.assertEqual(mock_create_item_s2.call_count, expected_items_scenario2)

    # Scenario 3: Probability fails
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect
    mock_random_random.return_value = 0.5 # Fail
    expected_items_scenario3 = 0 # if_false is 0
    list_items_config_s3 = {
        "chance": 0.1, "if_true": 5, "if_false": expected_items_scenario3,
        "max_nesting_depth": 1, "include_lists": True
    }
    specific_config_s3 = {
        "headings_config": {"count": 0},
        "md_list_items_config": list_items_config_s3,
        "md_images_config": {"count": 0},
        "gfm_features": {}, "frontmatter": {"include_chance": 0.0}, "md_variant": "basic_elements"
    }
    output_path_s3 = os.path.join(self.output_dir, "test_prob_list_items_s3.md")
    with patch.object(self.generator, '_create_md_list_item', return_value="- item\n") as mock_create_item_s3:
        self.generator.generate(specific_config_s3, {"default_language": "en"}, output_path_s3)

    self.assertIn(call(self.generator, list_items_config_s3, "md_list_items"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    mock_randint.assert_not_called()
    self.assertEqual(mock_create_item_s3.call_count, expected_items_scenario3)

@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
@patch('synth_data_gen.core.base.random.randint')
def test_generate_range_images_count(
    self, mock_randint, mock_determine_count, mock_ensure_dirs
):
    """Test that generate respects md_images_config for range-based image generation."""
    min_images = 1
    max_images = 3
    expected_images_from_range = 2
    mock_randint.return_value = expected_images_from_range

    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(self_instance, config_value, context_key):
        if context_key == "md_images":
            return original_determine_count(self_instance, config_value, context_key)
        elif context_key == "headings": return 1
        elif context_key == "md_list_items": return 0
        return 0
    mock_determine_count.side_effect = determine_count_side_effect
    
    specific_config = {
        "headings_config": {"count": 1},
        "md_list_items_config": {"count": 0, "include_lists": False},
        "md_images_config": {
            "min": min_images, "max": max_images, "include_images": True
        },
        "gfm_features": {}, "frontmatter": {"include_chance": 0.0}, "md_variant": "basic_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(self.output_dir, "test_range_images.md")

    with patch.object(self.generator, '_create_md_image', return_value="![alt](src)\n") as mock_create_image:
        self.generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_any_call(os.path.dirname(output_path))
    self.assertIn(
        call(self.generator, specific_config["md_images_config"], "md_images"),
        mock_determine_count.call_args_list
    )
    mock_randint.assert_called_once_with(min_images, max_images)
    self.assertEqual(mock_create_image.call_count, expected_images_from_range)

@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
@patch('synth_data_gen.core.base.random.random')
@patch('synth_data_gen.core.base.random.randint')
def test_generate_probabilistic_images_count(
    self, mock_randint, mock_random_random, mock_determine_count, mock_ensure_dirs
):
    """Test probabilistic md_images_config for image generation."""
    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(self_instance, config_value, context_key):
        if context_key == "md_images":
            return original_determine_count(self_instance, config_value, context_key)
        elif context_key == "headings": return 1
        elif context_key == "md_list_items": return 0
        return 0
    mock_determine_count.side_effect = determine_count_side_effect

    # Scenario 1: Probability passes, if_true is exact
    mock_random_random.return_value = 0.05 # Pass
    expected_images_s1 = 1
    images_config_s1 = {
        "chance": 0.1, "if_true": expected_images_s1, "if_false": 0, "include_images": True
    }
    specific_config_s1 = {
        "headings_config": {"count": 0}, "md_list_items_config": {"count": 0},
        "md_images_config": images_config_s1,
        "gfm_features": {}, "frontmatter": {"include_chance": 0.0}, "md_variant": "basic_elements"
    }
    output_path_s1 = os.path.join(self.output_dir, "test_prob_images_s1.md")
    with patch.object(self.generator, '_create_md_image', return_value="![alt](src)\n") as mock_create_image_s1:
        self.generator.generate(specific_config_s1, {"default_language": "en"}, output_path_s1)
    
    self.assertIn(call(self.generator, images_config_s1, "md_images"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    self.assertEqual(mock_create_image_s1.call_count, expected_images_s1)

    # Reset mocks for Scenario 2
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect

    # Scenario 2: Probability passes, if_true is a range
    mock_random_random.return_value = 0.02 # Pass
    min_images_s2, max_images_s2 = 1, 2
    expected_images_s2 = 1 # Assume randint returns this
    mock_randint.return_value = expected_images_s2
    images_config_s2 = {
        "chance": 0.1, "if_true": {"min": min_images_s2, "max": max_images_s2}, "if_false": 0, "include_images": True
    }
    specific_config_s2 = {
        "headings_config": {"count": 0}, "md_list_items_config": {"count": 0},
        "md_images_config": images_config_s2,
        "gfm_features": {}, "frontmatter": {"include_chance": 0.0}, "md_variant": "basic_elements"
    }
    output_path_s2 = os.path.join(self.output_dir, "test_prob_images_s2.md")
    with patch.object(self.generator, '_create_md_image', return_value="![alt](src)\n") as mock_create_image_s2:
        self.generator.generate(specific_config_s2, {"default_language": "en"}, output_path_s2)

    self.assertIn(call(self.generator, images_config_s2, "md_images"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    mock_randint.assert_called_once_with(min_images_s2, max_images_s2)
    self.assertEqual(mock_create_image_s2.call_count, expected_images_s2)

    # Scenario 3: Probability fails
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect
    mock_random_random.return_value = 0.5 # Fail
    expected_images_s3 = 0 # if_false is 0
    images_config_s3 = {
        "chance": 0.1, "if_true": 3, "if_false": expected_images_s3, "include_images": True
    }
    specific_config_s3 = {
        "headings_config": {"count": 0}, "md_list_items_config": {"count": 0},
        "md_images_config": images_config_s3,
        "gfm_features": {}, "frontmatter": {"include_chance": 0.0}, "md_variant": "basic_elements"
    }
    output_path_s3 = os.path.join(self.output_dir, "test_prob_images_s3.md")
    with patch.object(self.generator, '_create_md_image', return_value="![alt](src)\n") as mock_create_image_s3:
        self.generator.generate(specific_config_s3, {"default_language": "en"}, output_path_s3)

    self.assertIn(call(self.generator, images_config_s3, "md_images"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    mock_randint.assert_not_called()
    self.assertEqual(mock_create_image_s3.call_count, expected_images_s3)

@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
def test_generate_exact_footnotes_count(
    self, mock_determine_count, mock_ensure_dirs
):
    """Test exact count for md_footnotes_occurrence_config."""
    exact_footnotes_count = 2
    
    def determine_count_side_effect(config_value, context_key):
        if context_key == "md_footnotes":
            return exact_footnotes_count
        # Defaults for other GFM features in _create_md_extended_elements_content
        elif context_key == "md_tables": return 0
        elif context_key == "md_task_lists": return 0
        elif context_key == "md_code_blocks": return 0
        return 0
    mock_determine_count.side_effect = determine_count_side_effect

    specific_config = {
        "gfm_features": {
            "md_footnotes_occurrence_config": {"count": exact_footnotes_count},
            "md_tables_occurrence_config": {"count": 0},
            "md_task_lists_occurrence_config": {"count": 0},
            "md_code_blocks_config": {"count": 0, "include_code_blocks": False},
        },
        "headings_config": {"count": 0}, "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0}, "frontmatter": {"include_chance": 0.0},
        "md_variant": "extended_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(self.output_dir, "test_exact_footnotes.md")

    with patch.object(self.generator, '_create_md_footnote', return_value="[^1]: Footnote\n") as mock_create_footnote:
        self.generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_any_call(os.path.dirname(output_path))
    self.assertIn(
        call(specific_config["gfm_features"]["md_footnotes_occurrence_config"], "md_footnotes"),
        mock_determine_count.call_args_list
    )
    self.assertEqual(mock_create_footnote.call_count, exact_footnotes_count)

@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
@patch('synth_data_gen.core.base.random.randint')
def test_generate_range_footnotes_count(
    self, mock_randint, mock_determine_count, mock_ensure_dirs
):
    """Test range count for md_footnotes_occurrence_config."""
    min_footnotes, max_footnotes = 1, 4
    expected_footnotes = 2
    mock_randint.return_value = expected_footnotes

    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(self_instance, config_value, context_key):
        if context_key == "md_footnotes":
            return original_determine_count(self_instance, config_value, context_key)
        return 0 # For other GFM features
    mock_determine_count.side_effect = determine_count_side_effect

    footnotes_config = {"min": min_footnotes, "max": max_footnotes}
    specific_config = {
        "gfm_features": {
            "md_footnotes_occurrence_config": footnotes_config,
            "md_tables_occurrence_config": {"count": 0},
            "md_task_lists_occurrence_config": {"count": 0},
            "md_code_blocks_config": {"count": 0, "include_code_blocks": False},
        },
        "headings_config": {"count": 0}, "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0}, "frontmatter": {"include_chance": 0.0},
        "md_variant": "extended_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(self.output_dir, "test_range_footnotes.md")

    with patch.object(self.generator, '_create_md_footnote', return_value="[^1]: Footnote\n") as mock_create_footnote:
        self.generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_any_call(os.path.dirname(output_path))
    self.assertIn(
        call(self.generator, footnotes_config, "md_footnotes"),
        mock_determine_count.call_args_list
    )
    mock_randint.assert_called_once_with(min_footnotes, max_footnotes)
    self.assertEqual(mock_create_footnote.call_count, expected_footnotes)

@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
@patch('synth_data_gen.core.base.random.random')
@patch('synth_data_gen.core.base.random.randint')
def test_generate_probabilistic_footnotes_count(
    self, mock_randint, mock_random_random, mock_determine_count, mock_ensure_dirs
):
    """Test probabilistic md_footnotes_occurrence_config."""
    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(self_instance, config_value, context_key):
        if context_key == "md_footnotes":
            return original_determine_count(self_instance, config_value, context_key)
        return 0 # For other GFM features
    mock_determine_count.side_effect = determine_count_side_effect

    # Scenario 1: Passes, if_true is exact
    mock_random_random.return_value = 0.05
    expected_s1 = 1
    config_s1 = {"chance": 0.1, "if_true": expected_s1, "if_false": 0}
    specific_s1 = {
        "gfm_features": {"md_footnotes_occurrence_config": config_s1, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_s1 = os.path.join(self.output_dir, "test_prob_footnotes_s1.md")
    with patch.object(self.generator, '_create_md_footnote', return_value="") as mock_create_s1:
        self.generator.generate(specific_s1, {}, output_s1)
    self.assertIn(call(self.generator, config_s1, "md_footnotes"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    self.assertEqual(mock_create_s1.call_count, expected_s1)
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect

    # Scenario 2: Passes, if_true is range
    mock_random_random.return_value = 0.02
    min_s2, max_s2 = 2, 3
    expected_s2 = 2
    mock_randint.return_value = expected_s2
    config_s2 = {"chance": 0.1, "if_true": {"min": min_s2, "max": max_s2}, "if_false": 0}
    specific_s2 = {
        "gfm_features": {"md_footnotes_occurrence_config": config_s2, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_s2 = os.path.join(self.output_dir, "test_prob_footnotes_s2.md")
    with patch.object(self.generator, '_create_md_footnote', return_value="") as mock_create_s2:
        self.generator.generate(specific_s2, {}, output_s2)
    self.assertIn(call(self.generator, config_s2, "md_footnotes"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    mock_randint.assert_called_once_with(min_s2, max_s2)
    self.assertEqual(mock_create_s2.call_count, expected_s2)
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect
    
    # Scenario 3: Fails
    mock_random_random.return_value = 0.5
    expected_s3 = 0
    config_s3 = {"chance": 0.1, "if_true": 5, "if_false": expected_s3}
    specific_s3 = {
        "gfm_features": {"md_footnotes_occurrence_config": config_s3, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_s3 = os.path.join(self.output_dir, "test_prob_footnotes_s3.md")
    with patch.object(self.generator, '_create_md_footnote', return_value="") as mock_create_s3:
        self.generator.generate(specific_s3, {}, output_s3)
    self.assertIn(call(self.generator, config_s3, "md_footnotes"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    mock_randint.assert_not_called()
    self.assertEqual(mock_create_s3.call_count, expected_s3)

@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
def test_generate_exact_task_lists_count(
    self, mock_determine_count, mock_ensure_dirs
):
    """Test exact count for md_task_lists_occurrence_config."""
    exact_count = 1
    def side_effect(config, key): return exact_count if key == "md_task_lists" else 0
    mock_determine_count.side_effect = side_effect
    config = {"count": exact_count}
    specific = {
        "gfm_features": {"md_task_lists_occurrence_config": config, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_path = os.path.join(self.output_dir, "test_exact_task_lists.md")
    with patch.object(self.generator, '_create_md_task_list', return_value="- [ ] Task\n") as mock_create:
        self.generator.generate(specific, {}, output_path)
    self.assertIn(call(config, "md_task_lists"), mock_determine_count.call_args_list)
    self.assertEqual(mock_create.call_count, exact_count)

@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
@patch('synth_data_gen.core.base.random.randint')
def test_generate_range_task_lists_count(
    self, mock_randint, mock_determine_count, mock_ensure_dirs
):
    """Test range count for md_task_lists_occurrence_config."""
    min_val, max_val = 1, 3
    expected_val = 2
    mock_randint.return_value = expected_val
    original_determine_count = BaseGenerator._determine_count
    def side_effect(self_i, config, key): return original_determine_count(self_i, config, key) if key == "md_task_lists" else 0
    mock_determine_count.side_effect = side_effect
    config = {"min": min_val, "max": max_val}
    specific = {
        "gfm_features": {"md_task_lists_occurrence_config": config, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_path = os.path.join(self.output_dir, "test_range_task_lists.md")
    with patch.object(self.generator, '_create_md_task_list', return_value="") as mock_create:
        self.generator.generate(specific, {}, output_path)
    self.assertIn(call(self.generator, config, "md_task_lists"), mock_determine_count.call_args_list)
    mock_randint.assert_called_once_with(min_val, max_val)
    self.assertEqual(mock_create.call_count, expected_val)

@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
@patch('synth_data_gen.core.base.random.random')
@patch('synth_data_gen.core.base.random.randint')
def test_generate_probabilistic_task_lists_count(
    self, mock_randint, mock_random_random, mock_determine_count, mock_ensure_dirs
):
    """Test probabilistic md_task_lists_occurrence_config."""
    original_determine_count = BaseGenerator._determine_count
    def side_effect(self_i, config, key): return original_determine_count(self_i, config, key) if key == "md_task_lists" else 0
    mock_determine_count.side_effect = side_effect

    # Scenario 1: Passes, if_true is exact
    mock_random_random.return_value = 0.05
    expected_s1 = 1
    config_s1 = {"chance": 0.1, "if_true": expected_s1, "if_false": 0}
    specific_s1 = {
        "gfm_features": {"md_task_lists_occurrence_config": config_s1, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    with patch.object(self.generator, '_create_md_task_list', return_value="") as mock_create_s1:
        self.generator.generate(specific_s1, {}, "path1.md")
    self.assertIn(call(self.generator, config_s1, "md_task_lists"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    self.assertEqual(mock_create_s1.call_count, expected_s1)
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_determine_count.side_effect = side_effect

    # Scenario 2: Passes, if_true is range
    mock_random_random.return_value = 0.02
    min_s2, max_s2 = 1, 2
    expected_s2 = 1
    mock_randint.return_value = expected_s2
    config_s2 = {"chance": 0.1, "if_true": {"min": min_s2, "max": max_s2}, "if_false": 0}
    specific_s2 = {
        "gfm_features": {"md_task_lists_occurrence_config": config_s2, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    with patch.object(self.generator, '_create_md_task_list', return_value="") as mock_create_s2:
        self.generator.generate(specific_s2, {}, "path2.md")
    self.assertIn(call(self.generator, config_s2, "md_task_lists"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    mock_randint.assert_called_once_with(min_s2, max_s2)
    self.assertEqual(mock_create_s2.call_count, expected_s2)
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_determine_count.side_effect = side_effect
    
    # Scenario 3: Fails
    mock_random_random.return_value = 0.5
    expected_s3 = 0
    config_s3 = {"chance": 0.1, "if_true": 3, "if_false": expected_s3}
    specific_s3 = {
        "gfm_features": {"md_task_lists_occurrence_config": config_s3, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    with patch.object(self.generator, '_create_md_task_list', return_value="") as mock_create_s3:
        self.generator.generate(specific_s3, {}, "path3.md")
    self.assertIn(call(self.generator, config_s3, "md_task_lists"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    mock_randint.assert_not_called()
    self.assertEqual(mock_create_s3.call_count, expected_s3)

@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
def test_generate_exact_code_blocks_count(
    self, mock_determine_count, mock_ensure_dirs
):
    """Test exact count for md_code_blocks_config."""
    exact_count = 1
    def side_effect(config, key): return exact_count if key == "md_code_blocks" else 0
    mock_determine_count.side_effect = side_effect
    config = {"count": exact_count, "include_code_blocks": True}
    specific = {
        "gfm_features": {"md_code_blocks_config": config, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_path = os.path.join(self.output_dir, "test_exact_code_blocks.md")
    with patch.object(self.generator, '_create_md_code_block', return_value="```\ncode\n```\n") as mock_create:
        self.generator.generate(specific, {}, output_path)
    self.assertIn(call(config, "md_code_blocks"), mock_determine_count.call_args_list)
    self.assertEqual(mock_create.call_count, exact_count)

@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
@patch('synth_data_gen.core.base.random.randint')
def test_generate_range_code_blocks_count(
    self, mock_randint, mock_determine_count, mock_ensure_dirs
):
    """Test range count for md_code_blocks_config."""
    min_val, max_val = 2, 4
    expected_val = 3
    mock_randint.return_value = expected_val
    original_determine_count = BaseGenerator._determine_count
    def side_effect(self_i, config, key): return original_determine_count(self_i, config, key) if key == "md_code_blocks" else 0
    mock_determine_count.side_effect = side_effect
    config = {"min": min_val, "max": max_val, "include_code_blocks": True}
    specific = {
        "gfm_features": {"md_code_blocks_config": config, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_path = os.path.join(self.output_dir, "test_range_code_blocks.md")
    with patch.object(self.generator, '_create_md_code_block', return_value="") as mock_create:
        self.generator.generate(specific, {}, output_path)
    self.assertIn(call(self.generator, config, "md_code_blocks"), mock_determine_count.call_args_list)
    mock_randint.assert_called_once_with(min_val, max_val)
    self.assertEqual(mock_create.call_count, expected_val)

@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_determine_count')
@patch('synth_data_gen.core.base.random.random')
@patch('synth_data_gen.core.base.random.randint')
def test_generate_probabilistic_code_blocks_count(
    self, mock_randint, mock_random_random, mock_determine_count, mock_ensure_dirs
):
    """Test probabilistic md_code_blocks_config."""
    original_determine_count = BaseGenerator._determine_count
    def side_effect(self_i, config, key): return original_determine_count(self_i, config, key) if key == "md_code_blocks" else 0
    mock_determine_count.side_effect = side_effect

    # Scenario 1: Passes, if_true is exact
    mock_random_random.return_value = 0.05
    expected_s1 = 2
    config_s1 = {"chance": 0.1, "if_true": expected_s1, "if_false": 0, "include_code_blocks": True}
    specific_s1 = {
        "gfm_features": {"md_code_blocks_config": config_s1, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    with patch.object(self.generator, '_create_md_code_block', return_value="") as mock_create_s1:
        self.generator.generate(specific_s1, {}, "path1.md")
    self.assertIn(call(self.generator, config_s1, "md_code_blocks"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    self.assertEqual(mock_create_s1.call_count, expected_s1)
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_determine_count.side_effect = side_effect

    # Scenario 2: Passes, if_true is range
    mock_random_random.return_value = 0.02
    min_s2, max_s2 = 1, 3
    expected_s2 = 2
    mock_randint.return_value = expected_s2
    config_s2 = {"chance": 0.1, "if_true": {"min": min_s2, "max": max_s2}, "if_false": 0, "include_code_blocks": True}
    specific_s2 = {
        "gfm_features": {"md_code_blocks_config": config_s2, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    with patch.object(self.generator, '_create_md_code_block', return_value="") as mock_create_s2:
        self.generator.generate(specific_s2, {}, "path2.md")
    self.assertIn(call(self.generator, config_s2, "md_code_blocks"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    mock_randint.assert_called_once_with(min_s2, max_s2)
    self.assertEqual(mock_create_s2.call_count, expected_s2)
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_determine_count.side_effect = side_effect
    
    # Scenario 3: Fails
    mock_random_random.return_value = 0.5
    expected_s3 = 0
    config_s3 = {"chance": 0.1, "if_true": 3, "if_false": expected_s3, "include_code_blocks": True}
    specific_s3 = {
        "gfm_features": {"md_code_blocks_config": config_s3, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    with patch.object(self.generator, '_create_md_code_block', return_value="") as mock_create_s3:
        self.generator.generate(specific_s3, {}, "path3.md")
    self.assertIn(call(self.generator, config_s3, "md_code_blocks"), mock_determine_count.call_args_list)
    mock_random_random.assert_called_once()
    mock_randint.assert_not_called()
    self.assertEqual(mock_create_s3.call_count, expected_s3)

@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_create_md_frontmatter') # Mock the actual frontmatter creation
@patch.object(MarkdownGenerator, '_create_md_basic_elements_content', return_value="") # Mock other content
def test_generate_frontmatter_yaml_basic(
    self, mock_basic_content, mock_create_md_frontmatter, mock_ensure_dirs
):
    """Test basic YAML frontmatter generation."""
    expected_fm_content = "---\ntitle: Test YAML\n---\n"
    mock_create_md_frontmatter.return_value = expected_fm_content
    
    frontmatter_config = {
        "style": "yaml",
        "fields": [{"name": "title", "type": "string", "value": "Test YAML"}],
        "include_chance": 1.0
    }
    specific_config = {
        "frontmatter": frontmatter_config,
        "headings_config": {"count": 0}, # No other content for this specific test
        "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0},
        "gfm_features": {},
        "md_variant": "basic_elements" # Frontmatter generation is independent of variant
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(self.output_dir, "test_frontmatter_yaml.md")

    self.generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
    mock_create_md_frontmatter.assert_called_once_with(
        frontmatter_config, global_config
    )
    
    # Verify file content starts with the frontmatter
    with open(output_path, 'r') as f:
        content = f.read()
    self.assertTrue(content.startswith(expected_fm_content))
@patch('synth_data_gen.generators.markdown.ensure_output_directories')
@patch.object(MarkdownGenerator, '_create_md_frontmatter')
def test_generate_frontmatter_yaml_not_included_when_chance_is_zero(
    self, mock_create_frontmatter, mock_ensure_dirs
):
    """Test frontmatter is not generated when include_chance is 0.0."""
    frontmatter_config = {
        "style": "yaml",
        "fields": [{"name": "title", "type": "string", "value": "Test Title"}],
        "include_chance": 0.0 # Ensure it's NOT included
    }
    specific_config = {
        "frontmatter": frontmatter_config,
        "headings_config": {"count": 1, "max_depth": 1}, # Add some basic content
        "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0}, "gfm_features": {},
        "md_variant": "basic_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(self.output_dir, "test_no_frontmatter.md")

    # Mock _create_md_frontmatter to ensure it's not called
    # and to prevent it from actually trying to create frontmatter.
    mock_create_frontmatter.return_value = "---\ntitle: Should Not Be Written\n---\n"

    # Mock _create_md_basic_elements_content to return minimal content
    with patch.object(self.generator, '_create_md_basic_elements_content', return_value="# Dummy Content\n") as mock_basic_content:
        self.generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_any_call(os.path.dirname(output_path))
    # Crucially, _create_md_frontmatter should NOT have been called
    mock_create_frontmatter.assert_not_called()
    
    # Verify file content does NOT start with the frontmatter
    with open(output_path, 'r') as f:
        content = f.read()
    self.assertFalse(content.startswith("---"))
    # Ensure some other content was written
    mock_basic_content.assert_called_once()
    self.assertEqual(content, "# Dummy Content\n")
    @patch('synth_data_gen.generators.markdown.ensure_output_directories')
    # Removed @patch.object(MarkdownGenerator, '_create_md_frontmatter')
    def test_generate_frontmatter_toml_basic(
            self, mock_ensure_dirs # Removed mock_create_md_frontmatter
    ):
            """Test basic TOML frontmatter generation - expecting failure."""
            specific_config = {
                "frontmatter": {
                    "style": "toml",
                    "include_chance": 1.0,
                    "fields": [{"name": "title", "type": "string", "value": "Test TOML"}]
                },
                # Minimal other configs to ensure frontmatter is the focus
                "headings_config": {"count": 0},
                "md_list_items_config": {"count": 0},
                "md_images_config": {"count": 0},
                "gfm_features": {},
                "md_variant": "basic_elements"
            }
            global_config = {"default_language": "en"}
            output_path = os.path.join(self.output_dir, "test_frontmatter_toml.md")
    
            # Ensure the file is empty or non-existent before generation
            if os.path.exists(output_path):
                os.remove(output_path)

            self.generator.generate(specific_config, global_config, output_path)
    
            mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
            
            self.assertTrue(os.path.exists(output_path), "Output file was not created")
            with open(output_path, 'r') as f:
                content = f.read()
            
            # This assertion should fail if _create_md_frontmatter produces YAML (e.g., "---")
            self.assertTrue(content.startswith("+++"),
                            f"Content should start with TOML delimiter '+++', but was: '{content[:10]}...'")
    @patch('synth_data_gen.generators.markdown.ensure_output_directories')
    def test_generate_frontmatter_json_basic(
            self, mock_ensure_dirs
    ):
            """Test basic JSON frontmatter generation."""
            specific_config = {
                "headings_config": {"count": 0},
                "md_list_items_config": {"count": 0},
                "md_images_config": {"count": 0},
                "gfm_features": {},
                "frontmatter": {
                    "style": "json",
                    "include_chance": 1.0,
                    "fields": [{"name": "title", "type": "string", "value": "Test JSON"}]
                },
                "md_variant": "basic_elements"
            }
            global_config = {"default_language": "en"}
            output_path = os.path.join(self.output_dir, "test_frontmatter_json.md")
    
            self.generator.generate(specific_config, global_config, output_path)
    
            mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
            
            with open(output_path, 'r') as f:
                # Assuming frontmatter is at the very beginning, separated by ---
                # and the actual content (if any) follows.
                # The _create_md_frontmatter method is expected to return *only* the frontmatter string.
                # The generate method prepends it.
                full_file_content = f.read()

            # Extract frontmatter part if delimiters are present
            # Current _create_md_frontmatter produces YAML with --- delimiters
            # This test should fail if it's not JSON.
            # A simple check for JSON would be to try and parse it.
            # For now, we'll check for JSON-like properties if it's not strictly YAML.
            # If it's YAML, it will likely start with "---"
            # If it's JSON, it should start with "{" or be empty if no fields.
            # If it's TOML, it starts with "+++"

            # This assertion will fail if the output is YAML, which is the current behavior.
            # A more robust check for JSON would be to attempt json.loads()
            # and check for specific JSON delimiters if the spec requires them (e.g. if it's embedded in ---)
            
            # Forcing a failure if it's not explicitly JSON style, e.g. by checking for { }
            # and not --- if it's meant to be *only* JSON without YAML delimiters.
            # The current SUT produces YAML: "--- \nfields:\n- name: title\n  type: string\n  value: Test JSON\nstyle: json\n---"
            # So, this test needs to be more specific for JSON.
            # If the spec implies JSON frontmatter is *just* the JSON object:
            self.assertTrue(full_file_content.strip().startswith("{") and full_file_content.strip().endswith("}"), "Content should be a JSON object if style is JSON")
            import json
            try:
                # Attempt to parse the frontmatter part as JSON
                # This assumes the frontmatter is the entire content for this test
                json_data = json.loads(full_file_content.strip())
                self.assertEqual(json_data.get("title"), "Test JSON")
            except json.JSONDecodeError:
                self.fail("Frontmatter was not valid JSON.")
if __name__ == '__main__':
    unittest.main()