import yaml
from typing import Any, Dict, Optional, Union
import logging


class ConfigStore:
    """
    A class to manage configuration data loaded from and saved to a YAML file.
    """

    def __init__(self, file_path: str, auto_extend=False):
        """
        Initializes the ConfigStore with the file path of the YAML configuration file.

        :param file_path: The path to the YAML configuration file.
        """
        self.file_path = file_path
        self.config_data: Dict[str, Any] = self.load_config()
        self.auto_extend = auto_extend

    def load_config(self) -> Dict[str, Any]:
        """
        Loads configuration data from the YAML file.

        :return: A dictionary containing the configuration data.
        """
        with open(self.file_path, 'r') as file:
            try:
                config_data = yaml.safe_load(file)
                return config_data
            except yaml.YAMLError as exc:
                logging.error(f"Error in opening configuration file at {self.file_path}: {exc}")
                return {}

    def get(self, key: str, default=None) -> Any:
        """
        Retrieves a configuration value for a given key.

        :param default: Default value that should be returned if the key does not exist.
        :param key: The key of the configuration value.
        :return: The configuration value, or default if the key does not exist.
        """
        rvalue = self.config_data.get(key, None)
        if rvalue is None:
            default_value = self.config_data.get("default", None)
            if default_value is not None:
                self.config_data[key] = default
            if self.auto_extend:
                self.save_to_file()
            return default
        return rvalue

    def update(self, data: Dict[str, Any]) -> None:
        """
        Updates the configuration data with the provided data.

        :param data: A dictionary containing the data to update.
        """
        self.config_data.update(data)

    def set_config_value(self, key: str, data: Any) -> None:
        """
        Sets a configuration value for a given key.

        :param key: The key of the configuration value.
        :param data: The new configuration value.
        """
        self.config_data[key] = data

    def __getitem__(self, item: str) -> Any:
        """
        Allows dictionary-like access to configuration values.

        :param item: The key of the configuration value.
        :return: The configuration value.
        """
        return self.get(item)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Allows dictionary-like setting of configuration values.

        :param key: The key of the configuration value.
        :param value: The new configuration value.
        """
        self.set_config_value(key, value)

    def save_to_file(self) -> None:
        """
        Saves the current configuration data back to the YAML file.
        """
        with open(self.file_path, 'w') as file:
            yaml.dump(self.config_data, file)


class ConfigStoreManager:
    """
    A class to manage multiple ConfigStore instances.
    """
    _instances: Dict[str, ConfigStore] = {}

    MAIN_CONFIG_NAME = "MainConfig"
    LOGGING_CONFIG_NAME = "LoggingConfig"
    main_config = None
    logging_config = None

    @staticmethod
    def get_instance(configstore_name: str) -> Optional[ConfigStore]:
        """
        Retrieves a ConfigStore instance by name.

        :param configstore_name: The name of the ConfigStore instance.
        :return: The ConfigStore instance, or None if it does not exist.
        """
        return ConfigStoreManager._instances.get(configstore_name, None)

    @staticmethod
    def add(configstore_name: str, filepath: str, auto_extend=False) -> Union[ConfigStore, None]:
        """
        Creates a new ConfigStore instance and adds it to the manager.
        If a ConfigStore of same name exists, it is returned.

        :param configstore_name: The name of the new ConfigStore instance.
        :param filepath: The path to the YAML configuration file.
        :return: The new ConfigStore instance, or None if it already exists.
        """
        instance: Optional[ConfigStore] = ConfigStoreManager._instances.get(configstore_name, None)
        if instance is not None:
            return instance
        instance = ConfigStore(file_path=filepath, auto_extend=auto_extend)
        if instance is not None:
            ConfigStoreManager._instances[configstore_name] = instance
            logging.info(f"Created a new ConfigStore with name {configstore_name}")
            return instance
        else:
            logging.error(f"The config store {configstore_name} could not be created.")
            return None

    @staticmethod
    def __getitem__(item):
        """
        Retrieves a ConfigStore instance by its name using indexing syntax.

        :param item: The name of the ConfigStore instance.
        :return: The ConfigStore instance associated with the specified name.
        """
        return ConfigStoreManager.get_instance(item)

    @staticmethod
    def __setitem__(key, value):
        """
        Associates a ConfigStore instance with a specified name using indexing syntax.
        Only instances of ConfigStore are accepted; any other type will trigger an error message.

        :param key: The name to associate with the ConfigStore instance.
        :param value: The ConfigStore instance to be stored.
        """
        if type(value) is ConfigStore:
            ConfigStoreManager._instances[key] = value
        else:
            logging.error(f"Error: ConfigStoreManager only accepts ConfigStore instances, not {type(value)}")

    @classmethod
    def keys(cls):
        """
        Retrieves the names of all stored ConfigStore instances.

        :return: A view object displaying the names of all stored ConfigStore instances.
        """
        return cls._instances.keys()


if ConfigStoreManager.get_instance(ConfigStoreManager.MAIN_CONFIG_NAME) is None:
    ConfigStoreManager.add(configstore_name=ConfigStoreManager.MAIN_CONFIG_NAME,
                           filepath="config/config.yaml")
    main_config: ConfigStore = ConfigStoreManager.get_instance(ConfigStoreManager.MAIN_CONFIG_NAME)
    ConfigStoreManager.main_config = main_config
