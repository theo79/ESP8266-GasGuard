import time
from machine import I2C, Pin

class LCD1602:
    def __init__(self, i2c, addr=0x27):
        self.i2c = i2c
        self.addr = addr
        self.backlight = 0x08
        self.init_lcd()

    def send(self, data, mode):
        highnib = data & 0xF0
        lownib = (data << 4) & 0xF0
        self.i2c.writeto(self.addr, bytearray([highnib | self.backlight | mode | 0x04]))
        self.i2c.writeto(self.addr, bytearray([highnib | self.backlight | mode]))
        self.i2c.writeto(self.addr, bytearray([lownib | self.backlight | mode | 0x04]))
        self.i2c.writeto(self.addr, bytearray([lownib | self.backlight | mode]))

    def send_cmd(self, cmd):
        self.send(cmd, 0)

    def send_data(self, data):
        self.send(data, 1)

    def init_lcd(self):
        self.send_cmd(0x33)  # Initialize
        self.send_cmd(0x32)  # Set to 4-bit mode
        self.send_cmd(0x06)  # Cursor move direction
        self.send_cmd(0x0C)  # Turn cursor off
        self.send_cmd(0x28)  # 2 line display
        self.send_cmd(0x01)  # Clear display
        time.sleep_ms(5)

    def clear(self):
        self.send_cmd(0x01)  # Clear display
        time.sleep_ms(5)

    def print(self, msg, col=0, row=0):
        pos = col + 0x80 if row == 0 else col + 0xC0
        self.send_cmd(pos)
        for char in msg:
            self.send_data(ord(char))
