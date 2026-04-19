from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
import time

# Initialize I2C (usually address 0x3C)
serial = i2c(port=1, address=0x3C)

# IMPORTANT: 128x64 display
device = ssd1306(serial, width=128, height=64)

# Create image buffer
image = Image.new("1", (device.width, device.height))
draw = ImageDraw.Draw(image)

# Clear screen
draw.rectangle((0, 0, 128, 64), outline=0, fill=0)

# Load default font
font = ImageFont.load_default()

# Write text
draw.text((0, 0), "Hello Branco!", font=font, fill=255)
draw.text((0, 20), "128x64 OK", font=font, fill=255)

# Display
device.display(image)

# Keep running
while True:
    time.sleep(60)
