# synth_data_gen/__init__.py
"""
Synthetic Test Data Generator

A library for generating synthetic test data in EPUB, PDF, and Markdown formats
for testing document processing pipelines.
"""
import logging
import os
from typing import Any, Dict, List, Optional, Type

from .constants import GeneratorType, FileExtension
from .core.base import BaseGenerator
from .core.config_loader import ConfigLoader
from .generators.epub import EpubGenerator
from .generators.pdf import PdfGenerator
from .generators.markdown import MarkdownGenerator
from .common.utils import ensure_output_directories

# Configure module logger
logger = logging.getLogger(__name__)


# Custom exceptions
class InvalidConfigError(ValueError):
    """Raised when configuration is invalid."""
    pass


class GeneratorError(RuntimeError):
    """Base exception for generator errors."""
    pass


class EpubGenerationError(GeneratorError):
    """Raised when EPUB generation fails."""
    pass


class PdfGenerationError(GeneratorError):
    """Raised when PDF generation fails."""
    pass


class MarkdownGenerationError(GeneratorError):
    """Raised when Markdown generation fails."""
    pass


class PluginError(RuntimeError):
    """Raised when a plugin fails to load or execute."""
    pass


# Mapping of type strings to generator classes
GENERATOR_MAP: Dict[str, Type[BaseGenerator]] = {
    GeneratorType.EPUB.value: EpubGenerator,
    GeneratorType.PDF.value: PdfGenerator,
    GeneratorType.MARKDOWN.value: MarkdownGenerator,
}


def generate_data(
    config_path: Optional[str] = None,
    config_obj: Optional[Dict[str, Any]] = None,
    output_dir_override: Optional[str] = None
) -> List[str]:
    """
    Generates synthetic data files based on the provided configuration.

    Args:
        config_path: Path to a YAML/JSON configuration file.
        config_obj: A dictionary configuration object. If both config_path and
                   config_obj are provided, config_obj values override file values.
        output_dir_override: Override the output directory from configuration.

    Returns:
        List of paths to generated files.

    Raises:
        InvalidConfigError: If the configuration is invalid.
        GeneratorError: If file generation fails.
    """
    logger.info(
        "Starting synthetic data generation (config_path='%s', config_obj=%s, output_dir='%s')",
        config_path, "provided" if config_obj else "None", output_dir_override
    )

    loader = ConfigLoader()

    try:
        # ConfigLoader handles merging: default <- file <- override object
        config = loader.load_and_validate_config(
            file_path=config_path,
            config_override_object=config_obj
        )
    except FileNotFoundError as e:
        logger.error("Configuration error: %s", e)
        raise InvalidConfigError(f"Configuration not found: {e}") from e
    except Exception as e:
        logger.error("Configuration error: %s", e)
        raise InvalidConfigError(f"Invalid configuration: {e}") from e

    global_settings = config.get("global_settings", {})
    base_output_dir = output_dir_override if output_dir_override else config.get("output_directory_base", "synthetic_output")
    
    ensure_output_directories(base_output_dir)

    generated_files: List[str] = []

    for file_type_config in config.get("file_types", []):
        generator_type_str = file_type_config.get("type")
        if not generator_type_str:
            logger.warning("Missing 'type' in file_type configuration: %s. Skipping.", file_type_config)
            continue

        GeneratorClass = GENERATOR_MAP.get(generator_type_str.lower())
        if not GeneratorClass:
            logger.warning("Unknown generator type '%s'. Skipping.", generator_type_str)
            continue

        generator_instance = GeneratorClass()

        count = file_type_config.get("count", 1)
        if not isinstance(count, int) or count < 0:
            logger.warning("Invalid 'count' for type '%s': %s. Defaulting to 1.", generator_type_str, count)
            count = 1

        # Get generator-specific config from the file_type_config (per spec)
        # Config is in file_types[].<type>_specific_settings (e.g., epub_specific_settings)
        specific_settings_key = f"{generator_type_str.lower()}_specific_settings"
        specific_config = file_type_config.get(specific_settings_key, {})

        # Merge with generator defaults if needed
        default_config = generator_instance.get_default_specific_config()
        if specific_config:
            # Merge user config over defaults
            merged_config = {**default_config, **specific_config}
            specific_config = merged_config
        else:
            specific_config = default_config
            logger.debug("Using default settings for %s (none found in config).", generator_type_str)

        # Validate the specific config
        try:
            if not isinstance(specific_config, dict):
                logger.warning("Config for %s is not a dictionary. Using defaults.", generator_type_str)
                specific_config = generator_instance.get_default_specific_config()

            if not generator_instance.validate_config(specific_config, global_settings):
                logger.warning("Invalid configuration for %s. Skipping.", generator_type_str)
                continue
        except Exception as e:
            logger.error("Error validating config for %s: %s. Skipping.", generator_type_str, e)
            continue

        file_output_subdir = file_type_config.get("output_subdir", generator_type_str + "s")
        current_output_dir = os.path.join(base_output_dir, file_output_subdir)
        ensure_output_directories(current_output_dir)

        # Determine file extension: markdown -> .md, others use type name
        if generator_type_str == GeneratorType.MARKDOWN.value:
            default_extension = "md"
        else:
            default_extension = generator_type_str
        filename_pattern = file_type_config.get(
            "filename_pattern",
            f"{generator_type_str}_{{index}}.{default_extension}"
        )

        for i in range(count):
            # Create a unique filename with basic slugification
            slug_title = specific_config.get("title", f"doc_{i+1}").lower()
            slug_title = slug_title.replace(" ", "_").replace(":", "").replace("'", "")
            slug_title = "".join(c for c in slug_title if c.isalnum() or c == '_')[:30]

            filename = filename_pattern.format(index=i+1, slug_title=slug_title)
            output_file_path = os.path.join(current_output_dir, filename)

            logger.info("Generating %s (%d/%d): %s", generator_type_str, i+1, count, output_file_path)
            try:
                generated_path = generator_instance.generate(specific_config, global_settings, output_file_path)
                generated_files.append(generated_path)
            except (EpubGenerationError, PdfGenerationError, MarkdownGenerationError) as e:
                logger.error("Generation failed for %s: %s", output_file_path, e)
            except Exception as e:
                logger.error("Unexpected error generating %s: %s", output_file_path, e)

    logger.info("Synthetic data generation finished. Generated %d files.", len(generated_files))
    return generated_files


__all__ = [
    'generate_data',
    'InvalidConfigError',
    'GeneratorError',
    'EpubGenerationError',
    'PdfGenerationError',
    'MarkdownGenerationError',
    'PluginError',
    'ConfigLoader',
    'BaseGenerator',
    'EpubGenerator',
    'PdfGenerator',
    'MarkdownGenerator',
]