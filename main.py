# Anastopoulos Theocharis @2024
from mq9 import MQ
from machine import Pin, I2C
from time import sleep
import lcd

# Initialize the MQ sensor
mq = MQ()

# Initialize LEDs and buzzer
green_led = Pin(2, Pin.OUT)
red_led = Pin(0, Pin.OUT)
buzzer = Pin(15, Pin.OUT)

# Turn on the green LED to indicate the ESP8266 is running
green_led.on()

# Initialize the I2C bus and LCD
i2c = I2C(scl=Pin(5), sda=Pin(4))
lcd = lcd.LCD1602(i2c)

# Function to display sensor readings on the LCD
def display_lcd(lpg, ch4):
    lcd.clear()
    lcd.print("LPG: {:.2f} ppm".format(lpg), 0, 0)
    lcd.print("CH4: {:.2f} ppm".format(ch4), 0, 1)

# Display startup message on LCD
lcd.clear()
lcd.print("LPG&CH4-T.Anasto", 0, 0)

sleep(3)  # Display message for 3 seconds
lcd.clear()
lcd.print("Warming up..")
sleep(120)  # 2 minutes of warm-up time (for more accurate readings raise this number)
# Clear LCD after startup message
lcd.clear()

# Main loop
while True:
    perc = mq.MQPercentage()
    lpg = perc["GAS_LPG"]
    ch4 = perc["CH4"]

    print("LPG: %g ppm, CH4: %g ppm" % (lpg, ch4))
    
    # Update the LCD display
    display_lcd(lpg, ch4)

    # Check if gas levels exceed 40 ppm
    if lpg > 15 or ch4 > 20:
        # If gas levels are high, turn on LEDs and buzzer
        red_led.on()
        buzzer.on()
    else:
        # If gas levels are below threshold, turn off LEDs and buzzer
        red_led.off()
        buzzer.off()

    # Wait for 5 seconds before the next reading
    sleep(5)
