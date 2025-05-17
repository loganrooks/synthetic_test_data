import pytest
from unittest.mock import patch, MagicMock

from synth_data_gen import generate_data
from synth_data_gen.generators.epub import EpubGenerator # Import EpubGenerator
# Assuming ConfigLoader will be imported in synth_data_gen.__init__
# from synth_data_gen.core.config_loader import ConfigLoader

# A simple schema for testing
SIMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "project_name": {"type": "string"},
        "output_directory": {"type": "string"},
        "file_types": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["project_name", "output_directory", "file_types"]
}

@pytest.fixture
def mock_config_loader_instance():
    """Fixture to provide a mocked ConfigLoader instance."""
    mock_instance = MagicMock()
    mock_instance.load_and_validate_config.return_value = {
        "project_name": "TestProject",
        "output_directory": "test_output",
        "file_types": [
            {"type": "epub", "count": 1, "output_subdir": "epubs", "epub_specific_settings": {"title": "Test EPUB"}},
            {"type": "pdf", "count": 1, "output_subdir": "pdfs", "pdf_specific_settings": {"author": "Test PDF Author"}}
        ],
        # The generator-specific settings are now part of the file_types items
        # So, we don't need separate top-level epub_settings and pdf_settings here
        # for the mock load_and_validate_config.
        # However, get_generator_config will still need to extract them from the main loaded config.
        # The main `config` object that `get_generator_config` receives will be the one above.
    }
    # Adjusting get_generator_config mock to reflect that generator settings are nested
    # within the main config, typically under keys like "epub_settings", "pdf_settings" etc.
    # The test's `generate_data` will call `loader.get_generator_config(config, "epub")`
    # So, the mock should look for "epub_settings" in the `config` passed to it.
    # The `config` passed to it will be the one returned by `load_and_validate_config`.
    # Let's make the mock config simpler for get_generator_config to work with the test structure
    # The actual config loaded by ConfigLoader will have these nested.
    # The test calls generate_data -> which calls loader.load_and_validate_config (returns the above)
    # -> then calls loader.get_generator_config(returned_config, "epub")
    
    # Simpler approach for the mock:
    # The mock_config_loader_instance.load_and_validate_config.return_value IS the 'full_config'
    # that get_generator_config will receive.
    # So, the side_effect should extract from that structure.
    
    # Let's refine the return_value of load_and_validate_config to include top-level settings
    # that get_generator_config would expect, based on how ConfigLoader is implemented.
    # The ConfigLoader.get_generator_config(self, full_config, generator_id)
    # expects full_config to have keys like 'epub_settings', 'pdf_settings'.
    
    # Corrected mock return value for load_and_validate_config
    mock_instance.load_and_validate_config.return_value = {
        "project_name": "TestProject",
        "output_directory": "test_output",
        "file_types": [ # This is what generate_data iterates over
            {"type": "epub", "count": 1, "output_subdir": "epubs"},
            {"type": "pdf", "count": 1, "output_subdir": "pdfs"}
        ],
        # These are the top-level sections ConfigLoader.get_generator_config expects
        "epub_settings": {"title": "Test EPUB From Mock"},
        "pdf_settings": {"author": "Test PDF Author From Mock"}
    }

    mock_instance.get_generator_config.side_effect = lambda conf, gen_id: conf.get(f"{gen_id}_settings", {})
    return mock_instance

@pytest.fixture
def mock_config_loader_class(mock_config_loader_instance):
    """Fixture to patch the ConfigLoader class."""
    with patch('synth_data_gen.ConfigLoader', return_value=mock_config_loader_instance) as mock_class:
        yield mock_class

def test_generate_data_calls_config_loader_load_and_validate(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test that generate_data instantiates ConfigLoader and calls
    load_and_validate_config with the correct config_path and schema.
    """
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text("""
project_name: TestProject
output_directory: test_output
file_types:
  - epub
  - pdf
epub_settings:
  title: Test EPUB
pdf_settings:
  author: Test PDF Author
""")
    
    # Mock individual generators to prevent actual file generation
    with patch('synth_data_gen.EpubGenerator') as mock_epub_gen, \
         patch('synth_data_gen.PdfGenerator') as mock_pdf_gen, \
         patch('synth_data_gen.MarkdownGenerator') as mock_md_gen:

        generate_data(config_path=str(config_file))

        # Assert ConfigLoader was instantiated with the default schema path
        # This part of the assertion might need adjustment based on how ConfigLoader
        # actually gets its schema (e.g., if it's hardcoded or passed differently)
        # For now, we assume it's instantiated and then load_and_validate_config is called.
        mock_config_loader_class.assert_called_once() 
        
        # Assert load_and_validate_config was called with the correct path
        # If ConfigLoader uses an internal default schema when schema is None,
        # the call from generate_data might not explicitly pass schema=None.
        # The mock should expect the call as it's made by the SUT.
        mock_config_loader_instance.load_and_validate_config.assert_called_once_with(
            config_path=str(config_file) # Schema is not passed if default is used
        )

def test_generate_data_dispatches_epub_config_correctly(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test that generate_data calls get_generator_config for 'epub'
    and passes the result to EpubGenerator.
    """
    config_file = tmp_path / "test_config_epub_dispatch.yaml"
    config_file.write_text("""
project_name: EpubDispatchTest
output_directory: epub_dispatch_output
file_types:
  - type: epub
    count: 1
# epub_settings are at the top level of the loaded config in the mock
epub_settings:
  title: "Dispatched EPUB Title"
  author: "Dispatched Author"
""")

    # The mock_config_loader_instance.load_and_validate_config.return_value is already set up
    # in the fixture to include "epub_settings".
    # The mock_config_loader_instance.get_generator_config side_effect will use this.
    
    expected_epub_config = {"title": "Test EPUB From Mock", "author": "Dispatched Author"} # This should match what get_generator_config returns
    # Update expected_epub_config to match the mock_config_loader_instance setup
    expected_epub_config = mock_config_loader_instance.load_and_validate_config.return_value["epub_settings"]

    MockEpubGeneratorClass = MagicMock(spec=EpubGenerator) # Use the actual class for spec if available
    mock_epub_generator_instance = MockEpubGeneratorClass.return_value

    # Patch the GENERATOR_MAP directly for this test
    # Need to import EpubGenerator, PdfGenerator, MarkdownGenerator if they are part of the original map
    # For this specific test, we only care about 'epub' being mocked.
    
    original_generator_map = {}
    try:
        # Attempt to import the original map to preserve other generators if needed
        # This import might fail if the test environment is tricky, so guard it.
        from synth_data_gen import GENERATOR_MAP as SUT_GENERATOR_MAP
        original_generator_map = SUT_GENERATOR_MAP.copy()
    except ImportError:
        # Fallback if direct import is an issue in test setup,
        # though for this test, we only need to ensure 'epub' is our mock.
        # This might mean other generators won't be in the map if not explicitly added.
        pass

    test_generator_map = original_generator_map.copy()
    test_generator_map["epub"] = MockEpubGeneratorClass
    
    # Patch where EpubGenerator is defined and also where it's used in the map
    with patch('synth_data_gen.generators.epub.EpubGenerator', MockEpubGeneratorClass), \
         patch('synth_data_gen.GENERATOR_MAP', test_generator_map):
        
        generate_data(config_path=str(config_file))

        mock_config_loader_instance.get_generator_config.assert_any_call(
            mock_config_loader_instance.load_and_validate_config.return_value,
            "epub"
        )
        
        # Check that EpubGenerator was instantiated and its generate method was called
        # with the specific config.
        MockEpubGeneratorClass.assert_called_once()
        mock_epub_generator_instance.generate.assert_called_once()
        
        # Get the actual arguments passed to the generate method
        actual_call_args = mock_epub_generator_instance.generate.call_args
        assert actual_call_args is not None, "EpubGenerator.generate was not called"
        
        # The generate method signature is generate(self, specific_config, global_settings, output_file_path)
        # So, the specific_config is the first positional argument (index 0)
        # or the 'specific_config' keyword argument.
        
        passed_specific_config = None
        if actual_call_args.args:
            passed_specific_config = actual_call_args.args[0]
        elif 'specific_config' in actual_call_args.kwargs:
            passed_specific_config = actual_call_args.kwargs['specific_config']
            
        assert passed_specific_config == expected_epub_config, \
            f"EpubGenerator.generate called with incorrect specific_config. Expected {expected_epub_config}, got {passed_specific_config}"

def test_generate_data_handles_missing_epub_config_gracefully(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test that if 'epub_settings' is missing from the main config,
    EpubGenerator is still called, and it likely receives an empty dict or its defaults.
    The SUT's `generate_data` should ensure `get_generator_config` is called,
    and if it returns empty, the generator's own default logic should kick in.
    """
    config_file = tmp_path / "test_config_no_epub_settings.yaml"
    config_file.write_text("""
project_name: NoEpubSettingsTest
output_directory: no_epub_settings_output
file_types:
  - type: epub # We still ask for an epub
    count: 1
# Note: no epub_settings section here
pdf_settings:
  author: "Some PDF Author"
""")

    # Adjust the mock_config_loader_instance for this test case:
    # load_and_validate_config should return a config *without* 'epub_settings'
    # get_generator_config for 'epub' should then return {}
    
    config_without_epub_settings = {
        "project_name": "NoEpubSettingsTest",
        "output_directory": "no_epub_settings_output",
        "file_types": [{"type": "epub", "count": 1}],
        "pdf_settings": {"author": "Some PDF Author"}
        # "epub_settings" is deliberately missing
    }
    mock_config_loader_instance.load_and_validate_config.return_value = config_without_epub_settings
    
    # get_generator_config for 'epub' will return {} due to the side_effect and missing key
    # The generator's own get_default_specific_config() should be used by generate_data
    
    # We need to know what EpubGenerator's default config is to assert it's passed.
    # For now, let's assume the SUT will pass an empty dict if get_generator_config returns empty,
    # and the generator itself handles merging with its internal defaults.
    # Or, the SUT (generate_data) will call generator_instance.get_default_specific_config().
    # The current SUT logic:
    # specific_config = loader.get_generator_config(config, generator_type_str.lower())
    # if not specific_config:
    #     specific_config = generator_instance.get_default_specific_config()
    
    # So, we expect generator_instance.get_default_specific_config() to be called and its result passed.
    
    MockEpubGeneratorClass = MagicMock(spec=EpubGenerator)
    mock_epub_generator_instance = MockEpubGeneratorClass.return_value
    
    # Mock the default config that EpubGenerator would return
    default_epub_specific_config = {"title": "Default EPUB Title", "epub_version": "3.0"}
    mock_epub_generator_instance.get_default_specific_config.return_value = default_epub_specific_config

    test_generator_map = {"epub": MockEpubGeneratorClass} # Keep it simple for this test

    with patch('synth_data_gen.generators.epub.EpubGenerator', MockEpubGeneratorClass), \
         patch('synth_data_gen.GENERATOR_MAP', test_generator_map):

        generate_data(config_path=str(config_file))

        mock_config_loader_instance.get_generator_config.assert_any_call(
            config_without_epub_settings,
            "epub"
        )
        MockEpubGeneratorClass.assert_called_once() # Generator class instantiated
        mock_epub_generator_instance.get_default_specific_config.assert_called_once() # Default config method called
        
        # Assert that generate method was called with the default specific config
        mock_epub_generator_instance.generate.assert_called_once()
        actual_call_args = mock_epub_generator_instance.generate.call_args
        assert actual_call_args is not None
        
        passed_specific_config = None
        if actual_call_args.args:
            passed_specific_config = actual_call_args.args[0]
        elif 'specific_config' in actual_call_args.kwargs:
            passed_specific_config = actual_call_args.kwargs['specific_config']
            
        assert passed_specific_config == default_epub_specific_config, \
            f"EpubGenerator.generate called with incorrect specific_config when main config section is missing. Expected defaults {default_epub_specific_config}, got {passed_specific_config}"

def test_generate_data_end_to_end_with_mocked_generators(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test generate_data end-to-end with mocked generators, focusing on config flow.
    It verifies that ConfigLoader is used, and specific configs are passed to generators.
    """
    config_content = """
project_name: EndToEndTest
output_directory: e2e_output
file_types:
  - type: epub
    count: 1
    output_subdir: epubs
  - type: pdf
    count: 2
    output_subdir: pdfs
    # pdf_specific_settings are NOT in file_types, they are top-level in the loaded config
  - type: markdown # No specific settings for markdown in this test config
    count: 1
    output_subdir: mds

global_settings:
  default_language: "fr"

epub_settings:
  title: "E2E EPUB Title"
  epub_version: "2.0"

pdf_settings:
  author: "E2E PDF Author"
  page_size: "A4"
"""
    config_file = tmp_path / "e2e_test_config.yaml"
    config_file.write_text(config_content)

    # Configure the mock ConfigLoader instance for this test
    loaded_config_for_e2e = {
        "project_name": "EndToEndTest",
        "output_directory_base": "e2e_output", # Corrected key
        "file_types": [
            {"type": "epub", "count": 1, "output_subdir": "epubs"},
            {"type": "pdf", "count": 2, "output_subdir": "pdfs"},
            {"type": "markdown", "count": 1, "output_subdir": "mds"}
        ],
        "global_settings": {"default_language": "fr"},
        "epub_settings": {"title": "E2E EPUB Title", "epub_version": "2.0"},
        "pdf_settings": {"author": "E2E PDF Author", "page_size": "A4"},
        # Markdown settings will be empty from get_generator_config,
        # so generator's default will be used.
    }
    mock_config_loader_instance.load_and_validate_config.return_value = loaded_config_for_e2e
    # get_generator_config side_effect is already set up in the fixture

    # Expected specific configs
    expected_epub_specific_config = loaded_config_for_e2e["epub_settings"]
    expected_pdf_specific_config = loaded_config_for_e2e["pdf_settings"]
    # For markdown, get_generator_config will return {}, so its default will be used.
    
    MockEpubGeneratorClass = MagicMock(spec=EpubGenerator)
    mock_epub_gen_instance = MockEpubGeneratorClass.return_value
    mock_epub_gen_instance.get_default_specific_config.return_value = {"default_epub": True} # Dummy default
    mock_epub_gen_instance.generate.return_value = "path/to/epub_1.epub"

    MockPdfGeneratorClass = MagicMock() # spec=PdfGenerator (need to import PdfGenerator)
    mock_pdf_gen_instance = MockPdfGeneratorClass.return_value
    mock_pdf_gen_instance.get_default_specific_config.return_value = {"default_pdf": True}
    mock_pdf_gen_instance.generate.side_effect = lambda sc, gs, op: op # Return output path

    MockMarkdownGeneratorClass = MagicMock() # spec=MarkdownGenerator (need to import MarkdownGenerator)
    mock_md_gen_instance = MockMarkdownGeneratorClass.return_value
    expected_md_default_config = {"default_markdown": True, "another_setting": "value"}
    mock_md_gen_instance.get_default_specific_config.return_value = expected_md_default_config
    mock_md_gen_instance.generate.return_value = "path/to/md_1.md"

    test_generator_map = {
        "epub": MockEpubGeneratorClass,
        "pdf": MockPdfGeneratorClass,
        "markdown": MockMarkdownGeneratorClass
    }

    with patch('synth_data_gen.generators.epub.EpubGenerator', MockEpubGeneratorClass), \
         patch('synth_data_gen.generators.pdf.PdfGenerator', MockPdfGeneratorClass), \
         patch('synth_data_gen.generators.markdown.MarkdownGenerator', MockMarkdownGeneratorClass), \
         patch('synth_data_gen.GENERATOR_MAP', test_generator_map):

        generated_files = generate_data(config_path=str(config_file))

        # Verify ConfigLoader calls
        mock_config_loader_class.assert_called_once()
        mock_config_loader_instance.load_and_validate_config.assert_called_once_with(config_path=str(config_file))
        
        mock_config_loader_instance.get_generator_config.assert_any_call(loaded_config_for_e2e, "epub")
        mock_config_loader_instance.get_generator_config.assert_any_call(loaded_config_for_e2e, "pdf")
        mock_config_loader_instance.get_generator_config.assert_any_call(loaded_config_for_e2e, "markdown")

        # Verify EpubGenerator
        MockEpubGeneratorClass.assert_called_once()
        mock_epub_gen_instance.generate.assert_called_once()
        epub_args, _ = mock_epub_gen_instance.generate.call_args
        assert epub_args[0] == expected_epub_specific_config
        assert epub_args[1] == loaded_config_for_e2e["global_settings"]
        assert "e2e_output/epubs/epub_1.epub" in epub_args[2] # Check output path

        # Verify PdfGenerator (called twice)
        assert MockPdfGeneratorClass.call_count == 1 # Instantiated once
        assert mock_pdf_gen_instance.generate.call_count == 2
        pdf_call_args_list = mock_pdf_gen_instance.generate.call_args_list
        
        # Call 1 for PDF
        pdf_args_1, _ = pdf_call_args_list[0]
        assert pdf_args_1[0] == expected_pdf_specific_config
        assert pdf_args_1[1] == loaded_config_for_e2e["global_settings"]
        assert "e2e_output/pdfs/pdf_1.pdf" in pdf_args_1[2]
        
        # Call 2 for PDF
        pdf_args_2, _ = pdf_call_args_list[1]
        assert pdf_args_2[0] == expected_pdf_specific_config # Same specific config
        assert pdf_args_2[1] == loaded_config_for_e2e["global_settings"]
        assert "e2e_output/pdfs/pdf_2.pdf" in pdf_args_2[2]

        # Verify MarkdownGenerator
        MockMarkdownGeneratorClass.assert_called_once()
        mock_md_gen_instance.get_default_specific_config.assert_called_once() # Because markdown_settings is missing
        mock_md_gen_instance.generate.assert_called_once()
        md_args, _ = mock_md_gen_instance.generate.call_args
        assert md_args[0] == expected_md_default_config # Should use its default
        assert md_args[1] == loaded_config_for_e2e["global_settings"]
        assert "e2e_output/mds/markdown_1.md" in md_args[2]
        
        assert len(generated_files) == 4 # 1 epub, 2 pdf, 1 md
        assert "path/to/epub_1.epub" in generated_files
        assert "e2e_output/pdfs/pdf_1.pdf" in generated_files # Since generate returns output_path
        assert "e2e_output/pdfs/pdf_2.pdf" in generated_files
        assert "path/to/md_1.md" in generated_files

# def test_generate_data_dispatches_pdf_config_correctly():
#     pass