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

    def load_and_validate_config(
        self,
        file_path: str = None,
        schema: dict = None,
        config_override_object: dict = None
    ) -> dict:
        """
        Loads configuration and validates it.

        Args:
            file_path: Path to a YAML/JSON configuration file.
            schema: JSON schema to validate the configuration against.
            config_override_object: A dictionary to use as configuration or to merge
                                   over file-based configuration.

        Priority order (highest to lowest):
        1. config_override_object (if provided, merges over file config)
        2. file_path configuration (if provided)
        3. default configuration

        Returns:
            dict: The effective configuration after merging and validation.

        Raises:
            FileNotFoundError: If no configuration source is available.
            jsonschema.ValidationError: If schema validation fails.
        """
        default_config = self.get_default_config()  # Returns {} if issues
        file_config = {}
        file_config_loaded = False

        # Load file-based configuration if provided
        if file_path:
            file_config = self.load_config(file_path)
            file_config_loaded = True

        # Build effective configuration through merging
        effective_config = {}

        # Start with default config if available
        if default_config:
            effective_config = copy.deepcopy(default_config)

        # Merge file config over defaults
        if file_config_loaded:
            if effective_config:
                effective_config = self._merge_configs(effective_config, file_config)
            else:
                effective_config = copy.deepcopy(file_config)

        # Merge override object over everything else
        if config_override_object:
            if effective_config:
                effective_config = self._merge_configs(effective_config, config_override_object)
            else:
                effective_config = copy.deepcopy(config_override_object)

        # Ensure we have some configuration
        if not effective_config:
            raise FileNotFoundError(
                "No configuration available: no file_path, config_override_object, "
                "or default configuration could be loaded."
            )

        # Validate against schema if provided
        if schema:
            jsonschema.validate(instance=effective_config, schema=schema)

        return effective_config

    def get_generator_config(self, full_config: dict, section_name: str) -> dict:
        """
        Retrieves a specific generator's configuration section from the full config.
        """
        return full_config.get(section_name, {})