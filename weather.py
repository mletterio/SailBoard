import json
from datetime import datetime
from noaa import NoaaClient

weather = NoaaClient(lat=42.36, long=-71.04)


# Function to convert kph to knots
def kph_to_knots(kph):
    return kph / 1.852


# Example usage
def merge_wind_data_with_forecast():
    grid_data = weather.get_grid_data()
    forecast_data = weather.get_forecast_data()

    wind_gusts = grid_data['properties']['windGust']['values']
    transport_winds = grid_data['properties']['windSpeed']['values']
    periods = forecast_data['properties']['periods']

    # Convert wind gusts to a dictionary with datetime keys for easier lookup
    wind_gusts_dict = {datetime.strptime(wind_gust['validTime'][:16], "%Y-%m-%dT%H:%M"): wind_gust['value']
                       for wind_gust in wind_gusts}

    # Convert transport wind speeds to a dictionary with datetime keys for easier lookup
    transport_winds_dict = {
        datetime.strptime(transport_wind['validTime'][:16], "%Y-%m-%dT%H:%M"): transport_wind['value']
        for transport_wind in transport_winds}

    for period in periods:
        if not period['isDaytime']:
            continue  # Skip periods where isDaytime is False

        period_start_time = datetime.strptime(period['startTime'][:16], "%Y-%m-%dT%H:%M")
        period_end_time = datetime.strptime(period['endTime'][:16], "%Y-%m-%dT%H:%M")

        # Find the maximum wind gust within the forecast period
        max_wind_gust = None
        for gust_time, gust_value in wind_gusts_dict.items():
            if period_start_time <= gust_time <= period_end_time:
                if max_wind_gust is None or gust_value > max_wind_gust:
                    max_wind_gust = gust_value

        # Calculate average transport wind speed within the forecast period
        total_transport_wind_speed = 0
        count_transport_wind_speed = 0
        for transport_time, transport_value in transport_winds_dict.items():
            if period_start_time <= transport_time <= period_end_time:
                total_transport_wind_speed += transport_value
                count_transport_wind_speed += 1

        average_transport_wind_speed = total_transport_wind_speed / count_transport_wind_speed if count_transport_wind_speed > 0 else None

        # Convert the maximum wind gust to knots
        if max_wind_gust is not None:
            max_wind_gust = kph_to_knots(max_wind_gust)

        # Convert average transport wind speed to knots
        if average_transport_wind_speed is not None:
            average_transport_wind_speed = kph_to_knots(average_transport_wind_speed)

        period['maxWindGust'] = max_wind_gust
        period['averageTransportWindSpeed'] = average_transport_wind_speed

    return [period for period in periods if period['isDaytime']]


def print_forecast_with_wind_data():
    merged_data = merge_wind_data_with_forecast()

    for i, forecast_day in enumerate(merged_data):
        print(f"Date: {forecast_day['startTime']} to {forecast_day['endTime']}")
        print(f"{forecast_day['name']}")
        print(f"Forecast: {forecast_day['shortForecast']}")
        print(f"Temperature: {forecast_day['temperature']} °F")
        print(f"Wind Direction: {forecast_day['windDirection']}")

        # Include wind gust data if available
        if forecast_day['maxWindGust'] is not None:
            print(f"Max Wind Gust: {forecast_day['maxWindGust']:.2f} knots")

        # Include average transport wind speed data if available
        if forecast_day['averageTransportWindSpeed'] is not None:
            print(f"Wind Speed: {forecast_day['averageTransportWindSpeed']:.2f} knots")

        print("-" * 30)


print_forecast_with_wind_data()
