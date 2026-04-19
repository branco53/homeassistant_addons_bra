
import os

SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
HEADERS = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}

import time
import socket
import psutil
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont


# OLED setup
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=128, height=64)

# Fonts
font_small = ImageFont.load_default()
try:
    font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except:
    font_big = font_small

# Helpers
def center_text(draw, text, y, font):
    w, h = draw.textbbox((0, 0), text, font=font)[2:]
    draw.text(((128 - w) // 2, y), text, font=font, fill=255)

def get_host():
    try:
        r = requests.get("http://supervisor/host/info", headers=HEADERS)
        return r.json()["data"]["hostname"]
    except:
        return "unknown"


def get_ip():
    try:
        r = requests.get("http://supervisor/network/info", headers=HEADERS)
        interfaces = r.json()["data"]["interfaces"]
        for i in interfaces:
            if i["ipv4"]["address"]:
                return i["ipv4"]["address"][0].split("/")[0]
        return "0.0.0.0"
    except:
        return "no ip"
        
def get_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000
    except:
        return 0

def draw_bar(draw, x, y, width, height, percent):
    # outline
    draw.rectangle((x, y, x + width, y + height), outline=255, fill=0)
    # fill
    filled = int((percent / 100.0) * (width - 2))
    draw.rectangle((x + 1, y + 1, x + 1 + filled, y + height - 1), fill=255)

# Main loop
while True:
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    temp = get_temp()
    ip = get_ip()
   # host = socket.gethostname()
    host = get_host()

    # ===== PAGE 1: CPU + TEMP =====
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)

    center_text(draw, "System", 0, font_small)

    # CPU
    draw.text((4, 14), "CPU", font=font_small, fill=255)
    draw.text((90, 14), f"{cpu:.0f}%", font=font_small, fill=255)
    draw_bar(draw, 4, 24, 120, 8, cpu)

    # TEMP
    draw.text((4, 38), "TEMP", font=font_small, fill=255)
    draw.text((80, 38), f"{temp:.1f}C", font=font_small, fill=255)
    temp_percent = min(max(temp, 0), 100)
    draw_bar(draw, 4, 48, 120, 8, temp_percent)

    device.display(image)
    time.sleep(6)

    # ===== PAGE 2: MEMORY =====
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)

    center_text(draw, "Memory", 0, font_small)

    # RAM
    draw.text((4, 14), "RAM", font=font_small, fill=255)
    draw.text((90, 14), f"{ram:.0f}%", font=font_small, fill=255)
    draw_bar(draw, 4, 24, 120, 8, ram)

    # DISK
    draw.text((4, 38), "DISK", font=font_small, fill=255)
    draw.text((90, 38), f"{disk:.0f}%", font=font_small, fill=255)
    draw_bar(draw, 4, 48, 120, 8, disk)

    device.display(image)
    time.sleep(6)

    # ===== PAGE 3: NETWORK =====
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)

    center_text(draw, "Network", 0, font_small)

    center_text(draw, host, 18, font_big)
    center_text(draw, ip, 40, font_small)

    device.display(image)
    time.sleep(6)
