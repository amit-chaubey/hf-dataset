import os
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_env_file(env_file=".env"):
    """
    Load environment variables from a .env file
    
    Args:
        env_file (str): Path to the .env file
        
    Returns:
        bool: True if environment variables were loaded successfully
    """
    env_path = Path(env_file)
    
    if not env_path.exists():
        logger.warning(f"Environment file {env_file} not found")
        return False
    
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
                
            # Parse key-value pairs
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                # Don't override existing environment variables
                if key not in os.environ:
                    os.environ[key] = value
                    logger.debug(f"Set environment variable: {key}")
    
    return True

def check_required_env_vars(required_vars):
    """
    Check if required environment variables are set
    
    Args:
        required_vars (list): List of required environment variable names
        
    Returns:
        bool: True if all required variables are set
    """
    missing_vars = []
    
    for var in required_vars:
        if var not in os.environ or not os.environ[var]:
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def setup_env(required_vars=None):
    """
    Setup environment variables from .env file and check required variables
    
    Args:
        required_vars (list): List of required environment variable names
        
    Returns:
        bool: True if environment was set up successfully
    """
    # Try to load from .env file
    load_env_file()
    
    # Check for required variables if specified
    if required_vars and not check_required_env_vars(required_vars):
        return False
    
    return True

if __name__ == "__main__":
    # If run directly, load .env file and print status
    logging.basicConfig(level=logging.INFO)
    
    if load_env_file():
        print("Environment variables loaded successfully")
        
        # Print loaded variables (only for demo purposes)
        for key in ["OPENAI_API_KEY", "HF_TOKEN"]:
            if key in os.environ:
                value = os.environ[key]
                masked_value = value[:4] + "*" * (len(value) - 4) if len(value) > 4 else "****"
                print(f"{key}: {masked_value}")
    else:
        print("Failed to load environment variables")
        sys.exit(1) 