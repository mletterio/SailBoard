from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd


class DataSource(ABC):
    """Abstract base class for all data sources."""

    @abstractmethod
    def fetch(self, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Fetch data for the given time range and return as DataFrame."""
        pass
