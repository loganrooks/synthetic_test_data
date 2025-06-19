# synth_data_gen/__init__.py
import os
import json
import sys # For sys.stderr
from jsonschema import ValidationError # Direct import for better type checking

from .core.config_loader import ConfigLoader # Relative import
from .core import InvalidConfigError # Added this line
from .generators import main_generator as main_generator_module # New import step 1
MainGenerator = main_generator_module.MainGenerator # New import step 2

_CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_CONFIG_PATH = os.path.join(_CURRENT_SCRIPT_DIR, "core", "default_config.yaml")
_DEFAULT_SCHEMA_PATH = os.path.join(_CURRENT_SCRIPT_DIR, "core", "config_schema.json")

def generate_data(config_file_path: str | None = None, config_obj: dict | None = None, output_file: str | None = None) -> dict | None:
    """
    Main function to generate synthetic data based on a configuration file or object.
    Returns a dictionary of generated file paths keyed by type, or None if generation fails.
    """
    loader = ConfigLoader(default_config_path=_DEFAULT_CONFIG_PATH)
    schema = None
    if os.path.exists(_DEFAULT_SCHEMA_PATH):
        try:
            with open(_DEFAULT_SCHEMA_PATH, 'r') as f:
                schema = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load schema from {_DEFAULT_SCHEMA_PATH}: {e}", file=sys.stderr)
    
    try:
        loaded_config = loader.load_and_validate_config(
            file_path=config_file_path, 
            schema=schema, 
            config_override_object=config_obj
        )
    except FileNotFoundError as e:
        print(f"Error: Configuration file not found or no config could be loaded. Details: {e}")
        raise # Re-raise FileNotFoundError
    except ValueError as e: 
        print(f"Error: Invalid configuration format or value. Details: {e}")
        return None
    except ValidationError as e: 
        print(f"Error: Configuration validation failed. Details: {e}")
        return None
    except Exception as e: 
        print(f"An unexpected error occurred during configuration loading: {e}")
        return None

    if not loaded_config:
        print("Error: Configuration resulted in an empty set of parameters. Cannot proceed.")
        return None

    if output_file:
        loaded_config['output_path_override'] = output_file

    try:
        # Use the imported module to access MainGenerator
        generator = MainGenerator(loaded_config) 
        generated_files_details = generator.generate()
        
        output_dir_base = loaded_config.get('output_directory_base')
        if output_dir_base and not os.path.exists(output_dir_base):
            try:
                os.makedirs(output_dir_base, exist_ok=True)
            except OSError as e:
                print(f"Warning: Could not create base output directory '{output_dir_base}': {e}")

        print("Data generation process initiated. Check logs for status.")
        if generated_files_details:
            print("Generated files:")
            for file_type, paths in generated_files_details.items():
                print(f"  {file_type}:")
                for path in paths:
                    print(f"    - {path}")
        else:
            print("No files were generated according to the MainGenerator.")
            
        return generated_files_details
    except AttributeError as e: # If MainGenerator is not found in main_generator module
        print(f"Error: Could not find MainGenerator class. Import issue? Details: {e}")
        return None
    except KeyError as e:
        print(f"Error: Missing critical configuration key during generation: {e}. Please check your configuration.")
        return None
    except Exception as e:
        print(f"An error occurred during data generation: {e}")
        return None

if __name__ == '__main__':
    # Example usage (optional, for direct script execution)
    # You would typically call generate_data from another script or a CLI interface.
    
    # Example 1: Using a config file
    # Create a dummy my_config.yaml for this example to work
    # with open("my_config.yaml", "w") as f:
    #     f.write("output_path: 'output/generated_data.json'\\\\n")
    #     f.write("num_records: 50\\\\n")
    # generate_data(config_file_path="my_config.yaml")

    # Example 2: Using a config object (overriding or supplementing default)
    # custom_config = {
    #     "output_path": "output/custom_data.xml",
    #     "format": "xml",
    #     "num_records": 75,
    #     "custom_generator_settings": {
    #         "field_a": "value_a"
    #     }
    # }
    # generate_data(config_obj=custom_config)

    # Example 3: Using default config only (if default_config.yaml exists and is valid)
    # generate_data()

    # Example 4: Specifying output file directly
    # generate_data(output_file="output/direct_output.csv")
    pass