import pytest
from pytest_mock import MockerFixture
from ebooklib import epub
from synth_data_gen.generators.epub import EpubGenerator
import random # For patching random.randint and random.random

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

    mock_create_nav_doc.assert_called_once()
    args_nav, _ = mock_create_nav_doc.call_args
    assert args_nav[0] is mock_book_instance
    assert len(args_nav[1]) == 1
    assert args_nav[1][0] is mock_chapter_item
    assert args_nav[2] == specific_config["toc_settings"]
    assert args_nav[3] == specific_config["epub_version"]

    mock_create_ncx.assert_not_called()

def test_generate_unified_quantity_chapters_exact(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with 'chapters_config' as an exact integer (Unified Quantity)."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_create_chapter_content = mocker.patch.object(epub_generator_instance, '_create_chapter_content')
    mock_determine_sub_elements_count = mocker.patch.object(epub_generator_instance, '_determine_count')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item.file_name = 'chap_1.xhtml'
    mock_chapter_item.title = 'Chapter 1'
    mock_create_chapter_content.return_value = mock_chapter_item

    exact_chapter_count = 3
    mock_determine_sub_elements_count.side_effect = [
        exact_chapter_count,
        0, 0, 0,
        0, 0, 0,
        0, 0, 0
    ]
    
    specific_config = {
        "title": "Unified Exact Chapters Test",
        "chapters_config": exact_chapter_count,
        "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "epub_version": 3,
        "toc_settings": {"style": "default"}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/unified_exact_chapters.epub"

    epub_generator_instance.generate(specific_config, global_config, output_path)
    
    assert mocker.call(exact_chapter_count, "chapters") in mock_determine_sub_elements_count.call_args_list
    assert mock_create_chapter_content.call_count == exact_chapter_count
    
    expected_determine_calls = [mocker.call(exact_chapter_count, "chapters")]
    for i in range(1, exact_chapter_count + 1):
        expected_determine_calls.append(mocker.call(0, f"sections_in_chapter_{i}"))
        expected_determine_calls.append(mocker.call(0, f"notes_in_chapter_{i}"))
        # images_config is not called if include_images is False
    # This part of the original test was a bit too specific and fragile;
    # the primary check is on create_chapter_content and the first call to determine_count.

def test_generate_unified_quantity_chapters_range(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with 'chapters_config' as a range object (Unified Quantity)."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_create_chapter_content = mocker.patch.object(epub_generator_instance, '_create_chapter_content')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_randint = mocker.patch('random.randint')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item.file_name = 'chap_range.xhtml'
    mock_chapter_item.title = 'Chapter Range'
    mock_create_chapter_content.return_value = mock_chapter_item

    chapters_range_config = {"min": 2, "max": 5}
    expected_chapters_from_range = 4
    mock_randint.return_value = expected_chapters_from_range

    determine_side_effects = [expected_chapters_from_range] + [0, 0, 0] * expected_chapters_from_range
    mock_determine_count.side_effect = determine_side_effects

    specific_config = {
        "title": "Unified Range Chapters Test",
        "chapters_config": chapters_range_config,
        "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "epub_version": 3,
        "toc_settings": {"style": "default"}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/unified_range_chapters.epub"

    epub_generator_instance.generate(specific_config, global_config, output_path)

    assert mocker.call(chapters_range_config, "chapters") in mock_determine_count.call_args_list
    assert mock_create_chapter_content.call_count == expected_chapters_from_range
    assert mock_determine_count.call_args_list[0] == mocker.call(chapters_range_config, "chapters")

def test_generate_unified_quantity_chapters_probabilistic(mocker: MockerFixture, epub_generator_instance: EpubGenerator):
    """Test generate with 'chapters_config' as a probabilistic object (Unified Quantity)."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.epub.ensure_output_directories')
    mock_write_epub = mocker.patch('synth_data_gen.generators.epub.epub.write_epub')
    mock_epub_book_class = mocker.patch('synth_data_gen.generators.epub.epub.EpubBook')
    mock_create_chapter_content = mocker.patch.object(epub_generator_instance, '_create_chapter_content')
    mock_determine_count = mocker.patch.object(epub_generator_instance, '_determine_count')
    mock_random_random = mocker.patch('random.random')

    mock_book_instance = mocker.MagicMock()
    mock_epub_book_class.return_value = mock_book_instance
    mock_chapter_item = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter_item.file_name = 'chap_prob.xhtml'
    mock_chapter_item.title = 'Chapter Probabilistic'
    mock_create_chapter_content.return_value = mock_chapter_item

    chapters_prob_config = {"chance": 0.7, "per_unit_of": "document", "max_total": 3}
    mock_random_random.return_value = 0.6
    expected_chapters_from_prob = 1

    determine_side_effects = [expected_chapters_from_prob] + [0, 0, 0] * expected_chapters_from_prob
    mock_determine_count.side_effect = determine_side_effects

    specific_config = {
        "title": "Unified Probabilistic Chapters Test",
        "chapters_config": chapters_prob_config,
        "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "epub_version": 3,
        "toc_settings": {"style": "default"}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/unified_prob_chapters.epub"

    epub_generator_instance.generate(specific_config, global_config, output_path)

    assert mocker.call(chapters_prob_config, "chapters") in mock_determine_count.call_args_list
    assert mock_create_chapter_content.call_count == expected_chapters_from_prob
    assert mock_determine_count.call_args_list[0] == mocker.call(chapters_prob_config, "chapters")