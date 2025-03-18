from datetime import datetime

from models.PeriodWeatherForecast import get_period_weather_forecast


class PeriodWeatherForecastService:

    def __init__(self):
        self.period_weather_forecast_data = get_period_weather_forecast(datetime.now())

    def get_hourly_temperature_forecast(self):
        return [day.forecast_temperature for day in
                self.period_weather_forecast_data.hourly_weather_forecast]
