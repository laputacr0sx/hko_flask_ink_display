from dataclasses import dataclass
from datetime import datetime
import time
from typing import Optional, List

import requests


@dataclass
class DailyForecast:
    forecast_date: datetime
    forecast_chance_of_rain: str
    forecast_daily_weather: int
    forecast_maximum_temperature: float
    forecast_minimum_temperature: float


@dataclass
class HourlyWeatherForecast:
    forecast_hour: datetime
    forecast_relative_humidity: Optional[float]
    forecast_temperature: Optional[float]
    forecast_wind_direction: Optional[int]
    forecast_wind_speed: Optional[float]
    forecast_weather: Optional[int]


@dataclass
class WeatherForcastData:
    last_modified: datetime
    station_code: str
    latitude: float
    longitude: float
    model_time: datetime
    daily_forecast: List[DailyForecast]
    hourly_weather_forecast: List[HourlyWeatherForecast]


def get_period_weather_forecast(current_time: datetime) -> WeatherForcastData:
    print("getting period weather forecast at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    params = {"v": current_time.strftime("%Y%m%d%H%M"), "t": int(time.time())}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://maps.weather.gov.hk/ocf/text_e.html?mode=0&station=SHA",
        "Connection": "keep-alive",
        "Cookie": "i18n_redirected=en",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "no-cache",  # Add this to prevent caching
        "Pragma": "no-cache",  # Add this for older browsers
    }
    forecast_url = "https://maps.weather.gov.hk/ocf/dat/SHA.xml"
    res = requests.get(forecast_url, params=params, headers=headers)
    res.raise_for_status()
    current_json = res.json()
    print("Period weather forecast got!")

    return WeatherForcastData(
        last_modified=datetime.strptime(str(current_json["LastModified"]), "%Y%m%d%H%M%S"),
        station_code=current_json["StationCode"],
        latitude=current_json["Latitude"],
        longitude=current_json["Longitude"],
        model_time=datetime.strptime(str(current_json["ModelTime"]), "%Y%m%d%H"),
        daily_forecast=[
            DailyForecast(
                forecast_date=datetime.strptime(forecast["ForecastDate"], "%Y%m%d"),
                forecast_chance_of_rain=forecast["ForecastChanceOfRain"],
                forecast_daily_weather=forecast["ForecastDailyWeather"],
                forecast_maximum_temperature=forecast["ForecastMaximumTemperature"],
                forecast_minimum_temperature=forecast["ForecastMinimumTemperature"],
            )
            for forecast in current_json["DailyForecast"]
        ],
        hourly_weather_forecast=[HourlyWeatherForecast(
            forecast_hour=datetime.strptime(forecast["ForecastHour"], "%Y%m%d%H"),
            forecast_relative_humidity=forecast.get("ForecastRelative_humidity"),
            forecast_temperature=forecast.get("ForecastTemperature"),
            forecast_wind_direction=forecast.get("ForecastWindDirection"),
            forecast_wind_speed=forecast.get("ForecastWindSpeed"),
            forecast_weather=forecast.get("ForecastWeather")
        )
            for forecast in current_json["HourlyWeatherForecast"]]
    )
