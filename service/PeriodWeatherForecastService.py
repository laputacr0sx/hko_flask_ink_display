from models.PeriodWeatherForecast import get_period_weather_forecast


class PeriodWeatherForecastService:
    def __init__(self):
        self.period_weather_forecast_data = get_period_weather_forecast()
        self.hourly_temperature_forecast = [day.forecast_temperature for day in
                                            self.period_weather_forecast_data.hourly_weather_forecast]
