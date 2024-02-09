import os
from datetime import datetime

import pandas as pd
import folium
import itertools

from src.ConfigManager.config_store import ConfigStoreManager
from src.datadownloader import DataDownloader


# Funktion, um unterschiedliche Farben zu generieren
def get_colors(num_colors):
    colors = [
        "red", "blue", "green", "purple", "orange", "darkred",
        "lightred", "beige", "darkblue", "darkgreen", "cadetblue",
        "darkpurple", "white", "pink", "lightblue", "lightgreen",
        "gray", "black", "lightgray"
    ]
    return list(itertools.islice(itertools.cycle(colors), num_colors))


class CoordTools:
    def __init__(self, data, quantile=0.01):
        self.border_quantile = quantile
        self.min_lat = data['lat'].min()
        self.min_lon = data['lon'].min()
        self.max_lat = data['lat'].max()
        self.max_lon = data['lon'].max()
        self.splat = self.max_lat - self.min_lat
        self.splon = self.max_lon - self.min_lon
        self.qslat = self.border_quantile * self.splat
        self.qslon = self.border_quantile * self.splon
        self.nthresh = self.max_lat - self.qslat  # north threshold
        self.ethresh = self.max_lon - self.qslon  # ...
        self.sthresh = self.min_lat + self.qslat
        self.wthresh = self.min_lon + self.qslon

        self.format_string = "%Y-%m-%dT%H:%M:%S.000Z"

        # Erstellen einer Karte zentriert um den durchschnittlichen Breiten- und Längengrad
        map_center = [data['lat'].mean(), data['lon'].mean()]
        self.car_map = folium.Map(location=map_center, zoom_start=12)

    def in_center(self, lat, lon):
        # only expecting values according to min and max
        return self.sthresh <= lat <= self.nthresh and self.wthresh <= lon <= self.ethresh

    def at_border(self, lat, lon):
        return not self.in_center(lat, lon)

    def add_car(self, row):
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=1,
            popup=""  # f'Ende: Car ID {car_id}, Time: {row["timestamp"]}'
        ).add_to(car_map)

    def to_time(self, time_string):
        return datetime.strptime(time_string, self.format_string)

    def to_typ(self, el_start, el_end):
        start = self.in_center(float(el_start['lat']), float(el_start['lon']))
        end = self.in_center(float(el_end['lat']), float(el_end['lon']))
        if (start and end):
            return "innen"
        elif (start and not end):
            return "raus"
        elif (not start and end):
            return "rein"
        elif (not start and not end):
            return "durch"


if __name__ == '__main__':
    config_store = ConfigStoreManager()[ConfigStoreManager.MAIN_CONFIG_NAME]
    # Konfigurations- und Dateipfade (Beispielwerte)
    BASE_INPUT_FOLDER = config_store["input_folder"]
    BASE_OUTPUT_FOLDER = config_store["output_folder"]
    input_file = DataDownloader().filenames[0]

    # Laden der CSV-Daten in einen DataFrame
    input_file_path = os.path.join(BASE_INPUT_FOLDER, input_file)
    data = pd.read_csv(input_file_path)

    original_columns = data.columns.tolist()

    new_columns = original_columns + ['Fahrtnummer'] + ['Typ']

    single_data: pd.DataFrame = pd.DataFrame(columns=new_columns)

    # Farben für jedes Auto generieren
    unique_cars = data['id'].unique()
    car_colors = get_colors(len(unique_cars))
    color_dict = dict(zip(unique_cars, car_colors))

    max_cars = 999999999
    # Iterieren über jede Car_ID und deren Punkte
    max_cars = data.nunique(0)[0]
    car_count = 0
    fahrt_id = 0
    data['timestamp'] = pd.to_datetime(data['timestamp'], format="%Y-%m-%dT%H:%M:%S.000Z")

    time_threshold = 300  # in seconds
    ct = CoordTools(data, 0.04)  # scalar for border size
    stats = {'innen': 0, 'durch': 0, 'rein': 0, 'raus': 0}

    for car_id, group in data.groupby('id'):
        # Hält den Start Datensatz der aktuellen Fahrt parat.
        single_start_index = 0
        group = group.sort_values('timestamp')

        # setting initial start time
        first_point = group.iloc[0]
        prev_time = first_point['timestamp']
        prev_time = ct.to_time(prev_time)

        # for i, el in enumerate(group.iterrows()):
        for i in range(len(group)):
            current_timestamp = ct.to_time(group.iloc[i]['timestamp'])
            time_diff = (current_timestamp - prev_time).seconds

            if time_diff > time_threshold or i == len(group) - 1:
                # Fahrtende erkannt. bzw. letzter Datensatz des Fahrzeugs
                if i - single_start_index > 1:
                    new_index_start = len(single_data)
                    new_index_end = new_index_start + i - single_start_index
                    single_data = single_data._append(group.iloc[single_start_index:i], ignore_index=True)
                    typ = ct.to_typ(group.iloc[single_start_index], group.iloc[i])
                    for j in range(new_index_start, new_index_end):
                        single_data.loc[j, 'Fahrtnummer'] = fahrt_id
                        single_data.loc[j, 'Typ'] = typ
                    # single_data[new_index_start:new_index_end, 'Fahrtnummer'] = fahrt_id
                    # print(f"Fahrtnummer: {fahrt_id}, erstellt.")
                    fahrt_id += 1
                single_start_index = i
                stats[typ] += 1  # use some panda count fnc instead
            prev_time = current_timestamp
        car_count = car_count + 1
        # if car_count > 5:
        #    break
        print(f"{car_count} / {max_cars} finished.")

    print(f"Innen: {stats['innen']}, Durch: {stats['durch']}, Rein: {stats['rein']}, Raus: {stats['raus']} ")
    # single_data['lon'] -= ct.min_lon #for now dont normalize, so we can look at the data - maybe do it in the machinelearning part instead
    # single_data['lat'] -= ct.min_lat
    single_data.to_csv(path_or_buf=f"{BASE_OUTPUT_FOLDER}/single_data.csv", index=False)

    # Speichern der Karte als HTML-Datei
    html_path = os.path.join(BASE_OUTPUT_FOLDER, "car_start_and_end.html")
    ct.car_map.save(html_path)
