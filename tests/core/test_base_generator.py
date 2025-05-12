import pytest
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

@pytest.fixture
def concrete_generator_instance():
    return ConcreteGenerator()

def test_validate_config_valid_inputs(concrete_generator_instance):
    """Test validate_config with valid dictionary inputs."""
    specific_config = {"key1": "value1"}
    global_config = {"global_key": "global_value"}
    assert concrete_generator_instance.validate_config(specific_config, global_config)

def test_validate_config_invalid_specific_config_type(concrete_generator_instance):
    """Test validate_config with specific_config not being a dictionary."""
    specific_config = "not_a_dict"
    global_config = {"global_key": "global_value"}
    # Expecting False because the base method prints an error and returns False
    assert not concrete_generator_instance.validate_config(specific_config, global_config)

def test_validate_config_invalid_global_config_type(concrete_generator_instance):
    """Test validate_config with global_config not being a dictionary."""
    specific_config = {"key1": "value1"}
    global_config = "not_a_dict"
    # Expecting False
    assert not concrete_generator_instance.validate_config(specific_config, global_config)

def test_validate_config_empty_configs(concrete_generator_instance):
    """Test validate_config with empty but valid dictionary inputs."""
    specific_config = {}
    global_config = {}
    assert concrete_generator_instance.validate_config(specific_config, global_config)