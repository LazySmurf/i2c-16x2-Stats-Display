#!/usr/bin/python3
print("\nStarting 1602 stats script...\n")

"""
16x2 i2c LCD Stats Script
Written by LazySmurf Development
Based on: https://github.com/mheidenreich/LCDDemo/blob/main/lcd-hello.py

Dependencies:
pip install rpi_lcd
pip install psutil
pip install gpiozero
"""

#Import necessary libraries
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD
from gpiozero import CPUTemperature
import socket
import os
import re
import time
import psutil

#Create instance of the LCD to manipulate
lcd = LCD()

#Update the display to know it's working before the rest of the script runs
#Mostly useful on very slow computers
lcd.text("Stats script", 1)
lcd.text("started running", 2)

#Get INTERNAL IP
def getIntIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local = s.getsockname()[0]
    s.close()
    return local
print("Int IP: " + getIntIP())

#Get EXTERNAL IP
def getExtIP():
    rawip = os.popen("curl -s icanhazip.com").read() # Grab IP from icanhazip.com
    matchip = re.search("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$", rawip) # remove any characters that aren't the IP (sometimes a newline character at the end)
    ip = matchip.group(0) # select the match
    return ip
print("Ext IP: " + getExtIP())

#Get CPU Info
def getCPU():
    cpu = str(psutil.cpu_percent()) + '%'
    return cpu
def getTemp():
    temp = str(round(float(CPUTemperature().temperature), 1))
    return temp

#Get RAM Info
def getRAM():
    memory = psutil.virtual_memory()
    #bytes -> kilobytes -> megabytes
    usedmem = int(round((memory.total - memory.free)/1024.0/1024.0, 1))
    totalmem = int(round(memory.total/1024.0/1024.0, 1))
    memstring = str(usedmem) + " / " + str(totalmem) + " MB"
    return memstring

#Get Disk Info
def getDisk():
    disk = psutil.disk_usage('/')
    #bytes -> kilobytes -> megabytes -> gigabytes
    useddisk = round((disk.total - disk.free)/1024.0/1024.0/1024.0, 1)
    totaldisk = round(disk.total/1024.0/1024.0/1024.0, 1)
    diskstring = str(useddisk) + " / " + str(totaldisk) + " GB"
    return diskstring

def safe_exit(signum, frame):
    exit(1)

#Main program loop
try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    count = 1 # Sometimes Python doesn't like while(true) so instead we do it this way
    while (count > 0):

        #Show IP Addresses
        lcd.text(getIntIP(), 1)
        lcd.text(getExtIP(), 2)

        time.sleep(5) # Wait 5 seconds to show next screen

        #Show CPU Info
        lcd.text("CPU Use:  " + getCPU(), 1)
        lcd.text("CPU Temp: " + getTemp() + chr(223) + "C", 2) #chr(223) is the degrees symbol

        time.sleep(5) # Wait 5 seconds to show next screen

        #Show RAM info
        lcd.text("Memory Usage", 1)
        lcd.text(getRAM(), 2)

        time.sleep(5) # Wait 5 seconds to show next screen

        lcd.text("Disk Usage", 1)
        lcd.text(getDisk(), 2)

        time.sleep(5) # Wait 5 seconds to show first screen again
    pause()

except KeyboardInterrupt:
    pass

finally:
    lcd.text("Stats script", 1)
    lcd.text("stopped running", 2)
    # Instead of having an error message when the script stops,
    # you can instead clear the screen. In this case, it is more
    # helpful to know the script stopped running since it is headless.
    #lcd.clear()
    print("\nClosing 1602 stats script!\n")