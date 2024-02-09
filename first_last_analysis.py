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

if __name__ == '__main__':
    config_store = ConfigStoreManager()[ConfigStoreManager.MAIN_CONFIG_NAME]
    # Konfigurations- und Dateipfade (Beispielwerte)
    BASE_INPUT_FOLDER = config_store["input_folder"]
    BASE_OUTPUT_FOLDER = config_store["output_folder"]
    input_file = DataDownloader().filenames[0]

    # Laden der CSV-Daten in einen DataFrame
    input_file_path = os.path.join(BASE_INPUT_FOLDER, input_file)
    data = pd.read_csv(input_file_path)

    # Erstellen einer Karte zentriert um den durchschnittlichen Breiten- und Längengrad
    map_center = [data['lat'].mean(), data['lon'].mean()]
    car_map = folium.Map(location=map_center, zoom_start=12)

    # Farben für jedes Auto generieren
    unique_cars = data['id'].unique()
    car_colors = get_colors(len(unique_cars))
    color_dict = dict(zip(unique_cars, car_colors))

    max_cars = 999999999
    # Iterieren über jede Car_ID und deren Punkte
    for car_id, group in data.groupby('id'):
        color = color_dict[car_id]
        first_point = group.iloc[0]
        last_point = group.iloc[-1]

        # Hinzufügen der Anfangs- und Endpunkte
        folium.CircleMarker(
            location=[first_point['lat'], first_point['lon']],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=1,
            popup=f'Start: Car ID {car_id}, Time: {first_point["timestamp"]}'
        ).add_to(car_map)

        folium.CircleMarker(
            location=[last_point['lat'], last_point['lon']],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=1,
            popup=f'Ende: Car ID {car_id}, Time: {last_point["timestamp"]}'
        ).add_to(car_map)


        start_time = first_point['timestamp']
        format_string = "%Y-%m-%dT%H:%M:%S.000Z"
        start_time = datetime.strptime(start_time, format_string)

        end_time =  last_point['timestamp']
        end_time = datetime.strptime(end_time, format_string)

        time_diff = end_time - start_time

        # Verbindungslinie zwischen den Punkten zeichnen
        line_points = [[first_point['lat'], first_point['lon']], [last_point['lat'], last_point['lon']]]
        #line_points = [group[['lat', 'lon']].values.tolist()]
        folium.PolyLine(line_points, color=color, weight=2.5, opacity=1).add_to(car_map)
        max_cars = max_cars - 1
        if max_cars < 0:
            break

    # Speichern der Karte als HTML-Datei
    html_path = os.path.join(BASE_OUTPUT_FOLDER, "car_start_and_end.html")
    car_map.save(html_path)