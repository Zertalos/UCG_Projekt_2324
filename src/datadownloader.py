"""
This module provides functionality for downloading data files from specified URLs.
It uses a configuration store to manage settings related to downloading, including
URLs and the input folder location. The module is designed to work with a 
ConfigStoreManager to retrieve configuration details.
"""

import os
import requests
import src.setup
from src.ConfigManager.config_store import ConfigStoreManager

# Initialize and add configuration for the downloader
ConfigStoreManager.add(configstore_name="downloader", filepath="config/DataDownloader.yaml", auto_extend=True)

class DataDownloader:
    """
    A class for downloading data files from URLs specified in a configuration file.

    Attributes:
        config: Instance of the configuration store for the downloader.
        enabled: Boolean indicating if auto-download is enabled.
        input_folder: Folder path where downloaded files are saved.
        filenames: List of filenames of successfully downloaded files.
    """

    def __init__(self):
        """
        Initializes the DataDownloader, loads configuration, and starts the download process if enabled.
        """
        self.config = ConfigStoreManager.get_instance(configstore_name="downloader")
        self.enabled = self.config.get("enable_auto_download", True)
        url_list = self.config.get("data_url", None)

        if url_list is None and self.enabled:
            raise ValueError("No download URL was given. Configure 'data_url' in DataDownloader.yaml, or disable auto download.")

        config_store = ConfigStoreManager()[ConfigStoreManager.MAIN_CONFIG_NAME]
        self.input_folder = config_store["input_folder"]
        self.filenames = [self.__download_file(url) for url in url_list] if url_list else []

    def __download_file(self, url: str) -> str:
        """
        Downloads a file from the specified URL and saves it to the input folder.

        Parameters:
            url (str): URL from where the file should be downloaded.

        Returns:
            str: Filename of the downloaded file.

        Raises:
            ConnectionError: If the download fails due to network issues or incorrect URL.
        """
        response = requests.get(url)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to download data from {url}. Check the network connection or URL.")

        filename = url.split("/")[-1]
        save_path = os.path.join(self.input_folder, filename)

        with open(save_path, 'wb') as file:
            file.write(response.content)
        return filename
