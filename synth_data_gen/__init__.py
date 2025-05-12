# synth_data_gen/__init__.py
import os
import yaml # For loading YAML config files
import json # For loading JSON config files (optional, if supporting JSON config)
from typing import Any, Dict, List, Optional, Type

# Import the new generator classes
from .core.base import BaseGenerator
from .generators.epub import EpubGenerator
from .generators.pdf import PdfGenerator
from .generators.markdown import MarkdownGenerator
from .common.utils import ensure_output_directories

# Placeholder for custom exceptions (as defined in spec)
class InvalidConfigError(ValueError): pass
class GeneratorError(RuntimeError): pass
class EpubGenerationError(GeneratorError): pass
class PdfGenerationError(GeneratorError): pass
class MarkdownGenerationError(GeneratorError): pass
class PluginError(RuntimeError): pass


# Stub for ConfigLoader class
class ConfigLoader:
    def __init__(self, config_path: Optional[str] = None, config_obj: Optional[Dict[str, Any]] = None):
        self.config_path = config_path
        self.config_obj = config_obj
        self.config: Dict[str, Any] = {}

    def load_config(self) -> Dict[str, Any]:
        if self.config_obj:
            self.config = self.config_obj
            print("Loaded configuration from object.")
        elif self.config_path:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.endswith(".yaml") or self.config_path.endswith(".yml"):
                        self.config = yaml.safe_load(f)
                    elif self.config_path.endswith(".json"):
                        self.config = json.load(f)
                    else:
                        raise InvalidConfigError(f"Unsupported configuration file format: {self.config_path}. Use YAML or JSON.")
                print(f"Loaded configuration from file: {self.config_path}")
            except Exception as e:
                raise InvalidConfigError(f"Error parsing configuration file {self.config_path}: {e}")
        else:
            # Default configuration logic (simplified)
            print("No configuration provided, using default settings for generation.")
            self.config = {
                "output_directory_base": "synthetic_output_default",
                "global_settings": {
                    "default_author": "Default Synth Author",
                    "default_language": "en"
                },
                "file_types": [
                    {
                        "type": "epub", "count": 1, "output_subdir": "default_epubs",
                        "epub_specific_settings": EpubGenerator().get_default_specific_config()
                    },
                    {
                        "type": "pdf", "count": 1, "output_subdir": "default_pdfs",
                        "pdf_specific_settings": PdfGenerator().get_default_specific_config()
                    },
                    {
                        "type": "markdown", "count": 1, "output_subdir": "default_markdown",
                        "markdown_specific_settings": MarkdownGenerator().get_default_specific_config()
                    }
                ]
            }
        
        self._validate_root_config()
        return self.config

    def _validate_root_config(self):
        if not isinstance(self.config, dict):
            raise InvalidConfigError("Root configuration must be a dictionary.")
        if "file_types" not in self.config or not isinstance(self.config["file_types"], list):
            raise InvalidConfigError("'file_types' must be a list in the configuration.")
        if not self.config["file_types"]:
            print("Warning: 'file_types' list is empty. No files will be generated.")


# Mapping of type strings to generator classes
GENERATOR_MAP: Dict[str, Type[BaseGenerator]] = {
    "epub": EpubGenerator,
    "pdf": PdfGenerator,
    "markdown": MarkdownGenerator,
    # Plugins would extend this map
}

def generate_data(config_path: Optional[str] = None, config_obj: Optional[Dict[str, Any]] = None, output_dir_override: Optional[str] = None) -> List[str]:
    """
    Generates synthetic data files based on the provided configuration.
    """
    print(f"Starting synthetic data generation (config_path='{config_path}', config_obj provided: {config_obj is not None}, output_dir_override='{output_dir_override}')...")

    loader = ConfigLoader(config_path=config_path, config_obj=config_obj)
    try:
        config = loader.load_config()
    except (FileNotFoundError, InvalidConfigError) as e:
        print(f"Configuration error: {e}") # Or re-raise specific exceptions
        raise # Re-raise for now as per original spec for generate_data

    global_settings = config.get("global_settings", {})
    base_output_dir = output_dir_override if output_dir_override else config.get("output_directory_base", "synthetic_output")
    
    ensure_output_directories(base_output_dir) # Ensure base output directory exists

    generated_files: List[str] = []

    for file_type_config in config.get("file_types", []):
        generator_type_str = file_type_config.get("type")
        if not generator_type_str:
            print(f"Warning: Missing 'type' in file_type configuration: {file_type_config}. Skipping.")
            continue

        GeneratorClass = GENERATOR_MAP.get(generator_type_str.lower())
        if not GeneratorClass:
            print(f"Warning: Unknown generator type '{generator_type_str}'. Skipping.")
            # Potentially use PluginManager here in the future
            continue
        
        generator_instance = GeneratorClass()
        
        count = file_type_config.get("count", 1)
        if not isinstance(count, int) or count < 0:
            print(f"Warning: Invalid 'count' for type '{generator_type_str}': {count}. Defaulting to 1.")
            count = 1
            
        specific_settings_key = f"{generator_type_str.lower()}_specific_settings"
        specific_config = file_type_config.get(specific_settings_key, {})
        
        # If specific settings are empty, use generator's defaults
        if not specific_config:
            specific_config = generator_instance.get_default_specific_config()
            print(f"Using default specific settings for {generator_type_str}")

        # Validate the specific config using the generator's method
        try:
            if not generator_instance.validate_config(specific_config, global_settings):
                print(f"Warning: Invalid specific configuration for {generator_type_str}. Skipping.")
                # Or raise InvalidConfigError
                continue
        except Exception as e:
            print(f"Error validating config for {generator_type_str}: {e}. Skipping.")
            continue

        file_output_subdir = file_type_config.get("output_subdir", generator_type_str + "s")
        current_output_dir = os.path.join(base_output_dir, file_output_subdir)
        ensure_output_directories(current_output_dir)

        default_extension = generator_type_str if generator_type_str != "markdown" else "md"
        filename_pattern = file_type_config.get("filename_pattern", f"{generator_type_str}_{{index}}.{default_extension}")


        for i in range(count):
            # Create a unique filename
            # Basic slugification for title, could be more robust
            slug_title = specific_config.get("title", f"doc_{i+1}").lower().replace(" ", "_").replace(":", "").replace("'", "")
            slug_title = "".join(c for c in slug_title if c.isalnum() or c == '_')[:30] # Limit length

            filename = filename_pattern.format(index=i+1, slug_title=slug_title)
            output_file_path = os.path.join(current_output_dir, filename)
            
            print(f"Generating {generator_type_str} ({i+1}/{count}): {output_file_path}")
            try:
                generated_path = generator_instance.generate(specific_config, global_settings, output_file_path)
                generated_files.append(generated_path)
            except Exception as e:
                # Wrap in GeneratorError as per spec
                gen_error = GeneratorError(f"Error during {generator_type_str} generation for {output_file_path}: {e}")
                # Specific errors can also be raised by generators themselves
                if isinstance(e, (EpubGenerationError, PdfGenerationError, MarkdownGenerationError)):
                    gen_error = e # Use the more specific error if already raised
                
                print(str(gen_error))
                # Decide whether to continue with other files or stop
                # For now, we'll log and continue

    print(f"Synthetic data generation finished. Generated {len(generated_files)} files.")
    return generated_files

__all__ = ['generate_data', 'InvalidConfigError', 'GeneratorError', 'EpubGenerationError', 'PdfGenerationError', 'MarkdownGenerationError', 'PluginError']