import sys
import time
from datetime import datetime, timedelta
import socket

from data_manager import SailingDataManager
from display import InkyDisplay, BoardLayout


def has_internet(host="8.8.8.8", port=53, timeout=3) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def main():
    display = InkyDisplay()
    sailing_data = SailingDataManager()
    layout = BoardLayout(display)

    while not has_internet():
        time.sleep(10)

    while True:
        if has_internet():
            sailing_data.fetch(days=3)
            forecast = sailing_data.get_daytime_forecast(num_days=3)
            tides = sailing_data.get_next_tides(4)

            wind_dir   = forecast.iloc[0].get('wind_direction', 'N')   if not forecast.empty else 'N'
            wind_speed = forecast.iloc[0].get('wind_speed_avg_kts', 0) if not forecast.empty else 0

            layout.render(forecast, tides, wind_dir, wind_speed, datetime.now())
            display.show()

        now = datetime.now()
        next_update = now + timedelta(minutes=2 - now.minute % 2, seconds=-now.second, microseconds=-now.microsecond)
        time.sleep((next_update - now).total_seconds())


if __name__ == "__main__":
    sys.exit(main())
