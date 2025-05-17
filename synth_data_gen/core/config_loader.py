"""
Configuration Loader for the Synthetic Data Generation package.
"""
import yaml
import jsonschema
import os
import copy

class ConfigLoader:
    """
    Loads, validates, and merges YAML configuration files.
    """
    DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "default_config.yaml")

    def __init__(self, default_config_path: str = None):
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
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data if data is not None else {}
        except yaml.YAMLError as e:
            raise e

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
            except (FileNotFoundError, yaml.YAMLError):
                return {} 
        return {}

    def _merge_configs(self, base: dict, override: dict) -> dict:
        """
        Recursively merges two dictionaries. `override` takes precedence.
        Lists in `override` replace lists in `base`.
        """
        merged = copy.deepcopy(base)
        for key, value in override.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged

    def load_and_validate_config(self, file_path: str = None, schema: dict = None) -> dict:
        """
        Loads configuration and validates it.
        1. Loads default configuration.
        2. If file_path is provided, loads user configuration (raises FileNotFoundError if not found).
        3. Merges user_config over default_config (if both exist/loaded).
        4. If only default_config loaded, uses that.
        5. If only user_config loaded (no default_config found/loadable), uses that.
        6. If neither could be loaded, raises FileNotFoundError.
        7. Validates the resulting effective_config against the schema if provided.
        """
        default_config = self.get_default_config() # Returns {} if issues
        user_config = {}
        user_config_loaded_successfully = False
        
        if file_path:
            # load_config is strict and will raise FileNotFoundError or YAMLError if applicable
            user_config = self.load_config(file_path) 
            user_config_loaded_successfully = True

        effective_config = {}
        if user_config_loaded_successfully:
            if default_config: # If default_config is not an empty dict (i.e., was loaded)
                effective_config = self._merge_configs(default_config, user_config)
            else: # No default config, so effective is just user config
                effective_config = user_config
        elif default_config: # No user_file_path provided, use default if it was loaded
            effective_config = default_config
        else: # No user config was loaded (no path, or path failed) AND no default config
            # This means file_path was None, and get_default_config() returned {}
            raise FileNotFoundError(
                "No configuration file path provided and default configuration could not be loaded."
            )

        if schema:
            jsonschema.validate(instance=effective_config, schema=schema)
        return effective_config

    def get_generator_config(self, full_config: dict, section_name: str) -> dict:
        """
        Retrieves a specific generator's configuration section from the full config.
        """
        return full_config.get(section_name, {})