import pytest
import os
import shutil # Added for tearDown equivalent
from pytest_mock import MockerFixture
from unittest.mock import call # Keep call for checking mock arguments
from synth_data_gen.generators.markdown import MarkdownGenerator
from synth_data_gen.core.base import BaseGenerator
import random # For patching random.randint and random.random
import json # For JSON frontmatter test

@pytest.fixture
def markdown_generator_test_setup():
    generator = MarkdownGenerator()
    output_dir = "test_output_markdown"
    os.makedirs(output_dir, exist_ok=True)
    yield generator, output_dir # Provide the instance and output_dir
    # Clean up created files and directory
    if os.path.exists(output_dir):
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path): # Should not happen with current tests but good practice
                shutil.rmtree(item_path)
        os.rmdir(output_dir)

def test_get_default_specific_config(markdown_generator_test_setup):
    """Test that get_default_specific_config for Markdown returns the expected structure."""
    generator, _ = markdown_generator_test_setup
    defaults = generator.get_default_specific_config()
    
    assert isinstance(defaults, dict)
    assert "headings_config" in defaults
    assert isinstance(defaults["headings_config"], dict)
    assert "max_depth" in defaults["headings_config"]
    assert defaults["headings_config"]["max_depth"] == 3
    
    assert "md_list_items_config" in defaults
    assert isinstance(defaults["md_list_items_config"], dict)
    
    assert "md_images_config" in defaults
    assert isinstance(defaults["md_images_config"], dict)

    assert "gfm_features" in defaults
    assert isinstance(defaults["gfm_features"], dict)
    assert defaults["gfm_features"]["md_tables_occurrence_config"] # Example check

    assert "frontmatter" in defaults
    assert isinstance(defaults["frontmatter"], dict)

def test_generate_exact_headings_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test that generate respects headings_config.count for exact heading generation."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    
    exact_heading_count = 2
    
    def determine_count_side_effect(config_value, context_key): # Removed self_instance
        if context_key == "headings":
            return exact_heading_count
        elif context_key == "md_list_items":
            return config_value.get("count", 0) if isinstance(config_value, dict) else 0
        elif context_key == "md_images":
            return config_value.get("count", 0) if isinstance(config_value, dict) else 0
        elif context_key == "md_tables":
             return config_value.get("count", 0) if isinstance(config_value, dict) else 0
        elif context_key == "md_code_blocks":
             return config_value.get("count", 0) if isinstance(config_value, dict) else 0
        return 1
    mock_determine_count.side_effect = determine_count_side_effect
    
    specific_config = {
        "headings_config": {"count": exact_heading_count, "max_depth": 2},
        "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0},
        "gfm_features": {"md_tables_occurrence_config": {"count": 0}, "md_code_blocks_config": {"count": 0}},
        "frontmatter": {"include_chance": 0.0},
        "md_variant": "basic_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(output_dir, "test_exact_headings.md")

    generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
    
    assert call(specific_config["headings_config"], "headings") in mock_determine_count.call_args_list

def test_generate_exact_list_items_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test that generate respects md_list_items_config.count for exact list item generation."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    
    exact_list_item_count = 3
    
    def determine_count_side_effect(config_value, context_key): # Removed self_instance
        if context_key == "headings":
            return config_value.get("count", 1) if isinstance(config_value, dict) else 1
        elif context_key == "md_list_items":
            return exact_list_item_count
        elif context_key == "md_images":
            return config_value.get("count", 0) if isinstance(config_value, dict) else 0
        return 1
    mock_determine_count.side_effect = determine_count_side_effect

    specific_config = {
        "headings_config": {"count": 1, "max_depth": 1},
        "md_list_items_config": {"count": exact_list_item_count, "max_nesting_depth": 1, "include_lists": True},
        "md_images_config": {"count": 0},
        "gfm_features": {"md_tables_occurrence_config": {"count": 0}, "md_code_blocks_config": {"count": 0}},
        "frontmatter": {"include_chance": 0.0},
        "md_variant": "basic_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(output_dir, "test_exact_list_items.md")

    generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
    
    assert call(specific_config["md_list_items_config"], "md_list_items") in mock_determine_count.call_args_list

def test_generate_exact_images_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test that generate respects md_images_config.count for exact image generation."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    
    exact_image_count = 2
    
    def determine_count_side_effect(config_value, context_key): # Removed self_instance
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
    output_path = os.path.join(output_dir, "test_exact_images.md")

    generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
    
    assert call(specific_config["md_images_config"], "md_images") in mock_determine_count.call_args_list

def test_generate_exact_gfm_tables_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test that generate respects gfm_features.md_tables_occurrence_config.count."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    
    exact_table_count = 1
    
    def determine_count_side_effect(config_value, context_key): # Removed self_instance
        if context_key == "md_tables":
            return exact_table_count
        elif context_key == "md_footnotes":
            return config_value.get("count", 0) if isinstance(config_value, dict) else 0
        elif context_key == "md_task_lists":
            return config_value.get("count", 0) if isinstance(config_value, dict) else 0
        elif context_key == "md_code_blocks":
            return config_value.get("count", 0) if isinstance(config_value, dict) else 0
        return 0
    mock_determine_count.side_effect = determine_count_side_effect

    specific_config = {
        "headings_config": {"count": 0},
        "md_list_items_config": {"count": 0, "include_lists": False},
        "md_images_config": {"count": 0, "include_images": False},
        "gfm_features": {
            "md_tables_occurrence_config": {"count": exact_table_count},
            "md_footnotes_occurrence_config": {"count": 0},
            "md_task_lists_occurrence_config": {"count": 0},
            "md_code_blocks_config": {"count": 0, "include_code_blocks": False},
        },
        "frontmatter": {"include_chance": 0.0},
        "md_variant": "extended_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(output_dir, "test_exact_tables.md")

    generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
    
    assert call(specific_config["gfm_features"]["md_tables_occurrence_config"], "md_tables") in mock_determine_count.call_args_list

def test_generate_range_headings_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test that generate respects headings_config for range-based heading generation."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    mock_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    min_headings = 2
    max_headings = 5
    expected_headings_from_range = 3
    mock_randint.return_value = expected_headings_from_range

    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(config_value, context_key):
        return original_determine_count(generator, config_value, context_key)
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
    output_path = os.path.join(output_dir, "test_range_headings.md")

    mock_create_heading = mocker.patch.object(generator, '_create_md_heading', return_value="")
    generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
    
    assert call(specific_config["headings_config"], "headings") in mock_determine_count.call_args_list
    mock_randint.assert_called_once_with(min_headings, max_headings)
    assert mock_create_heading.call_count == expected_headings_from_range

def test_generate_probabilistic_headings_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test that generate respects headings_config for probabilistic heading generation."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    mock_random_random = mocker.patch('synth_data_gen.core.base.random.random')
    mock_randint = mocker.patch('synth_data_gen.core.base.random.randint')

    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(config_value, context_key): # Removed self_instance
        return original_determine_count(generator, config_value, context_key) # Use generator from fixture
    mock_determine_count.side_effect = determine_count_side_effect
    
    mock_create_heading_exact = mocker.patch.object(generator, '_create_md_heading', return_value="")

    # Scenario 1
    mock_random_random.return_value = 0.05
    expected_headings_from_prob_exact = 3
    headings_prob_config_exact = {
        "chance": 0.1, "if_true": expected_headings_from_prob_exact, "if_false": 0, "max_depth": 2
    }
    specific_config_exact = {
        "headings_config": headings_prob_config_exact, "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0}, "gfm_features": {}, "frontmatter": {"include_chance": 0},
        "md_variant": "basic_elements"
    }
    output_path_exact = os.path.join(output_dir, "test_prob_headings_exact.md")
    generator.generate(specific_config_exact, {"default_language": "en"}, output_path_exact)
    mock_ensure_dirs.assert_any_call(os.path.dirname(output_path_exact))
    assert call(headings_prob_config_exact, "headings") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    assert mock_create_heading_exact.call_count == expected_headings_from_prob_exact

    # Reset mocks for Scenario 2
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_create_heading_exact.reset_mock() # Reset this specific mock too
    mock_determine_count.side_effect = determine_count_side_effect
    
    # Scenario 2
    mock_random_random.return_value = 0.03
    min_headings_range, max_headings_range = 2, 4
    expected_headings_from_prob_range = 3
    mock_randint.return_value = expected_headings_from_prob_range
    headings_prob_config_range = {
        "chance": 0.05, "if_true": {"min": min_headings_range, "max": max_headings_range},
        "if_false": {"count": 0}, "max_depth": 2
    }
    specific_config_range = {
        "headings_config": headings_prob_config_range, "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0}, "gfm_features": {}, "frontmatter": {"include_chance": 0},
        "md_variant": "basic_elements"
    }
    output_path_range = os.path.join(output_dir, "test_prob_headings_range.md")
    # Re-patch _create_md_heading for this scenario if it's instance-specific or use a fresh mock
    mock_create_heading_range = mocker.patch.object(generator, '_create_md_heading', return_value="")
    generator.generate(specific_config_range, {"default_language": "en"}, output_path_range)
    assert call(headings_prob_config_range, "headings") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    mock_randint.assert_called_once_with(min_headings_range, max_headings_range)
    assert mock_create_heading_range.call_count == expected_headings_from_prob_range

    # Scenario 3
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_create_heading_range.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect
    mock_random_random.return_value = 0.5
    expected_headings_if_false = 1
    headings_prob_config_fail = {
        "chance": 0.1, "if_true": {"count": 5}, "if_false": expected_headings_if_false, "max_depth": 2
    }
    specific_config_fail = {
        "headings_config": headings_prob_config_fail, "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0}, "gfm_features": {}, "frontmatter": {"include_chance": 0},
        "md_variant": "basic_elements"
    }
    output_path_fail = os.path.join(output_dir, "test_prob_headings_fail.md")
    mock_create_heading_fail = mocker.patch.object(generator, '_create_md_heading', return_value="")
    generator.generate(specific_config_fail, {"default_language": "en"}, output_path_fail)
    assert call(headings_prob_config_fail, "headings") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    mock_randint.assert_not_called()
    assert mock_create_heading_fail.call_count == expected_headings_if_false

def test_generate_range_list_items_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test that generate respects md_list_items_config for range-based list item generation."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    mock_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    min_list_items, max_list_items = 2, 5
    expected_list_items_from_range = 4
    mock_randint.return_value = expected_list_items_from_range

    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(config_value, context_key):
        if context_key == "md_list_items":
            return original_determine_count(generator, config_value, context_key)
        elif context_key == "headings":
             return config_value.get("count", 1) if isinstance(config_value, dict) else 1
        elif context_key == "md_images":
             return config_value.get("count", 0) if isinstance(config_value, dict) else 0
        return 1
    mock_determine_count.side_effect = determine_count_side_effect
    
    specific_config = {
        "headings_config": {"count": 1, "max_depth": 1},
        "md_list_items_config": {
            "min": min_list_items, "max": max_list_items,
            "max_nesting_depth": 1, "include_lists": True
        },
        "md_images_config": {"count": 0},
        "gfm_features": {}, "frontmatter": {"include_chance": 0.0},
        "md_variant": "basic_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(output_dir, "test_range_list_items.md")

    mock_create_list_item = mocker.patch.object(generator, '_create_md_list_item', return_value="- item\n")
    generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_any_call(os.path.dirname(output_path))
    
    assert call(specific_config["md_list_items_config"], "md_list_items") in mock_determine_count.call_args_list
    mock_randint.assert_called_once_with(min_list_items, max_list_items)
    assert mock_create_list_item.call_count == expected_list_items_from_range

def test_generate_probabilistic_list_items_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test probabilistic md_list_items_config for list item generation."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories') # Added this line
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    mock_random_random = mocker.patch('synth_data_gen.core.base.random.random')
    mock_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(config_value, context_key):
        if context_key == "md_list_items":
            return original_determine_count(generator, config_value, context_key)
        elif context_key == "headings": return 1
        elif context_key == "md_images": return 0
        return 0
    mock_determine_count.side_effect = determine_count_side_effect

    mock_create_item_s1 = mocker.patch.object(generator, '_create_md_list_item', return_value="- item\n")

    # Scenario 1
    mock_random_random.return_value = 0.05
    expected_items_scenario1 = 2
    list_items_config_s1 = {
        "chance": 0.1, "if_true": expected_items_scenario1, "if_false": 0,
        "max_nesting_depth": 1, "include_lists": True
    }
    specific_config_s1 = {
        "headings_config": {"count": 0}, "md_list_items_config": list_items_config_s1,
        "md_images_config": {"count": 0}, "gfm_features": {},
        "frontmatter": {"include_chance": 0}, "md_variant": "basic_elements"
    }
    output_path_s1 = os.path.join(output_dir, "test_prob_list_items_s1.md")
    generator.generate(specific_config_s1, {"default_language": "en"}, output_path_s1)
    assert call(list_items_config_s1, "md_list_items") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    assert mock_create_item_s1.call_count == expected_items_scenario1

    # Reset mocks for Scenario 2
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_create_item_s1.reset_mock() # Reset this specific mock
    mock_determine_count.side_effect = determine_count_side_effect
    mock_create_item_s2 = mocker.patch.object(generator, '_create_md_list_item', return_value="- item\n")


    # Scenario 2
    mock_random_random.return_value = 0.02
    min_items_s2, max_items_s2 = 1, 3
    expected_items_scenario2 = 2
    mock_randint.return_value = expected_items_scenario2
    list_items_config_s2 = {
        "chance": 0.1, "if_true": {"min": min_items_s2, "max": max_items_s2}, "if_false": 0,
        "max_nesting_depth": 1, "include_lists": True
    }
    specific_config_s2 = {
        "headings_config": {"count": 0}, "md_list_items_config": list_items_config_s2,
        "md_images_config": {"count": 0}, "gfm_features": {},
        "frontmatter": {"include_chance": 0}, "md_variant": "basic_elements"
    }
    output_path_s2 = os.path.join(output_dir, "test_prob_list_items_s2.md")
    generator.generate(specific_config_s2, {"default_language": "en"}, output_path_s2)
    assert call(list_items_config_s2, "md_list_items") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    mock_randint.assert_called_once_with(min_items_s2, max_items_s2)
    assert mock_create_item_s2.call_count == expected_items_scenario2

    # Scenario 3
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_create_item_s2.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect
    mock_create_item_s3 = mocker.patch.object(generator, '_create_md_list_item', return_value="- item\n")
    mock_random_random.return_value = 0.5
    expected_items_scenario3 = 0
    list_items_config_s3 = {
        "chance": 0.1, "if_true": 5, "if_false": expected_items_scenario3,
        "max_nesting_depth": 1, "include_lists": True
    }
    specific_config_s3 = {
        "headings_config": {"count": 0}, "md_list_items_config": list_items_config_s3,
        "md_images_config": {"count": 0}, "gfm_features": {},
        "frontmatter": {"include_chance": 0}, "md_variant": "basic_elements"
    }
    output_path_s3 = os.path.join(output_dir, "test_prob_list_items_s3.md")
    generator.generate(specific_config_s3, {"default_language": "en"}, output_path_s3)
    assert call(list_items_config_s3, "md_list_items") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    mock_randint.assert_not_called()
    assert mock_create_item_s3.call_count == expected_items_scenario3

def test_generate_range_images_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test that generate respects md_images_config for range-based image generation."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    mock_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    min_images, max_images = 1, 3
    expected_images_from_range = 2
    mock_randint.return_value = expected_images_from_range

    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(config_value, context_key):
        if context_key == "md_images":
            return original_determine_count(generator, config_value, context_key)
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
    output_path = os.path.join(output_dir, "test_range_images.md")

    mock_create_image = mocker.patch.object(generator, '_create_md_image', return_value="![alt](src)\n")
    generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_any_call(os.path.dirname(output_path))
    assert call(specific_config["md_images_config"], "md_images") in mock_determine_count.call_args_list
    mock_randint.assert_called_once_with(min_images, max_images)
    assert mock_create_image.call_count == expected_images_from_range

def test_generate_probabilistic_images_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test probabilistic md_images_config for image generation."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories') # Added
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    mock_random_random = mocker.patch('synth_data_gen.core.base.random.random')
    mock_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(config_value, context_key):
        if context_key == "md_images":
            return original_determine_count(generator, config_value, context_key)
        elif context_key == "headings": return 1
        elif context_key == "md_list_items": return 0
        return 0
    mock_determine_count.side_effect = determine_count_side_effect
    
    mock_create_image_s1 = mocker.patch.object(generator, '_create_md_image', return_value="![alt](src)\n")

    # Scenario 1
    mock_random_random.return_value = 0.05
    expected_images_s1 = 1
    images_config_s1 = {
        "chance": 0.1, "if_true": expected_images_s1, "if_false": 0, "include_images": True
    }
    specific_config_s1 = {
        "headings_config": {"count": 0}, "md_list_items_config": {"count": 0},
        "md_images_config": images_config_s1, "gfm_features": {},
        "frontmatter": {"include_chance": 0}, "md_variant": "basic_elements"
    }
    output_path_s1 = os.path.join(output_dir, "test_prob_images_s1.md")
    generator.generate(specific_config_s1, {"default_language": "en"}, output_path_s1)
    assert call(images_config_s1, "md_images") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    assert mock_create_image_s1.call_count == expected_images_s1

    # Reset mocks for Scenario 2
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_create_image_s1.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect
    mock_create_image_s2 = mocker.patch.object(generator, '_create_md_image', return_value="![alt](src)\n")

    # Scenario 2
    mock_random_random.return_value = 0.02
    min_images_s2, max_images_s2 = 1, 2
    expected_images_s2 = 1
    mock_randint.return_value = expected_images_s2
    images_config_s2 = {
        "chance": 0.1, "if_true": {"min": min_images_s2, "max": max_images_s2},
        "if_false": 0, "include_images": True
    }
    specific_config_s2 = {
        "headings_config": {"count": 0}, "md_list_items_config": {"count": 0},
        "md_images_config": images_config_s2, "gfm_features": {},
        "frontmatter": {"include_chance": 0}, "md_variant": "basic_elements"
    }
    output_path_s2 = os.path.join(output_dir, "test_prob_images_s2.md")
    generator.generate(specific_config_s2, {"default_language": "en"}, output_path_s2)
    assert call(images_config_s2, "md_images") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    mock_randint.assert_called_once_with(min_images_s2, max_images_s2)
    assert mock_create_image_s2.call_count == expected_images_s2

    # Scenario 3
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_create_image_s2.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect
    mock_create_image_s3 = mocker.patch.object(generator, '_create_md_image', return_value="![alt](src)\n")
    mock_random_random.return_value = 0.5
    expected_images_s3 = 0
    images_config_s3 = {
        "chance": 0.1, "if_true": 3, "if_false": expected_images_s3, "include_images": True
    }
    specific_config_s3 = {
        "headings_config": {"count": 0}, "md_list_items_config": {"count": 0},
        "md_images_config": images_config_s3, "gfm_features": {},
        "frontmatter": {"include_chance": 0}, "md_variant": "basic_elements"
    }
    output_path_s3 = os.path.join(output_dir, "test_prob_images_s3.md")
    generator.generate(specific_config_s3, {"default_language": "en"}, output_path_s3)
    assert call(images_config_s3, "md_images") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    mock_randint.assert_not_called()
    assert mock_create_image_s3.call_count == expected_images_s3

def test_generate_exact_footnotes_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test exact count for md_footnotes_occurrence_config."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    
    exact_footnotes_count = 2
    
    def determine_count_side_effect(config_value, context_key): # Removed self_instance
        if context_key == "md_footnotes": return exact_footnotes_count
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
    output_path = os.path.join(output_dir, "test_exact_footnotes.md")

    mock_create_footnote = mocker.patch.object(generator, '_create_md_footnote', return_value="[^1]: Footnote\n")
    generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_any_call(os.path.dirname(output_path))
    assert call(specific_config["gfm_features"]["md_footnotes_occurrence_config"], "md_footnotes") in mock_determine_count.call_args_list
    assert mock_create_footnote.call_count == exact_footnotes_count

def test_generate_range_footnotes_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test range count for md_footnotes_occurrence_config."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    mock_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    min_footnotes, max_footnotes = 1, 4
    expected_footnotes = 2
    mock_randint.return_value = expected_footnotes

    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(config_value, context_key):
        if context_key == "md_footnotes":
            return original_determine_count(generator, config_value, context_key)
        return 0
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
    output_path = os.path.join(output_dir, "test_range_footnotes.md")

    mock_create_footnote = mocker.patch.object(generator, '_create_md_footnote', return_value="[^1]: Footnote\n")
    generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_any_call(os.path.dirname(output_path))
    assert call(footnotes_config, "md_footnotes") in mock_determine_count.call_args_list
    mock_randint.assert_called_once_with(min_footnotes, max_footnotes)
    assert mock_create_footnote.call_count == expected_footnotes

def test_generate_probabilistic_footnotes_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test probabilistic md_footnotes_occurrence_config."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories') # Added
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    mock_random_random = mocker.patch('synth_data_gen.core.base.random.random')
    mock_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    original_determine_count = BaseGenerator._determine_count
    def determine_count_side_effect(config_value, context_key):
        if context_key == "md_footnotes":
            return original_determine_count(generator, config_value, context_key)
        return 0
    mock_determine_count.side_effect = determine_count_side_effect
    
    mock_create_s1 = mocker.patch.object(generator, '_create_md_footnote', return_value="")

    # Scenario 1
    mock_random_random.return_value = 0.05
    expected_s1 = 1
    config_s1 = {"chance": 0.1, "if_true": expected_s1, "if_false": 0}
    specific_s1 = {
        "gfm_features": {"md_footnotes_occurrence_config": config_s1, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_s1 = os.path.join(output_dir, "test_prob_footnotes_s1.md")
    generator.generate(specific_s1, {}, output_s1)
    assert call(config_s1, "md_footnotes") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    assert mock_create_s1.call_count == expected_s1
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_create_s1.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect
    mock_create_s2 = mocker.patch.object(generator, '_create_md_footnote', return_value="")


    # Scenario 2
    mock_random_random.return_value = 0.02
    min_s2, max_s2 = 2, 3
    expected_s2 = 2
    mock_randint.return_value = expected_s2
    config_s2 = {"chance": 0.1, "if_true": {"min": min_s2, "max": max_s2}, "if_false": 0}
    specific_s2 = {
        "gfm_features": {"md_footnotes_occurrence_config": config_s2, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_s2 = os.path.join(output_dir, "test_prob_footnotes_s2.md")
    generator.generate(specific_s2, {}, output_s2)
    assert call(config_s2, "md_footnotes") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    mock_randint.assert_called_once_with(min_s2, max_s2)
    assert mock_create_s2.call_count == expected_s2
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_create_s2.reset_mock()
    mock_determine_count.side_effect = determine_count_side_effect
    mock_create_s3 = mocker.patch.object(generator, '_create_md_footnote', return_value="")
    
    # Scenario 3
    mock_random_random.return_value = 0.5
    expected_s3 = 0
    config_s3 = {"chance": 0.1, "if_true": 5, "if_false": expected_s3}
    specific_s3 = {
        "gfm_features": {"md_footnotes_occurrence_config": config_s3, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_s3 = os.path.join(output_dir, "test_prob_footnotes_s3.md")
    generator.generate(specific_s3, {}, output_s3)
    assert call(config_s3, "md_footnotes") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    mock_randint.assert_not_called()
    assert mock_create_s3.call_count == expected_s3

def test_generate_exact_task_lists_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test exact count for md_task_lists_occurrence_config."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    
    exact_count = 1
    def side_effect(config, key): return exact_count if key == "md_task_lists" else 0 # Removed self_instance
    mock_determine_count.side_effect = side_effect
    config = {"count": exact_count}
    specific = {
        "gfm_features": {"md_task_lists_occurrence_config": config, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_path = os.path.join(output_dir, "test_exact_task_lists.md")
    mock_create = mocker.patch.object(generator, '_create_md_task_list', return_value="- [ ] Task\n")
    generator.generate(specific, {}, output_path)
    assert call(config, "md_task_lists") in mock_determine_count.call_args_list
    assert mock_create.call_count == exact_count

def test_generate_range_task_lists_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test range count for md_task_lists_occurrence_config."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    mock_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    min_val, max_val = 1, 3
    expected_val = 2
    mock_randint.return_value = expected_val
    original_determine_count = BaseGenerator._determine_count
    def side_effect(config_value, key): return original_determine_count(generator, config_value, key) if key == "md_task_lists" else 0
    mock_determine_count.side_effect = side_effect
    config = {"min": min_val, "max": max_val}
    specific = {
        "gfm_features": {"md_task_lists_occurrence_config": config, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_path = os.path.join(output_dir, "test_range_task_lists.md")
    mock_create = mocker.patch.object(generator, '_create_md_task_list', return_value="")
    generator.generate(specific, {}, output_path)
    assert call(config, "md_task_lists") in mock_determine_count.call_args_list
    mock_randint.assert_called_once_with(min_val, max_val)
    assert mock_create.call_count == expected_val

def test_generate_probabilistic_task_lists_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test probabilistic md_task_lists_occurrence_config."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories') # Added
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    mock_random_random = mocker.patch('synth_data_gen.core.base.random.random')
    mock_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    original_determine_count = BaseGenerator._determine_count
    def side_effect(config_value, key): return original_determine_count(generator, config_value, key) if key == "md_task_lists" else 0
    mock_determine_count.side_effect = side_effect
    
    mock_create_s1 = mocker.patch.object(generator, '_create_md_task_list', return_value="")

    # Scenario 1
    mock_random_random.return_value = 0.05
    expected_s1 = 1
    config_s1 = {"chance": 0.1, "if_true": expected_s1, "if_false": 0}
    specific_s1 = {
        "gfm_features": {"md_task_lists_occurrence_config": config_s1, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    generator.generate(specific_s1, {}, os.path.join(output_dir, "path1.md"))
    assert call(config_s1, "md_task_lists") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    assert mock_create_s1.call_count == expected_s1
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_create_s1.reset_mock()
    mock_determine_count.side_effect = side_effect
    mock_create_s2 = mocker.patch.object(generator, '_create_md_task_list', return_value="")

    # Scenario 2
    mock_random_random.return_value = 0.02
    min_s2, max_s2 = 1, 2
    expected_s2 = 1
    mock_randint.return_value = expected_s2
    config_s2 = {"chance": 0.1, "if_true": {"min": min_s2, "max": max_s2}, "if_false": 0}
    specific_s2 = {
        "gfm_features": {"md_task_lists_occurrence_config": config_s2, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    generator.generate(specific_s2, {}, os.path.join(output_dir, "path2.md"))
    assert call(config_s2, "md_task_lists") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    mock_randint.assert_called_once_with(min_s2, max_s2)
    assert mock_create_s2.call_count == expected_s2
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_create_s2.reset_mock()
    mock_determine_count.side_effect = side_effect
    mock_create_s3 = mocker.patch.object(generator, '_create_md_task_list', return_value="")
    
    # Scenario 3
    mock_random_random.return_value = 0.5
    expected_s3 = 0
    config_s3 = {"chance": 0.1, "if_true": 3, "if_false": expected_s3}
    specific_s3 = {
        "gfm_features": {"md_task_lists_occurrence_config": config_s3, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    generator.generate(specific_s3, {}, os.path.join(output_dir, "path3.md"))
    assert call(config_s3, "md_task_lists") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    mock_randint.assert_not_called()
    assert mock_create_s3.call_count == expected_s3

def test_generate_exact_code_blocks_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test exact count for md_code_blocks_config."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    
    exact_count = 1
    def side_effect(config, key): return exact_count if key == "md_code_blocks" else 0 # Removed self_instance
    mock_determine_count.side_effect = side_effect
    config = {"count": exact_count, "include_code_blocks": True}
    specific = {
        "gfm_features": {"md_code_blocks_config": config, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_path = os.path.join(output_dir, "test_exact_code_blocks.md")
    mock_create = mocker.patch.object(generator, '_create_md_code_block', return_value="```\ncode\n```\n")
    generator.generate(specific, {}, output_path)
    assert call(config, "md_code_blocks") in mock_determine_count.call_args_list
    assert mock_create.call_count == exact_count

def test_generate_range_code_blocks_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test range count for md_code_blocks_config."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    mock_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    min_val, max_val = 2, 4
    expected_val = 3
    mock_randint.return_value = expected_val
    original_determine_count = BaseGenerator._determine_count
    def side_effect(config_value, key): return original_determine_count(generator, config_value, key) if key == "md_code_blocks" else 0
    mock_determine_count.side_effect = side_effect
    config = {"min": min_val, "max": max_val, "include_code_blocks": True}
    specific = {
        "gfm_features": {"md_code_blocks_config": config, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    output_path = os.path.join(output_dir, "test_range_code_blocks.md")
    mock_create = mocker.patch.object(generator, '_create_md_code_block', return_value="")
    generator.generate(specific, {}, output_path)
    assert call(config, "md_code_blocks") in mock_determine_count.call_args_list
    mock_randint.assert_called_once_with(min_val, max_val)
    assert mock_create.call_count == expected_val

def test_generate_probabilistic_code_blocks_count(mocker: MockerFixture, markdown_generator_test_setup):
    """Test probabilistic md_code_blocks_config."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories') # Added
    mock_determine_count = mocker.patch.object(generator, '_determine_count')
    mock_random_random = mocker.patch('synth_data_gen.core.base.random.random')
    mock_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    original_determine_count = BaseGenerator._determine_count
    def side_effect(config_value, key): return original_determine_count(generator, config_value, key) if key == "md_code_blocks" else 0
    mock_determine_count.side_effect = side_effect
    
    mock_create_s1 = mocker.patch.object(generator, '_create_md_code_block', return_value="")

    # Scenario 1
    mock_random_random.return_value = 0.05
    expected_s1 = 2
    config_s1 = {"chance": 0.1, "if_true": expected_s1, "if_false": 0, "include_code_blocks": True}
    specific_s1 = {
        "gfm_features": {"md_code_blocks_config": config_s1, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    generator.generate(specific_s1, {}, os.path.join(output_dir, "path1.md"))
    assert call(config_s1, "md_code_blocks") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    assert mock_create_s1.call_count == expected_s1
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_create_s1.reset_mock()
    mock_determine_count.side_effect = side_effect
    mock_create_s2 = mocker.patch.object(generator, '_create_md_code_block', return_value="")

    # Scenario 2
    mock_random_random.return_value = 0.02
    min_s2, max_s2 = 1, 3
    expected_s2 = 2
    mock_randint.return_value = expected_s2
    config_s2 = {"chance": 0.1, "if_true": {"min": min_s2, "max": max_s2}, "if_false": 0, "include_code_blocks": True}
    specific_s2 = {
        "gfm_features": {"md_code_blocks_config": config_s2, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    generator.generate(specific_s2, {}, os.path.join(output_dir, "path2.md"))
    assert call(config_s2, "md_code_blocks") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    mock_randint.assert_called_once_with(min_s2, max_s2)
    assert mock_create_s2.call_count == expected_s2
    mock_random_random.reset_mock(); mock_randint.reset_mock(); mock_determine_count.reset_mock()
    mock_create_s2.reset_mock()
    mock_determine_count.side_effect = side_effect
    mock_create_s3 = mocker.patch.object(generator, '_create_md_code_block', return_value="")
    
    # Scenario 3
    mock_random_random.return_value = 0.5
    expected_s3 = 0
    config_s3 = {"chance": 0.1, "if_true": 3, "if_false": expected_s3, "include_code_blocks": True}
    specific_s3 = {
        "gfm_features": {"md_code_blocks_config": config_s3, "md_tables_occurrence_config": {"count":0}},
        "md_variant": "extended_elements", "headings_config": {"count":0}, "frontmatter": {"include_chance":0.0}
    }
    generator.generate(specific_s3, {}, os.path.join(output_dir, "path3.md"))
    assert call(config_s3, "md_code_blocks") in mock_determine_count.call_args_list
    mock_random_random.assert_called_once()
    mock_randint.assert_not_called()
    assert mock_create_s3.call_count == expected_s3

def test_generate_frontmatter_yaml_basic(mocker: MockerFixture, markdown_generator_test_setup):
    """Test basic YAML frontmatter generation."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_generate_frontmatter = mocker.patch.object(generator, '_generate_frontmatter')
    mocker.patch.object(generator, '_create_md_basic_elements_content', return_value="")
    
    expected_fm_content = "---\ntitle: Test YAML\n---\n"
    mock_generate_frontmatter.return_value = expected_fm_content
    
    frontmatter_config = {
        "style": "yaml", "fields": {"title": "Test YAML"}, "include_chance": 1.0
    }
    specific_config = {
        "frontmatter": frontmatter_config, "headings_config": {"count": 0},
        "md_list_items_config": {"count": 0}, "md_images_config": {"count": 0},
        "gfm_features": {}, "md_variant": "basic_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(output_dir, "test_frontmatter_yaml.md")

    generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
    mock_generate_frontmatter.assert_called_once_with(specific_config, global_config)
    
    with open(output_path, 'r') as f:
        content = f.read()
    assert content.startswith(expected_fm_content)

def test_generate_frontmatter_yaml_not_included_when_chance_is_zero(mocker: MockerFixture, markdown_generator_test_setup):
    """Test frontmatter is not generated when include_chance is 0.0."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    mock_generate_frontmatter = mocker.patch.object(generator, '_generate_frontmatter')
    
    frontmatter_config = {
        "style": "yaml", "fields": {"title": "Test Title"}, "include_chance": 0.0
    }
    specific_config = {
        "frontmatter": frontmatter_config, "headings_config": {"count": 1, "max_depth": 1},
        "md_list_items_config": {"count": 0}, "md_images_config": {"count": 0},
        "gfm_features": {}, "md_variant": "basic_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(output_dir, "test_no_frontmatter.md")

    mock_generate_frontmatter.return_value = "---\ntitle: Should Not Be Written\n---\n"
    
    mock_basic_content = mocker.patch.object(generator, '_create_md_basic_elements_content', return_value="# Dummy Content\n")
    generator.generate(specific_config, global_config, output_path)
    
    mock_ensure_dirs.assert_any_call(os.path.dirname(output_path))
    mock_generate_frontmatter.assert_not_called()
    
    with open(output_path, 'r') as f:
        content = f.read()
    assert not content.startswith("---")
    mock_basic_content.assert_called_once()
    assert content == "# Dummy Content\n"

def test_generate_frontmatter_toml_basic(mocker: MockerFixture, markdown_generator_test_setup):
    """Test basic TOML frontmatter generation - expecting failure."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    
    specific_config = {
        "frontmatter": {
            "style": "toml", "include_chance": 1.0, "fields": {"title": "Test TOML"}
        },
        "headings_config": {"count": 0}, "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0}, "gfm_features": {}, "md_variant": "basic_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(output_dir, "test_frontmatter_toml.md")

    if os.path.exists(output_path):
        os.remove(output_path)

    generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
    
    assert os.path.exists(output_path), "Output file was not created"
    with open(output_path, 'r') as f:
        content = f.read()
    
    assert content.startswith("+++"), f"Content should start with TOML delimiter '+++', but was: '{content[:10]}...'"

def test_generate_frontmatter_json_basic(mocker: MockerFixture, markdown_generator_test_setup):
    """Test basic JSON frontmatter generation."""
    generator, output_dir = markdown_generator_test_setup
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    
    specific_config = {
        "headings_config": {"count": 0}, "md_list_items_config": {"count": 0},
        "md_images_config": {"count": 0}, "gfm_features": {},
        "frontmatter": {
            "style": "json", "include_chance": 1.0, "fields": {"title": "Test JSON"}
        },
        "md_variant": "basic_elements"
    }
    global_config = {"default_language": "en"}
    output_path = os.path.join(output_dir, "test_frontmatter_json.md")

    generator.generate(specific_config, global_config, output_path)

    mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
    
    with open(output_path, 'r') as f:
        full_file_content = f.read()

    assert full_file_content.strip().startswith("{") and full_file_content.strip().endswith("}"), \
        "Content should be a JSON object if style is JSON"
    
    try:
        json_data = json.loads(full_file_content.strip())
        assert json_data.get("title") == "Test JSON"
    except json.JSONDecodeError:
        pytest.fail("Frontmatter was not valid JSON.")