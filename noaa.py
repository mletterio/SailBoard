import requests


class NoaaClient:

    def __init__(self, lat, long):
        self.lat = lat
        self.long = long
        self.points_data = requests.get(f"https://api.weather.gov/points/{self.lat},{self.long}").json()
        self.grid_data_endpoint = self.points_data['properties']['forecastGridData']
        self.forecast_endpoint = self.points_data['properties']['forecast']
        print(f"GridPoint URL: {self.grid_data_endpoint}\nForecast URL: {self.forecast_endpoint}")

    def get_grid_data(self):
        grid_response = requests.get(self.grid_data_endpoint)
        return grid_response.json()

    def get_forecast_data(self):
        forecast_response = requests.get(self.forecast_endpoint)
        return forecast_response.json()
