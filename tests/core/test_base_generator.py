import unittest
from synth_data_gen.core.base import BaseGenerator

# A concrete implementation of BaseGenerator for testing purposes
class ConcreteGenerator(BaseGenerator):
    GENERATOR_ID = "concrete"

    def generate(self, specific_config, global_config, output_path):
        # Not used in these tests for BaseGenerator's validate_config
        return output_path 

    def get_default_specific_config(self):
        # Not used in these tests for BaseGenerator's validate_config
        return {"default_concrete_setting": "concrete_value"}

class TestBaseGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = ConcreteGenerator()

    def test_validate_config_valid_inputs(self):
        """Test validate_config with valid dictionary inputs."""
        specific_config = {"key1": "value1"}
        global_config = {"global_key": "global_value"}
        self.assertTrue(self.generator.validate_config(specific_config, global_config))

    def test_validate_config_invalid_specific_config_type(self):
        """Test validate_config with specific_config not being a dictionary."""
        specific_config = "not_a_dict"
        global_config = {"global_key": "global_value"}
        # Expecting False because the base method prints an error and returns False
        self.assertFalse(self.generator.validate_config(specific_config, global_config))

    def test_validate_config_invalid_global_config_type(self):
        """Test validate_config with global_config not being a dictionary."""
        specific_config = {"key1": "value1"}
        global_config = "not_a_dict"
        # Expecting False
        self.assertFalse(self.generator.validate_config(specific_config, global_config))

    def test_validate_config_empty_configs(self):
        """Test validate_config with empty but valid dictionary inputs."""
        specific_config = {}
        global_config = {}
        self.assertTrue(self.generator.validate_config(specific_config, global_config))

if __name__ == '__main__':
    unittest.main()