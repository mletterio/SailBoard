import time
from datetime import datetime, timedelta
import weather
from display import Display

if __name__ == "__main__":
    # Coordinates for 42.36°N, 71.04°W (Boston, MA)
    latitude = 42.36
    longitude = -71.04
    ePaper = Display()

    while True:
        weather_data = weather.merge_wind_data_with_forecast()
        weather.print_forecast_with_wind_data()
        weather_string = ""

        for i in range(3):
            weather_string += (f"{weather_data[i]['name']}:\n"
                               f"{weather_data[i]['averageTransportWindSpeed']:.2f}/"
                               f"{weather_data[i]['maxWindGust']:.2f} kts {weather_data[i]['windDirection']}\n")

        ePaper.clear_canvas()
        ePaper.write_header()
        ePaper.write_info(weather_string)
        ePaper.write_timestamp(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        ePaper.update_display()

        now = datetime.now()
        # Calculate the next 5-minute interval
        next_update = now + timedelta(minutes=60 - now.minute % 60, seconds=-now.second, microseconds=-now.microsecond)

        # Calculate the wait time
        wait_time = (next_update - now).total_seconds()

        # Sleep until the next update
        time.sleep(wait_time)
