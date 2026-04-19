
import os
import requests

SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
    "Content-Type": "application/json",
}

import subprocess

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

def get_wifi_signal():
    try:
        output = subprocess.check_output("iw dev wlan0 link", shell=True).decode()

        for line in output.split("\n"):
            if "signal" in line:
                # example: signal: -55 dBm
                dbm = int(line.split("signal:")[1].split("dBm")[0].strip())
                
                # convert dBm to percentage (approx)
                percent = min(max(2 * (dbm + 100), 0), 100)
                return percent, f"{dbm} dBm"

        return 0, "no signal"
    except:
        return 0, "no wifi"

def get_uptime():
    try:
        with open("/proc/uptime") as f:
            seconds = int(float(f.read().split()[0]))

        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60

        return f"{days}d {hours}h {minutes}m"
    except:
        return "N/A"

def get_host():
    try:
        r = requests.get("http://supervisor/host/info", headers=HEADERS)
        return r.json()["data"]["hostname"]
    except Exception as e:
        return "no-host"


def get_ip():
    try:
        r = requests.get("http://supervisor/network/info", headers=HEADERS)
        interfaces = r.json()["data"]["interfaces"]

        for iface in interfaces:
            ipv4 = iface.get("ipv4", {})
            addr = ipv4.get("address")
            if addr:
                return addr[0].split("/")[0]

        return "0.0.0.0"
    except Exception as e:
        return "no-ip"
        
def get_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000
    except:
        return 0

def draw_metric(draw, label, value, percent, y):
    # Label (left)
    draw.text((6, y), label, font=font_small, fill=255)

    # Value (right aligned better)
    draw.text((88, y), value, font=font_small, fill=255)

    # MORE SPACE before bar (was +10 → now +14)
    draw_bar(draw, 6, y + 14, 116, 6, percent)

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
    
    draw_metric(draw, "CPU", f"{cpu:.0f}%", cpu, 10)
    draw_metric(draw, "TEMP", f"{temp:.1f}C", temp, 34)
    
    device.display(image)
    time.sleep(6)

    # ===== PAGE 2: MEMORY =====
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)
    
    center_text(draw, "Memory", 0, font_small)
    
    draw_metric(draw, "RAM", f"{ram:.0f}%", ram, 10)
    draw_metric(draw, "DISK", f"{disk:.0f}%", disk, 34)
    
    device.display(image)
    time.sleep(6)

    # ===== PAGE 3: NETWORK =====
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)
    
    center_text(draw, "Network", 0, font_small)
    
    center_text(draw, host, 18, font_big)
    center_text(draw, ip, 42, font_small)
    
    device.display(image)
    time.sleep(6)

    # ===== PAGE 4: WiFi =====    
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)
    
    center_text(draw, "WiFi", 0, font_small)
    
    wifi_percent, wifi_text = get_wifi_signal()
    
    center_text(draw, wifi_text, 18, font_small)
    
    draw_bar(draw, 6, 40, 116, 10, wifi_percent)
    
    device.display(image)
    time.sleep(6)

    # ===== PAGE 5: Uptime ===== 
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)
    
    center_text(draw, "Uptime", 0, font_small)
    
    uptime = get_uptime()
    
    center_text(draw, uptime, 28, font_big)
    
    device.display(image)
    time.sleep(6)
