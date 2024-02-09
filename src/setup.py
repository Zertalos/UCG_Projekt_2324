import os

from src.ConfigManager.config_store import ConfigStoreManager

config_store = ConfigStoreManager()[ConfigStoreManager.MAIN_CONFIG_NAME]
BASE_INPUT_FOLDER = config_store["input_folder"]
BASE_OUTPUT_FOLDER = config_store["output_folder"]

setup_already_ran = config_store.get("setup_ran", False)

if not setup_already_ran:
    for folder in [BASE_INPUT_FOLDER, BASE_OUTPUT_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)

config_store.set_config_value("setup_ran", True)