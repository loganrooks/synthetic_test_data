"""
Integration tests for configuration loading and data generation flow.

These tests verify that:
1. ConfigLoader is properly instantiated and called
2. Config from file_types[].<type>_specific_settings is passed to generators
3. Default configs are merged with user configs
"""
import pytest
from unittest.mock import patch, MagicMock

from synth_data_gen import generate_data
from synth_data_gen.generators.epub import EpubGenerator
from synth_data_gen.generators.pdf import PdfGenerator
from synth_data_gen.generators.markdown import MarkdownGenerator


@pytest.fixture
def mock_config_loader_instance():
    """Fixture to provide a mocked ConfigLoader instance."""
    mock_instance = MagicMock()
    # Default return value - tests can override this
    mock_instance.load_and_validate_config.return_value = {
        "output_directory_base": "test_output",
        "global_settings": {"default_language": "en"},
        "file_types": [
            {
                "type": "epub",
                "count": 1,
                "output_subdir": "epubs",
                "epub_specific_settings": {"title": "Test EPUB"}
            }
        ]
    }
    return mock_instance


@pytest.fixture
def mock_config_loader_class(mock_config_loader_instance):
    """Fixture to patch the ConfigLoader class."""
    with patch('synth_data_gen.ConfigLoader', return_value=mock_config_loader_instance) as mock_class:
        yield mock_class


def test_generate_data_calls_config_loader_load_and_validate(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test that generate_data instantiates ConfigLoader and calls
    load_and_validate_config with correct parameters.
    """
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text("""
output_directory_base: test_output
file_types:
  - type: epub
    count: 1
    epub_specific_settings:
      title: Test EPUB
""")

    # Mock generators to prevent actual file generation
    with patch('synth_data_gen.EpubGenerator') as mock_epub_gen:
        mock_instance = mock_epub_gen.return_value
        mock_instance.get_default_specific_config.return_value = {}
        mock_instance.validate_config.return_value = True
        mock_instance.generate.return_value = "/tmp/test.epub"

        generate_data(config_path=str(config_file))

        # Assert ConfigLoader was instantiated
        mock_config_loader_class.assert_called_once()

        # Assert load_and_validate_config was called with correct parameters
        mock_config_loader_instance.load_and_validate_config.assert_called_once_with(
            file_path=str(config_file),
            config_override_object=None
        )


def test_generate_data_passes_specific_settings_to_generator(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test that generate_data extracts epub_specific_settings from file_types
    and passes it (merged with defaults) to the generator.
    """
    user_epub_settings = {"title": "Custom Title", "chapters_config": 5}

    mock_config_loader_instance.load_and_validate_config.return_value = {
        "output_directory_base": "test_output",
        "global_settings": {"default_language": "en"},
        "file_types": [
            {
                "type": "epub",
                "count": 1,
                "output_subdir": "epubs",
                "epub_specific_settings": user_epub_settings
            }
        ]
    }

    MockEpubGeneratorClass = MagicMock(spec=EpubGenerator)
    mock_epub_gen_instance = MockEpubGeneratorClass.return_value

    # Set up default config that will be merged with user settings
    default_config = {"title": "Default Title", "epub_version": "3.0", "language": "en"}
    mock_epub_gen_instance.get_default_specific_config.return_value = default_config
    mock_epub_gen_instance.validate_config.return_value = True
    mock_epub_gen_instance.generate.return_value = "/tmp/test.epub"

    test_generator_map = {"epub": MockEpubGeneratorClass}

    with patch('synth_data_gen.GENERATOR_MAP', test_generator_map):
        generate_data(config_path=str(tmp_path / "dummy.yaml"))

        # Verify generator was instantiated and called
        MockEpubGeneratorClass.assert_called_once()
        mock_epub_gen_instance.generate.assert_called_once()

        # Get the actual config passed to generate
        call_args = mock_epub_gen_instance.generate.call_args
        passed_specific_config = call_args[0][0]  # First positional arg

        # Should be merged: defaults + user settings
        # User settings override defaults
        assert passed_specific_config["title"] == "Custom Title"  # From user
        assert passed_specific_config["chapters_config"] == 5  # From user
        assert passed_specific_config["epub_version"] == "3.0"  # From defaults
        assert passed_specific_config["language"] == "en"  # From defaults


def test_generate_data_uses_defaults_when_no_specific_settings(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test that when epub_specific_settings is missing, generator's defaults are used.
    """
    mock_config_loader_instance.load_and_validate_config.return_value = {
        "output_directory_base": "test_output",
        "global_settings": {},
        "file_types": [
            {
                "type": "epub",
                "count": 1
                # No epub_specific_settings
            }
        ]
    }

    MockEpubGeneratorClass = MagicMock(spec=EpubGenerator)
    mock_epub_gen_instance = MockEpubGeneratorClass.return_value

    default_config = {"title": "Default EPUB", "epub_version": "3.0"}
    mock_epub_gen_instance.get_default_specific_config.return_value = default_config
    mock_epub_gen_instance.validate_config.return_value = True
    mock_epub_gen_instance.generate.return_value = "/tmp/test.epub"

    test_generator_map = {"epub": MockEpubGeneratorClass}

    with patch('synth_data_gen.GENERATOR_MAP', test_generator_map):
        generate_data(config_path=str(tmp_path / "dummy.yaml"))

        # Get the config passed to generate
        call_args = mock_epub_gen_instance.generate.call_args
        passed_specific_config = call_args[0][0]

        # Should be exactly the defaults
        assert passed_specific_config == default_config


def test_generate_data_end_to_end_with_mocked_generators(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test generate_data end-to-end with mocked generators for all three types.
    """
    mock_config_loader_instance.load_and_validate_config.return_value = {
        "output_directory_base": str(tmp_path / "e2e_output"),
        "global_settings": {"default_language": "fr"},
        "file_types": [
            {
                "type": "epub",
                "count": 1,
                "output_subdir": "epubs",
                "epub_specific_settings": {"title": "E2E EPUB"}
            },
            {
                "type": "pdf",
                "count": 2,
                "output_subdir": "pdfs",
                "pdf_specific_settings": {"author": "E2E PDF Author"}
            },
            {
                "type": "markdown",
                "count": 1,
                "output_subdir": "mds",
                "markdown_specific_settings": {"title": "E2E Markdown"}
            }
        ]
    }

    MockEpubGeneratorClass = MagicMock(spec=EpubGenerator)
    mock_epub_instance = MockEpubGeneratorClass.return_value
    mock_epub_instance.get_default_specific_config.return_value = {"epub_default": True}
    mock_epub_instance.validate_config.return_value = True
    mock_epub_instance.generate.return_value = str(tmp_path / "epub_1.epub")

    MockPdfGeneratorClass = MagicMock(spec=PdfGenerator)
    mock_pdf_instance = MockPdfGeneratorClass.return_value
    mock_pdf_instance.get_default_specific_config.return_value = {"pdf_default": True}
    mock_pdf_instance.validate_config.return_value = True
    mock_pdf_instance.generate.side_effect = lambda sc, gs, path: path

    MockMarkdownGeneratorClass = MagicMock(spec=MarkdownGenerator)
    mock_md_instance = MockMarkdownGeneratorClass.return_value
    mock_md_instance.get_default_specific_config.return_value = {"md_default": True}
    mock_md_instance.validate_config.return_value = True
    mock_md_instance.generate.return_value = str(tmp_path / "md_1.md")

    test_generator_map = {
        "epub": MockEpubGeneratorClass,
        "pdf": MockPdfGeneratorClass,
        "markdown": MockMarkdownGeneratorClass
    }

    with patch('synth_data_gen.GENERATOR_MAP', test_generator_map):
        generated_files = generate_data(config_path=str(tmp_path / "e2e.yaml"))

        # Verify generators were called correct number of times
        assert mock_epub_instance.generate.call_count == 1
        assert mock_pdf_instance.generate.call_count == 2
        assert mock_md_instance.generate.call_count == 1

        # Verify total files generated
        assert len(generated_files) == 4  # 1 epub + 2 pdf + 1 markdown

        # Verify correct global_settings was passed
        epub_call_args = mock_epub_instance.generate.call_args
        assert epub_call_args[0][1] == {"default_language": "fr"}  # global_settings

        # Verify specific_config was merged correctly for EPUB
        epub_specific = epub_call_args[0][0]
        assert epub_specific["title"] == "E2E EPUB"  # From user
        assert epub_specific["epub_default"] == True  # From defaults


def test_generate_data_with_config_obj_override(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test that config_obj is passed to load_and_validate_config as override.
    """
    config_override = {
        "file_types": [
            {"type": "epub", "count": 1, "epub_specific_settings": {"title": "Override Title"}}
        ]
    }

    MockEpubGeneratorClass = MagicMock(spec=EpubGenerator)
    mock_instance = MockEpubGeneratorClass.return_value
    mock_instance.get_default_specific_config.return_value = {}
    mock_instance.validate_config.return_value = True
    mock_instance.generate.return_value = "/tmp/test.epub"

    with patch('synth_data_gen.GENERATOR_MAP', {"epub": MockEpubGeneratorClass}):
        generate_data(config_obj=config_override)

        # Verify load_and_validate_config was called with config_override_object
        mock_config_loader_instance.load_and_validate_config.assert_called_once_with(
            file_path=None,
            config_override_object=config_override
        )
