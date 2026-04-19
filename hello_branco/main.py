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
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "No IP"

def get_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000
    except:
        return 0

def draw_bar(draw, x, y, width, height, percent):
    filled = int((percent / 100.0) * width)
    draw.rectangle((x, y, x + width, y + height), outline=255, fill=0)
    draw.rectangle((x, y, x + filled, y + height), outline=255, fill=255)

while True:
    # SYSTEM DATA
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    temp = get_temp()
    ip = get_ip()
    host = socket.gethostname()

    # -------- PAGE 1: CPU + TEMP --------
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)

    draw.text((0, 0), "CPU & TEMP", font=font, fill=255)

    draw.text((0, 12), f"CPU: {cpu:.0f}%", font=font, fill=255)
    draw_bar(draw, 0, 22, 120, 8, cpu)

    draw.text((0, 36), f"TEMP: {temp:.1f}C", font=font, fill=255)
    
    # Map temp to % (0–100C → 0–100%)
    temp_percent = min(max(temp, 0), 100)
    draw_bar(draw, 0, 46, 120, 8, temp_percent)

    device.display(image)
    time.sleep(6)

    # -------- PAGE 2: RAM + DISK --------
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)

    draw.text((0, 0), "MEMORY", font=font, fill=255)

    draw.text((0, 12), f"RAM: {ram:.0f}%", font=font, fill=255)
    draw_bar(draw, 0, 22, 120, 8, ram)

    draw.text((0, 36), f"DSK: {disk:.0f}%", font=font, fill=255)
    draw_bar(draw, 0, 46, 120, 8, disk)

    device.display(image)
    time.sleep(6)

    # -------- PAGE 3: HOST + IP --------
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)

    draw.text((0, 0), "NETWORK", font=font, fill=255)

    draw.text((0, 16), f"{host}", font=font, fill=255)
    draw.text((0, 32), f"{ip}", font=font, fill=255)

    device.display(image)
    time.sleep(6)
