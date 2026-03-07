import os
from dotenv import load_dotenv

load_dotenv()

LATITUDE = float(os.getenv('LATITUDE', 42.36))
LONGITUDE = float(os.getenv('LONGITUDE', -71.04))
TIDE_STATION_ID = os.getenv('TIDE_STATION_ID', '8443970')
MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN', '')
