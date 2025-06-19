"""
Configuration Loader for the Synthetic Data Generation package.
"""
from typing import Optional
import yaml
import jsonschema
from jsonschema import ValidationError
import os
import copy
import sys

# Define InvalidConfigError here to avoid circular imports
class InvalidConfigError(ValueError):
    """Raised when a configuration is invalid."""
    pass

class ConfigLoader:
    """
    Loads, validates, and merges YAML configuration files.
    """
    DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "default_config.yaml")

    def __init__(self, default_config_path: Optional[str] = None):
        if default_config_path is not None:
            self.default_config_path = default_config_path
        else:
            self.default_config_path = self.DEFAULT_CONFIG_PATH

    def _load_single_config_file(self, file_path: str) -> dict:
        """Loads a single YAML config file.
        Raises FileNotFoundError if not found, or yaml.YAMLError for syntax issues.
        Returns an empty dict if the YAML file is valid but empty."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found at {file_path}")

        # Check if the file has a valid extension
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() not in ['.yaml', '.yml', '.json']:
            raise InvalidConfigError(f"Unsupported configuration file format: {file_extension}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data if data is not None else {}
        except yaml.YAMLError as e:
            raise InvalidConfigError(f"Error parsing configuration file: {file_path}. Details: {e}")
        except Exception as e:
            raise InvalidConfigError(f"Error loading configuration file: {file_path}. Details: {e}")

    def load_config(self, file_path: str) -> dict:
        """
        Strictly loads a configuration from the given file_path.
        No default loading or merging occurs in this method.
        """
        return self._load_single_config_file(file_path)

    def get_default_config(self) -> dict:
        """
        Loads the default configuration file.
        Returns an empty dict if the default config is not found or is invalid/empty.
        """
        if self.default_config_path and os.path.exists(self.default_config_path):
            try:
                return self._load_single_config_file(self.default_config_path)
            except Exception as e:
                print(f"Error loading default config: {e}")
                return {}
        return {}

    def _merge_configs(self, base_config: dict, override_config: dict) -> dict:
        """
        Recursively merges two dictionaries. `override` takes precedence.
        Lists in `override` replace lists in `base`.
        """
        merged = copy.deepcopy(base_config)
        for key, value in override_config.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged

    def load_and_validate_config(self, file_path: Optional[str] = None, schema: Optional[dict] = None, config_override_object: Optional[dict] = None) -> dict:
        """Loads configuration, merges with defaults/overrides, and validates against a schema."""
        default_config = None
        default_config_loaded_successfully = False # Flag to track if default config load was attempted and did not error
        if self.default_config_path and os.path.exists(self.default_config_path):
            try:
                default_config = self.load_config(self.default_config_path)
                default_config_loaded_successfully = True # Loaded without raising an exception
            except Exception as e:
                print(f"Warning: Could not load default config from {self.default_config_path}: {e}", file=sys.stderr)
                # default_config remains None, default_config_loaded_successfully remains False

        user_config = None
        user_config_loaded_successfully = False
        if file_path:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Configuration file not found: {file_path}")
            try:
                user_config = self.load_config(file_path)
                user_config_loaded_successfully = True
            except Exception as e:
                raise ValueError(f"Error loading configuration file {file_path}: {e}")

        effective_config = {}
        # Start with default config if it was loaded successfully
        if default_config_loaded_successfully and default_config:
            effective_config = copy.deepcopy(default_config)
        
        # Merge user_config if it was loaded successfully
        if user_config_loaded_successfully and user_config:
            if effective_config: # if default_config was the base
                effective_config = self._merge_configs(effective_config, user_config)
            else: # if no default_config or it was empty/None
                effective_config = copy.deepcopy(user_config)
        elif user_config: # User config was provided but default was not (or not successfully loaded)
             effective_config = copy.deepcopy(user_config) # Should have been handled by previous block, but as a safeguard

        # Apply override object if provided
        if config_override_object:
            if effective_config: 
                effective_config = self._merge_configs(effective_config, config_override_object)
            else: 
                effective_config = copy.deepcopy(config_override_object)

        if not effective_config: # This means no configuration source yielded a non-empty config
            error_message = "No configuration could be loaded or constructed. "
            if file_path and not user_config_loaded_successfully:
                error_message += f"User specified config file '{file_path}' failed to load or was empty. "
            if self.default_config_path and not default_config_loaded_successfully:
                error_message += f"Default config '{self.default_config_path}' failed to load. "
            elif self.default_config_path and default_config_loaded_successfully and not default_config:
                error_message += f"Default config '{self.default_config_path}' was loaded but was empty. "
            
            if not file_path and not config_override_object and not (self.default_config_path and default_config_loaded_successfully and default_config):
                error_message += "No configuration file path or override object was provided, and the default configuration could not be successfully loaded or was empty."
            elif not effective_config: # General fallback if still no specific message formed
                 error_message = "No configuration provided (file, object, or default) or all sources resulted in an empty configuration."

            raise FileNotFoundError(error_message.strip()) # Use strip to clean up potential trailing space

        if schema:
            try:
                jsonschema.validate(instance=effective_config, schema=schema)
            except ValidationError as e:
                raise ValidationError(f"Configuration validation error: {e.message} in config: {effective_config}")
        
        self.config = effective_config
        return self.config

    def get_generator_config(self, full_config: dict, section_name: str) -> dict:
        """
        Retrieves a specific generator's configuration section from the full config.
        """
        return full_config.get(section_name, {})