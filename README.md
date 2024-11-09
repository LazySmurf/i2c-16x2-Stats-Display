# Raspberry Pi Stats Display
 For the i2c 16x2 LCD, written in Python


A script which shows the internal/external IP addresses of the Pi, the CPU usage % and temperature, RAM usage, and disk usage on a 16x2 LCD display using the i2c interface.


## Installation

The script has a few dependencies. If you're using Raspberry Pi OS, some of these may already be installed.

Remember to check your i2c port is set correctly in the rpi_lcd library. It is usually 27, but it can be different. For more help getting the screen and i2c interface set up, see [M Heidenreich's video](https://www.youtube.com/watch?v=DHbLBTRpTWM) on this topic.

Once your screen is working, you can install the dependencies for this script.


First, you will need pip3
```bash
  sudo apt install python-pip
```

Once you have pip installed, you can use it to install the remaining dependencies. You can choose to do this in a virtual environment, or system-wide. I chose to do it system-wide using the ```--break-system-packages``` argument, [which may or may not be risky](https://stackoverflow.com/a/75722775), so proceed at your own risk. Since these libraries do not install anything that will overwrite existing system or python files, it should be fine.

The next thing we need is rpi_lcd library to interface with the screen over the i2c bus. 
```bash
pip install rpi_lcd --break-system-packages
```

Next, we need the libraries we will use to gather system information. First, psutil:
```bash
pip install psutil --break-system-packages
```
followed by gpiozero:
```bash
pip install gpiozero --break-system-packages
```

and that's it!

## Running the script

The script should be able to be run now, but if you don't have permission, you can give it to yourself with:
```bash
chmod 777 Raspberry_Pi_1602_LCD_Stats.py
```
and then go ahead and run it with either:
```bash
./Raspberry_Pi_1602_LCD_Stats.py
```
or
```bash
python Raspberry_Pi_1602_LCD_Stats.py
```
## Acknowledgements

 - [M Heidenreich](https://github.com/mheidenreich/LCDDemo/blob/main/lcd-hello.py)
 - [Reegz](https://stackoverflow.com/a/71019862)
 - [maciek97x and Karl Knechtel](https://stackoverflow.com/a/75722775)
