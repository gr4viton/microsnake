#!/usr/bin/python
#
#  lcd_i2c.py
#  lcd1602 class for character display initialization and usage via micropython
#  Supports 16x2 and 20x4 screens.
#
# Author : gr4vion
# Date   : 28-10-2016
#
# On the base of: Matt Hawkins
# http://www.raspberrypi-spy.co.uk/
#
# Copyright 2015 Matt Hawkins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#--------------------------------------
import pyb
from pyb import I2C 


class lcd1602():
    # Define some device parameters
    I2C_ADDR  = None # I2C device address
    LCD_WIDTH = 16   # Maximum characters per line
    NUM_LINES = 2    # Number of lines

    # Define some device constants
    LCD_CHR = 1 # Mode - Sending data
    LCD_CMD = 0 # Mode - Sending command

    LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
    LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
    LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

    line_nums = [LCD_LINE_1, LCD_LINE_2, LCD_LINE_3, LCD_LINE_4]

    LCD_BACKLIGHT_ON = 0x08  # On
    LCD_BACKLIGHT_OFF = 0x00  # Off
    backlight = LCD_BACKLIGHT_ON 

    ENABLE = 0b00000100 # Enable bit

    # Timing constants
    E_PULSE = 0.0005*1000000 #us
    E_DELAY = 0.0005*1000000 #us

    E_PULSE = int(E_PULSE)
    E_DELAY = int(E_DELAY)
    #Open I2C interface
    #bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
    #bus = smbus.SMBus(1) # Rev 2 Pi uses 1
    blank_char = ' '

    
    def __init__(self, i2c, lcd_addr,  LCD_WIDTH=16, NUM_LINES=2, backlight_status=True):
        self.i2c = i2c
        self.I2C_ADDR = lcd_addr
        self.LCD_WIDTH = LCD_WIDTH 
        self.NUM_LINES = NUM_LINES 
        self.backlight_status = backlight_status
        self.update_backligth()

#        self.lcd_a = lcd_addr

        self.send_init_sequence()

    def update_backligth(self):
        self.set_backligth(self.backlight_status)

    def set_backligth(self, status=True):
        self.backlight = self.LCD_BACKLIGHT_ON if status else self.LCD_BACKLIGHT_OFF

    def send_init_sequence(self):
      # Initialise display
      self.send_cmd(0x33) # 110011 Initialise
      self.send_cmd(0x32) # 110010 Initialise
      self.send_cmd(0x06) # 000110 Cursor move direction
      self.send_cmd(0x0C) # 001100 Display On,Cursor Off, Blink Off 
      self.send_cmd(0x28) # 101000 Data length, number of lines, font size
      self.send_cmd(0x01) # 000001 Clear display
      pyb.udelay(self.E_DELAY)

    def i2c_write_byte(self, add, byte):
      self.i2c.send(byte, addr=add)  

    def send_cmd(self, bits):
        self.send_byte(bits, self.LCD_CMD)

    def send_byte(self, bits, mode):
      # Send byte to data pins
      # bits = the data
      # mode = 1 for data
      #        0 for command

      bits_high = mode | (bits & 0xF0) | self.backlight
      bits_low = mode | ((bits<<4) & 0xF0) | self.backlight

      # High bits
      self.i2c_write_byte(self.I2C_ADDR, bits_high)
      self.lcd_toggle_enable(bits_high)

      # Low bits
      self.i2c_write_byte(self.I2C_ADDR, bits_low)
      self.lcd_toggle_enable(bits_low)

    def lcd_toggle_enable(self, bits):
      # Toggle enable
      pyb.udelay(self.E_DELAY)
      self.i2c_write_byte(self.I2C_ADDR, (bits | self.ENABLE))
      pyb.udelay(self.E_PULSE)
      self.i2c_write_byte(self.I2C_ADDR,(bits & ~self.ENABLE))
      pyb.udelay(self.E_DELAY)

    def disp(self, message, line_num):
      # Send string to display line
      if line_num > self.NUM_LINES:
          print('Cannot dips on line indexed {}. LCD initialized with only {} lines!'.format(
              line_num, self.NUM_LINES))
          return
      line = self.line_nums[line_num]


    #  message = message.ljust(LCD_WIDTH," ")

      self.send_byte(line, self.LCD_CMD)
      #print(message)

      #if LCD_WIDTH > len(message):
      #  length = len(message)
      #else:
      #  length = LCD_WIDTH

      length = len(message)
      for i in range(self.LCD_WIDTH):

        if i >= length:
          byte = ord(self.blank_char)
        else:
          byte = ord(message[i])

        self.send_byte(byte, self.LCD_CHR)

def main():
  # Main program block

  # Initialise display
  
  lcd = lcd1602()
#  lcd_init()

  while True:

    # Send some test
    lcd.disp("RPiSpy         <", 0)
    lcd.disp("I2C LCD        <", 1)

    pyb.delay(500)
  
    # Send some more text
    lcd.disp(">         RPiSpy", 0)
    lcd.disp(">        I2C LCD", 1)

    pyb.delay(500)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd.send_cmd(0x01)

