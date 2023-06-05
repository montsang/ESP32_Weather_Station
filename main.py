##########################################
# MicroPython-ESP32 Weather Station
# The MIT License (MIT)
# Copyright (c) 2023, Mon'tsang
# auritek@outlook.com
##########################################

import sh1106
import dht
import ds1302
import _thread
import ntptime
from urequests import get
from ujson import loads
from time import sleep, sleep_ms, localtime
from machine import SPI, Pin


amap_api = 'REPLACE YOUR AMAP API LINK HERE'

hspi = SPI(2, sck=Pin(18), mosi=Pin(23))

dc = Pin(27)
rst = Pin(26)
cs = Pin(25)

display = sh1106.SH1106_SPI(128, 64, hspi, dc, rst, cs)

sensor = dht.DHT11(Pin(17))
rtc = ds1302.DS1302()
mu = _thread.allocate_lock()

global dow, point, weather_status
w, wt, wh = "", "", ""

dow = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
point = ["00", "10", "20", "30", "40", "50"]

with open('weather.json') as wsf:
    weather_status = loads(wsf.read())
    
    
try:
    wrq = get(amap_api)
except:
    wt = wh = w = "ERR"
else:
    wr = loads(wrq.text)
            
    if wr["status"] == "0":
        wt = wh = "-"
        w = "N/A"
    else:
        wt = wr["lives"][0]["temperature"]
        wh = wr["lives"][0]["humidity"]
        w = weather_status[wr["lives"][0]["weather"]]


display.text("HAVE A NICE DAY!", 0, 0)
display.text(" [RTC] Loading ", 0, 10)
display.text("----------------", 0, 18)
display.text(" [T] - / "+ wt+ " 'C" , 0, 27)
display.text(" [H] - / "+ wh+ " %" , 0, 36)
display.text("----------------", 0, 45)
display.text("> "+ w, 0, 53)
display.show()

sleep(3)

#NTP Time Sync
try:
    ntptime.settime()
except Exception as e:
    print(e)
    pass;
else:
    ntp_time = localtime()
    rtc.adjust(ntp_time[2], ntp_time[1], ntp_time[0], ntp_time[6], ntp_time[3]+ 8, ntp_time[4], ntp_time[5])   # ntp_time[3]+ TIMEZONE


def rtc_thr():
    while True:
        mu.acquire()
        # clear disp blk
        display.fill_rect(0, 0, 128, 18, 0)
        mu.release()
        #display.show()
        #get rtc info
        try:
            rtc.now()
        except Exception as e:
            print(e)
            mu.acquire()
            display.text("HAVE A NICE DAY!", 0, 0)
            display.text("[RTC] ERROR!", 0, 10)
        else:
            mu.acquire()
            display.text(" " + rtc.get_date() + " <" + dow[eval(rtc.get_dow()) - 1] + ">", 0, 0)
            display.text("  = " + rtc.get_time() + " =  ", 0, 10)
        display.show()
        mu.release()
        sleep_ms(100)

def dht_thr():
    global h, t, wh, wt, w, wr, wrq
    #get weather
    while True:
        #
        if rtc.get_min() in point and rtc.get_sec() == "05":
            try:
                wrq = get(amap_api)
            except Exception as e:
                print(e)
                wt = wh = w = "ERR"
            else:    
                wr = loads(wrq.text)
                
                if wr["status"] == "0":
                    wt = wh = "-"
                    w = "N/A"
                else:
                    wt = wr["lives"][0]["temperature"]
                    wh = wr["lives"][0]["humidity"]
                    w = weather_status[wr["lives"][0]["weather"]]
                    mu.acquire()
                    display.fill_rect(0, 53, 128, 8, 0)
                    display.text("> "+ w, 0, 53)
                    mu.release()
        else:
            pass
        
        #get dht11 info
        if rtc.get_sec() in point:
            try:
                sensor.measure()
            except Exception as e:
                print(e)
                h = t = "ERR"
            else:
                h = str(sensor.humidity())
                t = str(sensor.temperature())
                
            mu.acquire()
            display.fill_rect(0, 27, 128, 18, 0)
            display.text(" [T] "+ t+ " / "+ wt+ " 'C" , 0, 27)
            display.text(" [H] "+ h+ " / "+ wh+ " %" , 0, 36)
            display.show()
            mu.release()
        else:
            pass
        sleep(1)
        
_thread.start_new_thread(dht_thr, ())
rtc_thr()
