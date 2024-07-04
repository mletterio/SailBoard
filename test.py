import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

# NOAA API endpoint
api_endpoint = "https://graphical.weather.gov/xml/SOAP_server/ndfdXMLclient.php"

# Define the parameters for the API request
params = {
    "whichClient": "NDFDgen",
    "lat": 41.25,  # Latitude for ANZ230 (approximate center)
    "lon": -70.0,  # Longitude for ANZ230 (approximate center)
    "product": "time-series",
    "begin": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
    "end": (datetime.now(timezone.utc) + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S'),
    "Unit": "e",  # e for English units, m for Metric units
    "maxt": "maxt",  # Max temperature
    "mint": "mint",  # Min temperature
    "wgust": "wgust",  # Wind gust
    "wdir": "wdir",  # Wind direction
    "pop12": "pop12",  # 12-hour Probability of Precipitation
    "wspd": "wspd",  # Wind speed
    "ptotsvrtstm": "ptotsvrtstm"  # Probability of Severe Thunderstorms
}

# Make the API request
response = requests.get(api_endpoint, params=params)
response.raise_for_status()

# Parse the XML response
root = ET.fromstring(response.content)


# Function to extract data for a specific variable and their timestamps with matching time layout key
def extract_data(root, variable_name):
    data_list = []

    # Extract time layout mappings
    time_layout_map = {}
    for time_layout in root.findall(".//time-layout"):
        layout_key = time_layout.find("layout-key").text
        start_times = [start_time.text for start_time in time_layout.findall("start-valid-time")]
        end_times = [end_time.text if end_time is not None else None for end_time in time_layout.findall("end-valid-time")]
        time_layout_map[layout_key] = {'start-time': start_times, 'end-times': end_times}

    # Extract data for the specified variable
    for parameter in root.findall(".//parameters"):
        if parameter.find(variable_name) is not None:
            layout_key = parameter.find(variable_name).get("time-layout")
            if layout_key in time_layout_map:
                layout_info = time_layout_map[layout_key]
                start_times = layout_info['start-time']
                end_times = layout_info['end-times']
                values = parameter.find(variable_name).findall("value")
                for i, value in enumerate(values):
                    start_time = start_times[i] if i < len(start_times) else None
                    end_time = end_times[i] if i < len(end_times) else None
                    data_list.append({
                        'start-time': start_time,
                        'end-time': end_time,
                        'value': value.text,
                        'unit': parameter.find(variable_name).get('units')
                    })

    return data_list


# Extract data for each variable
max_temps = extract_data(root, "temperature[@type='maximum']")
min_temps = extract_data(root, "temperature[@type='minimum']")
wind_gusts = extract_data(root, "wind-speed[@type='gust']")
wind_dirs = extract_data(root, "direction")
pop12 = extract_data(root, "probability-of-precipitation[@type='12 hour']")
wind_speeds = extract_data(root, "wind-speed[@type='sustained']")
ptotsvrtstm = extract_data(root, "convective-hazard/severe-component[@type='severe thunderstorms']")

# Print the data in a structured format
print("Max Temperatures:")
for data in max_temps:
    print(data)

print("\nMin Temperatures:")
for data in min_temps:
    print(data)

print("\nWind Gusts:")
for data in wind_gusts:
    print(data)

print("\nWind Directions:")
for data in wind_dirs:
    print(data)

print("\nProbability of Precipitation (12-hour):")
for data in pop12:
    print(data)

print("\nWind Speeds (Sustained):")
for data in wind_speeds:
    print(data)

print("\nProbability of Severe Thunderstorms:")
for data in ptotsvrtstm:
    print(data)
