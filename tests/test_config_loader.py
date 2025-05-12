import pytest
import os
import yaml
from pathlib import Path
from pytest_mock import MockerFixture

# Adjust import path as ConfigLoader is in __init__.py of the package
from synth_data_gen import ConfigLoader, InvalidConfigError

@pytest.fixture
def sample_config_file_setup():
    # Create a dummy YAML config file for testing file loading
    test_config_dir = Path("temp_test_config_dir")
    test_config_dir.mkdir(exist_ok=True)
    sample_yaml_path = test_config_dir / "sample_config.yaml"
    sample_config_data = {
        "output_directory_base": "test_output_yaml",
        "file_types": [{"type": "epub", "count": 1}]
    }
    with open(sample_yaml_path, 'w') as f:
        yaml.dump(sample_config_data, f)
    
    yield sample_yaml_path, test_config_dir # Provide paths to the test

    # Clean up the dummy config file and directory
    if sample_yaml_path.exists():
        sample_yaml_path.unlink()
    if test_config_dir.exists():
        test_config_dir.rmdir()

def test_load_from_object():
    """Test loading configuration from a dictionary object."""
    config_obj = {"key": "value", "file_types": []}
    loader = ConfigLoader(config_obj=config_obj)
    loaded_config = loader.load_config()
    assert loaded_config["key"] == "value"
    assert loader.config == config_obj

def test_load_from_yaml_file(sample_config_file_setup):
    """Test loading configuration from a YAML file."""
    sample_yaml_path, _ = sample_config_file_setup
    loader = ConfigLoader(config_path=str(sample_yaml_path))
    loaded_config = loader.load_config()
    assert loaded_config["output_directory_base"] == "test_output_yaml"
    assert len(loaded_config["file_types"]) == 1
    assert loaded_config["file_types"][0]["type"] == "epub"

def test_load_default_config():
    """Test loading default configuration when no path or object is provided."""
    loader = ConfigLoader()
    loaded_config = loader.load_config()
    assert "output_directory_base" in loaded_config
    assert loaded_config["output_directory_base"] == "synthetic_output_default"
    assert "file_types" in loaded_config
    assert isinstance(loaded_config["file_types"], list)
    assert len(loaded_config["file_types"]) > 0 # Default has epub, pdf, md

def test_file_not_found():
    """Test FileNotFoundError for a non-existent config file."""
    loader = ConfigLoader(config_path="non_existent_config.yaml")
    with pytest.raises(FileNotFoundError):
        loader.load_config()

def test_unsupported_file_type(sample_config_file_setup):
    """Test InvalidConfigError for an unsupported file type."""
    _, test_config_dir = sample_config_file_setup
    unsupported_file_path = test_config_dir / "config.txt"
    with open(unsupported_file_path, 'w') as f:
        f.write("some text")
    
    loader = ConfigLoader(config_path=str(unsupported_file_path))
    with pytest.raises(InvalidConfigError, match="Unsupported configuration file format"):
        loader.load_config()
    
    unsupported_file_path.unlink() # Clean up

def test_invalid_yaml_content(sample_config_file_setup):
    """Test InvalidConfigError for a YAML file with invalid syntax."""
    _, test_config_dir = sample_config_file_setup
    invalid_yaml_path = test_config_dir / "invalid_config.yaml"
    with open(invalid_yaml_path, 'w') as f:
        f.write("key_without_value:\n  - list_item_one\n unindented_key: value") # Invalid YAML
    
    loader = ConfigLoader(config_path=str(invalid_yaml_path))
    with pytest.raises(InvalidConfigError, match="Error parsing configuration file"):
        loader.load_config()
        
    invalid_yaml_path.unlink()

def test_validate_root_config_not_dict():
    """Test _validate_root_config raises error if root is not a dict."""
    loader = ConfigLoader()
    loader.config = "not a dictionary" # Force invalid config
    with pytest.raises(InvalidConfigError, match="Root configuration must be a dictionary."):
        loader._validate_root_config()

def test_validate_root_config_missing_file_types():
    """Test _validate_root_config raises error if 'file_types' is missing."""
    loader = ConfigLoader()
    loader.config = {"some_other_key": "value"}
    with pytest.raises(InvalidConfigError, match="'file_types' must be a list in the configuration."):
        loader._validate_root_config()

def test_validate_root_config_file_types_not_list():
    """Test _validate_root_config raises error if 'file_types' is not a list."""
    loader = ConfigLoader()
    loader.config = {"file_types": "not a list"}
    with pytest.raises(InvalidConfigError, match="'file_types' must be a list in the configuration."):
        loader._validate_root_config()
        
def test_validate_root_config_empty_file_types_list_prints_warning(mocker: MockerFixture):
    """Test _validate_root_config prints warning for empty 'file_types' list."""
    loader = ConfigLoader()
    loader.config = {"file_types": []}
    mock_print = mocker.patch('builtins.print')
    loader._validate_root_config() # Should not raise error, just print warning
    mock_print.assert_any_call("Warning: 'file_types' list is empty. No files will be generated.")