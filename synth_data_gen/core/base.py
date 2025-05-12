import random # Needed for range and probabilistic down the line
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseGenerator(ABC):
    """
    Abstract base class for all data generators.
    """
    GENERATOR_ID: str = "base"

    @abstractmethod
    def generate(self, specific_config: Dict[str, Any], global_config: Dict[str, Any], output_path: str) -> str:
        """
        Generates a single file based on the provided specific and global configurations.

        Args:
            specific_config (Dict[str, Any]): Configuration specific to this generator type.
            global_config (Dict[str, Any]): Global configuration settings.
            output_path (str): The full path (including filename) where the generated file should be saved.

        Returns:
            str: The path to the generated file.
        """
        pass

    def validate_config(self, specific_config: Dict[str, Any], global_config: Dict[str, Any]) -> bool:
        """
        Validates the specific configuration for this generator.
        The base implementation can be overridden by subclasses for more specific validation.

        Args:
            specific_config (Dict[str, Any]): Configuration specific to this generator type.
            global_config (Dict[str, Any]): Global configuration settings.

        Returns:
            bool: True if the configuration is valid, False otherwise.
        
        Raises:
            NotImplementedError: If a subclass does not implement this method and relies on it.
                                 Subclasses should implement their own validation logic.
        """
        # Basic validation can be added here if common to all generators
        # For now, subclasses are expected to implement their own comprehensive validation
        if not isinstance(specific_config, dict):
            # Or raise an InvalidConfigError from synth_data_gen.exceptions
            # For now, print and return False for simplicity until exceptions are defined
            print("Error: specific_config must be a dictionary.")
            return False
        if not isinstance(global_config, dict):
            print("Error: global_config must be a dictionary.")
            return False
        return True

    @abstractmethod
    def get_default_specific_config(self) -> Dict[str, Any]:
        """
        Returns the default specific configuration for this generator.
        This is used if no specific configuration is provided for this generator type.

        Returns:
            Dict[str, Any]: A dictionary containing the default specific settings.
        """
        pass

    def _determine_count(self, config_value: Any, context_key_name: str) -> int:
        """
        Determines the count of an element based on its configuration value.
        Handles exact integers, range objects, and probabilistic objects.

        Args:
            config_value: The configuration value for the element's count.
                          Can be an int, or a dict for range/probabilistic.
            context_key_name (str): A descriptive name for the context of this count
                                    (e.g., "chapters", "sections_in_chapter_1", "images_in_paragraph_5").
                                    Used for potential logging or more complex probabilistic scopes.

        Returns:
            int: The determined count for the element.
        """
        if isinstance(config_value, int):
            return config_value
        elif isinstance(config_value, dict):
            if "min" in config_value and "max" in config_value:
                # Range object
                min_val = config_value.get("min", 0)
                max_val = config_value.get("max", 0)
                if not (isinstance(min_val, int) and isinstance(max_val, int) and min_val >= 0 and max_val >= min_val):
                    print(f"Warning: Invalid range config for '{context_key_name}': {config_value}. Defaulting to 0.")
                    return 0
                return random.randint(min_val, max_val)
            elif "chance" in config_value:
                # Probabilistic object
                chance = config_value.get("chance", 0.0)
                max_total = config_value.get("max_total", 1) # Default max_total for simple chance
                # per_unit_of = config_value.get("per_unit_of") # For future more complex logic

                if not (isinstance(chance, float) and 0.0 <= chance <= 1.0 and isinstance(max_total, int) and max_total >=0):
                    print(f"Warning: Invalid probabilistic config for '{context_key_name}': {config_value}. Defaulting to 0.")
                    return 0
                
                # For now, a simple interpretation: if chance hits, return 1 (up to max_total), else 0.
                # More complex logic (e.g. for "per_unit_of") would go here.
                # If per_unit_of is "document" or not specified, it's a one-time check.
                count = 0
                if random.random() < chance:
                    count = 1 # For now, assume 1 if chance hits, up to max_total
                return min(count, max_total) # Ensure we don't exceed max_total
            else:
                print(f"Warning: Unknown dictionary structure for count config '{context_key_name}': {config_value}. Defaulting to 0.")
                return 0
        else:
            # Default or error for unhandled types
            print(f"Warning: Invalid type for count config '{context_key_name}': {type(config_value)}. Defaulting to 0.")
            return 0