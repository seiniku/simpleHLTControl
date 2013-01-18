#!/usr/bin/python
import sys, time, wiringpi
from decimal import *



def switch(gpio,pin,state):
    gpio.digitalWrite(pin,state)
    return
    
def get_temp():
    with open('/mnt/1wire/28.49B94A040000/temperature','r') as f:
        temp = Decimal(f.readline().strip())
        print temp


        return temp
'''
Sets pin to output mode, if temp is less than target+band then pin is on otherwise it's off
this runs as fast as the temp sensor will poll.
'''
def main(target, pin):
    io = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_PINS)
    
    on = io.HIGH
    off = io.LOW

    # sets pin to output mode 
    io.pinMode(pin,io.OUTPUT)
    print "output mode on pin " + str(pin)

    band = Decimal(0.2)
    while (True):
        if get_temp() < (target + band):
            print "on"
            switch(io, 7, on)
        else:
            print "off"
            switch(io, 7, off)
        
try: 
    if len(sys.argv) < 2:
        print 'usage: ' + sys.argv[0] + ' targettemp'
        sys.exit()
    if sys.argv[1].isdigit():    
        target = Decimal(sys.argv[1])
    else:
        print 'target must be a number'
        sys.exit()
    main(target)
except (KeyboardInterrupt, SystemExit):
    sys.exit()
