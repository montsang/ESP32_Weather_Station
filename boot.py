##########################################
# MicroPython-ESP32 Weather Station
# The MIT License (MIT)
# Copyright (c) 2023, Mon'tsang
# auritek@outlook.com
##########################################

import sh1106
import network
from time import sleep
from machine import SPI, Pin
    
  
hspi = SPI(2, sck=Pin(18), mosi=Pin(23)) 

dc = Pin(27)    # data/command
rst = Pin(26)   # reset
cs = Pin(25)   # chip select

display = sh1106.SH1106_SPI(128, 64, hspi, dc, rst, cs)    
    
wifi = network.WLAN(network.STA_IF)  
if not wifi.isconnected():
    display.text(" :::BOOTING::: ", 0, 28)
    display.show()
    print('[WLAN] Init...')
    wifi.active(True) 
    wifi.connect('REPLACE WITH YOUR SSID', 'REPLACE WITH YOUR PASSWORD')
    sleep(8)
        
    if not wifi.isconnected():
        wifi.active(False)
        display.fill(0)
        display.text("[WLAN] ERROR!!", 0, 28)
        display.show()
        print('WLAN Connection Error, Please Reconnect')
    else:
        display.fill(0)
        display.text("[WLAN] SUCCESS!!", 0, 28)
        display.show()
        print('Network Config:', wifi.ifconfig())
        sleep(1)
            
else:
    display.text(" Refreshing...", 0, 28)
    display.show()
