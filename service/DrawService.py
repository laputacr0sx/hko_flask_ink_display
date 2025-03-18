import base64
import logging
import os
from datetime import datetime, timedelta
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from asset.font.cubic_font import font14, font48, font32, font18, font64, font40, font12, font24
from models.BMEModel import EnvironmentModel
from models.CurrentWeather import get_current_weather, CurrentWeather
from models.Gregorian import GregorianDate, get_gregorian_date
from models.Humidity import HumidityData, get_humidity_data
from models.PeriodWeatherForecast import get_period_weather_forecast, HourlyWeatherForecast
from models.Sun import get_sun_status
from models.UVIndex import get_uv_data
from models.WeatherForecast import get_weather_forecast, WeatherForecastData
from models.Wind import get_wind_data
from service import PIC_DIR
from util.draw_rainfall_plot import render_rainfall_chart
from util.draw_temperature_forecast import create_temperature_plot


class DrawService:
    EPD_HEIGHT: int
    EPD_WIDTH: int
    font: ImageFont.FreeTypeFont
    logger: logging.Logger
    main_image: Image.Image
    draw: ImageDraw.ImageDraw

    def __init__(self):
        self.EPD_HEIGHT = 480
        self.EPD_WIDTH = 800
        self.main_image = Image.new('RGB', (800, 480), "#000")
        self.draw = ImageDraw.Draw(self.main_image)
        self.logger = logging.getLogger("draw_service")

    def iterate_all_pic_dir_img(self, img: Image.Image, draw: ImageDraw.ImageDraw, directory_path):
        cell_dimension = 80
        rows, cols = self.EPD_HEIGHT // cell_dimension, self.EPD_WIDTH // cell_dimension

        icon_size = (72, 72)
        center_pos = (cell_dimension - icon_size[0]) // 2

        png_files = [file for file in os.listdir(directory_path) if file.endswith('.png')]

        idx = 0
        for y in range(rows):
            for x in range(cols):
                if idx >= len(png_files):
                    break
                else:
                    png_file_path = os.path.join(directory_path, png_files[idx])
                    idx += 1

                    icon = Image.open(png_file_path)
                    icon_pos = (
                        center_pos + x * cell_dimension,
                        center_pos + y * cell_dimension,
                    )
                    resized_icon = icon.resize(icon_size)

                    draw.rectangle(
                        (
                            icon_pos[0] - 1,
                            icon_pos[1] - 1,
                            1 + icon_pos[0] + icon_size[0],
                            1 + icon_pos[1] + icon_size[1],
                        ),
                        fill=0,
                    )

                    img.paste(resized_icon, icon_pos)

                    print(f'Loading {png_file_path}')

    def test_draw(self):
        logging.info("Drawing board...")

        self.iterate_all_pic_dir_img(self.main_image, self.draw, 'asset/img/pic')
        logging.info("Display Image")
        buffered = BytesIO()
        buffered.seek(0)
        self.main_image.save(buffered, format="png")
        encoded_img = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return encoded_img

    def dates(self, location: str, now: str, gregorian: GregorianDate):
        location_length = len(location)
        current_date_length = len(now)

        number_of_digits = sum(c.isdigit() for c in now) + 2
        number_of_chinese_char = current_date_length - number_of_digits

        location_x_position = 800 - (location_length * 48 + (location_length - 1) * 4 + 2)
        date_x_position = 800 - (
                number_of_chinese_char * 32
                + number_of_digits * 16
                + (current_date_length - 1) * 2
                + 2
        )

        self.draw.text((location_x_position, 2), location, font=font48, fill="#FFF")
        self.draw.text((date_x_position, 54), now, font=font32, fill="#FFF")

        gregorian_date = (
            f'{gregorian.lunar_year[:3]}{gregorian.lunar_date}[{gregorian.lunar_year[4:5]}]'
        )
        greg_date_length = len(gregorian_date)
        greg_x_position = 800 - (
                (greg_date_length - 2) * 18 + 2 * 9 + (greg_date_length - 1) * 2 + 2
        )

        self.draw.text((greg_x_position, 92), gregorian_date, font=font18, fill="#FFF")

    def major_weather(self, weather, humidity):
        # Render weather icon

        icon = Image.open(os.path.join(PIC_DIR, f'{weather.icon[0]}.png'))
        icon_pos = (20, 0)
        icon_size = (220, 220)
        resized_icon = icon.resize(icon_size)
        self.main_image.paste(resized_icon, icon_pos)
        temperature_bounding_box = self.draw.textbbox(
            (278, 2),
            f'{weather.temperature.data[0].value}',
            font=font64,
            anchor=None,
            spacing=4,
            align='left',
            direction=None,
            features=None,
            language=None,
            stroke_width=0,
            embedded_color=False,
            font_size=None,
        )
        humidity_bounding_box = self.draw.textbbox(
            (278, 68),
            f'{humidity.humidity}',
            font=font48,
            anchor=None,
            spacing=4,
            align='left',
            direction=None,
            features=None,
            language=None,
            stroke_width=0,
            embedded_color=False,
            font_size=None,
        )

        # Render temperature
        self.draw.text(
            (278, 2), f'{weather.temperature.data[0].value:.00f}', font=font64, fill="#FFF"
        )
        self.draw.text((temperature_bounding_box[2] + 2, 14), 'o', font=font18, fill="#FFF")
        self.draw.text((temperature_bounding_box[2] + 10, 17), 'C', font=font48, fill="#FFF")
        # Render humidity
        self.draw.text((278, 68), f'{humidity.humidity}', font=font48, fill="#FFF")
        self.draw.text((humidity_bounding_box[2], 82), '%', font=font32, fill="#FFF")

    def in_house_weather(self, env: EnvironmentModel):
        top_left = (self.EPD_WIDTH - 388, 4)
        bottom_right = (self.EPD_WIDTH - 260, 130)
        # self.draw.rectangle(
        #     (top_left, bottom_right),
        #     '#8e8e8e',
        #     0,
        #     2,
        # )

        house_tip = (top_left[0] + (bottom_right[0] - top_left[0]) // 2, 10)
        left_wall = (top_left[0] + 8, top_left[1] + 50)
        left_ground = (left_wall[0], bottom_right[1] - 6)
        right_ground = (bottom_right[0] - 8, bottom_right[1] - 6)
        right_wall = (right_ground[0], left_wall[1])

        # Drawing house
        self.draw.polygon(
            ([house_tip, left_wall, left_ground, right_ground, right_wall]),
            "#FFF",
            "#FFF",
            4,
        )
        self.draw.line((left_wall, right_wall), "#FFF", 4)
        # Drawing window frame
        self.draw.rectangle(
            (
                (house_tip[0] - 10, house_tip[1] + 20),
                (house_tip[0] + 10, house_tip[1] + 40),
            ),
            "#FFF",
            0,
            3,
        )
        # Drawing window cross
        self.draw.line(
            ((house_tip[0], house_tip[1] + 20), (house_tip[0], house_tip[1] + 40)), 0, 2
        )
        self.draw.line(
            (
                (house_tip[0] - 10, house_tip[1] + 30),
                (house_tip[0] + 10, house_tip[1] + 30),
            ),
            0,
            2,
        )

        # Drawing chimney
        chimney_bottom_left = (house_tip[0] + 27, house_tip[1] + 21)
        chimney_top_right = (chimney_bottom_left[0] + 14, chimney_bottom_left[1] - 19)
        self.draw.line(
            (chimney_bottom_left, (chimney_bottom_left[0], chimney_bottom_left[1] - 19)),
            "#FFF",
            3,
        )
        self.draw.line(
            (
                (
                    (chimney_bottom_left[0], chimney_bottom_left[1] - 19),
                    chimney_top_right,
                )
            ),
            "#FFF",
            3,
        )
        self.draw.line(
            (
                chimney_top_right,
                (chimney_top_right[0], chimney_bottom_left[1] + 12),
            ),
            "#FFF",
            3,
        )
        self.draw.arc(
            (
                (chimney_top_right[0] - 8, chimney_top_right[1] - 10),
                (chimney_top_right[0] + 28, chimney_top_right[1] - 2),
            ),
            150,
            30,
            "#FFF",
            2,
        )
        self.draw.arc(
            (
                (chimney_top_right[0] + 4, chimney_top_right[1] - 4),
                (chimney_top_right[0] + 20, chimney_top_right[1] + 2),
            ),
            start=150,
            end=30,
            fill="#FFF",
            width=2,
        )
        # draw.arc([55, -10, 85, 10], start=30, end=150, fill=0, width=2)
        # draw.arc([50, -20, 90, 0], start=30, end=150, fill=0, width=2)

        # Drawing Temperature & Humidity Text
        degree_pos = (left_wall[0] + 2, left_ground[1] - 70)
        self.draw.text(degree_pos, f'{env.temperature:.01f}', font=font40, fill=0)
        self.draw.text((degree_pos[0] + 84, degree_pos[1] + 14), 'o', font=font12, fill=0)
        self.draw.text((degree_pos[0] + 90, degree_pos[1] + 15), 'C', font=font24, fill=0)

        humidity_pos = (left_ground[0] + 4, left_ground[1] - 26)
        inhouse_humidity_bb = self.draw.textbbox(
            humidity_pos,
            f'{env.humidity:0.1f}',
            font=font24,
            anchor=None,
            spacing=4,
            align='left',
            direction=None,
            features=None,
            language=None,
            stroke_width=0,
            embedded_color=False,
            font_size=None,
        )

        self.draw.text(humidity_pos, f'{env.humidity:0.1f}', font=font24, fill=0)
        self.draw.text((inhouse_humidity_bb[2], humidity_pos[1] + 11), '%', font=font12, fill=0)

    def render_header_section(
            self,
            gregorian: GregorianDate,
            weather: CurrentWeather,
            humidity: HumidityData,
            location: str,
            now: str,
            env: EnvironmentModel,
    ):
        self.major_weather(weather, humidity)
        self.dates(location, now, gregorian)
        self.in_house_weather(env)

    def render_forecast_section(
            self, forecast: WeatherForecastData, draw: ImageDraw.ImageDraw, image: Image.Image
    ):
        MINIMUM_WIDTH = 74
        FORECAST_SECTION_COORD = (272, 130)
        FORECAST_LENGTH = 5
        maximum_cell_width = (self.EPD_WIDTH - FORECAST_SECTION_COORD[0]) // FORECAST_LENGTH

        forecast_cell_width = (
            maximum_cell_width if (maximum_cell_width > MINIMUM_WIDTH) else MINIMUM_WIDTH
        )

        for i in range(FORECAST_LENGTH):
            curr_cast = forecast.weather_forecast[i]
            x1 = FORECAST_SECTION_COORD[0] + i * forecast_cell_width
            y1 = FORECAST_SECTION_COORD[1]

            # date_str = curr_cast.forecast_date
            htemp = curr_cast.forecast_maxtemp.value
            ltemp = curr_cast.forecast_mintemp.value

            hhum = curr_cast.forecast_maxrh.value
            lhum = curr_cast.forecast_minrh.value

            weather_icon = Image.open(f'{PIC_DIR}/{curr_cast.forecast_icon}.png')
            icon_size = (48, 48)
            resize_weather_icon = weather_icon.resize(icon_size)

            icon_offset = (22, 28)
            image.paste(resize_weather_icon, (x1 + icon_offset[0], y1 + icon_offset[1]))

            # draw.rectangle(
            #     (
            #         x1 + icon_offset[0],
            #         y1 + icon_offset[1],
            #         x1 + icon_offset[0] + icon_size[0],
            #         y1 + icon_offset[1] + icon_size[1],
            #     ),
            #     outline=0,
            #     width=1,
            # )

            # Draw border of each forecast cell
            # draw.rectangle((x1, y1, x2, y2), outline=0, width=1)

            # Draw weekday text , ie 一， 二，三...
            draw.text((x1 + 44, y1 + 2), f'{curr_cast.week[2]}', font=font24, fill="#FFF")

            # Draw TEMPERATURE text
            draw.text((x1 + 70, y1 + 28), f'{htemp:.0f}', font=font24, fill="#D74040")
            draw.text((x1 + 70, y1 + 54), f'{ltemp:.0f}', font=font24, fill="#2B80BE")

            # Draw HUMIDITY text
            draw.text((x1 + icon_offset[0], y1 + 78), f'{lhum:.0f}', font=font12, fill='#FFF')
            draw.text(
                (x1 + icon_offset[0] + 30, y1 + 78), f'{hhum:.0f}', font=font12, fill="#FFF"
            )

    @staticmethod
    def get_record_time_diff(curr: datetime, record_time: datetime) -> float:
        time_difference: timedelta = curr - record_time
        total_minutes: float = time_difference.total_seconds() // 60

        return total_minutes

    def get_now_str(self, now: datetime):
        chinese_months = [
            '一月',
            '二月',
            '三月',
            '四月',
            '五月',
            '六月',
            '七月',
            '八月',
            '九月',
            '十月',
            '十一月',
            '十二月',
        ]

        chinese_weekdays = ['一', '二', '三', '四', '五', '六', '日']

        month = now.month
        day = now.day
        weekday = chinese_weekdays[now.weekday()]

        return f'{month}月{day}日({weekday})'

    def render_rainfall_section(self, image: Image.Image, suitable_hourly_forecast: list[HourlyWeatherForecast]):
        rainfall_bytes = render_rainfall_chart()

        if rainfall_bytes is None:
            temperature_bytes = create_temperature_plot(suitable_hourly_forecast)
            chart = Image.open(BytesIO(base64.b64decode(temperature_bytes)))
        else:
            chart = Image.open(BytesIO(base64.b64decode(rainfall_bytes)))
        # resized_chart = chart.resize((500, 240), Image.Resampling.LANCZOS)
        image.paste(chart, (290, 220))

    def render_minor_dashboard(self, wind, uv, sun, draw, image):
        valid_data = [
            [
                {
                    'icon_uri': '80.png',
                    'name': f'{wind.station}風速',
                    'data': f'{wind.avg_wind_speed}',
                    'unit': f'{wind.wind_direction}',
                },
                {
                    'icon_uri': 'sunrise.png',
                    'name': '日出時間',
                    'data': sun.rise,
                    'unit': None,
                },
            ],
            [
                {
                    'icon_uri': 'uv.png',
                    'name': '紫外線指數',
                    # "data": weather.uvindex.data[0].value,
                    'data': uv.uv_index,
                    'unit': f"@{uv.datetime.strftime('%H:%M')}",
                },
                {
                    'icon_uri': 'sunset.png',
                    'name': '日落時間',
                    'data': sun.set,
                    'unit': None,
                },
            ],
        ]

        ROW = 2
        COL = 2
        top_left_x = 2
        top_left_y = 358
        cell_width = 150
        cell_height = 64

        for i in range(ROW):
            for j in range(COL):
                x1 = top_left_x + i * cell_width
                y1 = top_left_y + j * cell_height

                cell = valid_data[i][j]
                name = cell['name']
                data = cell['data']
                icon = cell['icon_uri'] or 'na.png'
                unit = cell['unit'] or ''

                data_length = len(data) if type(data) is str else len(str(abs(data)))

                draw.text((x1 + 48, y1), f'{name}', font=font12, fill="#FFF")
                draw.text((x1 + 48, y1 + 16), f'{data}', font=font32, fill="#FFF")
                draw.text(
                    (x1 + 48 + data_length * 14 + 4, y1 + cell_height - 30),
                    unit,
                    font=font14,
                    fill="#FFF",
                )

                icon = Image.open(os.path.join(PIC_DIR, icon))
                resized_icon = icon.resize((48, 48))
                image.paste(resized_icon, (x1, y1 + 8))

    def render_footer_section(self, draw, time_diff, now):
        draw.text((390, 464), f"資料更新於: {time_diff:.0f} 分鐘前", font=font12, fill="#8C8C8C")
        draw.text(
            (620, 464), f"渲染於:{now.strftime('%Y-%m-%d %H:%M:%S')}", font=font12, fill="#8C8C8C"
        )

    def render_alerts_section(self, draw, alerts):
        pass

    def render_color_image(self):
        logging.info('Gathering System Information')

        logging.info('Reading from BME280')
        env = EnvironmentModel(temperature=27.9, humidity=63.4, pressure=1009.5)
        logging.info('Environment Data GOT!')

        now: datetime = datetime.now()
        logging.info('Current Datetime GOT! ')

        weather = get_current_weather()
        logging.info('Current Weather GOT! ')

        forecast = get_weather_forecast()
        logging.info('Weather forecast GOT! ')

        uv = get_uv_data()[0]
        logging.info('UV Data GOT! ')

        wind = get_wind_data()
        logging.info('Wind Data GOT!')

        sun = get_sun_status()
        logging.info('Sun Data GOT!')

        weather_info = get_period_weather_forecast(current_time=datetime.now())
        hourly_forecast = weather_info.hourly_weather_forecast
        suitable_hourly_forecast = [forecast for forecast in hourly_forecast if
                                    datetime.now() < forecast.forecast_hour < datetime.now() + timedelta(hours=6)]

        time_diff = self.get_record_time_diff(now, weather.temperature.record_time)

        humidity = get_humidity_data()
        logging.info('Humidity Data GOT!')

        greg = get_gregorian_date()
        logging.info('Gregorian Date GOT!')

        location = '沙田馬鞍山'
        now_str = self.get_now_str(now)

        logging.info('Rendering different sections...')
        self.render_header_section(
            greg, weather, humidity, location, now_str, env
        )
        self.render_forecast_section(forecast, self.draw, self.main_image)
        self.render_rainfall_section(self.main_image, suitable_hourly_forecast)
        self.render_minor_dashboard(wind, uv, sun, self.draw, self.main_image)
        self.render_footer_section(self.draw, time_diff, now)
        # self.render_alerts_section()

        logging.info('Rendering Process Finished')

        logging.info('Display Image')
        # self.main_image.show()

        buffered = BytesIO()
        buffered.seek(0)
        self.main_image.save(buffered, format="png")
        encoded_img = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return encoded_img
