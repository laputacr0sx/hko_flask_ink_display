from models.CurrentWeather import get_current_weather


class HKOService:

    def current_weather(self):
        return get_current_weather()
