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
from .core.config_loader import ConfigLoader # Import the real ConfigLoader

# Placeholder for custom exceptions (as defined in spec)
class InvalidConfigError(ValueError): pass # This might be superseded by ConfigLoader's exceptions
class GeneratorError(RuntimeError): pass
class EpubGenerationError(GeneratorError): pass
class PdfGenerationError(GeneratorError): pass
class MarkdownGenerationError(GeneratorError): pass
class PluginError(RuntimeError): pass


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

    # Instantiate the real ConfigLoader
    # The schema path might be handled internally by ConfigLoader or passed here
    # For now, assuming ConfigLoader uses its default schema if schema_path is None
    loader = ConfigLoader() # ConfigLoader handles its own default schema path
    
    try:
        # Use load_and_validate_config
        # If config_obj is provided, it should take precedence or be handled by ConfigLoader
        if config_obj:
            # ConfigLoader's current load_and_validate_config doesn't directly take config_obj.
            # This part might need adjustment based on how ConfigLoader is designed to handle this.
            # For now, we'll assume if config_obj is given, config_path might be None or ignored.
            # This is a simplification and might need refinement.
            # A more robust ConfigLoader might have a load_from_object_and_validate method.
            # OR, the test setup needs to ensure config_path is always primary for this integration.
            # For this TDD step, we focus on config_path.
            if config_path:
                 print(f"Warning: Both config_path ('{config_path}') and config_obj provided. Prioritizing config_path for loading.")
            config = loader.load_and_validate_config(config_path=config_path, config_override_object=config_obj)

        elif config_path:
            config = loader.load_and_validate_config(config_path=config_path)
        else:
            # Load default config if neither path nor object is provided
            config = loader.load_and_validate_config()

    except Exception as e: # Catching a broader exception as ConfigLoader might raise various types
        print(f"Configuration error: {e}")
        raise # Re-raise for now

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
            
        # Get generator-specific config from the main loaded_config
        # The loader instance is 'loader', the full config is 'config'
        specific_config = loader.get_generator_config(config, generator_type_str.lower())
        
        # If specific settings are empty after trying to load from main config,
        # then use generator's defaults.
        if not specific_config: # and generator_type_str.lower() in GENERATOR_MAP: # Check if it's a known type
            # This check for GENERATOR_MAP might be redundant if specific_config is already empty
            specific_config = generator_instance.get_default_specific_config()
            print(f"Using default specific settings for {generator_type_str} as none were found in the main config.")

        # Validate the specific config using the generator's method
        try:
            # Ensure specific_config is a dict before validation,
            # as get_default_specific_config should return a dict.
            if not isinstance(specific_config, dict):
                print(f"Warning: Specific configuration for {generator_type_str} is not a dictionary. Using defaults.")
                specific_config = generator_instance.get_default_specific_config()

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