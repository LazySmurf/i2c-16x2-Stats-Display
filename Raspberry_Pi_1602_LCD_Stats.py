#!/usr/bin/python3

print("\nStarting 16x2 stats script...\n")

"""
16x2 I2C LCD Stats Script
Written by LazySmurf Development
Based on: https://github.com/mheidenreich/LCDDemo/blob/main/lcd-hello.py

Dependencies:
pip install rpi_lcd
pip install psutil
pip install gpiozero

Display synchronization:
Each page is assigned to an absolute 5-second time slot.
This means multiple Pis will display the same page at the same
time, regardless of when their individual scripts were started.
"""

# Import necessary libraries
from signal import signal, SIGTERM, SIGHUP
from rpi_lcd import LCD
from gpiozero import CPUTemperature
import socket
import os
import re
import time
import psutil
from datetime import datetime

# Create instance of the LCD to manipulate
lcd = LCD()

# Update the display to know it's working before the rest of the script runs
# Mostly useful on very slow computers
lcd.text("     Welcome to", 1)
lcd.text("      Lightning", 2)

# ------------------------------------------------------------
# SYSTEM INFORMATION
# ------------------------------------------------------------
# Get INTERNAL IP
def getIntIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        local = s.getsockname()[0]
    finally:
        s.close()

    return local

# Get EXTERNAL IP
def getExtIP():
    rawip = os.popen("curl -s icanhazip.com").read()
    matchip = re.search(
        "^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$",
        rawip.strip()
    )

    if matchip:
        return matchip.group(0)

    return "???.???.???.???"

# Get CPU Info
def getCPU():
    cpu = str(psutil.cpu_percent()) + '%'
    return cpu

# Get CPU Temperature
def getTemp():
    temp = str(round(float(CPUTemperature().temperature), 1))
    return temp

# Get RAM Info
def getRAM():
    memory = psutil.virtual_memory()
    # bytes -> kilobytes -> megabytes
    usedmem = int(round((memory.total - memory.free) / 1024.0 / 1024.0, 1))
    totalmem = int(round(memory.total / 1024.0 / 1024.0, 1))
    memstring = str(usedmem) + " / " + str(totalmem) + " MB"
    return memstring

# Get Disk Info
def getDisk():
    disk = psutil.disk_usage('/')
    # bytes -> kilobytes -> megabytes -> gigabytes
    useddisk = round((disk.total - disk.free) / 1024.0 / 1024.0 / 1024.0, 1)
    totaldisk = round(disk.total / 1024.0 / 1024.0 / 1024.0, 1)
    diskstring = str(useddisk) + " / " + str(totaldisk) + " GB"
    return diskstring

# ------------------------------------------------------------
# SIGNAL HANDLING
# ------------------------------------------------------------
# Gracefully exit when systemd stops the service
def safe_exit(signum, frame):
    raise SystemExit

# ------------------------------------------------------------
# DISPLAY SYNCHRONIZATION
# ------------------------------------------------------------
# Number of pages
PAGE_COUNT = 6
# How long each page is displayed, in seconds
PAGE_DURATION = 5

def get_current_page():
    """Calculate which page should currently be displayed."""
    time_slot = int(time.time() // PAGE_DURATION)
    return time_slot % PAGE_COUNT

def get_next_page_time():
    """Return the Unix timestamp at which the next page begins."""
    current_time = time.time()
    next_slot = (int(current_time // PAGE_DURATION) + 1) * PAGE_DURATION
    return next_slot

# ------------------------------------------------------------
# DISPLAY PAGES
# ------------------------------------------------------------
def display_page(page):
    """Display the requested page on the LCD."""

    if page == 0:
        # Hostname
        lcd.text("Hostname:", 1)
        lcd.text(socket.gethostname(), 2)

    elif page == 1:
        # IP Addresses
        lcd.text(getIntIP(), 1)
        lcd.text(getExtIP(), 2)

    elif page == 2:
        # Date and Time
        lcd.text(datetime.now().strftime("%b %d, %Y"), 1)
        lcd.text(datetime.now().strftime("%I:%M:%S %p"), 2)

    elif page == 3:
        # CPU Info
        lcd.text("CPU Use:  " + getCPU(), 1)
        lcd.text("CPU Temp: " + getTemp() + chr(223) + "C", 2)

    elif page == 4:
        # RAM Info
        lcd.text("Memory Usage", 1)
        lcd.text(getRAM(), 2)

    elif page == 5:
        # Disk Info
        lcd.text("Disk Usage", 1)
        lcd.text(getDisk(), 2)

# ------------------------------------------------------------
# DATE/TIME PAGE
# ------------------------------------------------------------
def update_datetime_page():
    """Update the date/time display."""
    lcd.text(datetime.now().strftime("%b %d, %Y"), 1)
    lcd.text(datetime.now().strftime("%I:%M:%S %p"), 2)

# ------------------------------------------------------------
# MAIN PROGRAM LOOP
# ------------------------------------------------------------
try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    last_page = None

    while True:
        current_page = get_current_page()

        # ----------------------------------------------------
        # DATE/TIME PAGE
        # ----------------------------------------------------
        if current_page == 2:
            print("Displaying page 2 at " + datetime.now().strftime("%H:%M:%S"))

            # Update the date/time once per second while
            # this page is active.
            while get_current_page() == 2:
                update_datetime_page()
                time.sleep(1)

            # Page has changed. Return to the main loop.
            last_page = None
            continue

        # ----------------------------------------------------
        # NORMAL PAGES
        # ----------------------------------------------------
        if current_page != last_page:
            print("Displaying page " + str(current_page) + " at " + datetime.now().strftime("%H:%M:%S"))
            display_page(current_page)
            last_page = current_page

        # Calculate how long until the next 5-second boundary.
        next_page = get_next_page_time()
        sleep_time = next_page - time.time()

        # Protect against extremely small/negative values.
        if sleep_time < 0.05:
            sleep_time = 0.05

        time.sleep(sleep_time)

except KeyboardInterrupt:
    pass

finally:
    lcd.text("Connection to", 1)
    lcd.text("screen lost :(", 2)
    print("\nClosing 16x2 stats script!\n")
