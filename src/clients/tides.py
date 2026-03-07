from datetime import datetime
import requests
import pandas as pd
from .base import DataSource


class NoaaTidesClient(DataSource):
    """Fetches tide data from NOAA Tides and Currents API."""

    BASE_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

    def __init__(self, station_id: str):
        self.station_id = station_id

    def fetch(self, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Fetch high/low tide predictions for the given time range."""
        params = {
            'begin_date': start_time.strftime('%Y%m%d'),
            'end_date': end_time.strftime('%Y%m%d'),
            'station': self.station_id,
            'product': 'predictions',
            'datum': 'MLLW',
            'units': 'metric',
            'time_zone': 'gmt',
            'format': 'json',
            'interval': 'hilo'
        }

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if 'predictions' not in data:
            return pd.DataFrame()

        records = []
        for pred in data['predictions']:
            records.append({
                'time': datetime.strptime(pred['t'], '%Y-%m-%d %H:%M'),
                'tide_height_m': float(pred['v']),
                'tide_type': 'high' if pred['type'] == 'H' else 'low'
            })

        return pd.DataFrame(records).set_index('time').sort_index()

    def fetch_hourly(self, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Fetch hourly tide predictions for more granular data."""
        params = {
            'begin_date': start_time.strftime('%Y%m%d'),
            'end_date': end_time.strftime('%Y%m%d'),
            'station': self.station_id,
            'product': 'predictions',
            'datum': 'MLLW',
            'units': 'metric',
            'time_zone': 'gmt',
            'format': 'json',
            'interval': 'h'
        }

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if 'predictions' not in data:
            return pd.DataFrame()

        records = []
        for pred in data['predictions']:
            records.append({
                'time': datetime.strptime(pred['t'], '%Y-%m-%d %H:%M'),
                'tide_height_m': float(pred['v'])
            })

        df = pd.DataFrame(records).set_index('time').sort_index()
        df['tide_height_ft'] = df['tide_height_m'] * 3.28084
        return df
