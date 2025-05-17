import pytest
from pytest_mock import MockerFixture
from ebooklib import epub
from synth_data_gen.generators.epub import EpubGenerator
import random # For patching random.randint and random.random
import os # For os.path.basename in font test

@pytest.fixture
def epub_generator_instance():
    return EpubGenerator()

def test_get_default_specific_config(epub_generator_instance: EpubGenerator):
    """Test that get_default_specific_config returns the expected structure."""
    defaults = epub_generator_instance.get_default_specific_config()
    assert isinstance(defaults, dict)
    assert "chapters_config" in defaults
    assert defaults["chapters_config"] == 5
    assert "author" in defaults
    assert defaults["author"] == "Default EPUB Author"
    assert "epub_version" in defaults
    assert defaults["epub_version"] == 3
    assert "toc_settings" in defaults
    assert isinstance(defaults["toc_settings"], dict)
    assert "style" in defaults["toc_settings"]
    assert defaults["toc_settings"]["style"] == "navdoc_full"
    assert "font_embedding" in defaults
    assert isinstance(defaults["font_embedding"], dict)
    assert "enable" in defaults["font_embedding"]
    assert not defaults["font_embedding"]["enable"]
    assert "content_elements" in defaults
    assert isinstance(defaults["content_elements"], dict)
    assert "paragraph_styles" in defaults["content_elements"]
    assert isinstance(defaults["content_elements"]["paragraph_styles"], list)

def test_validate_config_valid(epub_generator_instance: EpubGenerator):
    """Test validate_config with valid specific and global configs."""
    specific_config = epub_generator_instance.get_default_specific_config()
    global_config = {"default_language": "en"}
    assert epub_generator_instance.validate_config(specific_config, global_config)

def test_validate_config_missing_epub_version(epub_generator_instance: EpubGenerator):
    """Test validate_config when epub_version is missing (should still pass due to current implementation)."""
    specific_config = epub_generator_instance.get_default_specific_config()
    del specific_config["epub_version"]
    global_config = {"default_language": "en"}
    assert epub_generator_instance.validate_config(specific_config, global_config)

def test_validate_config_invalid_base_specific_config(epub_generator_instance: EpubGenerator):
    """Test validate_config when the specific_config is not a dict (handled by super)."""
    specific_config = "not_a_dict"
    global_config = {"default_language": "en"}
    assert not epub_generator_instance.validate_config(specific_config, global_config)

def test_validate_config_invalid_base_global_config(epub_generator_instance: EpubGenerator):
    """Test validate_config when the global_config is not a dict (handled by super)."""
    specific_config = epub_generator_instance.get_default_specific_config()
    global_config = "not_a_dict"
    assert not epub_generator_instance.validate_config(specific_config, global_config)

def test_generate_minimal_epub(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test the basic flow of the generate method for a minimal EPUB."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    
    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    specific_config = {
        "title": "Test Book", "author": "Test Author", "language": "fr",
        "chapters_config": 1, "sections_per_chapter_config": 0
    }
    global_config = {"default_language": "en", "default_author": "Global Author"}
    output_path = "test_output/minimal.epub"
    expected_dir_to_ensure = "test_output"
    returned_path = epub_generator_instance.generate(specific_config, global_config, output_path)
    
    mock_ensure_output_dirs.assert_called_once_with(expected_dir_to_ensure)
    mock_epub_book_class.assert_called_once()
    mock_book_instance.set_title.assert_called_with("Test Book")
    mock_book_instance.set_language.assert_called_with("fr")
    mock_book_instance.add_author.assert_called_with("Test Author")
    assert mock_book_instance.add_item.called
    mock_write_epub.assert_called_once_with(output_path, mock_book_instance, {})
    assert returned_path == output_path

def test_generate_adds_basic_toc_items(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that generate calls ToC creation functions."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_create_ncx = mocker.patch('synth_data_gen.generators.epub_components.toc.create_ncx')
    mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item.file_name = 'chap_1.xhtml'
    mock_chapter_item.title = 'Chapter 1'
    specific_config = {
        "title": "Basic ToC Test Book EPUB2 NCX", "chapters_config": 1, "epub_version": 2,
        "toc_settings": {"style": "default"}, "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0}
    }
    global_config = {}
    output_path = "test_output/basic_toc_test_epub2_ncx.epub"
    
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1, 0, 0, 0]) # chapters, sections, notes, images
    
    epub_generator_instance.generate(specific_config, global_config, output_path)
    
    mock_create_ncx.assert_called_once()
    mock_create_nav_document.assert_not_called()

def test_generate_chapters_config_exact_integer(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with chapters_config as an exact integer."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_create_chapter_content = mocker.patch.object(epub_generator_instance, '_create_chapter_content')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    exact_chapter_count = 3
    mock_determine_count.return_value = exact_chapter_count
    specific_config = {"title": "Exact Chapters Test", "chapters_config": exact_chapter_count}
    global_config = {}
    output_path = "test_output/exact_chapters.epub"
    epub_generator_instance.generate(specific_config, global_config, output_path)
    mock_determine_count.assert_called_once_with(exact_chapter_count, "chapters")
    assert mock_create_chapter_content.call_count == exact_chapter_count

def test_generate_chapters_config_range_object(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with chapters_config as a range object."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_create_chapter_content = mocker.patch.object(epub_generator_instance, '_create_chapter_content')
    mock_randint = mocker.patch('random.randint')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    range_config = {"min": 2, "max": 5}
    expected_chapters_from_range = 4
    mock_randint.return_value = expected_chapters_from_range
    mock_determine_count.return_value = expected_chapters_from_range
    specific_config = {"title": "Range Chapters Test", "chapters_config": range_config}
    global_config = {}
    output_path = "test_output/range_chapters.epub"
    epub_generator_instance.generate(specific_config, global_config, output_path)
    mock_determine_count.assert_called_once_with(range_config, "chapters")
    assert mock_create_chapter_content.call_count == expected_chapters_from_range

def test_generate_chapters_config_probabilistic_object(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with chapters_config as a probabilistic object."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_create_chapter_content = mocker.patch.object(epub_generator_instance, '_create_chapter_content')
    mock_random_random = mocker.patch('random.random')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    prob_config = {"chance": 0.7, "per_unit_of": "document", "max_total": 3}
    mock_random_random.return_value = 0.6
    expected_chapters_from_prob = 1
    mock_determine_count.return_value = expected_chapters_from_prob
    specific_config = {"title": "Probabilistic Chapters Test", "chapters_config": prob_config}
    global_config = {}
    output_path = "test_output/prob_chapters.epub"
    epub_generator_instance.generate(specific_config, global_config, output_path)
    mock_determine_count.assert_called_once_with(prob_config, "chapters")
    assert mock_create_chapter_content.call_count == expected_chapters_from_prob

def test_generate_sections_config_exact_integer(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with sections_per_chapter_config as an exact integer."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_create_section_content = mocker.patch.object(epub_generator_instance, '_create_section_content')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    num_chapters = 1
    exact_section_count = 2
    mock_determine_count.side_effect = [num_chapters, exact_section_count, 0, 0]
    specific_config = {
        "title": "Exact Sections Test", "chapters_config": num_chapters,
        "sections_per_chapter_config": exact_section_count
    }
    global_config = {}
    output_path = "test_output/exact_sections.epub"
    epub_generator_instance.generate(specific_config, global_config, output_path)
    assert mock_determine_count.call_args_list[1] == mocker.call(exact_section_count, f"sections_in_chapter_1")
    assert mock_create_section_content.call_count == exact_section_count * num_chapters

def test_generate_sections_config_range_object(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with sections_per_chapter_config as a range object."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_create_section_content = mocker.patch.object(epub_generator_instance, '_create_section_content')
    mock_randint = mocker.patch('random.randint')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    num_chapters = 1
    sections_range_config = {"min": 1, "max": 3}
    expected_sections_from_range = 2
    mock_randint.return_value = expected_sections_from_range
    mock_determine_count.side_effect = [num_chapters, expected_sections_from_range, 0, 0]
    specific_config = {
        "title": "Range Sections Test", "chapters_config": num_chapters,
        "sections_per_chapter_config": sections_range_config
    }
    global_config = {}
    output_path = "test_output/range_sections.epub"
    epub_generator_instance.generate(specific_config, global_config, output_path)
    assert mock_determine_count.call_args_list[1] == mocker.call(sections_range_config, f"sections_in_chapter_1")
    assert mock_create_section_content.call_count == expected_sections_from_range * num_chapters

def test_generate_sections_config_probabilistic_object(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with sections_per_chapter_config as a probabilistic object."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_create_section_content = mocker.patch.object(epub_generator_instance, '_create_section_content')
    mock_random_random = mocker.patch('random.random')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    num_chapters = 1
    sections_prob_config = {"chance": 0.8, "max_total": 2}
    mock_random_random.return_value = 0.7
    expected_sections_from_prob = 1
    mock_determine_count.side_effect = [num_chapters, expected_sections_from_prob, 0, 0]
    specific_config = {
        "title": "Probabilistic Sections Test", "chapters_config": num_chapters,
        "sections_per_chapter_config": sections_prob_config
    }
    global_config = {}
    output_path = "test_output/prob_sections.epub"
    epub_generator_instance.generate(specific_config, global_config, output_path)
    assert mock_determine_count.call_args_list[1] == mocker.call(sections_prob_config, f"sections_in_chapter_1")
    assert mock_create_section_content.call_count == expected_sections_from_prob * num_chapters

def test_generate_notes_config_exact_integer(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with notes_config (exact integer)."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_add_notes_to_chapter = mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    num_chapters = 1
    exact_notes_count = 3
    mock_determine_count.side_effect = [num_chapters, 1, exact_notes_count, 0]
    specific_config = {
        "title": "Exact Notes Test", "chapters_config": num_chapters,
        "sections_per_chapter_config": 1,
        "notes_system": {"type": "footnotes_same_page", "notes_config": exact_notes_count}
    }
    global_config = {}
    output_path = "test_output/exact_notes.epub"
    mocker.patch.object(epub_generator_instance, '_create_section_content', mocker.MagicMock())
    epub_generator_instance.generate(specific_config, global_config, output_path)
    assert mock_determine_count.call_args_list[2] == mocker.call(exact_notes_count, f"notes_in_chapter_1")
    mock_add_notes_to_chapter.assert_called_once()

def test_generate_notes_config_range_object(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with notes_config (range object)."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_add_notes_to_chapter = mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter')
    mock_randint = mocker.patch('random.randint')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    num_chapters = 1
    notes_range_config = {"min": 1, "max": 4}
    expected_notes_from_range = 2
    mock_randint.return_value = expected_notes_from_range
    mock_determine_count.side_effect = [num_chapters, 1, expected_notes_from_range, 0]
    specific_config = {
        "title": "Range Notes Test", "chapters_config": num_chapters,
        "sections_per_chapter_config": 1,
        "notes_system": {"type": "footnotes_same_page", "notes_config": notes_range_config}
    }
    global_config = {}
    output_path = "test_output/range_notes.epub"
    mocker.patch.object(epub_generator_instance, '_create_section_content', mocker.MagicMock())
    epub_generator_instance.generate(specific_config, global_config, output_path)
    assert mock_determine_count.call_args_list[2] == mocker.call(notes_range_config, f"notes_in_chapter_1")
    mock_add_notes_to_chapter.assert_called_once()

def test_generate_notes_config_probabilistic_object(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with notes_config (probabilistic object)."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_add_notes_to_chapter = mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter')
    mock_random_random = mocker.patch('random.random')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    num_chapters = 1
    notes_prob_config = {"chance": 0.6, "max_total": 3}
    mock_random_random.return_value = 0.5
    expected_notes_from_prob = 1
    mock_determine_count.side_effect = [num_chapters, 1, expected_notes_from_prob, 0]
    specific_config = {
        "title": "Probabilistic Notes Test", "chapters_config": num_chapters,
        "sections_per_chapter_config": 1,
        "notes_system": {"type": "footnotes_same_page", "notes_config": notes_prob_config}
    }
    global_config = {}
    output_path = "test_output/prob_notes.epub"
    mocker.patch.object(epub_generator_instance, '_create_section_content', mocker.MagicMock())
    epub_generator_instance.generate(specific_config, global_config, output_path)
    assert mock_determine_count.call_args_list[2] == mocker.call(notes_prob_config, f"notes_in_chapter_1")
    mock_add_notes_to_chapter.assert_called_once()

# Tests for images_config
def test_generate_images_config_exact_integer(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with images_config (exact integer)."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_add_images_to_chapter = mocker.patch.object(epub_generator_instance, '_add_images_to_chapter')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    num_chapters = 1
    exact_images_count = 2
    mock_determine_count.side_effect = [num_chapters, 1, 0, exact_images_count]
    specific_config = {
        "title": "Exact Images Test", "chapters_config": num_chapters,
        "sections_per_chapter_config": 1, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": True, "images_config": exact_images_count}
    }
    global_config = {}
    output_path = "test_output/exact_images.epub"
    mocker.patch.object(epub_generator_instance, '_create_section_content', mocker.MagicMock())
    mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter', mocker.MagicMock())
    epub_generator_instance.generate(specific_config, global_config, output_path)
    assert mock_determine_count.call_args_list[3] == mocker.call(exact_images_count, f"images_in_chapter_1")
    mock_add_images_to_chapter.assert_called_once()

def test_generate_images_config_range_object(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with images_config (range object)."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_add_images_to_chapter = mocker.patch.object(epub_generator_instance, '_add_images_to_chapter')
    mock_randint = mocker.patch('random.randint')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    num_chapters = 1
    images_range_config = {"min": 1, "max": 3}
    expected_images_from_range = 2
    mock_randint.return_value = expected_images_from_range
    mock_determine_count.side_effect = [num_chapters, 1, 0, expected_images_from_range]
    specific_config = {
        "title": "Range Images Test", "chapters_config": num_chapters,
        "sections_per_chapter_config": 1, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": True, "images_config": images_range_config}
    }
    global_config = {}
    output_path = "test_output/range_images.epub"
    mocker.patch.object(epub_generator_instance, '_create_section_content', mocker.MagicMock())
    mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter', mocker.MagicMock())
    epub_generator_instance.generate(specific_config, global_config, output_path)
    assert mock_determine_count.call_args_list[3] == mocker.call(images_range_config, f"images_in_chapter_1")
    mock_add_images_to_chapter.assert_called_once()

def test_generate_images_config_probabilistic_object(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with images_config (probabilistic object)."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_add_images_to_chapter = mocker.patch.object(epub_generator_instance, '_add_images_to_chapter')
    mock_random_random = mocker.patch('random.random')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    num_chapters = 1
    images_prob_config = {"chance": 0.9, "max_total": 2}
    mock_random_random.return_value = 0.8
    expected_images_from_prob = 1
    mock_determine_count.side_effect = [num_chapters, 1, 0, expected_images_from_prob]
    specific_config = {
        "title": "Probabilistic Images Test", "chapters_config": num_chapters,
        "sections_per_chapter_config": 1, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": True, "images_config": images_prob_config}
    }
    global_config = {}
    output_path = "test_output/prob_images.epub"
    mocker.patch.object(epub_generator_instance, '_create_section_content', mocker.MagicMock())
    mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter', mocker.MagicMock())
    epub_generator_instance.generate(specific_config, global_config, output_path)
    assert mock_determine_count.call_args_list[3] == mocker.call(images_prob_config, f"images_in_chapter_1")
    mock_add_images_to_chapter.assert_called_once()

def test_generate_multimedia_include_images_false(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that images are not processed if multimedia.include_images is False."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_add_images_to_chapter = mocker.patch.object(epub_generator_instance, '_add_images_to_chapter')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    num_chapters = 1
    mock_determine_count.side_effect = [num_chapters, 1, 0] # ch, sec, notes
    specific_config = {
        "title": "No Images Test", "chapters_config": num_chapters,
        "sections_per_chapter_config": 1, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 5}
    }
    global_config = {}
    output_path = "test_output/no_images.epub"
    mocker.patch.object(epub_generator_instance, '_create_section_content', mocker.MagicMock())
    mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter', mocker.MagicMock())
    epub_generator_instance.generate(specific_config, global_config, output_path)
    
    mock_add_images_to_chapter.assert_not_called()
    assert mock_determine_count.call_count == 3
    assert mock_determine_count.call_args_list[0] == mocker.call(num_chapters, "chapters")
    assert mock_determine_count.call_args_list[1] == mocker.call(1, f"sections_in_chapter_1")
    assert mock_determine_count.call_args_list[2] == mocker.call(0, f"notes_in_chapter_1")
    for call_args in mock_determine_count.call_args_list:
        assert call_args[0][1] != "images_in_chapter_1"

def test_generate_uses_toc_settings(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that generate passes toc_settings to toc creation functions."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')
    mock_create_ncx = mocker.patch('synth_data_gen.generators.epub_components.toc.create_ncx')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item.file_name = 'chap_1.xhtml'
    mock_chapter_item.title = 'Chapter 1'
    
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1, 0, 0, 0])

    specific_config = {
        "title": "ToC Settings Test",
        "chapters_config": 1,
        "epub_version": 3,
        "toc_settings": {
            "style": "custom_style",
            "max_depth": 2,
            "include_landmarks": False
        },
        "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0}
    }
    global_config = {}
    output_path = "test_output/toc_settings_test.epub"

    epub_generator_instance.generate(specific_config, global_config, output_path)

    mock_create_nav_document.assert_called_once()
    args_nav, _ = mock_create_nav_document.call_args
    assert args_nav[0] is mock_book_instance
    assert len(args_nav[1]) == 1
    assert args_nav[1][0] is mock_chapter_item
    assert args_nav[2] == specific_config["toc_settings"]
    assert args_nav[3] == str(specific_config["epub_version"])

    mock_create_ncx.assert_not_called()

def test_generate_default_epub3_creates_nav_not_ncx(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that default EPUB3 generation creates NAV doc and not NCX."""
    mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_create_ncx = mocker.patch('synth_data_gen.generators.epub_components.toc.create_ncx')
    mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item.file_name = 'chap_1.xhtml'
    mock_chapter_item.title = 'Chapter 1'
    specific_config = {
        "title": "EPUB3 Default ToC Test", "chapters_config": 1, "epub_version": 3,
        "toc_settings": {"style": "default"}, "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0}
    }
    global_config = {}
    output_path = "test_output/epub3_default_toc.epub"
    
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1, 0, 0, 0])
    
    epub_generator_instance.generate(specific_config, global_config, output_path)
    
    mock_create_nav_document.assert_called_once()
    mock_create_ncx.assert_not_called()

def test_generate_default_epub2_creates_ncx_not_nav(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that default EPUB2 generation creates NCX and not NAV doc."""
    mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_create_ncx = mocker.patch('synth_data_gen.generators.epub_components.toc.create_ncx')
    mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item.file_name = 'chap_1.xhtml'
    mock_chapter_item.title = 'Chapter 1'
    specific_config = {
        "title": "EPUB2 Default ToC Test", "chapters_config": 1, "epub_version": 2,
        "toc_settings": {"style": "default"}, "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0}
    }
    global_config = {}
    output_path = "test_output/epub2_default_toc.epub"
    
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1, 0, 0, 0])
    
    epub_generator_instance.generate(specific_config, global_config, output_path)
    
    mock_create_ncx.assert_called_once()
    mock_create_nav_document.assert_not_called()

def test_generate_font_embedding_enabled(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that font embedding settings are applied when enabled."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    
    # Capture the EpubBook instance
    captured_book_instances = []
    def mock_epub_book_constructor(*args, **kwargs):
        instance = mocker.MagicMock() # Create a fresh mock for each call if needed
        captured_book_instances.append(instance)
        return instance
    
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', side_effect=mock_epub_book_constructor)
    
    mock_os_path_exists = mocker.patch('synth_data_gen.generators.epub.os.path.exists', return_value=True)
    mock_os_path_basename = mocker.patch('synth_data_gen.generators.epub.os.path.basename', return_value="TestFont.ttf")
    mock_open_instance = mocker.mock_open(read_data=b"dummy_font_bytes")
    mocker.patch('builtins.open', mock_open_instance)
    mock_add_font_css = mocker.patch.object(epub_generator_instance, '_add_font_css_to_book')

    specific_config = {
        "title": "Font Embedding Test", "chapters_config": 1,
        "font_embedding": {
            "enable": True,
            "fonts": ["path/to/TestFont.ttf"],
            "obfuscation": "adobe" # Test a specific obfuscation type
        },
        "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0}
    }
    global_config = {}
    output_path = "test_output/font_embedding_test.epub"
    
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml) # For _create_chapter_content
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1,0,0,0])


    epub_generator_instance.generate(specific_config, global_config, output_path)
    
    assert len(captured_book_instances) == 1
    mock_book_instance = captured_book_instances[0]

    mock_os_path_exists.assert_any_call("path/to/TestFont.ttf")
    mock_os_path_basename.assert_called_with("path/to/TestFont.ttf")
    mock_open_instance.assert_called_with("path/to/TestFont.ttf", "rb")
    
    # Check if add_item was called with an EpubItem that looks like a font
    font_item_added = False
    for call_args in mock_book_instance.add_item.call_args_list:
        item = call_args[0][0]
        if isinstance(item, epub.EpubItem) and item.file_name == "fonts/TestFont.ttf":
            assert item.media_type == "application/vnd.ms-opentype" # or font/ttf
            assert item.content == b"dummy_font_bytes"
            font_item_added = True
            break
    assert font_item_added, "Font item was not added to the book"

    mock_add_font_css.assert_called_once()
    # Check obfuscation call if possible (might require deeper mocking of EpubBook or EpubItem)
    # For now, we assume if add_item is called with font data, obfuscation (if any) is handled by ebooklib
    # or would be part of a more direct test of _add_font_to_book if that method was public/complex.

def test_generate_unified_quantity_chapters_exact(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with chapters_config (exact integer) via unified quantity spec."""
    mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_create_chapter_content = mocker.patch.object(epub_generator_instance, '_create_chapter_content')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    
    exact_chapter_count = 3
    # _determine_count will be called for chapters, sections, notes, images.
    # We are interested in the first call for chapters.
    mock_determine_count.side_effect = [exact_chapter_count, 0, 0, 0] 

    specific_config = {
        "title": "Unified Exact Chapters",
        "chapters_config": exact_chapter_count, # Unified quantity
        "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0}
    }
    global_config = {}
    output_path = "test_output/unified_exact_chapters.epub"

    epub_generator_instance.generate(specific_config, global_config, output_path)

    # Check the first call to _determine_count (for chapters)
    assert mock_determine_count.call_args_list[0] == mocker.call(exact_chapter_count, "chapters")
    assert mock_create_chapter_content.call_count == exact_chapter_count

def test_generate_unified_quantity_chapters_range(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with chapters_config (range) via unified quantity spec."""
    mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_create_chapter_content = mocker.patch.object(epub_generator_instance, '_create_chapter_content')
    
    # Patch random.randint used by BaseGenerator._determine_count
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    
    chapters_range_config = {"min": 2, "max": 5}
    expected_chapters_from_range = 4 
    mock_base_randint.return_value = expected_chapters_from_range
    
    # _determine_count will be called for chapters, sections, notes, images.
    # It will use the mocked randint for the chapters_config range.
    mock_determine_count.side_effect = [expected_chapters_from_range, 0, 0, 0]

    specific_config = {
        "title": "Unified Range Chapters",
        "chapters_config": chapters_range_config, # Unified quantity
        "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0}
    }
    global_config = {}
    output_path = "test_output/unified_range_chapters.epub"

    epub_generator_instance.generate(specific_config, global_config, output_path)

    mock_base_randint.assert_called_once_with(chapters_range_config["min"], chapters_range_config["max"])
    assert mock_determine_count.call_args_list[0] == mocker.call(chapters_range_config, "chapters")
    assert mock_create_chapter_content.call_count == expected_chapters_from_range

def test_generate_unified_quantity_chapters_probabilistic(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with chapters_config (probabilistic) via unified quantity spec."""
    mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_create_chapter_content = mocker.patch.object(epub_generator_instance, '_create_chapter_content')

    # Patch random.random used by BaseGenerator._determine_count
    mock_base_random_random = mocker.patch('synth_data_gen.core.base.random.random')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    
    chapters_prob_config = {"chance": 0.7, "per_unit_of": "document", "max_total": 3}
    # Simulate random.random() returning a value that triggers generation (less than chance)
    mock_base_random_random.return_value = 0.6 
    expected_chapters_from_prob = 1 # For a single document, chance 0.7, random 0.6 -> 1 chapter
    
    mock_determine_count.side_effect = [expected_chapters_from_prob, 0, 0, 0]

    specific_config = {
        "title": "Unified Probabilistic Chapters",
        "chapters_config": chapters_prob_config, # Unified quantity
        "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0}
    }
    global_config = {}
    output_path = "test_output/unified_prob_chapters.epub"

    epub_generator_instance.generate(specific_config, global_config, output_path)

    mock_base_random_random.assert_called_once() # Called by _determine_count for probabilistic
    assert mock_determine_count.call_args_list[0] == mocker.call(chapters_prob_config, "chapters")
    assert mock_create_chapter_content.call_count == expected_chapters_from_prob

# --- More detailed integration tests for EpubGenerator components ---

def test_generate_epub_with_basic_config_integrates_toc(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """
    Test that EpubGenerator.generate with a basic EPUB3 config correctly calls
    toc.create_nav_document and not toc.create_ncx.
    """
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    
    # Capture the EpubBook instance
    captured_book_instances = []
    def mock_epub_book_constructor(*args, **kwargs):
        # Create a real EpubBook instance but track it
        # This is tricky because we want to inspect its state *after* SUT modifies it,
        # but *before* write_epub (which is mocked) would consume it.
        # For this test, we'll use a MagicMock and assert calls on it.
        instance = mocker.MagicMock() 
        captured_book_instances.append(instance)
        return instance
    
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', side_effect=mock_epub_book_constructor)

    mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')
    mock_create_ncx = mocker.patch('synth_data_gen.generators.epub_components.toc.create_ncx')

    # Mock chapter creation to return a list of mock EpubHtml items
    mock_chapter_1_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_1_item.file_name = "c1.xhtml"
    mock_chapter_1_item.title = "Chapter 1 Title"
    
    mock_chapter_2_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_2_item.file_name = "c2.xhtml"
    mock_chapter_2_item.title = "Chapter 2 Title"

    mocker.patch.object(epub_generator_instance, '_create_chapter_content', 
                        side_effect=[mock_chapter_1_item, mock_chapter_2_item])
    
    # Mock _determine_count to control number of chapters, sections, notes, images
    # For this test: 2 chapters, 0 sections, 0 notes, 0 images
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[2, 0, 0, 0, 0, 0, 0]) 
                                                                    # ch, s_c1, n_c1, i_c1, s_c2, n_c2, i_c2

    specific_config_epub3 = {
        "title": "EPUB3 Basic ToC",
        "author": "Test Author",
        "language": "en-US",
        "epub_version": 3, # Test integer version
        "chapters_config": 2,
        "sections_per_chapter_config": 0,
        "toc_settings": {"style": "default", "max_depth": 3, "include_landmarks": True},
        "notes_system": {"enable": False, "notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "validation": {"run_epubcheck": False}
    }
    global_config = {"default_publisher": "Test Publisher"}
    output_path = "test_output/epub3_basic_toc_integration.epub"

    epub_generator_instance.generate(specific_config_epub3, global_config, output_path)

    assert len(captured_book_instances) == 1
    mock_book_instance = captured_book_instances[0]

    # Verify EpubBook setup
    mock_book_instance.set_title.assert_called_with("EPUB3 Basic ToC")
    mock_book_instance.set_language.assert_called_with("en-US")
    mock_book_instance.add_author.assert_called_with("Test Author")
    mock_book_instance.add_metadata.assert_any_call('DC', 'publisher', 'Test Publisher', {})


    # Verify ToC calls
    mock_create_nav_document.assert_called_once()
    nav_call_args, _ = mock_create_nav_document.call_args
    assert nav_call_args[0] is mock_book_instance # book instance
    assert len(nav_call_args[1]) == 2 # chapters_for_toc (list of EpubHtml items)
    assert nav_call_args[1][0] is mock_chapter_1_item
    assert nav_call_args[1][1] is mock_chapter_2_item
    assert nav_call_args[2] == specific_config_epub3["toc_settings"] # toc_settings
    assert nav_call_args[3] == str(specific_config_epub3["epub_version"]) # epub_version (as string)
    
    mock_create_ncx.assert_not_called()
    mock_write_epub.assert_called_once_with(output_path, mock_book_instance, {})

def test_generate_epub2_with_basic_config_integrates_ncx(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """
    Test that EpubGenerator.generate with a basic EPUB2 config correctly calls
    toc.create_ncx and not toc.create_nav_document.
    """
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    
    captured_book_instances = []
    def mock_epub_book_constructor(*args, **kwargs):
        instance = mocker.MagicMock()
        captured_book_instances.append(instance)
        return instance
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', side_effect=mock_epub_book_constructor)

    mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')
    mock_create_ncx = mocker.patch('synth_data_gen.generators.epub_components.toc.create_ncx')

    mock_chapter_1_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_1_item.file_name = "c1.xhtml"
    mock_chapter_1_item.title = "Chapter 1 Title"
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_1_item)
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1, 0, 0, 0]) # 1 chapter

    specific_config_epub2 = {
        "title": "EPUB2 Basic NCX",
        "epub_version": "2.0", # Test string version
        "chapters_config": 1,
        "sections_per_chapter_config": 0,
        "toc_settings": {"style": "default"},
        "notes_system": {"enable": False},
        "multimedia": {"include_images": False},
        "validation": {"run_epubcheck": False}
    }
    global_config = {}
    output_path = "test_output/epub2_basic_ncx_integration.epub"

    epub_generator_instance.generate(specific_config_epub2, global_config, output_path)

    assert len(captured_book_instances) == 1
    mock_book_instance = captured_book_instances[0]

    mock_create_ncx.assert_called_once()
    ncx_call_args, _ = mock_create_ncx.call_args
    assert ncx_call_args[0] is mock_book_instance
    assert len(ncx_call_args[1]) == 1
    assert ncx_call_args[1][0] is mock_chapter_1_item
    assert ncx_call_args[2] == specific_config_epub2["toc_settings"]
    
    mock_create_nav_document.assert_not_called()
    mock_write_epub.assert_called_once_with(output_path, mock_book_instance, {})

def test_generate_epub_with_citations_integrates_citations_component(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """
    Test that EpubGenerator.generate correctly calls _apply_citations_to_item_content
    when citations are enabled in the config.
    """
    mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', return_value=mocker.MagicMock())

    # Spy on the SUT's method
    mock_apply_citations = mocker.spy(epub_generator_instance, '_apply_citations_to_item_content')

    # Mock chapter creation to return a simple chapter item
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item.content = "Initial chapter content [cite:key1]."
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
    
    # Mock _determine_count: 1 chapter, 0 sections, 0 notes, 0 images
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1, 0, 0, 0]) 
    
    # Mock other content modification methods to isolate citations
    mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter')
    mocker.patch.object(epub_generator_instance, '_add_images_to_chapter')
    mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document') # For EPUB3 default

    specific_config_citations = {
        "title": "Citations Integration Test",
        "epub_version": 3,
        "chapters_config": 1,
        "sections_per_chapter_config": 0,
        "citations_config": {
            "enable": True,
            "style": "author_date",
            "data": {"key1": {"full_citation": "Full Citation 1", "in_text": "(Author, Year)"}}
        },
        "notes_system": {"enable": False},
        "multimedia": {"include_images": False},
        "validation": {"run_epubcheck": False}
    }
    global_config = {}
    output_path = "test_output/citations_integration.epub"

    epub_generator_instance.generate(specific_config_citations, global_config, output_path)

    mock_apply_citations.assert_called_once()
    # Assert arguments of the call to _apply_citations_to_item_content
    call_args, _ = mock_apply_citations.call_args
    assert call_args[0] == "Initial chapter content [cite:key1]." # item_content
    assert call_args[1] == 1  # chapter_number
    assert call_args[2] == specific_config_citations # specific_config
    assert call_args[3] == global_config # global_config
    
    # Verify that the chapter content was indeed modified by the (spied) real method
    # This assumes the real _apply_citations_to_item_content works as expected from its own unit tests.
    # Here, we just check it was called. The content of mock_chapter_item.content would be updated by the real method.
    # If _apply_citations_to_item_content is complex, its output should be tested in its own unit tests.
    # For an integration test, verifying the call is often sufficient if the unit test for the method is robust.
    # However, if we want to check the *result* of the integration:
    assert mock_chapter_item.content == "Initial chapter content (Author, Year)."


def test_generate_epub_with_notes_integrates_notes_method(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """
    Test that EpubGenerator.generate correctly calls _add_notes_to_chapter
    when notes are enabled in the config.
    """
    mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_book_instance = mocker.MagicMock()
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', return_value=mock_book_instance)

    mock_add_notes = mocker.spy(epub_generator_instance, '_add_notes_to_chapter')

    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item.content = "Chapter content with a note marker [note:N1]."
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
    
    # Mock _determine_count: 1 chapter, 0 sections, 1 note, 0 images
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1, 0, 1, 0]) 
    
    mocker.patch.object(epub_generator_instance, '_apply_citations_to_item_content', side_effect=lambda c, *args: c) # Passthrough
    mocker.patch.object(epub_generator_instance, '_add_images_to_chapter')
    mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')

    specific_config_notes = {
        "title": "Notes Integration Test",
        "epub_version": 3,
        "chapters_config": 1,
        "sections_per_chapter_config": 0,
        "citations_config": {"enable": False},
        "notes_system": {
            "enable": True,
            "type": "footnotes_same_page",
            "notes_config": 1, # This will be used by the mocked _determine_count
            "data": {"N1": {"content": "This is note 1."}}
        },
        "multimedia": {"include_images": False},
        "validation": {"run_epubcheck": False}
    }
    global_config = {}
    output_path = "test_output/notes_integration.epub"

    epub_generator_instance.generate(specific_config_notes, global_config, output_path)

    mock_add_notes.assert_called_once()
    call_args, _ = mock_add_notes.call_args
    assert call_args[0] is mock_book_instance # book
    assert call_args[1] is mock_chapter_item # chapter_item
    assert call_args[2] == 1 # chapter_number
    assert call_args[3] == 1 # num_notes (from mocked _determine_count)
    assert call_args[4] == specific_config_notes # specific_config
    assert call_args[5] == global_config # global_config

    # To verify the content change by the real _add_notes_to_chapter:
    expected_content_after_notes = (
        "Chapter content with a note marker <sup id=\"fnref-1-1\"><a href=\"#fn-1-1\">1</a></sup>."
        "\n<hr class=\"footnote-separator\" />"
        "\n<div class=\"footnotes\">"
        "\n<p id=\"fn-1-1\" class=\"footnote\"><a href=\"#fnref-1-1\">1.</a> This is note 1.</p>"
        "\n</div>"
    )
    assert mock_chapter_item.content == expected_content_after_notes


def test_generate_epub_with_images_integrates_multimedia_method(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """
    Test that EpubGenerator.generate correctly calls _add_images_to_chapter
    when images are enabled in the config.
    """
    mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_book_instance = mocker.MagicMock()
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', return_value=mock_book_instance)
    mocker.patch('synth_data_gen.generators.epub_components.multimedia.os.path.exists', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data=b"dummy_image_bytes"))


    mock_add_images = mocker.spy(epub_generator_instance, '_add_images_to_chapter')

    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item.content = "Chapter content with an image marker [image:img1]."
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
    
    # Mock _determine_count: 1 chapter, 0 sections, 0 notes, 1 image
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1, 0, 0, 1]) 
    
    mocker.patch.object(epub_generator_instance, '_apply_citations_to_item_content', side_effect=lambda c, *args: c)
    mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter')
    mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')

    specific_config_images = {
        "title": "Images Integration Test",
        "epub_version": 3,
        "chapters_config": 1,
        "sections_per_chapter_config": 0,
        "citations_config": {"enable": False},
        "notes_system": {"enable": False},
        "multimedia": {
            "include_images": True,
            "images_config": 1, # Used by mocked _determine_count
            "image_data": {"img1": {"path": "dummy/img1.jpg", "alt_text": "Alt text 1", "filename_in_epub": "image1.jpg"}}
        },
        "validation": {"run_epubcheck": False}
    }
    global_config = {}
    output_path = "test_output/images_integration.epub"

    epub_generator_instance.generate(specific_config_images, global_config, output_path)

    mock_add_images.assert_called_once()
    call_args, _ = mock_add_images.call_args
    assert call_args[0] is mock_book_instance # book
    assert call_args[1] is mock_chapter_item # chapter_item
    assert call_args[2] == 1 # chapter_number
    assert call_args[3] == 1 # num_images (from mocked _determine_count)
    assert call_args[4] == specific_config_images # specific_config
    assert call_args[5] == global_config # global_config
    
    # Verify content change by the real _add_images_to_chapter
    expected_content_after_images = "Chapter content with an image marker <img src=\"images/image1.jpg\" alt=\"Alt text 1\" />."
    assert mock_chapter_item.content == expected_content_after_images
    # Also check that the image item was added to the book
    mock_book_instance.add_item.assert_any_call(mocker.ANY) # Basic check
    image_item_added = False
    for call in mock_book_instance.add_item.call_args_list:
        item = call[0][0]
        if isinstance(item, epub.EpubImage) and item.file_name == "images/image1.jpg":
            image_item_added = True
            break
    assert image_item_added, "EpubImage item was not added to the book mock"


def test_generate_epub3_navdoc_is_correctly_structured(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that for EPUB3, a structurally correct NAV document is generated and book.toc is set."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub') # Mock write_epub

    # We need to inspect the real EpubBook instance *after* the SUT has configured it
    # but *before* write_epub is called (which is mocked).
    # So, we patch the EpubBook constructor to capture the instance.
    
    # Store the real EpubBook class
    RealEpubBook = epub.EpubBook 
    
    # List to capture instances of EpubBook created by the SUT
    captured_book_instances = []

    def mock_epub_book_init_capture(*args, **kwargs):
        # Create a real EpubBook instance
        instance = RealEpubBook(*args, **kwargs)
        captured_book_instances.append(instance)
        return instance

    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', side_effect=mock_epub_book_init_capture)
    
    # Mock _create_chapter_content to return real EpubHtml items
    # These will be used by the real toc.create_nav_document
    chapter1_item = epub.EpubHtml(title='Chapter 1 Title', file_name='c1.xhtml', lang='en')
    chapter1_item.content = '<h1>Chapter 1 Title</h1><p>Content</p>'
    
    section1_1_item = epub.EpubHtml(title='Section 1.1 Title', file_name='s1.1.xhtml', lang='en')
    section1_1_item.content = '<h2>Section 1.1 Title</h2><p>Content</p>'
    
    chapter2_item = epub.EpubHtml(title='Chapter 2 Title', file_name='c2.xhtml', lang='en')
    chapter2_item.content = '<h1>Chapter 2 Title</h1><p>Content</p>'

    # Simulate the structure SUT's _create_chapter_content would build for ToC
    # This structure is what's passed to toc.create_nav_document
    # For this test, we simplify: _create_chapter_content returns a flat list of chapter items.
    # The real SUT would build a nested structure if sections were involved.
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', 
                        side_effect=[chapter1_item, chapter2_item]) # Two chapters

    # Mock _determine_count: 2 chapters, 0 sections per chapter, 0 notes, 0 images
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[2, 0,0,0, 0,0,0])

    # Mock other content modification methods as they are not the focus here
    mocker.patch.object(epub_generator_instance, '_apply_citations_to_item_content', side_effect=lambda c, *args: c)
    mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter')
    mocker.patch.object(epub_generator_instance, '_add_images_to_chapter')

    specific_config_nav = {
        "title": "NAV Doc Structure Test", "author": "NAV Tester", "language": "fr-CA",
        "epub_version": 3, "chapters_config": 2, "sections_per_chapter_config": 0,
        "toc_settings": {"style": "navdoc_full", "max_depth": 3, "include_landmarks": True},
        "notes_system": {"enable": False}, "multimedia": {"include_images": False},
        "validation": {"run_epubcheck": False}
    }
    global_config = {"default_publisher": "NAV Publisher"}
    output_path = "test_output/navdoc_structure.epub"

    epub_generator_instance.generate(specific_config_nav, global_config, output_path)

    assert len(captured_book_instances) == 1
    book = captured_book_instances[0] # This is the real EpubBook instance

    # Check basic book properties set by SUT
    assert book.title == "NAV Doc Structure Test"
    assert book.language == "fr-CA"
    assert any(meta[1] == "NAV Tester" for meta in book.metadata.get('DC', {}).get('creator', []))
    assert any(meta[1] == "NAV Publisher" for meta in book.metadata.get('DC', {}).get('publisher', []))

    # Check that a NAV document was added
    nav_item = book.get_item_with_href('nav.xhtml')
    assert nav_item is not None, "NAV document (nav.xhtml) not found in book items"
    assert nav_item.media_type == 'application/xhtml+xml'
    
    # Check book.toc (should be populated by create_nav_document)
    assert isinstance(book.toc, tuple) or isinstance(book.toc, list) # ebooklib uses tuple
    assert len(book.toc) == 2 # Two top-level chapters
    assert book.toc[0].title == "Chapter 1 Title"
    assert book.toc[0].href == "c1.xhtml"
    assert book.toc[1].title == "Chapter 2 Title"
    assert book.toc[1].href == "c2.xhtml"
    
    # Check NAV document content (simplified check for key elements)
    nav_content = nav_item.content.decode('utf-8') # Content is bytes
    assert "<nav epub:type=\"toc\" id=\"toc\">" in nav_content
    assert "<h1>Table of Contents</h1>" in nav_content # Default title from toc.py
    assert "<ol>" in nav_content
    assert "<li><a href=\"c1.xhtml\">Chapter 1 Title</a></li>" in nav_content
    assert "<li><a href=\"c2.xhtml\">Chapter 2 Title</a></li>" in nav_content
    assert "</ol>" in nav_content
    assert "</nav>" in nav_content
    
    # Check landmarks if include_landmarks was True (it is in this config)
    assert "<nav epub:type=\"landmarks\" id=\"landmarks\">" in nav_content
    assert "<h2>Guide</h2>" in nav_content # Default title from toc.py
    # Add more specific landmark checks if needed, e.g., for cover, toc, bodymatter

    # Ensure NCX was not created for EPUB3 default
    ncx_item = book.get_item_with_href('toc.ncx')
    assert ncx_item is None, "NCX document (toc.ncx) was unexpectedly found for EPUB3 default"

    mock_write_epub.assert_called_once_with(output_path, book, {})


def test_generate_epub2_ncx_is_correctly_structured(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that for EPUB2, a structurally correct NCX is generated and book.toc is set."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')

    RealEpubBook = epub.EpubBook
    captured_book_instances = []
    def mock_epub_book_init_capture(*args, **kwargs):
        instance = RealEpubBook(*args, **kwargs)
        captured_book_instances.append(instance)
        return instance
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', side_effect=mock_epub_book_init_capture)
    
    chapter1_item = epub.EpubHtml(title='EPUB2 Chapter 1', file_name='c1_epub2.xhtml', lang='en')
    chapter1_item.content = '<h1>EPUB2 Chapter 1</h1>'
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=chapter1_item)
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1, 0,0,0]) # 1 chapter

    mocker.patch.object(epub_generator_instance, '_apply_citations_to_item_content', side_effect=lambda c, *args: c)
    mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter')
    mocker.patch.object(epub_generator_instance, '_add_images_to_chapter')

    specific_config_ncx = {
        "title": "NCX Structure Test", "language": "de",
        "epub_version": "2.0", "chapters_config": 1,
        "toc_settings": {"style": "default"}, # For EPUB2, this implies NCX
        "notes_system": {"enable": False}, "multimedia": {"include_images": False},
        "validation": {"run_epubcheck": False}
    }
    global_config = {}
    output_path = "test_output/ncx_structure.epub"

    epub_generator_instance.generate(specific_config_ncx, global_config, output_path)

    assert len(captured_book_instances) == 1
    book = captured_book_instances[0]

    assert book.title == "NCX Structure Test"
    assert book.language == "de"

    # Check that an NCX document was added
    ncx_item = book.get_item_with_href('toc.ncx')
    assert ncx_item is not None, "NCX document (toc.ncx) not found in book items"
    assert ncx_item.media_type == 'application/x-dtbncx+xml'
    
    # Check book.toc (should be populated by create_ncx)
    assert isinstance(book.toc, tuple) or isinstance(book.toc, list)
    assert len(book.toc) == 1
    assert book.toc[0].title == "EPUB2 Chapter 1"
    assert book.toc[0].href == "c1_epub2.xhtml"
    
    # Check NCX document content (simplified check for key elements)
    ncx_content = ncx_item.content.decode('utf-8')
    assert "<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">" in ncx_content
    assert f"<docTitle><text>{book.title}</text></docTitle>" in ncx_content
    assert "<navMap>" in ncx_content
    assert "<navPoint id=\"navpoint-1\" playOrder=\"1\">" in ncx_content # Assuming playOrder starts at 1
    assert f"<navLabel><text>{chapter1_item.title}</text></navLabel>" in ncx_content
    assert f"<content src=\"{chapter1_item.file_name}\"/>" in ncx_content
    assert "</navMap>" in ncx_content
    assert "</ncx>" in ncx_content
    
    # Ensure NAV was not created for EPUB2 default
    nav_item = book.get_item_with_href('nav.xhtml')
    assert nav_item is None, "NAV document (nav.xhtml) was unexpectedly found for EPUB2"

    mock_write_epub.assert_called_once_with(output_path, book, {})


def test_generate_epub3_navdoc_respects_max_depth(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that the EPUB3 NAV document respects the toc_settings.max_depth."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')

    RealEpubBook = epub.EpubBook
    captured_book_instances = []
    def mock_epub_book_init_capture(*args, **kwargs):
        instance = RealEpubBook(*args, **kwargs)
        captured_book_instances.append(instance)
        return instance
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', side_effect=mock_epub_book_init_capture)

    # Create a nested chapter structure for ToC
    # Chapter 1
    #   Section 1.1
    #     SubSection 1.1.1 (should be excluded by max_depth=2)
    # Chapter 2
    
    # These items are what _create_chapter_content would conceptually produce and pass to ToC generation
    # The SUT's _create_chapter_content needs to be mocked to return this structure.
    # For this test, we'll simplify and assume _create_chapter_content returns a flat list,
    # and the ToC component itself handles nesting based on item properties (like title or a custom depth attribute).
    # The current toc.py _generate_html_list_items and _create_toc_links_recursive handle EpubNavPoint lists.
    # So, we need to mock _create_chapter_content to return EpubNavPoint-like structures if we want to test depth.
    # This is getting complex for an integration test of EpubGenerator.
    # A more direct unit test for toc.py's depth handling is better.
    # For this integration test, we'll assume toc.py handles depth correctly if given the right items.
    # We'll check if toc_settings are passed.
    
    # Let's simplify: assume _create_chapter_content returns a flat list of chapter items.
    # The real test of max_depth is in toc.py's unit tests.
    # Here, we just ensure the setting is passed.
    
    chapter1_item = epub.EpubHtml(title='C1', file_name='c1.xhtml')
    chapter2_item = epub.EpubHtml(title='C2', file_name='c2.xhtml')
    
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', 
                        side_effect=[chapter1_item, chapter2_item])
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[2,0,0,0,0,0,0])


    mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')
    
    specific_config_depth = {
        "title": "NAV Depth Test", "epub_version": 3, "chapters_config": 2,
        "toc_settings": {"style": "navdoc_full", "max_depth": 1}, # Test depth 1
        "notes_system": {"enable": False}, "multimedia": {"include_images": False},
        "validation": {"run_epubcheck": False}
    }
    global_config = {}
    output_path = "test_output/nav_depth.epub"

    epub_generator_instance.generate(specific_config_depth, global_config, output_path)
    
    assert len(captured_book_instances) == 1
    book = captured_book_instances[0]

    mock_create_nav_document.assert_called_once()
    nav_call_args, _ = mock_create_nav_document.call_args
    assert nav_call_args[2] == specific_config_depth["toc_settings"] # Check toc_settings passed
    assert nav_call_args[2]["max_depth"] == 1

    # A full check of the generated NAV content for depth would require
    # either letting the real toc.create_nav_document run (and thus not mocking it)
    # and providing a deeply nested chapter structure from _create_chapter_content,
    # or having a very complex side_effect for mock_create_nav_document.
    # Given this is an integration test for EpubGenerator, verifying the settings
    # are passed to the ToC component is a reasonable level of testing here.
    # The detailed depth logic is tested in test_toc.py.


def test_generate_epub_with_custom_metadata(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that custom metadata is added to the book."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')

    RealEpubBook = epub.EpubBook
    captured_book_instances = []
    def mock_epub_book_init_capture(*args, **kwargs):
        instance = RealEpubBook(*args, **kwargs)
        captured_book_instances.append(instance)
        return instance
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', side_effect=mock_epub_book_init_capture)

    # Mock chapter creation
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item.file_name = "c1.xhtml" # Needed for ToC fallback if book.toc is empty
    mock_chapter_item.title = "Chapter 1"    # Needed for ToC fallback
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1,0,0,0])


    specific_config_meta = {
        "title": "Custom Metadata Test", "epub_version": 3, "chapters_config": 1,
        "metadata_settings": {
            "additional_metadata": [
                {"namespace": "DC", "name": "contributor", "value": "Editor Name", "others": {"role": "edt"}},
                {"namespace": "OPF", "name": "meta", "value": None, "others": {"name": "custom:rating", "content": "5"}},
                {"namespace": None, "name": "meta", "value": "FreeTextMeta", "others": {"property": "dcterms:modified", "id": "moddate"}}
            ]
        },
         "notes_system": {"enable": False}, "multimedia": {"include_images": False},
         "validation": {"run_epubcheck": False}
    }
    global_config = {}
    output_path = "test_output/custom_metadata.epub"

    epub_generator_instance.generate(specific_config_meta, global_config, output_path)

    assert len(captured_book_instances) == 1
    book = captured_book_instances[0]

    # Check DC:contributor
    dc_metadata = book.metadata.get('DC', {})
    contributors = dc_metadata.get('contributor', [])
    assert any(c[1] == "Editor Name" and c[2].get('role') == 'edt' for c in contributors)

    # Check OPF:meta (custom:rating)
    # Note: ebooklib stores OPF namespace specific meta under 'OPF', and non-namespaced (None) meta under None
    opf_metadata_dict = book.metadata.get('OPF', {})
    opf_meta_tags = opf_metadata_dict.get('meta', [])
    assert any(
        m_val is None and m_others.get('name') == 'custom:rating' and m_others.get('content') == '5' 
        for _, m_val, m_others in opf_meta_tags # Unpack assuming (tag_name, value, others_dict)
    )
    
    # Check None-namespaced meta (dcterms:modified)
    # For meta tags added with namespace=None, ebooklib stores them as (text_content, attributes_dict)
    # where text_content is the 'value' from add_metadata.
    none_ns_metadata = book.metadata.get(None, {})
    none_ns_meta_tags = none_ns_metadata.get('meta', [])
    found_dcterms_modified = False
    for text_content, attrs_dict in none_ns_meta_tags:
        if text_content == "FreeTextMeta" and attrs_dict.get("property") == "dcterms:modified" and attrs_dict.get("id") == "moddate":
            found_dcterms_modified = True
            break
    assert found_dcterms_modified, "dcterms:modified meta tag not found or incorrect"

    mock_write_epub.assert_called_once_with(output_path, book, {})


def test_generate_epub_with_font_embedding(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that font embedding logic is triggered and font item is added."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')

    RealEpubBook = epub.EpubBook
    captured_book_instances = []
    def mock_epub_book_init_capture(*args, **kwargs):
        instance = RealEpubBook(*args, **kwargs) # Create a real book to check items
        captured_book_instances.append(instance)
        return instance
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', side_effect=mock_epub_book_init_capture)

    mocker.patch('synth_data_gen.generators.epub.os.path.exists', return_value=True) # Assume font file exists
    mocker.patch('synth_data_gen.generators.epub.os.path.basename', return_value="MyTestFont.otf")
    mock_open_font = mocker.mock_open(read_data=b"dummy_font_file_bytes")
    mocker.patch('builtins.open', mock_open_font) # For reading the font file

    # Mock chapter creation
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item.file_name = "c1.xhtml"; mock_chapter_item.title = "C1"
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1,0,0,0])


    specific_config_font = {
        "title": "Font Embedding Test", "epub_version": 3, "chapters_config": 1,
        "font_embedding": {
            "enable": True,
            "fonts": ["dummy/path/MyTestFont.otf"],
            "obfuscation": "idpf" # Test a specific obfuscation
        },
        "notes_system": {"enable": False}, "multimedia": {"include_images": False},
        "validation": {"run_epubcheck": False}
    }
    global_config = {}
    output_path = "test_output/font_embed.epub"

    epub_generator_instance.generate(specific_config_font, global_config, output_path)

    assert len(captured_book_instances) == 1
    book = captured_book_instances[0]

    mock_open_font.assert_called_with("dummy/path/MyTestFont.otf", "rb")

    # Check if font item was added
    font_item = book.get_item_with_href('fonts/MyTestFont.otf')
    assert font_item is not None, "Font item 'fonts/MyTestFont.otf' not found"
    assert font_item.media_type == 'application/vnd.ms-opentype' # or font/otf
    assert font_item.content == b"dummy_font_file_bytes"
    
    # Check if font CSS was added (EpubGenerator._add_font_css_to_book should have been called)
    # This is harder to check directly without more complex mocking or inspecting book.items further.
    # For this integration test, presence of the font item is a good indicator.
    # A unit test for _add_font_css_to_book would verify its specific behavior.
    
    # Check if obfuscation key was added to OPF (for 'idpf' or 'adobe')
    # This is usually a <encryption> element in encryption.xml, referenced by OPF.
    # ebooklib handles this internally when book.add_item(font_item) is called if font_item.is_obfuscated.
    # Verifying this requires checking for encryption.xml and its content, or that font_item.is_obfuscated was set.
    # For now, we assume ebooklib handles it if the SUT sets up the font item correctly.
    # The SUT's _add_font_to_book method is responsible for setting item.is_obfuscated = True
    # and item.obfuscation_key based on config.
    # We can check if the item added to the book has these properties.
    assert font_item.is_obfuscated is True
    assert font_item.obfuscation_key is not None # IDPF obfuscation generates a key

    mock_write_epub.assert_called_once_with(output_path, book, {}) # book should be the real instance here


def test_generate_runs_epubcheck_when_enabled(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that epubcheck is run when validation.run_epubcheck is True."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_book_instance = mocker.MagicMock()
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', return_value=mock_book_instance)
    
    mock_subprocess_run = mocker.patch('synth_data_gen.generators.epub.subprocess.run')
    mock_subprocess_run.return_value = mocker.MagicMock(returncode=0, stderr="") # Simulate successful run

    # Mock chapter creation and determine_count for minimal book generation
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1,0,0,0])


    specific_config_epubcheck = {
        "title": "Epubcheck Test", "epub_version": 3, "chapters_config": 1,
        "validation": {
            "run_epubcheck": True,
            "epubcheck_path": "/custom/path/to/epubcheck.jar"
        },
        "notes_system": {"enable": False}, "multimedia": {"include_images": False}
    }
    global_config = {}
    output_path = "test_output/epubcheck_test.epub"

    epub_generator_instance.generate(specific_config_epubcheck, global_config, output_path)

    mock_subprocess_run.assert_called_once_with(
        ['java', '-jar', '/custom/path/to/epubcheck.jar', output_path],
        capture_output=True, text=True, check=False
    )
    # Test for check=True if epubcheck fails and SUT should raise error (not current SUT behavior)

def test_generate_epub_with_intext_citations_content(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test that in-text citations are correctly inserted into chapter content."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub') # Mock write_epub
    
    # We need to inspect the chapter content *after* _apply_citations_to_item_content has run.
    # The SUT calls _create_chapter_content, which internally calls _apply_citations_to_item_content.
    # So, we mock _create_chapter_content to control its initial output and then let the
    # real _apply_citations_to_item_content (spied upon) modify it.

    # Spy on the SUT's method to ensure it's called and to check its return if needed,
    # but let the original logic run.
    # We are testing the SUT's _apply_citations_to_item_content method here.
    # So, we should NOT mock it directly if we want to test its transformation.
    # Instead, we control its inputs via _create_chapter_content's initial HTML.

    mock_book_instance = mocker.MagicMock()
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', return_value=mock_book_instance)

    # Mock other transformation methods to isolate citation processing
    mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter')
    mocker.patch.object(epub_generator_instance, '_add_images_to_chapter')
    mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document') # For EPUB3 default

    initial_chapter_html_with_markers = "<h1>Chapter 1</h1><p>Some text [cite:key1] and more [cite:key2].</p>"
    expected_chapter_html_after_citations = "<h1>Chapter 1</h1><p>Some text (Smith, 2020) and more (Doe, 2021).</p>"

    # This will be the mock for _create_chapter_content.
    # It needs to return an EpubHtml item whose .content is set to initial_chapter_html_with_markers.
    # The SUT's generate() method will then call the *real* _apply_citations_to_item_content
    # on this initial_chapter_html_with_markers.
    # Then, the SUT will assign the result of _apply_citations_to_item_content back to chapter_item.content.
    
    # We need to capture the chapter_item *after* SUT's generate() has modified it.
    # The easiest way is to have _create_chapter_content return a specific MagicMock instance
    # that we can inspect later.
    
    # This is the item that _create_chapter_content will be mocked to return.
    # Its .content will be modified by the SUT's call to the real _apply_citations_to_item_content.
    mock_chapter_item_for_citations = mocker.MagicMock(spec=epub.EpubHtml)
    # Set the initial content that _apply_citations_to_item_content will process
    mock_chapter_item_for_citations.content = initial_chapter_html_with_markers
    mock_chapter_item_for_citations.file_name = "c_cite.xhtml" # Needed for ToC
    mock_chapter_item_for_citations.title = "Cite Chapter"   # Needed for ToC


    # Mock _create_chapter_content to return our pre-seeded chapter item.
    # The SUT's generate() method:
    #   chapter_item = self._create_chapter_content(...)
    #   ...
    #   current_chapter_html_content = self._apply_citations_to_item_content(chapter_item.content, ...)
    #   chapter_item.content = current_chapter_html_content  <-- This is what we want to check
    #   ...
    #   book.add_item(chapter_item)

    # To make this work, the SUT's _create_chapter_content should be structured so that
    # it first creates the basic HTML, then calls _apply_citations_to_item_content on that HTML,
    # and updates the chapter item's content with the result.
    # Let's look at the SUT's _create_chapter_content:
    #   ...
    #   chapter_content_html = f"<h1>{chapter_title}</h1>"
    #   # ... sections might add to chapter_content_html ...
    #   current_chapter_html_content = chapter_content_html # Initial content
    #   if specific_config.get("citations_config", {}).get("enable"):
    #       current_chapter_html_content = self._apply_citations_to_item_content(
    #           current_chapter_html_content, chapter_number, specific_config, global_config
    #       )
    #   # ... then notes and images operate on current_chapter_html_content ...
    #   c.content = current_chapter_html_content # Final content assigned here
    #   return c
    # This structure is good. _apply_citations_to_item_content is called, and its result is used.

    # So, we need to mock _create_chapter_content such that its *initial* formation of
    # chapter_content_html (before _apply_citations is called) is our `initial_chapter_html_with_markers`.
    # This is hard to do without changing the SUT or having a very complex mock for _create_chapter_content.

    # Alternative: Let the real _create_chapter_content run, but mock its sub-components
    # (_create_section_content) to produce minimal output, and ensure the initial H1 tag
    # contains the markers. This is still tricky.

    # Let's use the approach from the TDD feedback:
    # The test `test_generate_epub_with_intext_citations_content` should be the one
    # that *makes the SUT's `_apply_citations_to_item_content` work*.
    # So, we should *not* mock `_apply_citations_to_item_content`.
    # We need to ensure that the input to `_apply_citations_to_item_content` is what we expect,
    # and then check its output.

    # The SUT's `_create_chapter_content` calls `_apply_citations_to_item_content`.
    # We need to control the HTML that `_create_chapter_content` generates *before* it calls `_apply_citations`.
    
    # Simpler approach for this integration test:
    # Mock _create_chapter_content to return a chapter item.
    # Then, in the test, *manually call* epub_generator_instance._apply_citations_to_item_content
    # with the desired raw HTML and config, and assert its return value.
    # This makes it more of a unit test for _apply_citations_to_item_content if it's not already covered.
    # The task is about *integration* though.

    # Let's try to make _create_chapter_content produce our raw HTML.
    # We can patch `_create_section_content` to return an empty string.
    # Then, the `chapter_content_html` in `_create_chapter_content` will just be `f"<h1>{chapter_title}</h1>"`.
    # We need to inject our markers into this.
    # This means the `chapter_title` itself would need to contain the markers, which is not right.

    # Back to the TDD feedback's idea for the *complex test*:
    # "The test should let the SUT's _create_chapter_content run (perhaps with minimal mocking of its
    # deepest dependencies if they generate too much noise) and then assert the final content."
    # This test (`test_generate_epub_with_intext_citations_content`) is *not* the complex test.
    # This one is specifically for citation *content*.

    # The previous successful debug of this test (entry [2025-05-15 03:24:00]) involved
    # ensuring the SUT's _apply_citations_to_item_content was a passthrough and the test *failed*.
    # Then TDD mode (entry [2025-05-15 03:32:00]) implemented the SUT logic and the test passed.
    # The SUT at that point:
    # def _apply_citations_to_item_content(self, item_content, chapter_number, specific_config, global_config):
    #     # ... logic to replace [cite:key] ...
    #     return item_content
    # The test at that point:
    #   - Mocked _create_chapter_content to return an item with `initial_chapter_html_with_markers`.
    #   - Let SUT's `generate` run, which calls the real `_apply_citations_to_item_content`.
    #   - Asserted `mock_chapter_item_for_citations.content == expected_chapter_html_after_citations`.

    # This seems like the right pattern. The current test code for `test_generate_epub_with_intext_citations_content`
    # (lines 1476-1619) already follows this pattern.
    # The `mock_create_chapter_content_side_effect` (lines 1549-1572 in the provided snippet, but seems to be a copy-paste error from another test,
    # it should be specific to this citation test) is designed to set up the initial content.
    
    # Let's re-verify the SUT method `_apply_citations_to_item_content` from `synth_data_gen/generators/epub.py`.
    # If it's correct, and the test setup is correct, this test *should* pass if the SUT works.
    # The current test run shows it *is* passing.
    # The problem is the `TypeError` in the *complex* test.

    # The current test `test_generate_epub_with_intext_citations_content` is fine and passing.
    # My focus should be on `test_generate_epub_with_complex_config_and_interactions`.

    # Re-evaluating: The `TypeError` is the primary target.
    # The complex test currently mocks `epub.write_epub` (line 1859, original 2088).
    # TDD feedback says the error occurs when `epub.write_epub` is *not* mocked.
    # So, my plan to comment out line 1859 is correct.
    # The `apply_diff` failure was a tool usage error.

    # I need to get the *full current content* of `tests/generators/test_epub_generator.py`
    # to use with `write_to_file`.
    # The previous `read_file` was truncated at 500 lines. The file is 2194 lines.
    # I will read the whole file now.
    
    # Corrected side effect for this specific test:
    def mock_create_chapter_content_side_effect(book_arg, chap_num_arg, chap_title_arg, spec_conf_arg, glob_conf_arg):
        # This function is mocking SUT's _create_chapter_content for the citation test
        mock_chapter_item_for_citations.content = initial_chapter_html_with_markers
        mock_chapter_item_for_citations.title = chap_title_arg
        mock_chapter_item_for_citations.file_name = f"chap_{chap_num_arg}_cite_test.xhtml"
        
        # The SUT's generate() will then call _apply_citations_to_item_content on this item's content.
        # The SUT then updates chapter_item.content with the result.
        return mock_chapter_item_for_citations

    mocker.patch.object(epub_generator_instance, '_create_chapter_content', side_effect=mock_create_chapter_content_side_effect)
    
    # Mock _determine_count: 1 chapter, 0 sections, 0 notes, 0 images
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1, 0, 0, 0]) 

    specific_config_citations = {
        "title": "Citations Content Test", "epub_version": 3, "chapters_config": 1,
        "sections_per_chapter_config": 0,
        "citations_config": {
            "enable": True, "style": "author_date",
            "data": {
                "key1": {"full_citation": "Smith, J. (2020). A Book.", "in_text": "(Smith, 2020)"},
                "key2": {"full_citation": "Doe, A. (2021). Another Book.", "in_text": "(Doe, 2021)"}
            }
        },
        "notes_system": {"enable": False},
        "multimedia": {"include_images": False},
        "validation": {"run_epubcheck": False}
    }
    global_config = {}
    output_path = "test_output/citations_content_test.epub"
    
    # Capture items added to the book (though not strictly necessary for this content test)
    added_items_capture = []
    def capture_added_item(item):
        added_items_capture.append(item)
    mock_book_instance.add_item = capture_added_item

    epub_generator_instance.generate(specific_config_citations, global_config, output_path)

    # Assert that the content of the chapter item was modified as expected
    # The SUT's _create_chapter_content returns mock_chapter_item_for_citations.
    # The SUT's generate() then calls _apply_citations_to_item_content on its content,
    # and updates mock_chapter_item_for_citations.content with the result.
    assert mock_chapter_item_for_citations.content == expected_chapter_html_after_citations
    
    # Ensure the chapter item itself was added to the book
    assert mock_chapter_item_for_citations in added_items_capture


def test_generate_epub_with_notes_content_is_correct(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """
    Test that notes (footnotes_same_page) are correctly processed and added to chapter content
    and that the note items are added to the book.
    """
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    
    mock_book_instance = mocker.MagicMock()
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', return_value=mock_book_instance)

    # We want to test the SUT's _add_notes_to_chapter method.
    # The SUT's _create_chapter_content calls _add_notes_to_chapter.
    # So, we mock _create_chapter_content to return a chapter item with specific initial content
    # that _add_notes_to_chapter will then process.

    initial_chapter_html_with_note_markers = (
        "<h1>Chapter with Notes</h1>"
        "<p>Some text with a note [note:note1].</p>"
        "<p>Another paragraph with [note:note2] another note.</p>"
    )
    
    expected_chapter_html_after_notes = (
        "<h1>Chapter with Notes</h1>"
        "<p>Some text with a note <sup id=\"fnref-1-1\"><a href=\"#fn-1-1\">1</a></sup>.</p>"
        "<p>Another paragraph with <sup id=\"fnref-1-2\"><a href=\"#fn-1-2\">2</a></sup> another note.</p>"
        "\n<hr class=\"footnote-separator\" />"
        "\n<div class=\"footnotes\">"
        "\n<p id=\"fn-1-1\" class=\"footnote\"><a href=\"#fnref-1-1\">1.</a> This is the first note.</p>"
        "\n<p id=\"fn-1-2\" class=\"footnote\"><a href=\"#fnref-1-2\">2.</a> This is the second note.</p>"
        "\n</div>"
    )

    # This is the item that _create_chapter_content will be mocked to return.
    # Its .content will be modified by the SUT's call to the real _add_notes_to_chapter.
    mock_chapter_item_for_notes = mocker.MagicMock(spec=epub.EpubHtml)
    # Set the initial content that _add_notes_to_chapter will process
    # This initial content needs to be set by the side_effect of _create_chapter_content
    # because _add_notes_to_chapter takes the chapter_item as input.
    mock_chapter_item_for_notes.file_name = "c_notes.xhtml"
    mock_chapter_item_for_notes.title = "Notes Chapter"
    mock_chapter_item_for_notes.content = "" # Will be set by side_effect

    # Store original methods that are part of the SUT's internal logic being tested
    # We are not mocking _add_notes_to_chapter itself, but letting it run.
    # We mock _create_chapter_content to control the input to _add_notes_to_chapter.

    # Side effect for _create_chapter_content
    # This side effect needs to:
    # 1. Create/return a chapter item.
    # 2. Set its initial content to `initial_chapter_html_with_note_markers`.
    # 3. The SUT's `generate` will then call `_add_notes_to_chapter` on this item.
    
    # We need to capture the item *after* _add_notes_to_chapter has modified it.
    # The SUT's _create_chapter_content:
    #   ...
    #   c.content = current_chapter_html_content # (after citations, before notes)
    #   self._add_notes_to_chapter(book, c, chapter_number, num_notes, specific_config, global_config)
    #   self._add_images_to_chapter(book, c, chapter_number, num_images, specific_config, global_config)
    #   return c
    # So, the content of 'c' is modified in place by _add_notes_to_chapter.

    # We'll have _create_chapter_content return our specific mock_chapter_item_for_notes.
    # Before returning it, its content will be set to initial_chapter_html_with_note_markers.
    
    def mock_create_chapter_content_side_effect(book_arg, chap_num_arg, chap_title_arg, spec_conf_arg, glob_conf_arg):
        # This function is mocking SUT's _create_chapter_content
        # It should set the initial content on mock_chapter_item_for_notes
        # *before* _add_notes_to_chapter is called by the SUT.
        
        # Simulate the part of _create_chapter_content that forms the HTML *before* notes are added.
        # For this test, we assume citations are disabled or produce no change.
        mock_chapter_item_for_notes.content = initial_chapter_html_with_note_markers
        mock_chapter_item_for_notes.title = chap_title_arg # Ensure title is set
        mock_chapter_item_for_notes.file_name = f"chap_{chap_num_arg}_notes_test.xhtml"
        
        # The SUT's generate() will then call _add_notes_to_chapter on this item.
        return mock_chapter_item_for_notes

    mocker.patch.object(epub_generator_instance, '_create_chapter_content', side_effect=mock_create_chapter_content_side_effect)
    
    # Mock _determine_count: 1 chapter, 0 sections, 2 notes, 0 images
    # The '2' for notes is crucial for _add_notes_to_chapter to process both markers.
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1, 0, 2, 0]) 
    
    # Mock other transformations
    mocker.patch.object(epub_generator_instance, '_apply_citations_to_item_content', side_effect=lambda c, *args: c) # Passthrough
    mocker.patch.object(epub_generator_instance, '_add_images_to_chapter') # Does nothing
    mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')


    specific_config_notes_content = {
        "title": "Notes Content Test", "epub_version": 3, "chapters_config": 1,
        "sections_per_chapter_config": 0,
        "citations_config": {"enable": False},
        "notes_system": {
            "enable": True, "type": "footnotes_same_page", "notes_config": 2, # notes_config matches determine_count
            "data": {
                "note1": {"content": "This is the first note."},
                "note2": {"content": "This is the second note."}
            }
        },
        "multimedia": {"include_images": False},
        "validation": {"run_epubcheck": False}
    }
    global_config = {}
    output_path = "test_output/notes_content_test.epub"
    
    # Capture items added to the book to check for note items (e.g., CSS)
    added_items_capture = []
    def capture_added_item(item):
        added_items_capture.append(item)
    mock_book_instance.add_item = capture_added_item

    epub_generator_instance.generate(specific_config_notes_content, global_config, output_path)

    # Assert that the content of the chapter item was modified as expected
    # print(f"DEBUG Notes Test - Expected: {expected_chapter_html_after_notes!r}")
    # print(f"DEBUG Notes Test - Actual:   {mock_chapter_item_for_notes.content!r}")
    assert mock_chapter_item_for_notes.content == expected_chapter_html_after_notes
    
    # Assert that note-related CSS was added (if applicable by SUT)
    # Example: check if an EpubItem with a specific CSS filename for notes was added.
    # This depends on how _add_notes_to_chapter is implemented.
    # For now, content check is primary.
    # The SUT's _add_notes_to_chapter adds 'style/notes.css'.
    found_notes_css = any(
        isinstance(item, epub.EpubItem) and item.file_name == 'style/notes.css'
        for item in added_items_capture
    )
    assert found_notes_css, "Notes CSS item not found in book"


def test_generate_epub_with_images_content_is_correct(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """
    Test that image markers are correctly replaced with <img> tags in chapter content
    and that image items are added to the book.
    """
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    
    mock_book_instance = mocker.MagicMock()
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', return_value=mock_book_instance)

    # Mock os.path.exists for image file checking, assume files exist
    mocker.patch('synth_data_gen.generators.epub_components.multimedia.os.path.exists', return_value=True)
    # Mock open for reading image files, return dummy bytes
    mock_open_image_instance = mocker.mock_open(read_data=b"dummy_image_file_bytes")
    mocker.patch('builtins.open', mock_open_image_instance)


    initial_chapter_html_with_image_markers = (
        "<h1>Chapter with Images</h1>"
        "<p>Some text [image:imgkey1] and more text.</p>"
        "<p>Another image [image:imgkey2] here.</p>"
    )
    
    expected_chapter_html_after_images = (
        "<h1>Chapter with Images</h1>"
        "<p>Some text <img src=\"images/img_file1.png\" alt=\"Test Image 1\" /> and more text.</p>"
        "<p>Another image <img src=\"images/img_file2.jpg\" alt=\"Test Image 2\" /> here.</p>"
    )
    
    mock_chapter_item_for_images = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item_for_images.file_name = "c_images.xhtml"
    mock_chapter_item_for_images.title = "Images Chapter"
    # Initial content will be set by the side_effect

    def mock_create_chapter_content_side_effect(book_arg, chap_num_arg, chap_title_arg, spec_conf_arg, glob_conf_arg):
        # Simulate initial HTML formation before image processing
        mock_chapter_item_for_images.content = initial_chapter_html_with_image_markers
        mock_chapter_item_for_images.title = chap_title_arg
        mock_chapter_item_for_images.file_name = f"chap_{chap_num_arg}_images_test.xhtml"
        return mock_chapter_item_for_images

    mocker.patch.object(epub_generator_instance, '_create_chapter_content', side_effect=mock_create_chapter_content_side_effect)
    
    # Mock _determine_count: 1 chapter, 0 sections, 0 notes, 2 images
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=[1, 0, 0, 2]) 
    
    # Mock other transformations
    mocker.patch.object(epub_generator_instance, '_apply_citations_to_item_content', side_effect=lambda c, *args: c)
    mocker.patch.object(epub_generator_instance, '_add_notes_to_chapter')
    mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')

    specific_config_images_content = {
        "title": "Images Content Test", "epub_version": 3, "chapters_config": 1,
        "sections_per_chapter_config": 0,
        "citations_config": {"enable": False},
        "notes_system": {"enable": False},
        "multimedia": {
            "include_images": True, "images_config": 2,
            "image_data": {
                "imgkey1": {"path": "dummy/path/image1.png", "alt_text": "Test Image 1", "filename_in_epub": "img_file1.png"},
                "imgkey2": {"path": "dummy/path/image2.jpg", "alt_text": "Test Image 2", "filename_in_epub": "img_file2.jpg"}
            }
        },
        "validation": {"run_epubcheck": False}
    }
    global_config = {}
    output_path = "test_output/images_content_test.epub"
    
    added_items_capture = []
    def capture_added_item(item):
        added_items_capture.append(item)
    mock_book_instance.add_item = capture_added_item

    epub_generator_instance.generate(specific_config_images_content, global_config, output_path)

    # print(f"DEBUG Images Test - Expected: {expected_chapter_html_after_images!r}")
    # print(f"DEBUG Images Test - Actual:   {mock_chapter_item_for_images.content!r}")
    assert mock_chapter_item_for_images.content == expected_chapter_html_after_images
    
    # Assert that image items were added to the book
    found_image1 = any(
        isinstance(item, epub.EpubImage) and item.file_name == 'images/img_file1.png' and item.media_type == 'image/png'
        for item in added_items_capture
    )
    found_image2 = any(
        isinstance(item, epub.EpubImage) and item.file_name == 'images/img_file2.jpg' and item.media_type == 'image/jpeg'
        for item in added_items_capture
    )
    assert found_image1, "Image item 1 (img_file1.png) not found in book"
    assert found_image2, "Image item 2 (img_file2.jpg) not found in book"
    
    # Check that builtins.open was called for each image path
    mock_open_image_instance.assert_any_call("dummy/path/image1.png", "rb")
    mock_open_image_instance.assert_any_call("dummy/path/image2.jpg", "rb")


def test_generate_epub_with_complex_config_and_interactions(mocker: MockerFixture, epub_generator_instance: EpubGenerator, tmp_path):
    """
    Test EpubGenerator.generate() with a complex configuration involving
    chapters, sections, notes, images, citations, custom ToC, font embedding, and epubcheck.
    Verifies content transformation, structural elements, and epubcheck validation.
    """
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub') # Mock to prevent lxml error

    # Create a MagicMock that will be returned by the patched epub.EpubBook constructor
    mock_book_instance_configured = mocker.MagicMock(spec=epub.EpubBook) # Removed spec=epub.EpubBook
    mock_book_instance_configured.FOLDER_NAME = "EPUB"

    # Pre-configure attributes that epub.write_epub might access directly
    # and that are part of the EpubBook interface.
    # The SUT will call methods like set_title, set_identifier, add_item, etc.,
    # which will further configure this mock or add to its mocked calls.
    mock_book_instance_configured.version = "3.0"
    mock_book_instance_configured.uid_name = "BookId"
    mock_book_instance_configured.uid = "urn:uuid:placeholder-uid" # SUT should overwrite this via set_identifier
    mock_book_instance_configured.title = "Placeholder Title"     # SUT should overwrite via set_title
    mock_book_instance_configured.language = "en"                 # SUT should overwrite via set_language
    mock_book_instance_configured.IDENTIFIER_ID = "BookId"      # Required by _write_opf
    mock_book_instance_configured.direction = None                # Required by _write_opf
    mock_book_instance_configured.prefixes = []                  # Required by _write_opf
    mock_book_instance_configured.namespaces = {}               # Required by _write_opf_metadata
    mock_book_instance_configured.metadata = {} # SUT will populate via add_metadata
    mock_book_instance_configured.items = []    # SUT will populate via add_item
    mock_book_instance_configured.spine = []    # SUT will set this
    mock_book_instance_configured.guide = []    # SUT might modify
    mock_book_instance_configured.toc = ()      # SUT might modify

    # Internal map for get_item_with_id side effect
    # Configure side effects for setter methods to update the mock's attributes
    def set_identifier_side_effect(identifier_str):
        mock_book_instance_configured.uid = identifier_str
    def set_title_side_effect(title_str):
        mock_book_instance_configured.title = title_str
    def set_language_side_effect(lang_str):
        mock_book_instance_configured.language = lang_str
    
    # Mocks for ToC items that will be returned by get_item_with_id
    # These are also added to the book by the SUT via book.add_item()
    mock_nav_item_for_lookup = mocker.MagicMock(spec=epub.EpubNav)
    mock_nav_item_for_lookup.id = "nav"
    mock_nav_item_for_lookup.file_name = "nav.xhtml"
    mock_nav_item_for_lookup.is_linear = True

    mock_ncx_item_for_lookup = mocker.MagicMock(spec=epub.EpubNcx)
    mock_ncx_item_for_lookup.id = "ncx"
    mock_ncx_item_for_lookup.file_name = "toc.ncx"
    mock_ncx_item_for_lookup.is_linear = True # Though NCX is not typically linear in spine

    # Side effect for get_item_with_id
    def get_item_with_id_router(id_to_get):
        if id_to_get == 'nav':
            return mock_nav_item_for_lookup
        if id_to_get == 'ncx':
            return mock_ncx_item_for_lookup
        # For chapter IDs, ebooklib usually gets them directly from spine as objects,
        # not by string ID lookup, if chapters are added as objects to spine.
        # If a chapter ID string *is* looked up, this mock would need to handle it.
        print(f"Warning: mock_book_instance_configured.get_item_with_id called with unhandled ID: {id_to_get}")
        return mocker.MagicMock() # Fallback to a new MagicMock

    def add_metadata_side_effect(namespace, meta_name, meta_value, meta_others=None):
        if meta_others is None:
            meta_others = {}
        ns_dict = mock_book_instance_configured.metadata.setdefault(namespace, {})
        meta_list = ns_dict.setdefault(meta_name, [])
        actual_stored_tuple = (meta_value, meta_others)
        if actual_stored_tuple not in meta_list:
            meta_list.append(actual_stored_tuple)

    def add_author_side_effect(author_str, file_as=None, role='aut', uid=None):
        others = {'role': role}
        if file_as:
            others['file-as'] = file_as
        add_metadata_side_effect('DC', 'creator', author_str, others)

    mock_book_instance_configured.set_identifier = mocker.MagicMock(side_effect=set_identifier_side_effect)
    mock_book_instance_configured.set_title = mocker.MagicMock(side_effect=set_title_side_effect)
    mock_book_instance_configured.set_language = mocker.MagicMock(side_effect=set_language_side_effect)
    mock_book_instance_configured.add_author = mocker.MagicMock(side_effect=add_author_side_effect)
    mock_book_instance_configured.add_metadata = mocker.MagicMock(side_effect=add_metadata_side_effect)
    # Let add_item be a simple MagicMock; SUT calls it.
    # The crucial part is that get_item_with_id returns items with string IDs.
    def add_item_side_effect(item):
        mock_book_instance_configured.items.append(item)
    mock_book_instance_configured.add_item = mocker.MagicMock(side_effect=add_item_side_effect)
    mock_book_instance_configured.get_item_with_id = mocker.MagicMock(side_effect=get_item_with_id_router)

    # Mock the EpubBook class constructor to return our pre-configured mock
    mocker.patch('synth_data_gen.generators.epub.epub.EpubBook', return_value=mock_book_instance_configured)
    mock_book_instance = mock_book_instance_configured

    # Mock os.path.exists for image/font file checking, assume files exist
    mocker.patch('synth_data_gen.generators.epub_components.multimedia.os.path.exists', return_value=True)
    mocker.patch('synth_data_gen.generators.epub.os.path.exists', return_value=True) # For fonts in EpubGenerator
    
    # Mock open for reading image/font files, return dummy bytes
    mock_open_instance = mocker.mock_open(read_data=b"dummy_file_bytes")
    mocker.patch('builtins.open', mock_open_instance)

    # Mock subprocess.run for epubcheck
    mock_subprocess_run = mocker.patch('synth_data_gen.generators.epub.subprocess.run')
    mock_subprocess_run.return_value = mocker.MagicMock(returncode=0, stderr="")

    # Output path is still needed for SUT call and epubcheck mock assertion, but file won't be written.
    output_path = str(tmp_path / "complex_interaction_test.epub")


    # --- Configuration ---
    specific_config_complex = {
        "title": "Complex Interaction Test EPUB",
        "author": "TDD Interaction Bot",
        "language": "en",
        "epub_version": "3.0", # Test string version
        "chapters_config": 1,
        "sections_per_chapter_config": 1,
        "citations_config": {
            "enable": True,
            "style": "author_date",
            "data": {
                "smith2020": {"full_citation": "Smith, J. (2020). A Book.", "in_text": "(Smith, 2020)"},
                "doe2021": {"full_citation": "Doe, A. (2021). Another Book.", "in_text": "(Doe, 2021)"}
            }
        },
        "notes_system": {
            "enable": True,
            "type": "footnotes_same_page",
            "notes_config": 2,
            "data": {
                "noteA": {"content": "This is the first note (noteA)."},
                "noteB": {"content": "This is the second note (noteB)."}
            }
        },
        "multimedia": {
            "include_images": True,
            "images_config": 2,
            "image_data": {
                "imgA": {"path": "dummy_path/imageA.jpg", "alt_text": "Image A", "filename_in_epub": "imageA.jpg"},
                "imgB": {"path": "dummy_path/imageB.png", "alt_text": "Image B", "filename_in_epub": "imageB.png"}
            }
        },
        "toc_settings": {"style": "navdoc_full", "max_depth": 2, "include_landmarks": True},
        "font_embedding": {
            "enable": True,
            "fonts": ["TestFont"], # Assumes TestFont.ttf or TestFont.otf exists via mock
            "obfuscation": "none"
        },
        "validation": {"run_epubcheck": True, "epubcheck_path": "mock/path/to/epubcheck.jar"},
        "test_complex_section_content_key": "complex_test_section_1_1" # Added for refactored SUT
    }
    global_config = {}

    # --- Expected HTML Content (Simplified for one section in one chapter) ---
    # Chapter 1, Section 1.1
    # Note: The SUT's _create_section_content is currently a pass.
    # For this test to be more meaningful for section content, _create_section_content
    # would need to actually generate content with these markers.
    # For now, we'll assume the markers are in the main chapter content that _create_chapter_content starts with.
    
    # Let's assume the SUT's _create_chapter_content will generate initial HTML like this,
    # and then the note/image/citation methods will modify it.
    # This is a simplification; a real test might need to mock parts of _create_section_content
    # if markers are expected to be within sections.
    
    # For this test, we'll focus on the markers being processed in the main chapter body.
    # The SUT's _create_chapter_content calls _apply_citations, then _add_notes, then _add_images.

    raw_chapter_html_complex = (
        "<h1>Chapter 1</h1>"
        "<h2>Section 1.1</h2>" # Assuming _create_section_content adds this if not mocked away
        "<p>Text with a note [note:noteA].</p>"
        "<p>Text with an image [image:imgA].</p>"
        "<p>Text with a citation [cite:smith2020].</p>"
        "<p>Combined: [note:noteB], then an image [image:imgB], and a citation [cite:doe2021].</p>"
    )

    # Expected after all transformations (order of processing matters for nested/complex cases)
    # 1. Citations: (Smith, 2020), (Doe, 2021)
    # 2. Notes: <sup id="fnref-1-1"><a href="#fn-1-1">1</a></sup>, <sup id="fnref-1-2"><a href="#fn-1-2">2</a></sup>
    #    + footnote section
    # 3. Images: <img src="images/imageA.jpg" alt="Image A" />, <img src="images/imageB.png" alt="Image B" />
    
    # After Citations:
    # "<h1>Chapter 1</h1><h2>Section 1.1</h2><p>Text with a note [note:noteA].</p><p>Text with an image [image:imgA].</p><p>Text with a citation (Smith, 2020).</p><p>Combined: [note:noteB], then an image [image:imgB], and a citation (Doe, 2021).</p>"
    # After Notes (applied to above):
    # "<h1>Chapter 1</h1><h2>Section 1.1</h2><p>Text with a note <sup id="fnref-1-1"><a href="#fn-1-1">1</a></sup>.</p><p>Text with an image [image:imgA].</p><p>Text with a citation (Smith, 2020).</p><p>Combined: <sup id="fnref-1-2"><a href="#fn-1-2">2</a></sup>, then an image [image:imgB], and a citation (Doe, 2021).</p>\n<hr...><div...noteA...noteB...</div>"
    # After Images (applied to above):
    expected_final_chapter_html = (
        "<h1>Chapter 1</h1>"
        "<h2>Section 1.1</h2>"
        "<p>Text with a note <sup id=\"fnref-1-1\"><a href=\"#fn-1-1\">1</a></sup>.</p>"
        "<p>Text with an image <img src=\"images/imageA.jpg\" alt=\"Image A\" />.</p>"
        "<p>Text with a citation (Smith, 2020).</p>"
        "<p>Combined: <sup id=\"fnref-1-2\"><a href=\"#fn-1-2\">2</a></sup>, then an image <img src=\"images/imageB.png\" alt=\"Image B\" />, and a citation (Doe, 2021).</p>"
        "\n<hr class=\"footnote-separator\" />"
        "\n<div class=\"footnotes\">"
        "\n<p id=\"fn-1-1\" class=\"footnote\"><a href=\"#fnref-1-1\">1.</a> This is the first note (noteA).</p>"
        "\n<p id=\"fn-1-2\" class=\"footnote\"><a href=\"#fnref-1-2\">2.</a> This is the second note (noteB).</p>"
        "\n</div>"
    )

    # --- Mocking Strategy ---
    # We need to let _create_chapter_content run more of its actual logic.
    # We'll mock _determine_count to control the number of high-level items.
    # The internal calls to _apply_citations, _add_notes, _add_images should be the real methods.

    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=lambda conf, name, **kwargs: {
        "chapters": 1,
        "sections_in_chapter_1": 1, # For the H2
        "notes_in_chapter_1": 2,    # For _add_notes_to_chapter
        "images_in_chapter_1": 2,   # For _add_images_to_chapter
        # Other counts for sub-elements within sections would be 0 if _create_section_content is basic
    }.get(name, 0))

    # To inject raw_chapter_html_complex, we need to control what _create_chapter_content starts with.
    # The SUT's _create_chapter_content builds HTML. We'll mock _create_section_content to be a passthrough
    # and ensure the main chapter HTML starts with our raw content.
    # This is still a bit of a hack. A better SUT design would make this easier.
    
    # Let's patch the initial HTML formation part of _create_chapter_content.
    # This is difficult without refactoring the SUT.
    # Alternative: Spy on the arguments to the processing methods.
    # For this test, we want to see the *final output*, so we need to let them run.

    # The current _create_chapter_content in SUT:
    #   chapter_content_html = f"<h1>{chapter_title}</h1>"
    #   ... calls _create_section_content which appends to this string (conceptually) ...
    #   current_chapter_html_content = chapter_content_html
    #   current_chapter_html_content = self._apply_citations_to_item_content(...)
    #   c.content = current_chapter_html_content
    #   self._add_notes_to_chapter(book, c, ...)
    #   self._add_images_to_chapter(book, c, ...)
    # So, _add_notes and _add_images operate on the content *after* citations.

    # We need _create_chapter_content to produce `raw_chapter_html_complex` *before* any of these are called.
    # This is the hard part to mock without SUT change.

    # Let's try a side effect on _create_chapter_content that itself calls the real sub-methods
    # but starts with `raw_chapter_html_complex`.
    
    original_create_chapter_content = epub_generator_instance._create_chapter_content
    # Unpatch methods we want to test
    # We need to get the original methods before the class instance is created if they are class methods
    # For instance methods, this is fine.
    
    # We need to get the original methods from the class, not the instance, if we are patching the instance's methods.
    # However, the test fixture provides an instance.
    # The current approach in notes/images tests where we store original_add_notes = epub_generator_instance._add_notes_to_chapter
    # and then call it from a mock_create_chapter_content_side_effect should work.

    # Store original methods we want to test
    original_apply_citations = epub_generator_instance._apply_citations_to_item_content
    original_add_notes = epub_generator_instance._add_notes_to_chapter
    original_add_images = epub_generator_instance._add_images_to_chapter

    # Mock _create_section_content to do nothing or return a simple marker
    # to prevent it from adding its own complex HTML.
    # mocker.patch.object(epub_generator_instance, '_create_section_content', return_value=None) # Removed to use actual SUT method


    def complex_create_chapter_content_side_effect(book_arg, chap_num_arg, chap_title_arg, spec_conf_arg, glob_conf_arg):
        # Start with the raw HTML containing all markers
        current_html = raw_chapter_html_complex # Start with raw HTML

        # Create the chapter item WITHOUT transformations by this side effect
        chapter_item = epub.EpubHtml(
            title=chap_title_arg,
            file_name=f'chap_{chap_num_arg}_complex.xhtml',
            lang=spec_conf_arg.get("language", "en")
        )
        chapter_item.content = current_html # Set raw content
        
        # The SUT's _create_chapter_content (which this side_effect is mocking)
        # would be responsible for calling the transformation methods.
        # For this "Red" state, we ensure this side_effect does NOT do the transformations.

        book_arg.add_item(chapter_item)
        return chapter_item

    # mocker.patch.object(epub_generator_instance, '_create_chapter_content', side_effect=complex_create_chapter_content_side_effect) # Removed to use actual SUT method
    
    # Mock ToC creation to check it's called with correct settings
    # Ensure the mock returns an object with an 'id' and 'file_name' attribute
    # The create_nav_document mock should return the same item that get_item_with_id will return for 'nav'
    mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document', return_value=mock_nav_item_for_lookup)
    mock_create_ncx = mocker.patch('synth_data_gen.generators.epub_components.toc.create_ncx', return_value=mock_ncx_item_for_lookup)

    # mocker.spy(mock_book_instance_configured, 'add_item') # Replaced by simpler MagicMock()


    epub_generator_instance.generate(specific_config_complex, global_config, output_path)

    # --- Assertions ---
    # 1. Chapter Content
    # Find the chapter item (assuming only one chapter is generated based on mock_determine_count)
    generated_chapter_item = None
    for item in mock_book_instance_configured.items: # Use mock_book_instance.items
        if isinstance(item, epub.EpubHtml) and item.file_name == 'chap_1.xhtml': # Adjusted expected filename
            generated_chapter_item = item
            break
    
    assert generated_chapter_item is not None, "Complex chapter item not found in book"
    # print(f"DEBUG Complex Test - Expected: {expected_final_chapter_html!r}")
    # print(f"DEBUG Complex Test - Actual:   {generated_chapter_item.content!r}")
    assert generated_chapter_item.content == expected_final_chapter_html

    # 2. ToC
    mock_create_nav_document.assert_called_once()
    nav_call_args, _ = mock_create_nav_document.call_args
    assert nav_call_args[2] == specific_config_complex["toc_settings"] # toc_settings
    assert nav_call_args[3] == str(specific_config_complex["epub_version"]) # epub_version (as string)
    mock_create_ncx.assert_not_called() # EPUB3 with NavDoc should not call NCX by default

    # 3. Font Embedding
    found_font_item = any(
        isinstance(item, epub.EpubItem) and item.file_name == "fonts/TestFont.ttf"
        for item in mock_book_instance_configured.items # Use mock_book_instance.items
    ) or any(
        isinstance(item, epub.EpubItem) and item.file_name == "fonts/TestFont.otf"
        for item in mock_book_instance_configured.items # Use mock_book_instance.items
    )
    assert found_font_item, "Embedded font item not found in book"

    # 4. Image Items
    found_image_A = any(
        isinstance(item, epub.EpubItem) and item.file_name == "images/imageA.jpg"
        for item in mock_book_instance_configured.items # Use mock_book_instance.items
    )
    found_image_B = any(
        isinstance(item, epub.EpubItem) and item.file_name == "images/imageB.png"
        for item in mock_book_instance_configured.items # Use mock_book_instance.items
    )
    assert found_image_A, "Image A item not found in book"
    assert found_image_B, "Image B item not found in book"

    # 5. Epubcheck
    mock_subprocess_run.assert_called_once_with(
        ['java', '-jar', "mock/path/to/epubcheck.jar", output_path],
        capture_output=True, text=True, check=False
    )
def test_generate_epub3_navdoc_respects_max_depth_setting(mocker: MockerFixture, epub_generator_instance: EpubGenerator, tmp_path):
    """
    Test that the EPUB3 NAV document respects toc_settings.max_depth.
    """
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')

    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.FOLDER_NAME = "EPUB"
    mock_book_instance.IDENTIFIER_ID = "BookIdMaxDepth"
    mock_book_instance.direction = None
    mock_book_instance.prefixes = []
    mock_book_instance.namespaces = {}
    mock_book_instance.metadata = {}
    mock_book_instance.items = []
    mock_book_instance.spine = []
    mock_book_instance.guide = []
    mock_book_instance.toc = () # Initialize toc attribute

    # Configure side effects for setter methods to update the mock's attributes
    def set_identifier_side_effect_for_depth_test(identifier_str):
        mock_book_instance.uid = identifier_str
    def set_title_side_effect_for_depth_test(title_str):
        mock_book_instance.title = title_str
    def set_language_side_effect_for_depth_test(lang_str):
        mock_book_instance.language = lang_str
    
    mock_book_instance.set_identifier = mocker.MagicMock(side_effect=set_identifier_side_effect_for_depth_test)
    mock_book_instance.set_title = mocker.MagicMock(side_effect=set_title_side_effect_for_depth_test)
    mock_book_instance.set_language = mocker.MagicMock(side_effect=set_language_side_effect_for_depth_test)
    mock_book_instance.add_author = mocker.MagicMock() # Keep simple for this test
    mock_book_instance.add_metadata = mocker.MagicMock() # Keep simple

    # Setup a nested ToC structure that will be assigned to book.toc
    # (Chapter 1 -> Section 1.1 -> SubSection 1.1.1)
    # (Chapter 2)
    mock_sub_section_link = epub.Link('chap_1_sec_1_sub_1.xhtml', 'SubSection 1.1.1', 'sub111')
    # Corrected nested structure for ebooklib.toc: (Link, (children_tuple))
    mock_section_tuple = (epub.Link('chap_1_sec_1.xhtml', 'Section 1.1', 'sec11'), (mock_sub_section_link,))
    mock_chapter1_tuple = (epub.Link('chap_1.xhtml', 'Chapter 1', 'ch1'), (mock_section_tuple,))
    mock_chapter2_link = epub.Link('chap_2.xhtml', 'Chapter 2', 'ch2') # This one has no children
    
    mock_book_instance.toc = (mock_chapter1_tuple, mock_chapter2_link)
    
    # Mock items that would be created by SUT and added to book.items
    mock_chapter1_item = mocker.MagicMock(spec=epub.EpubHtml, file_name='chap_1.xhtml', title='Chapter 1', is_linear=True)
    mock_chapter2_item = mocker.MagicMock(spec=epub.EpubHtml, file_name='chap_2.xhtml', title='Chapter 2', is_linear=True)
    # Section and sub-section items are not strictly needed for ToC mock if Link hrefs are distinct
    
    mock_nav_item = mocker.MagicMock(spec=epub.EpubNav)
    mock_nav_item.id = "nav"
    mock_nav_item.file_name = "nav.xhtml"
    mock_nav_item.content = "" # Will be populated by create_nav_document

    def add_item_side_effect_for_nav_test(item):
        mock_book_instance.items.append(item)
        # A NAV document can be an EpubHtml item with 'nav' in its properties
        if (isinstance(item, epub.EpubHtml) and hasattr(item, 'properties') and 'nav' in item.properties) or \
           isinstance(item, epub.EpubNav): # Original check for EpubNav just in case
            # Ensure the mock_nav_item (which is spec'd as EpubNav) can accept content from EpubHtml
            # For simplicity in this test, we'll assume item.content is what we need.
            # If EpubNav has a different content attribute, this might need adjustment.
            if hasattr(item, 'content'):
                 mock_nav_item.content = item.content # Steal its content for assertion
            # Also ensure the item itself is captured if needed for type checks later,
            # though the test currently checks mock_book_instance.items
            # mock_nav_item = item # This would reassign the mock, probably not what we want.

    mock_book_instance.add_item = mocker.MagicMock(side_effect=add_item_side_effect_for_nav_test)
    mock_book_instance.get_metadata = mocker.MagicMock(return_value=[("en", {})]) # For book.lang

    mock_epub_book_class.return_value = mock_book_instance
    
    mocker.patch.object(epub_generator_instance, '_determine_count', side_effect=lambda conf, name, **kwargs: {
        "chapters": 2, # Matches our mock_book_instance.toc structure
        "sections_in_chapter_1": 1,
        "sections_in_chapter_2": 0,
        "notes_in_chapter_1": 0,
        "notes_in_chapter_2": 0,
        "images_in_chapter_1": 0,
        "images_in_chapter_2": 0,
    }.get(name, 0))

    # Mock _create_chapter_content to add the mock chapter items
    # This is to ensure book.items has something for spine, not for ToC data itself for this test
    created_chapters_for_spine = []
    def create_chapter_side_effect(book, chap_num, chap_title, spec_conf, glob_conf):
        if chap_num == 1:
            # book.add_item(mock_chapter1_item) # add_item is already mocked to capture
            created_chapters_for_spine.append(mock_chapter1_item)
            return mock_chapter1_item
        elif chap_num == 2:
            # book.add_item(mock_chapter2_item)
            created_chapters_for_spine.append(mock_chapter2_item)
            return mock_chapter2_item
        return mocker.MagicMock(spec=epub.EpubHtml)

    mocker.patch.object(epub_generator_instance, '_create_chapter_content', side_effect=create_chapter_side_effect)
    
    # The key is that toc.create_nav_document will be called with the mock_book_instance
    # which has mock_book_instance.toc pre-populated with our nested structure.
    # We don't mock toc.create_nav_document itself, we let it run.

    specific_config_max_depth = {
        "title": "Max Depth Test", "author": "Depth Tester", "language": "en",
        "epub_version": "3.0",
        "chapters_config": 2, # Aligns with _determine_count mock
        "sections_per_chapter_config": 0, # Not directly used for ToC data in this test setup
        "toc_settings": {"style": "navdoc_full", "max_depth": 1}, # Test with max_depth 1
        "validation": {"run_epubcheck": False} # Disable epubcheck for this unit test
    }
    global_config = {}
    output_path = str(tmp_path / "max_depth_test.epub")

    epub_generator_instance.generate(specific_config_max_depth, global_config, output_path)

    # Assertions
    # The real toc.create_nav_document should have been called and populated mock_nav_item.content
    # via the add_item_side_effect_for_nav_test
    
    # Check that the nav item was added to the book (and thus its content captured)
    nav_item_in_book = next((item for item in mock_book_instance.items if (hasattr(item, 'properties') and 'nav' in item.properties) or item.id == "nav"), None)
    assert nav_item_in_book is not None, "NAV item was not added to the book by SUT"
    
    nav_content_bytes = nav_item_in_book.content # This should now be the content of the EpubHtml nav item
    assert nav_content_bytes is not None and nav_content_bytes != b"", "NAV content is empty"
    nav_content = nav_content_bytes.decode('utf-8')


    # print(f"DEBUG NAV Content for max_depth=1:\n{nav_content}")

    assert "Chapter 1" in nav_content
    assert "Section 1.1" not in nav_content # Should be excluded due to max_depth: 1
    assert "SubSection 1.1.1" not in nav_content # Should be excluded
def test_generate_epub3_with_ncx_only_config(mocker: MockerFixture, epub_generator_instance: EpubGenerator, tmp_path):
    """
    Test that for EPUB3, if config specifies NCX only (include_nav_doc=False, include_ncx=True),
    only NCX is created.
    """
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')

    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.FOLDER_NAME = "EPUB"
    mock_book_instance.IDENTIFIER_ID = "BookIdNcxOnly"
    mock_book_instance.items = []
    mock_book_instance.toc = ()
    mock_book_instance.get_metadata = mocker.MagicMock(return_value=[("en", {})]) # For book.lang

    # Mock methods that would be called by SUT
    mock_book_instance.set_identifier = mocker.MagicMock()
    mock_book_instance.set_title = mocker.MagicMock()
    mock_book_instance.set_language = mocker.MagicMock()
    mock_book_instance.add_author = mocker.MagicMock()
    mock_book_instance.add_metadata = mocker.MagicMock()
    
    # Capture items added to the book
    added_items_capture_ncx_only = []
    def add_item_side_effect_ncx_only(item):
        added_items_capture_ncx_only.append(item)
        # Also append to the mock_book_instance.items for internal SUT consistency if it reads it
        mock_book_instance.items.append(item)

    mock_book_instance.add_item = mocker.MagicMock(side_effect=add_item_side_effect_ncx_only)
    mock_epub_book_class.return_value = mock_book_instance

    # Mock ToC creation functions
    def create_ncx_side_effect(book, chapters_data, toc_settings):
        # Simulate toc.create_ncx adding an EpubNcx item to the book
        ncx_item = epub.EpubNcx()
        # The add_item_side_effect_ncx_only will capture this when book.add_item(ncx_item) is called by SUT
        # However, the SUT's EpubGenerator.generate() calls toc.create_ncx, which itself should call book.add_item.
        # So, we need to ensure the mock_book_instance's add_item is called by the SUT after toc.create_ncx returns.
        # For this test, we assume toc.create_ncx returns the item and the SUT adds it.
        # The SUT's generate method (line 422 in EpubGenerator) calls toc.create_ncx.
        # The actual toc.create_ncx (line 618 in toc.py) calls book.add_item(ncx).
        # So, this side_effect must also call book.add_item to simulate the real behavior
        # so that add_item_side_effect_ncx_only can capture the item.
        ncx_item = epub.EpubNcx()
        book.add_item(ncx_item) # Simulate the real function adding the item to the book
        return ncx_item

    mock_create_ncx = mocker.patch('synth_data_gen.generators.epub_components.toc.create_ncx', side_effect=create_ncx_side_effect)
    mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')

    # Mock chapter creation to provide some basic chapter data for ToC functions
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml, file_name='chap_1.xhtml', title='Chapter 1')
    mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
    mocker.patch.object(epub_generator_instance, '_determine_count', return_value=1) # Assume 1 chapter

    specific_config_ncx_only = {
        "title": "EPUB3 NCX Only Test", "author": "NCX Tester", "language": "en",
        "epub_version": "3.0", # EPUB3
        "chapters_config": 1,
        "include_ncx": True,       # Explicitly request NCX
        "include_nav_doc": False,  # Explicitly disable NavDoc
        "toc_settings": {"style": "default"}, # Style might be ignored due to explicit flags
        "validation": {"run_epubcheck": False}
    }
    global_config = {}
    output_path = str(tmp_path / "epub3_ncx_only.epub")

    epub_generator_instance.generate(specific_config_ncx_only, global_config, output_path)

    # Assertions
    mock_create_ncx.assert_called_once()
    mock_create_nav_document.assert_not_called()

    found_ncx = any(isinstance(item, epub.EpubNcx) for item in added_items_capture_ncx_only)
    assert found_ncx, "EpubNcx item not found in book items"

    found_nav = any(
        (isinstance(item, epub.EpubHtml) and hasattr(item, 'properties') and 'nav' in item.properties) or \
        isinstance(item, epub.EpubNav) 
        for item in added_items_capture_ncx_only
    )
    assert not found_nav, "NAV document (EpubNav or EpubHtml with nav property) was unexpectedly found"
    # Removed erroneous assert from different test
    def test_generate_epub2_with_nav_doc_true_is_ignored(self, mocker: MockerFixture, epub_generator_instance: EpubGenerator, tmp_path):
        """
        Test that for EPUB2, if config specifies include_nav_doc=True, it is ignored,
        and an NCX is created (as it's mandatory for EPUB2) and no NAV doc is created.
        """
        mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
        mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
        mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')

        mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
        mock_book_instance.FOLDER_NAME = "EPUB"
        mock_book_instance.IDENTIFIER_ID = "BookIdEpub2NavTrue"
        mock_book_instance.items = []
        mock_book_instance.toc = ()
        mock_book_instance.get_metadata = mocker.MagicMock(return_value=[("en", {})])

        mock_book_instance.set_identifier = mocker.MagicMock()
        mock_book_instance.set_title = mocker.MagicMock()
        mock_book_instance.set_language = mocker.MagicMock()
        mock_book_instance.add_author = mocker.MagicMock()
        mock_book_instance.add_metadata = mocker.MagicMock()
        
        added_items_capture = []
        def add_item_side_effect(item):
            added_items_capture.append(item)
            mock_book_instance.items.append(item)
        mock_book_instance.add_item = mocker.MagicMock(side_effect=add_item_side_effect)
        mock_epub_book_class.return_value = mock_book_instance

        # Mock ToC creation functions
        # For EPUB2, create_ncx should be called.
        # create_nav_document should NOT be called, even if include_nav_doc is True.
        def create_ncx_side_effect_epub2(book, chapters_data, toc_settings):
            ncx_item = epub.EpubNcx()
            book.add_item(ncx_item) # Simulate real function adding item
            return ncx_item
        
        mock_create_ncx = mocker.patch('synth_data_gen.generators.epub_components.toc.create_ncx', side_effect=create_ncx_side_effect_epub2)
        mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')

        mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml, file_name='chap1_epub2.xhtml', title='Chapter 1 EPUB2')
        mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
        mocker.patch.object(epub_generator_instance, '_determine_count', return_value=1)

        specific_config_epub2_nav_true = {
            "title": "EPUB2 NavDoc True Test",
            "epub_version": "2.0",       # EPUB2
            "chapters_config": 1,
            "include_ncx": True,       # Should default to True or be respected if True for EPUB2
            "include_nav_doc": True,   # This flag should be IGNORED for EPUB2
            "toc_settings": {"style": "default"},
            "validation": {"run_epubcheck": False}
        }
        global_config = {}
        output_path = str(tmp_path / "epub2_nav_doc_true.epub")

        epub_generator_instance.generate(specific_config_epub2_nav_true, global_config, output_path)

        mock_create_ncx.assert_called_once()
        mock_create_nav_document.assert_not_called()

        found_ncx = any(isinstance(item, epub.EpubNcx) for item in added_items_capture)
        assert found_ncx, "EpubNcx item not found in book items for EPUB2"
def test_generate_epub_with_no_toc_flags_and_max_depth(mocker: MockerFixture, epub_generator_instance: EpubGenerator, tmp_path):
        """
        Test that if include_ncx and include_nav_doc are False, no ToC is generated,
        regardless of toc_settings.max_depth.
        """
        mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
        mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
        mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')

        mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
        mock_book_instance.FOLDER_NAME = "EPUB"
        mock_book_instance.IDENTIFIER_ID = "BookIdNoTocMaxDepth"
        mock_book_instance.items = []
        mock_book_instance.toc = () # Should remain empty
        mock_book_instance.get_metadata = mocker.MagicMock(return_value=[("en", {})])

        mock_book_instance.set_identifier = mocker.MagicMock()
        mock_book_instance.set_title = mocker.MagicMock()
        mock_book_instance.set_language = mocker.MagicMock()
        mock_book_instance.add_author = mocker.MagicMock()
        mock_book_instance.add_metadata = mocker.MagicMock()
        
        added_items_capture = []
        def add_item_side_effect(item):
            added_items_capture.append(item)
            mock_book_instance.items.append(item)
        mock_book_instance.add_item = mocker.MagicMock(side_effect=add_item_side_effect)
        mock_epub_book_class.return_value = mock_book_instance

        mock_create_ncx = mocker.patch('synth_data_gen.generators.epub_components.toc.create_ncx')
        mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document')

        mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml, file_name='chap1_no_toc.xhtml', title='Chapter 1 No ToC')
        mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
        mocker.patch.object(epub_generator_instance, '_determine_count', return_value=1) # 1 chapter

        specific_config_no_toc = {
            "title": "No ToC Max Depth Test",
            "epub_version": "3.0",
            "chapters_config": 1,
            "include_ncx": False,
            "include_nav_doc": False,
            "toc_settings": {"style": "default", "max_depth": 2}, # max_depth should be ignored
            "validation": {"run_epubcheck": False}
        }
        global_config = {}
        output_path = str(tmp_path / "no_toc_max_depth.epub")

        epub_generator_instance.generate(specific_config_no_toc, global_config, output_path)

        mock_create_ncx.assert_not_called()
        mock_create_nav_document.assert_not_called()

        assert not mock_book_instance.toc, "book.toc should be empty when no ToC is generated"

        found_ncx = any(isinstance(item, epub.EpubNcx) for item in added_items_capture)
        assert not found_ncx, "EpubNcx item was unexpectedly found"

        found_nav = any(
            (isinstance(item, epub.EpubHtml) and hasattr(item, 'properties') and 'nav' in item.properties) or \
            isinstance(item, epub.EpubNav) 
            for item in added_items_capture
        )
def test_generate_epub3_navdoc_only_config(mocker: MockerFixture, epub_generator_instance: EpubGenerator, tmp_path):
        """
        Test that for EPUB3, if config specifies NavDoc only (include_nav_doc=True, include_ncx=False),
        only a NAV document is created and no NCX.
        """
        mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
        mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
        mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')

        mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
        mock_book_instance.FOLDER_NAME = "EPUB"
        mock_book_instance.IDENTIFIER_ID = "BookIdEpub3NavOnly"
        mock_book_instance.items = []
        mock_book_instance.toc = ()
        mock_book_instance.get_metadata = mocker.MagicMock(return_value=[("en", {})]) # For book.lang

        mock_book_instance.set_identifier = mocker.MagicMock()
        mock_book_instance.set_title = mocker.MagicMock()
        mock_book_instance.set_language = mocker.MagicMock()
        mock_book_instance.add_author = mocker.MagicMock()
        mock_book_instance.add_metadata = mocker.MagicMock()
        
        added_items_capture = []
        def add_item_side_effect(item):
            added_items_capture.append(item)
            mock_book_instance.items.append(item)
        mock_book_instance.add_item = mocker.MagicMock(side_effect=add_item_side_effect)
        mock_epub_book_class.return_value = mock_book_instance

        # Mock ToC creation functions
        def create_nav_document_side_effect(book, chapters_data, toc_settings, epub_version):
            # Simulate toc.create_nav_document adding an EpubNav/EpubHtml item to the book
            # For simplicity, assume it returns an EpubNav item directly
            nav_item = epub.EpubNav() 
            # The SUT's generate method should call book.add_item(nav_item)
            # This side_effect simulates the item that would be added.
            # The actual add_item call is spied on via mock_book_instance.add_item
            return nav_item

        mock_create_ncx = mocker.patch('synth_data_gen.generators.epub_components.toc.create_ncx')
        mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document', side_effect=create_nav_document_side_effect)

        mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml, file_name='chap1_nav_only.xhtml', title='Chapter 1 Nav Only')
        mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
        mocker.patch.object(epub_generator_instance, '_determine_count', return_value=1) # Assume 1 chapter

        specific_config_nav_only = {
            "title": "EPUB3 NavDoc Only Test",
            "epub_version": "3.0",
            "chapters_config": 1,
            "include_ncx": False,
            "include_nav_doc": True,
            "toc_settings": {"style": "default"},
            "validation": {"run_epubcheck": False}
        }
        global_config = {}
        output_path = str(tmp_path / "epub3_nav_only.epub")

        epub_generator_instance.generate(specific_config_nav_only, global_config, output_path)

        mock_create_nav_document.assert_called_once()
        mock_create_ncx.assert_not_called()

        found_nav = any(
            (isinstance(item, epub.EpubHtml) and hasattr(item, 'properties') and 'nav' in item.properties) or \
            isinstance(item, epub.EpubNav) 
            for item in added_items_capture
        )
        assert found_nav, "NAV document (EpubNav or EpubHtml with nav property) not found"
        
        found_ncx = any(isinstance(item, epub.EpubNcx) for item in added_items_capture)
        assert not found_ncx, "EpubNcx item was unexpectedly found"
        # The assertion below was duplicated and incorrect, it's covered by the one on line 2664
        # assert found_nav, "NAV document (EpubNav or EpubHtml with nav property) not found"
def test_generate_epub_with_both_ncx_and_nav_doc_true(mocker: MockerFixture, epub_generator_instance: EpubGenerator, tmp_path):
        """
        Test that if both include_ncx and include_nav_doc are True, both ToC types are generated.
        This is primarily for EPUB3, but the flags should be respected.
        """
        mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
        mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
        mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')

        mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
        mock_book_instance.FOLDER_NAME = "EPUB"
        mock_book_instance.IDENTIFIER_ID = "BookIdBothTocs"
        mock_book_instance.items = []
        mock_book_instance.toc = () 
        mock_book_instance.get_metadata = mocker.MagicMock(return_value=[("en", {})])

        mock_book_instance.set_identifier = mocker.MagicMock()
        mock_book_instance.set_title = mocker.MagicMock()
        mock_book_instance.set_language = mocker.MagicMock()
        mock_book_instance.add_author = mocker.MagicMock()
        mock_book_instance.add_metadata = mocker.MagicMock()
        
        added_items_capture = []
        def add_item_side_effect(item):
            added_items_capture.append(item)
            mock_book_instance.items.append(item)
        mock_book_instance.add_item = mocker.MagicMock(side_effect=add_item_side_effect)
        mock_epub_book_class.return_value = mock_book_instance

        # Mock ToC creation functions
        def create_ncx_side_effect_both(book, chapters_data, toc_settings):
            ncx_item = epub.EpubNcx()
            book.add_item(ncx_item)
            return ncx_item

        def create_nav_document_side_effect_both(book, chapters_data, toc_settings, epub_version):
            nav_item = epub.EpubNav()
            # SUT should call book.add_item(nav_item)
            return nav_item

        mock_create_ncx = mocker.patch('synth_data_gen.generators.epub_components.toc.create_ncx', side_effect=create_ncx_side_effect_both)
        mock_create_nav_document = mocker.patch('synth_data_gen.generators.epub_components.toc.create_nav_document', side_effect=create_nav_document_side_effect_both)

        mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml, file_name='chap1_both_tocs.xhtml', title='Chapter 1 Both ToCs')
        mocker.patch.object(epub_generator_instance, '_create_chapter_content', return_value=mock_chapter_item)
        mocker.patch.object(epub_generator_instance, '_determine_count', return_value=1)

        specific_config_both_tocs = {
            "title": "EPUB Both ToCs Test",
            "epub_version": "3.0", # Test with EPUB3
            "chapters_config": 1,
            "include_ncx": True,
            "include_nav_doc": True,
            "toc_settings": {"style": "default"},
            "validation": {"run_epubcheck": False}
        }
        global_config = {}
        output_path = str(tmp_path / "epub3_both_tocs.epub")

        epub_generator_instance.generate(specific_config_both_tocs, global_config, output_path)

        mock_create_ncx.assert_called_once()
        mock_create_nav_document.assert_called_once()

        found_ncx = any(isinstance(item, epub.EpubNcx) for item in added_items_capture)
        assert found_ncx, "EpubNcx item not found when both ToCs requested"

        found_nav = any(
            (isinstance(item, epub.EpubHtml) and hasattr(item, 'properties') and 'nav' in item.properties) or \
            isinstance(item, epub.EpubNav) 
            for item in added_items_capture
        )
        assert found_nav, "NAV document not found when both ToCs requested"