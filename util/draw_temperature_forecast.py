import base64
from io import BytesIO

import matplotlib
from matplotlib.dates import date2num

matplotlib.use('Agg')  # Use the 'Agg' backend, which doesn't require a GUI

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from models.PeriodWeatherForecast import HourlyWeatherForecast


def create_temperature_plot(suitable_hourly_forecast: list[HourlyWeatherForecast]):
    # Clear any existing figures and axes
    plt.clf()
    plt.close()

    # Extract data
    hours = [forecast.forecast_hour for forecast in suitable_hourly_forecast]
    temperatures = [forecast.forecast_temperature for forecast in suitable_hourly_forecast]

    # Convert datetime to numeric format
    numeric_hours = date2num(hours)

    # Create the plot
    fig, ax = plt.subplots(figsize=(1.7, 0.8))

    try:
        font = {'family': 'Cubic 11', 'size': 4}
        plt.rc('font', **font)

        # Set a dark background
        plt.style.use('dark_background')

        # Plot the temperature line
        ax.plot(numeric_hours, temperatures, marker='o', linestyle='-', linewidth=1, markersize=1,
                color='#FFD700', markerfacecolor='#FF4500', markeredgecolor='white')

        # Customize the plot
        # ax.set_ylabel("°C", fontsize=12, fontweight='bold', color='white')

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))

        # Customize ticks
        ax.tick_params(axis='both', colors='white', which='both')

        # Add grid
        ax.grid(True, linestyle='--', alpha=0.3, color='gray')

        # Set y-axis limits with some padding
        temp_min, temp_max = min(temperatures), max(temperatures)
        ax.set_ylim(temp_min - 2, temp_max + 2)

        # Add value labels
        for i, temp in enumerate(temperatures):
            ax.annotate(f'{temp:.1f}°C', (numeric_hours[i], temp), textcoords="offset points",
                        xytext=(0, 10), ha='center', va='bottom', fontsize=4,
                        color='white', bbox=dict(facecolor='#1E90FF', edgecolor='none', pad=2))

        # Adjust layout
        plt.tight_layout()

        # Save the plot to a BytesIO object
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)

        # Close the figure to free up memory
        plt.close(fig)

        # Encode the image to base64
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    except Exception as e:
        print(f'Error creating temperature plot: {e}')
        return ''

    finally:
        # Ensure resources are release
        plt.close(fig)
        plt.clf()
        plt.close('all')
