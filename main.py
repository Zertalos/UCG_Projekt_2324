# This is a sample Python script.
import os.path

from src.ConfigManager.config_store import ConfigStoreManager
from src.datadownloader import DataDownloader
from src import  setup

import pandas as pd
import folium
import itertools




# Function to generate distinct colors
def get_colors(num_colors):
    colors = [
        "red", "blue", "green", "purple", "orange", "darkred",
        "lightred", "beige", "darkblue", "darkgreen", "cadetblue",
        "darkpurple", "white", "pink", "lightblue", "lightgreen",
        "gray", "black", "lightgray"
    ]
    return list(itertools.islice(itertools.cycle(colors), num_colors))




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    config_store = ConfigStoreManager()[ConfigStoreManager.MAIN_CONFIG_NAME]
    BASE_INPUT_FOLDER = config_store["input_folder"]
    BASE_OUTPUT_FOLDER = config_store["output_folder"]
    input_file = DataDownloader().filenames[0]
    # Load the CSV data into a DataFrame
    input_file_path = os.path.join(BASE_INPUT_FOLDER, input_file)
    data = pd.read_csv(input_file_path)

    # Create a map centered around the average latitude and longitude
    map_center = [data['lat'].mean(), data['lon'].mean()]
    car_map = folium.Map(location=map_center, zoom_start=12)

    # Generate colors for each car
    car_colors = get_colors(len(data['id'].unique()))

    # Iterate over each data point
    map_center = [data['lat'].mean(), data['lon'].mean()]
    car_map = folium.Map(location=map_center, zoom_start=12)

    # Generate colors for each car
    unique_cars = data['id'].unique()
    car_colors = get_colors(len(unique_cars))
    color_dict = dict(zip(unique_cars, car_colors))

    # Group by car ID and plot each car's points
    cars_amount = len(data.groupby('id'))
    i = 0
    for car_id, group in data.groupby('id'):
        color = color_dict[car_id]
        for _, row in group.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=3,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=f'Car ID: {car_id}, Time: {row["timestamp"]}'
            ).add_to(car_map)
        print(f" {i} / {cars_amount} done.")
        i += 1
        if i > 6:
            break
    # Save the map to an HTML file
    html_path = os.path.join(BASE_OUTPUT_FOLDER,"car_positions_map.html")
    car_map.save(html_path)
