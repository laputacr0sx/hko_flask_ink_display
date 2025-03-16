from models.PeriodWeatherForecast import get_period_weather_forecast, WeatherForcastData


class PeriodWeatherForecastService:
    period_weather_forecast_data: WeatherForcastData
    hourly_temperature_forecast: list[float | None]

    def __init__(self):
        self.period_weather_forecast_data = get_period_weather_forecast()

    def set_hourly_temperature_forecast(self):
        self.hourly_temperature_forecast = [day.forecast_temperature for day in
                                            self.period_weather_forecast_data.hourly_weather_forecast]

