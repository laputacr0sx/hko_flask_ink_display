import os
from io import BytesIO
from PIL import ImageFont
from pathlib import Path


CUBIC_FONT_PATH = str(Path("asset/font/Cubic_11.ttf"))

font20 = ImageFont.truetype(CUBIC_FONT_PATH, 20)
font64 = ImageFont.truetype(CUBIC_FONT_PATH, 64)
font48 = ImageFont.truetype(CUBIC_FONT_PATH, 48)
font40 = ImageFont.truetype(CUBIC_FONT_PATH, 40)
font32 = ImageFont.truetype(CUBIC_FONT_PATH, 32)
font24 = ImageFont.truetype(CUBIC_FONT_PATH, 24)
font18 = ImageFont.truetype(CUBIC_FONT_PATH, 18)
font14 = ImageFont.truetype(CUBIC_FONT_PATH, 14)
font12 = ImageFont.truetype(CUBIC_FONT_PATH, 12)
