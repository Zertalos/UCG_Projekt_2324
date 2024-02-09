import os
import shutil
import subprocess
import zipfile


def create_temp_directory(directory_path):
    """
    Creates a temporary directory if it does not already exist.

    Parameters:
    - directory_path (str): The path of the directory to be created.
    """
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
        
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)



def copy_items(src, dst, blacklist):
    """
    Copies files and directories from src to dst, excluding items in the blacklist.

    Parameters:
    - src (str): The source directory path.
    - dst (str): The destination directory path.
    - blacklist (list): A list of directory or file names to be excluded.
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if item in blacklist:
            continue
        if os.path.isdir(s):
            shutil.copytree(s, d, ignore=shutil.ignore_patterns(*blacklist))
        else:
            shutil.copy2(s, d)


def create_zip_file(source_dir, zip_filename):
    """
    Creates a zip file of the specified directory.

    Parameters:
    - source_dir (str): The directory to be zipped.
    - zip_filename (str): The filename for the created zip file.
    """
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, start=source_dir))
    print(f"Backup ZIP file created: {zip_filename}")

def generate_requirements_txt(project_path):
    """
    Generates a requirements.txt file for the given project path using pipreqs.

    Parameters:
    - project_path (str): The path of the project for which requirements.txt is to be generated.
    """
    try:
        subprocess.check_call(['pipreqs', project_path, '--force'])
        print("requirements.txt generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while generating requirements.txt: {e}")


def main():
    """
    Main function to execute the script.
    """
    os.chdir("../..")




if __name__ == '__main__':
    main()

import src.setup
from src.ConfigManager.config_store import ConfigStoreManager

source_path = "."
temp_path = 'temp'
config_store = ConfigStoreManager()[ConfigStoreManager.MAIN_CONFIG_NAME]
BASE_OUTPUT_FOLDER = config_store["output_folder"]

# Initialize the base folder structur
create_temp_directory("temp")

# Define the list of files and folders to exclude
BLACKLIST = ['venv', 'data', BASE_OUTPUT_FOLDER, config_store["input_folder"], ".idea", temp_path]
generate_requirements_txt(".")
# Create temp directory and copy items

copy_items(source_path, temp_path, BLACKLIST)

# Creating and removing the ZIP file
create_zip_file(temp_path, f"{BASE_OUTPUT_FOLDER}/UC Data Explorer.zip")
shutil.rmtree("temp")