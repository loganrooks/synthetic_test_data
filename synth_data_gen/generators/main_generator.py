"""
Main generator class responsible for orchestrating the generation of different document types.
"""
import logging
from .epub import EpubGenerator
from .markdown import MarkdownGenerator
from .pdf import PdfGenerator

logger = logging.getLogger(__name__)

class MainGenerator:
    """
    Orchestrates the generation of synthetic documents based on the provided configuration.
    """
    def __init__(self, config):
        """
        Initializes the MainGenerator with a configuration object.

        Args:
            config (dict): The validated configuration dictionary.
        """
        self.config = config
        self.output_path = self.config.get("output_path", "output")
        self.generators = {
            "epub": EpubGenerator,
            "markdown": MarkdownGenerator,
            "pdf": PdfGenerator,
            # Add other generator types here as they are implemented
        }

    def generate(self): # Renamed from generate_documents
        """
        Generates documents based on the 'output_formats' specified in the config.

        Returns:
            dict: A dictionary where keys are output format names (e.g., 'epub_files')
                  and values are lists of generated file paths for that format.
                  Returns None if no documents were generated or an error occurred.
        """
        generated_files_all_formats = {}
        output_formats_config = self.config.get("output_formats", {})

        if not output_formats_config:
            logger.warning("No 'output_formats' specified in the configuration. No documents will be generated.")
            return None

        for format_name, format_config in output_formats_config.items():
            if not format_config.get("enabled", False):
                logger.info(f"Skipping {format_name} generation as it is not enabled in the configuration.")
                continue

            generator_class = self.generators.get(format_name)
            if generator_class:
                try:
                    logger.info(f"Initializing {format_name} generator.")
                    # Pass the global config and the specific format config
                    generator_instance = generator_class(self.config, format_config)
                    
                    logger.info(f"Starting {format_name} document generation...")
                    # Assuming each generator has a 'generate' method
                    # and returns a list of generated file paths
                    generated_files = generator_instance.generate() 
                    
                    if generated_files:
                        generated_files_all_formats[f"{format_name}_files"] = generated_files
                        logger.info(f"Successfully generated {len(generated_files)} {format_name} document(s).")
                    else:
                        logger.warning(f"No files were generated for {format_name} format.")
                        generated_files_all_formats[f"{format_name}_files"] = []

                except Exception as e:
                    logger.error(f"Error during {format_name} generation: {e}", exc_info=True)
                    generated_files_all_formats[f"{format_name}_files"] = [] # Indicate failure for this format
            else:
                logger.warning(f"No generator found for format: {format_name}. Skipping.")
        
        if not generated_files_all_formats:
            logger.info("No documents were generated across all specified formats.")
            return None
            
        return generated_files_all_formats

# Example of how specific generators might look (to be defined in their respective files)
# class EpubGenerator:
#     def __init__(self, global_config, format_config):
#         self.global_config = global_config
#         self.format_config = format_config
#         # ...
#     def generate(self):
#         # ... generation logic ...
#         return ["path/to/generated.epub"]

# class MarkdownGenerator:
#     def __init__(self, global_config, format_config):
#         self.global_config = global_config
#         self.format_config = format_config
#         # ...
#     def generate(self):
#         # ... generation logic ...
#         return ["path/to/generated.md"]

# class PdfGenerator:
#     def __init__(self, global_config, format_config):
#         self.global_config = global_config
#         self.format_config = format_config
#         # ...
#     def generate(self):
#         # ... generation logic ...
#         return ["path/to/generated.pdf"]

