import pytest
import os
import shutil
import yaml
import jsonschema
from pathlib import Path
from pytest_mock import MockerFixture

# Adjust import path as ConfigLoader is in __init__.py of the package
from synth_data_gen import ConfigLoader, InvalidConfigError

# Define a basic schema for testing
TEST_SCHEMA = {
    "type": "object",
    "properties": {
        "output_path": {"type": "string"},
        "num_records": {"type": "number"},
        "format": {"type": "string"},
        "some_nested": { # Added for testing nested key access
            "type": "object",
            "properties": {"key": {"type": "string"}},
            "required": ["key"]
        }
    },
    "required": ["output_path", "num_records", "format"]
}

@pytest.fixture(scope="function")
def temp_config_files(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("config_data")
    
    # Valid default config
    default_config_path = temp_dir / "default_config.yaml"
    with open(default_config_path, 'w') as f:
        yaml.dump({
            'output_path': '/default/path', 
            'num_records': 100, 
            'format': 'json', 
            'some_nested': {'key': 'default_nested_value'}
        }, f)

    # Valid user config
    user_config_path = temp_dir / "user_config.yaml"
    with open(user_config_path, 'w') as f:
        yaml.dump({'output_path': '/user/path', 'num_records': 200, 'format': 'user_format'}, f) # Added format

    # Invalid user config (schema violation)
    invalid_config_path = temp_dir / "invalid_config.yaml"
    with open(invalid_config_path, 'w') as f:
        yaml.dump({'output_path': 123, 'num_records': 'not_a_number', 'format': 'bad_format'}, f)

    # Empty user config
    empty_config_path = temp_dir / "empty_config.yaml"
    with open(empty_config_path, 'w') as f:
        pass # Creates an empty file

    # Invalid default config (for a specific test)
    invalid_default_config_path = temp_dir / "invalid_default.yaml"
    with open(invalid_default_config_path, 'w') as f:
        yaml.dump({'output_path': 123, 'num_records': 'bad', 'format': 'also_bad'}, f) # schema violation

    yield {
        "default": default_config_path,
        "user": user_config_path,
        "invalid_user": invalid_config_path,
        "empty_user": empty_config_path,
        "invalid_default": invalid_default_config_path,
        "dir": temp_dir
    }

@pytest.fixture
def sample_config_file_setup(temp_config_files):
    test_config_dir = temp_config_files["dir"]
    sample_yaml_path = test_config_dir / "sample_config.yaml"
    sample_config_data = {
        "output_directory_base": "test_output_yaml",
        "file_types": [{"type": "epub", "count": 1}]
    }
    with open(sample_yaml_path, 'w') as f:
        yaml.dump(sample_config_data, f)
    yield sample_yaml_path, test_config_dir


def test_load_from_object():
    """Test loading configuration from a dictionary object."""
    config_obj = {"key": "value", "file_types": [], "output_path": "/obj", "num_records": 1, "format": "obj_fmt"}
    loader = ConfigLoader()
    loaded_config = loader.load_and_validate_config(config_override_object=config_obj, schema=TEST_SCHEMA)
    assert loaded_config["key"] == "value"
    assert loaded_config["output_path"] == "/obj"


def test_load_from_yaml_file(sample_config_file_setup):
    """Test loading configuration from a YAML file."""
    sample_yaml_path, _ = sample_config_file_setup
    loader = ConfigLoader()
    # This test used a schema-less load before, but load_and_validate_config implies validation
    # For it to pass without a schema or with a schema that matches sample_config.yaml, adjust accordingly.
    # Assuming sample_config.yaml is not meant to be validated against TEST_SCHEMA here.
    loaded_config = loader.load_config(file_path=str(sample_yaml_path)) # Test load_config directly
    assert loaded_config["output_directory_base"] == "test_output_yaml"
    assert len(loaded_config["file_types"]) == 1


def test_load_default_config(mocker: MockerFixture, temp_config_files):
    """Test loading default configuration when no path or object is provided."""
    # Mock the class attribute DEFAULT_CONFIG_PATH that the constructor uses
    mocker.patch.object(ConfigLoader, 'DEFAULT_CONFIG_PATH', str(temp_config_files["default"]))
    
    loader = ConfigLoader() # Constructor will now use the mocked DEFAULT_CONFIG_PATH
    loaded_config = loader.load_and_validate_config(schema=TEST_SCHEMA)
    assert loaded_config['output_path'] == '/default/path'
    assert loaded_config['num_records'] == 100
    assert loaded_config['format'] == 'json'


def test_file_not_found(temp_config_files):
    """Test FileNotFoundError for a non-existent config file."""
    loader = ConfigLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_and_validate_config(file_path=str(temp_config_files["dir"] / "non_existent_config.yaml"))


def test_unsupported_file_type(temp_config_files):
    """Test InvalidConfigError for an unsupported file type."""
    unsupported_file_path = temp_config_files["dir"] / "unsupported.txt"
    with open(unsupported_file_path, 'w') as f:
        f.write("some text")
    loader = ConfigLoader()
    with pytest.raises(InvalidConfigError, match="Unsupported configuration file format"):
        loader.load_config(file_path=str(unsupported_file_path))


def test_invalid_yaml_content(temp_config_files):
    """Test InvalidConfigError for a YAML file with invalid syntax."""
    invalid_yaml_path = temp_config_files["dir"] / "invalid_syntax.yaml"
    with open(invalid_yaml_path, 'w') as f:
        # This YAML is malformed due to an unclosed string quote
        f.write("key: 'unclosed_string")
    loader = ConfigLoader()
    with pytest.raises(InvalidConfigError, match="Error parsing configuration file"):
        loader.load_config(file_path=str(invalid_yaml_path))
        

def test_load_and_validate_config_user_only_valid(temp_config_files):
    loader = ConfigLoader() # No default path specified
    config = loader.load_and_validate_config(str(temp_config_files["user"]), schema=TEST_SCHEMA)
    assert config['output_path'] == '/user/path'
    assert config['num_records'] == 200
    assert config['format'] == 'user_format'


def test_load_and_validate_config_default_and_user_valid(temp_config_files):
    loader = ConfigLoader(default_config_path=str(temp_config_files["default"]))
    config = loader.load_and_validate_config(str(temp_config_files["user"]), schema=TEST_SCHEMA)
    assert config['output_path'] == '/user/path' 
    assert config['num_records'] == 200       
    assert config['format'] == 'user_format' # User's format should take precedence


def test_load_and_validate_config_default_only_valid(temp_config_files):
    loader = ConfigLoader(default_config_path=str(temp_config_files["default"]))
    config = loader.load_and_validate_config(schema=TEST_SCHEMA)
    assert config['output_path'] == '/default/path'
    assert config['num_records'] == 100
    assert config['format'] == 'json'

def test_load_and_validate_config_user_invalid_schema(temp_config_files):
    loader = ConfigLoader()
    with pytest.raises(jsonschema.exceptions.ValidationError):
        loader.load_and_validate_config(str(temp_config_files["invalid_user"]), schema=TEST_SCHEMA)

def test_load_and_validate_config_default_invalid_schema(temp_config_files):
    loader = ConfigLoader(default_config_path=str(temp_config_files["invalid_default"]))
    with pytest.raises(jsonschema.exceptions.ValidationError):
        loader.load_and_validate_config(schema=TEST_SCHEMA)

def test_load_and_validate_config_file_not_found(temp_config_files):
    loader = ConfigLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_and_validate_config(str(temp_config_files["dir"] / "non_existent_config.yaml"), schema=TEST_SCHEMA)

def test_load_and_validate_config_empty_user_file(temp_config_files):
    loader = ConfigLoader(default_config_path=str(temp_config_files["default"]))
    # Empty user file means default config should be used, then validated.
    config = loader.load_and_validate_config(str(temp_config_files["empty_user"]), schema=TEST_SCHEMA)
    assert config['output_path'] == '/default/path'
    assert config['num_records'] == 100
    assert config['format'] == 'json'


def test_load_and_validate_config_no_file_no_default_no_override(mocker: MockerFixture, temp_config_files):
    # Mock os.path.exists to simulate no default config file being found
    # Also ensure the instance's default_config_path is set to something that would trigger this check
    mocker.patch('os.path.exists', return_value=False)
    
    # Patch the class attribute as well, so the constructor picks up a non-existent path if it relies on it
    # and os.path.exists is mocked.
    mocker.patch.object(ConfigLoader, 'DEFAULT_CONFIG_PATH', str(temp_config_files["dir"] / "non_existent_default.yaml"))

    loader = ConfigLoader(default_config_path=str(temp_config_files["dir"] / "non_existent_default.yaml")) 
    
    with pytest.raises(FileNotFoundError, match="No configuration could be loaded or constructed"): 
        loader.load_and_validate_config(schema=TEST_SCHEMA)

def test_load_and_validate_config_with_override(temp_config_files):
    loader = ConfigLoader(default_config_path=str(temp_config_files["default"]))
    override_obj = {'num_records': 500, 'new_param': 'test', 'format': 'override_format'}
    config = loader.load_and_validate_config(
        str(temp_config_files["user"]), 
        schema=TEST_SCHEMA, 
        config_override_object=override_obj
    )
    assert config['output_path'] == '/user/path' 
    assert config['num_records'] == 500       
    assert config['format'] == 'override_format' 
    assert config['new_param'] == 'test'       

def test_load_and_validate_config_override_only(temp_config_files):
    loader = ConfigLoader()
    override_obj = {'output_path': '/override/path', 'num_records': 300, 'format': 'xml'}
    config = loader.load_and_validate_config(
        schema=TEST_SCHEMA, 
        config_override_object=override_obj
    )
    assert config['output_path'] == '/override/path'
    assert config['num_records'] == 300
    assert config['format'] == 'xml'

def test_load_and_validate_config_override_empty_user_file(temp_config_files):
    loader = ConfigLoader(default_config_path=str(temp_config_files["default"]))
    override_obj = {'output_path': '/override/path', 'num_records': 700, 'format': 'csv'}
    config = loader.load_and_validate_config(
        str(temp_config_files["empty_user"]), 
        schema=TEST_SCHEMA, 
        config_override_object=override_obj
    )
    assert config['output_path'] == '/override/path'
    assert config['num_records'] == 700
    assert config['format'] == 'csv'

def test_load_and_validate_config_override_non_existent_user_file(temp_config_files):
    loader = ConfigLoader(default_config_path=str(temp_config_files["default"]))
    override_obj = {'output_path': '/override/path', 'num_records': 800, 'format': 'txt'}
    with pytest.raises(FileNotFoundError):
        loader.load_and_validate_config(
            str(temp_config_files["dir"] / "non_existent_user_config.yaml"), 
            schema=TEST_SCHEMA, 
            config_override_object=override_obj
        )

def test_load_and_validate_config_no_user_file_with_override_and_default(temp_config_files):
    loader = ConfigLoader(default_config_path=str(temp_config_files["default"]))
    override_obj = {'num_records': 900, 'format': 'bin'}
    config = loader.load_and_validate_config(
        file_path=None, 
        schema=TEST_SCHEMA, 
        config_override_object=override_obj
    )
    assert config['output_path'] == '/default/path' 
    assert config['num_records'] == 900       
    assert config['format'] == 'bin'          

def test_check_nested_key_in_loaded_config(temp_config_files):
    loader = ConfigLoader(default_config_path=str(temp_config_files["default"]))
    config = loader.load_and_validate_config(schema=TEST_SCHEMA) 
    assert config['some_nested']['key'] == 'default_nested_value'
