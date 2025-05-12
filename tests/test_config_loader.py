import unittest
import os
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

# Adjust import path as ConfigLoader is in __init__.py of the package
from synth_data_gen import ConfigLoader, InvalidConfigError

class TestConfigLoader(unittest.TestCase):

    def setUp(self):
        # Create a dummy YAML config file for testing file loading
        self.test_config_dir = Path("temp_test_config_dir")
        self.test_config_dir.mkdir(exist_ok=True)
        self.sample_yaml_path = self.test_config_dir / "sample_config.yaml"
        self.sample_config_data = {
            "output_directory_base": "test_output_yaml",
            "file_types": [{"type": "epub", "count": 1}]
        }
        with open(self.sample_yaml_path, 'w') as f:
            yaml.dump(self.sample_config_data, f)

    def tearDown(self):
        # Clean up the dummy config file and directory
        if self.sample_yaml_path.exists():
            self.sample_yaml_path.unlink()
        if self.test_config_dir.exists():
            self.test_config_dir.rmdir()

    def test_load_from_object(self):
        """Test loading configuration from a dictionary object."""
        config_obj = {"key": "value", "file_types": []}
        loader = ConfigLoader(config_obj=config_obj)
        loaded_config = loader.load_config()
        self.assertEqual(loaded_config["key"], "value")
        self.assertEqual(loader.config, config_obj)

    def test_load_from_yaml_file(self):
        """Test loading configuration from a YAML file."""
        loader = ConfigLoader(config_path=str(self.sample_yaml_path))
        loaded_config = loader.load_config()
        self.assertEqual(loaded_config["output_directory_base"], "test_output_yaml")
        self.assertEqual(len(loaded_config["file_types"]), 1)
        self.assertEqual(loaded_config["file_types"][0]["type"], "epub")

    def test_load_default_config(self):
        """Test loading default configuration when no path or object is provided."""
        loader = ConfigLoader()
        loaded_config = loader.load_config()
        self.assertIn("output_directory_base", loaded_config)
        self.assertEqual(loaded_config["output_directory_base"], "synthetic_output_default")
        self.assertIn("file_types", loaded_config)
        self.assertTrue(isinstance(loaded_config["file_types"], list))
        self.assertTrue(len(loaded_config["file_types"]) > 0) # Default has epub, pdf, md

    def test_file_not_found(self):
        """Test FileNotFoundError for a non-existent config file."""
        loader = ConfigLoader(config_path="non_existent_config.yaml")
        with self.assertRaises(FileNotFoundError):
            loader.load_config()

    def test_unsupported_file_type(self):
        """Test InvalidConfigError for an unsupported file type."""
        unsupported_file_path = self.test_config_dir / "config.txt"
        with open(unsupported_file_path, 'w') as f:
            f.write("some text")
        
        loader = ConfigLoader(config_path=str(unsupported_file_path))
        with self.assertRaisesRegex(InvalidConfigError, "Unsupported configuration file format"):
            loader.load_config()
        
        unsupported_file_path.unlink() # Clean up

    def test_invalid_yaml_content(self):
        """Test InvalidConfigError for a YAML file with invalid syntax."""
        invalid_yaml_path = self.test_config_dir / "invalid_config.yaml"
        with open(invalid_yaml_path, 'w') as f:
            f.write("key_without_value:\n  - list_item_one\n unindented_key: value") # Invalid YAML
        
        loader = ConfigLoader(config_path=str(invalid_yaml_path))
        with self.assertRaisesRegex(InvalidConfigError, "Error parsing configuration file"):
            loader.load_config()
            
        invalid_yaml_path.unlink()

    def test_validate_root_config_not_dict(self):
        """Test _validate_root_config raises error if root is not a dict."""
        loader = ConfigLoader()
        loader.config = "not a dictionary" # Force invalid config
        with self.assertRaisesRegex(InvalidConfigError, "Root configuration must be a dictionary."):
            loader._validate_root_config()

    def test_validate_root_config_missing_file_types(self):
        """Test _validate_root_config raises error if 'file_types' is missing."""
        loader = ConfigLoader()
        loader.config = {"some_other_key": "value"}
        with self.assertRaisesRegex(InvalidConfigError, "'file_types' must be a list in the configuration."):
            loader._validate_root_config()

    def test_validate_root_config_file_types_not_list(self):
        """Test _validate_root_config raises error if 'file_types' is not a list."""
        loader = ConfigLoader()
        loader.config = {"file_types": "not a list"}
        with self.assertRaisesRegex(InvalidConfigError, "'file_types' must be a list in the configuration."):
            loader._validate_root_config()
            
    def test_validate_root_config_empty_file_types_list_prints_warning(self):
        """Test _validate_root_config prints warning for empty 'file_types' list."""
        loader = ConfigLoader()
        loader.config = {"file_types": []}
        with patch('builtins.print') as mock_print:
            loader._validate_root_config() # Should not raise error, just print warning
            mock_print.assert_any_call("Warning: 'file_types' list is empty. No files will be generated.")


if __name__ == '__main__':
    unittest.main()