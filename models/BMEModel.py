from dataclasses import dataclass


@dataclass
class EnvironmentModel:
    temperature: float
    humidity: float
    pressure: float

    def __init__(self, temperature: float, humidity: float, pressure: float):
        self.temperature = temperature if temperature else 25.0
        self.humidity = humidity if humidity else 50.0
        self.pressure = pressure if pressure else 1013.25  # in hPa (hectopascals)
