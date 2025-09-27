import yaml
from pathlib import Path

class AttrDict(dict):
    """A dictionary that allows for attribute-style access."""
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @classmethod
    def from_dict(cls, data: dict):
        """Recursively convert a dictionary to an AttrDict."""
        if not isinstance(data, dict):
            return data
        return cls({k: cls.from_dict(v) for k, v in data.items()})

def load_config(config_path: str = 'config/user_config.yaml') -> AttrDict:
    """
    Loads the YAML configuration file and returns it as an AttrDict.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        AttrDict: The configuration object.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {path.resolve()}")

    with open(path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    return AttrDict.from_dict(config_data)

# Example of how to use it (optional, for direct testing)
if __name__ == '__main__':
    try:
        config = load_config()
        print("Config loaded successfully!")
        print("User Name:", config.user.name)
        print("GitHub Assistant Enabled:", config.agents.github_assistant.enabled)
        print("Security Encryption Key:", config.security.encryption.encryption_key)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")