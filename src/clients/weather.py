from datetime import datetime
import requests
import pandas as pd
from .base import DataSource


class NoaaWeatherClient(DataSource):
    """Fetches weather data from NOAA Weather API."""

    BASE_URL = "https://api.weather.gov/points"
    KPH_TO_KNOTS = 1 / 1.852

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
        self._init_endpoints()

    def _init_endpoints(self):
        response = requests.get(f"{self.BASE_URL}/{self.lat},{self.lon}")
        response.raise_for_status()
        props = response.json()['properties']
        self._grid_endpoint = props['forecastGridData']
        self._forecast_endpoint = props['forecast']

    def fetch(self, start_time: datetime, end_time: datetime, min_daytime_periods: int = 3) -> pd.DataFrame:
        wind_df = self._fetch_wind_data()
        forecast_df = self._fetch_forecast_data()

        wind_df = wind_df[(wind_df.index >= start_time) & (wind_df.index <= end_time)]

        forecast_df = forecast_df[forecast_df.index >= start_time]
        daytime_periods = forecast_df[forecast_df['is_daytime']]
        if len(daytime_periods) >= min_daytime_periods:
            extended_end = daytime_periods.iloc[min_daytime_periods - 1]['period_end']
            effective_end = max(end_time, extended_end)
        else:
            effective_end = end_time
        forecast_df = forecast_df[forecast_df.index <= effective_end]

        return self._merge(wind_df, forecast_df)

    def _fetch_wind_data(self) -> pd.DataFrame:
        response = requests.get(self._grid_endpoint)
        response.raise_for_status()
        props = response.json()['properties']

        gust_df = self._parse_values(props['windGust']['values'], 'wind_gust_kph')
        speed_df = self._parse_values(props['windSpeed']['values'], 'wind_speed_kph')

        wind_df = gust_df.join(speed_df, how='outer')
        wind_df['wind_gust_kts'] = wind_df['wind_gust_kph'] * self.KPH_TO_KNOTS
        wind_df['wind_speed_kts'] = wind_df['wind_speed_kph'] * self.KPH_TO_KNOTS

        return wind_df.sort_index()

    def _fetch_forecast_data(self) -> pd.DataFrame:
        response = requests.get(self._forecast_endpoint)
        response.raise_for_status()
        periods = response.json()['properties']['periods']

        records = []
        for p in periods:
            start = self._parse_iso(p['startTime'])
            records.append({
                'time': start,
                'period_name': p['name'],
                'is_daytime': p['isDaytime'],
                'temperature_f': p['temperature'],
                'wind_direction': p['windDirection'],
                'short_forecast': p['shortForecast'],
                'period_end': self._parse_iso(p['endTime'])
            })

        return pd.DataFrame(records).set_index('time').sort_index()

    def _merge(self, wind_df: pd.DataFrame, forecast_df: pd.DataFrame) -> pd.DataFrame:
        merged = forecast_df.copy()
        merged['wind_speed_avg_kts'] = None
        merged['wind_gust_max_kts'] = None

        for idx, row in merged.iterrows():
            mask = (wind_df.index >= idx) & (wind_df.index <= row['period_end'])
            period_wind = wind_df[mask]

            if not period_wind.empty:
                merged.at[idx, 'wind_speed_avg_kts'] = period_wind['wind_speed_kts'].mean()
                merged.at[idx, 'wind_gust_max_kts'] = period_wind['wind_gust_kts'].max()

        return merged

    def _parse_values(self, values: list, col_name: str) -> pd.DataFrame:
        records = [{'time': self._parse_valid_time(v['validTime']), col_name: v['value']} for v in values]
        return pd.DataFrame(records).set_index('time')

    @staticmethod
    def _parse_valid_time(valid_time: str) -> datetime:
        time_str = valid_time.split('/')[0]
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.replace(tzinfo=None)

    @staticmethod
    def _parse_iso(iso_str: str) -> datetime:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.replace(tzinfo=None)
