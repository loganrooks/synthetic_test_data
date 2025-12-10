import logging
import random  # Needed for range and probabilistic down the line
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger(__name__)


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
            logger.error("specific_config must be a dictionary.")
            return False
        if not isinstance(global_config, dict):
            logger.error("global_config must be a dictionary.")
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
                    logger.warning("Invalid range config for '%s': %s. Defaulting to 0.", context_key_name, config_value)
                    return 0
                return random.randint(min_val, max_val)
            elif "chance" in config_value:
                # Probabilistic object
                chance = config_value.get("chance", 0.0)
                if_true_config = config_value.get("if_true", 1)  # Default to 1 if chance met and if_true missing
                if_false_config = config_value.get("if_false", 0) # Default to 0 if chance not met and if_false missing
                max_total_val = config_value.get("max_total") # Can be None

                if not (isinstance(chance, float) and 0.0 <= chance <= 1.0):
                    logger.warning("Invalid chance value for probabilistic config '%s': %s. Defaulting to determined if_false value.", context_key_name, chance)
                    # Determine count based on if_false_config directly
                    if isinstance(if_false_config, int):
                        determined_count = if_false_config
                    elif isinstance(if_false_config, dict) and "min" in if_false_config and "max" in if_false_config:
                        min_val_f = if_false_config.get("min", 0)
                        max_val_f = if_false_config.get("max", 0)
                        if not (isinstance(min_val_f, int) and isinstance(max_val_f, int) and min_val_f >= 0 and max_val_f >= min_val_f):
                            determined_count = 0
                        else:
                            determined_count = random.randint(min_val_f, max_val_f)
                    else:
                        determined_count = 0 # Default for invalid if_false_config
                else:
                    # Valid chance, proceed with probability check
                    if random.random() < chance:
                        # Process if_true_config
                        if isinstance(if_true_config, int):
                            determined_count = if_true_config
                        elif isinstance(if_true_config, dict) and "min" in if_true_config and "max" in if_true_config:
                            min_val_t = if_true_config.get("min", 0)
                            max_val_t = if_true_config.get("max", 0)
                            if not (isinstance(min_val_t, int) and isinstance(max_val_t, int) and min_val_t >= 0 and max_val_t >= min_val_t):
                                logger.warning("Invalid range in if_true for probabilistic config '%s': %s. Defaulting to 1.", context_key_name, if_true_config)
                                determined_count = 1
                            else:
                                determined_count = random.randint(min_val_t, max_val_t)
                        else:
                            logger.warning("Invalid if_true structure in probabilistic config '%s': %s. Defaulting to 1.", context_key_name, if_true_config)
                            determined_count = 1
                    else:
                        # Process if_false_config
                        if isinstance(if_false_config, int):
                            determined_count = if_false_config
                        elif isinstance(if_false_config, dict) and "min" in if_false_config and "max" in if_false_config:
                            min_val_f = if_false_config.get("min", 0)
                            max_val_f = if_false_config.get("max", 0)
                            if not (isinstance(min_val_f, int) and isinstance(max_val_f, int) and min_val_f >= 0 and max_val_f >= min_val_f):
                                logger.warning("Invalid range in if_false for probabilistic config '%s': %s. Defaulting to 0.", context_key_name, if_false_config)
                                determined_count = 0
                            else:
                                determined_count = random.randint(min_val_f, max_val_f)
                        else:
                            logger.warning("Invalid if_false structure in probabilistic config '%s': %s. Defaulting to 0.", context_key_name, if_false_config)
                            determined_count = 0

                if max_total_val is not None:
                    if not (isinstance(max_total_val, int) and max_total_val >= 0):
                        logger.warning("Invalid max_total value for probabilistic config '%s': %s. Ignoring max_total.", context_key_name, max_total_val)
                    else:
                        determined_count = min(determined_count, max_total_val)
                return determined_count
            else:
                logger.warning("Unknown dictionary structure for count config '%s': %s. Defaulting to 0.", context_key_name, config_value)
                return 0
        else:
            # Default or error for unhandled types
            logger.warning("Invalid type for count config '%s': %s. Defaulting to 0.", context_key_name, type(config_value))
            return 0
