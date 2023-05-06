##########################################################################
# (C) 2021, Original by JarutEx
# (https://www.jarutex.com/index.php/2021/10/19/7295/  demo_ds1302.py)
# Mon'tsang modified
##########################################################################


from machine import Pin

# setting
class DS1302:
    REG_SECOND = const(0x80)
    REG_MINUTE = const(0x82)
    REG_HOUR   = const(0x84)
    REG_DAY    = const(0x86)
    REG_MONTH  = const(0x88)
    REG_WEEKDAY= const(0x8A)
    REG_YEAR   = const(0x8C)
    REG_WP     = const(0x8E)
    REG_CTRL   = const(0x90)
    REG_RAM    = const(0xC0)
    
    def __init__(self, _sclk=2, _io=5, _ce=4):
        self.pinClk = Pin( _sclk, Pin.OUT )
        self.pinIO = Pin( _io )
        self.pinCE = Pin( _ce, Pin.OUT )
        self.pinCE.value(0) # disable
        self.pinClk.value(0)
        self.rtc = [0,0,0,0,0,0,0] # y/m/d/dw/h/mi/s

    def dec2bcd(self, n):
        return ((n // 10 * 16) + (n % 10))

    def bcd2dec(self, n):
        return ((n // 16 * 10) + (n % 16))

    def write(self, data):
        self.pinIO.init(Pin.OUT)
        for i in range(8):
            bit = (data & 0x01)
            data = (data >> 1)
            self.pinIO.value(bit)
            self.pinClk.value(1)
            self.pinClk.value(0)
        
    def read(self):
        self.pinIO.init( Pin.IN )
        byte = 0
        for i in range(8):
            bit = self.pinIO.value() & 0x01
            bit = (bit << i)
            byte = (byte | bit)
            self.pinClk.value(1)
            self.pinClk.value(0)
        return byte
            
    def set(self, reg, data):
        self.pinCE.value(1)
        self.write( reg )
        self.write( data )
        self.pinCE.value(0)
            
    def get(self, reg):
        self.pinCE.value(1)
        self.write( reg+1 )
        data = self.read()
        self.pinCE.value(0)
        return data

    def now(self):
        self.rtc[0] = self.bcd2dec(self.get(REG_YEAR))+2000
        self.rtc[1] = self.bcd2dec(self.get(REG_MONTH))
        self.rtc[2] = self.bcd2dec(self.get(REG_DAY))
        self.rtc[3] = self.bcd2dec(self.get(REG_WEEKDAY))
        self.rtc[4] = self.bcd2dec(self.get(REG_HOUR))
        
        self.rtc[5] = ""
        if self.bcd2dec(self.get(REG_MINUTE)) < 10:
            self.rtc[5] = "0" + str(self.bcd2dec(self.get(REG_MINUTE)))
        else:
            self.rtc[5] = self.bcd2dec(self.get(REG_MINUTE))
            
        self.rtc[6] = ""
        if self.bcd2dec(self.get(REG_SECOND)) < 10:
            self.rtc[6] = "0" + str(self.bcd2dec(self.get(REG_SECOND)))
        else:
            self.rtc[6] = self.bcd2dec(self.get(REG_SECOND))
            
    def adjust(self, day, month, year, dow, hour, minute, second ):
        # convert
        year = year - 2000
        year = self.dec2bcd(year)
        month = self.dec2bcd(month)
        day = self.dec2bcd(day)
        dow = self.dec2bcd(dow)
        minute = self.dec2bcd(minute)
        hour = hour & 0x1F
        hour = self.dec2bcd(hour)
        second = self.dec2bcd(second)
        # adjust
        self.set(REG_YEAR, year)
        self.set(REG_MONTH, month)
        self.set(REG_DAY, day)
        self.set(REG_WEEKDAY, dow)
        self.set(REG_HOUR, hour)
        self.set(REG_MINUTE, minute)
        self.set(REG_SECOND, second)

    def show(self):
        print("{} {}-{}-{} {}:{}:{}".format(
            self.rtc[3],
            self.rtc[0], self.rtc[1], self.rtc[2],
            self.rtc[4], self.rtc[5], self.rtc[6]
            ))
        
    def get_date(self):
        date = "{}-{}-{}".format(self.rtc[0], self.rtc[1], self.rtc[2])
        return date
    
    def get_time(self):
        time = "{}:{}:{}".format(self.rtc[4], self.rtc[5], self.rtc[6])
        return time
        
    def get_dow(self):
        dow = "{}".format(self.rtc[3])
        return dow
    
    def get_sec(self):
        sec = "{}".format(self.rtc[6])
        return sec
    
    def get_min(self):
        mins = "{}".format(self.rtc[5])
        return mins
