import os
from typing import LiteralString

import pandas as pd
from pandas import Timedelta

from src.ConfigManager.config_store import ConfigStoreManager
from src.datadownloader import DataDownloader


def get_prepared_input_data(file_location: str) -> None | pd.DataFrame:
    loaded_data = load_input_data(file_location)
    prepare_input_data(loaded_data)
    return loaded_data


def load_input_data(file_location: str) -> pd.DataFrame:
    return pd.read_csv(file_location)


def prepare_input_data(data: pd.DataFrame):
    data['timestamp'] = pd.to_datetime(data['timestamp'], format="%Y-%m-%dT%H:%M:%S.000Z")


def create_empty_target_data_frame(original_data: pd.DataFrame, new_columns: list = None) -> pd.DataFrame:
    if not new_columns:
        new_columns = []
    original_columns: list = original_data.columns.tolist()
    target_columns: list = original_columns + new_columns
    return pd.DataFrame(columns=target_columns)


if __name__ == '__main__':
    main_config_store = ConfigStoreManager()[ConfigStoreManager.MAIN_CONFIG_NAME]
    seperate_singles_config_store = ConfigStoreManager.add("seperate_singles", "config/seperate_singles.yaml")
    # Konfigurations- und Dateipfade (Beispielwerte)
    BASE_INPUT_FOLDER = main_config_store["input_folder"]
    BASE_OUTPUT_FOLDER = main_config_store["output_folder"]
    # Set input file location
    input_file = DataDownloader().filenames[0]

    # Laden der CSV-Daten in einen DataFrame
    input_file_path: str = str(os.path.join(BASE_INPUT_FOLDER, input_file))
    data: pd.DataFrame = get_prepared_input_data(input_file_path)

    # Erstellen des leeren DataFrames zur Speicherung der Einzelfahrten
    trip_data_frame: pd.DataFrame = create_empty_target_data_frame(data, ['Fahrtnummer', 'Typ'])

    time_threshold = seperate_singles_config_store["time_threshold"]
    min_data_points = seperate_singles_config_store["min_data_points"]
    fahrt_id = 0

    count_cars =17000
    processed_cars = 0
    pd.options.mode.copy_on_write = False
    pd.options.mode.chained_assignment = None

    data = data.sort_values(by=['id', 'timestamp'], ascending=True)

    for car_id, group in data.groupby('id', as_index=False):
        # Get data for that car_id
        group.reset_index(drop=True, inplace=True)
        trip_start_index = 0
        last_time_stamp = group['timestamp'][trip_start_index]
        for row in group.index:
            current_time_stamp = group['timestamp'][row]
            time_difference: Timedelta = current_time_stamp - last_time_stamp
            if time_difference.seconds > time_threshold or row == len(group.index) - 1:
                count_data_points = row - trip_start_index - 1
                # Neue Fahrt erkannt
                if count_data_points > min_data_points:
                    # Fahrt aus mehr als min_data_points
                    # Damit handelt es sich um eine Fahrt die gespeichert werden muss.
                    trip_end_index = trip_start_index + count_data_points - 1
                    trip_data_index_start = len(trip_data_frame)
                    trip_data_index_end = trip_end_index + count_data_points
                    trip_data_frame = trip_data_frame._append(group.loc[trip_start_index:trip_end_index],
                                                              ignore_index=True)
                    trip_data_frame.loc[trip_data_index_start:trip_data_index_end, 'Fahrtnummer'] = fahrt_id
                    fahrt_id += 1
                trip_start_index = row
            last_time_stamp = group['timestamp'][row]
        processed_cars += 1
        print(f"Processed {processed_cars} / {count_cars} Cars.")
    trip_data_frame.sort_values(['Fahrtnummer', 'timestamp']).to_csv(path_or_buf=f"{BASE_OUTPUT_FOLDER}/single2_data.csv", index=False)
    print("finished")
