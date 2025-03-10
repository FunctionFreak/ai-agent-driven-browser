import os
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the path to the YAML configuration file
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')

def load_config():
    """
    Loads configuration from the YAML file and overrides values with any matching environment variables.
    """
    with open(CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)
    
    # Override YAML values with environment variables if they exist
    for key, value in config.items():
        config[key] = os.getenv(key, value)
    
    return config
