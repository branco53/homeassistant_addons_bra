import time
import socket
import psutil
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont

# OLED setup
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=128, height=64)

font = ImageFont.load_default()

def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "No IP"

def get_temp():
    try:
        # Raspberry Pi typical path
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp = int(f.read()) / 1000
            return f"{temp:.1f}C"
    except:
        return "N/A"

while True:
    # Create image
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)

    # System data
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    ip = get_ip()
    temp = get_temp()
    host = socket.gethostname()

    # Draw text (6 lines max)
    draw.text((0, 0), f"{host}", font=font, fill=255)
    draw.text((0, 10), f"CPU: {cpu}%", font=font, fill=255)
    draw.text((0, 20), f"TEMP: {temp}", font=font, fill=255)
    draw.text((0, 30), f"RAM: {ram}%", font=font, fill=255)
    draw.text((0, 40), f"DSK: {disk}%", font=font, fill=255)
    draw.text((0, 50), f"IP: {ip}", font=font, fill=255)

    # Display
    device.display(image)

    # Refresh every 2 sec (10 cycles ≈ 20 sec)
    time.sleep(2)
