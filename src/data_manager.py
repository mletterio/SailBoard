from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

from clients import NoaaWeatherClient, NoaaTidesClient
import config


class SailingDataManager:
    """Unified data manager for sailing weather and tide information."""

    def __init__(
        self,
        lat: float = config.LATITUDE,
        lon: float = config.LONGITUDE,
        tide_station: str = config.TIDE_STATION_ID
    ):
        self.lat = lat
        self.lon = lon
        self._weather_client = NoaaWeatherClient(lat, lon)
        self._tides_client = NoaaTidesClient(tide_station)

        self._weather_df: Optional[pd.DataFrame] = None
        self._tides_df: Optional[pd.DataFrame] = None
        self._unified_df: Optional[pd.DataFrame] = None

    def fetch(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        days: int = 3
    ) -> pd.DataFrame:
        """Fetch all sailing data for the specified time range."""
        if start_time is None:
            start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if end_time is None:
            end_time = start_time + timedelta(days=days)

        self._weather_df = self._weather_client.fetch(start_time, end_time)
        self._tides_df = self._tides_client.fetch(start_time, end_time)
        self._unified_df = self._create_unified_dataframe()

        return self._unified_df

    def _create_unified_dataframe(self) -> pd.DataFrame:
        if self._weather_df is None or self._weather_df.empty:
            return pd.DataFrame()

        unified = self._weather_df.copy()

        if self._tides_df is not None and not self._tides_df.empty:
            unified = self._merge_tide_data(unified, self._tides_df)

        return unified

    def _merge_tide_data(self, weather_df: pd.DataFrame, tides_df: pd.DataFrame) -> pd.DataFrame:
        weather_df = weather_df.copy()
        weather_df['next_tide_time'] = None
        weather_df['next_tide_type'] = None
        weather_df['next_tide_height_m'] = None

        for idx in weather_df.index:
            future_tides = tides_df[tides_df.index >= idx]
            if not future_tides.empty:
                next_tide = future_tides.iloc[0]
                weather_df.at[idx, 'next_tide_time'] = future_tides.index[0]
                weather_df.at[idx, 'next_tide_type'] = next_tide['tide_type']
                weather_df.at[idx, 'next_tide_height_m'] = next_tide['tide_height_m']

        return weather_df

    @property
    def weather(self) -> Optional[pd.DataFrame]:
        return self._weather_df

    @property
    def tides(self) -> Optional[pd.DataFrame]:
        return self._tides_df

    @property
    def unified(self) -> Optional[pd.DataFrame]:
        return self._unified_df

    def get_daytime_forecast(self, num_days: int = 3) -> pd.DataFrame:
        if self._unified_df is None:
            self.fetch()
        daytime = self._unified_df[self._unified_df['is_daytime'] == True]
        return daytime.head(num_days)

    def get_next_tides(self, count: int = 4) -> pd.DataFrame:
        if self._tides_df is None:
            self.fetch()
        now = datetime.now()
        future_tides = self._tides_df[self._tides_df.index >= now]
        return future_tides.head(count)
