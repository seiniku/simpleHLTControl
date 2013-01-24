#!/usr/bin/python
import sys, time, wiringpi
from decimal import *
from smbus import SMBus
import sqlite3



#sets heat on or off for a gpio pin. needs changing to adafruit expansion.
def switch(gpio,pin,heatIsOn):
#    gpio.digitalWrite(pin,state)
    bus = SMBus(0)
    address = 0x26
    bus.write_byte_data(address,0x00,0x00)
    if heatIsOn:
        bus.write_byte_data(address,0x09,0x01)
    else:
        bus.write_byte_data(address,0x09,0x00)
    return
# returns temperature of the 1wire sensor. Needs to be abstracted more.    
def get_temp():
    with open('/mnt/1wire/28.49B94A040000/temperature','r') as f:
        temp = Decimal(f.readline().strip())
        print temp


        return temp

#makes database connection, and creates the table if it doesn't exist yet.
def connectdb():
    conn = sqlite3.connect("simplehtl.db")
    cursor = conn.cursor()
    cursor.execute('create table if not exists templog (time, temp, target, state, pin)')
    cursor.close()
    return conn

#updates the relevant info in the database.
def updatedb(temp, target, state, pin, sql):
    now = time.time()
    data =(now,temp,target,state, pin)
    cursor = sql.cursor()
    cursor.execute('INSERT INTO templog VALUES(?,?,?,?,?)',data)
    cursor.close()

'''
Sets pin to output mode, if temp is less than target+band then pin is on otherwise it's off
this runs as fast as the temp sensor will poll.
'''
def main(target, pin):
    database = connectdb()
    io = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_PINS)
    
    on = io.HIGH
    off = io.LOW

    # sets pin to output mode 
    io.pinMode(pin,io.OUTPUT)
    print "output mode on pin " + str(pin)

    band = Decimal(0.2)
    while (True):
        temp = get_temp()
        if temp < (target - band):
            print "on"
            isHeatOn = True
        elif temp > (target + band):
            print "off"
            isHeatOn = False
#        updatedb(temp, target, isHeatOn, pin, database) #currently broken
        switch(io, pin, isHeatOn)
        
try: 
    if len(sys.argv) < 2:
        print 'usage: ' + sys.argv[0] + ' targettemp'
        sys.exit()
    if sys.argv[1].isdigit():    
        target = Decimal(sys.argv[1])
    else:
        print 'target must be a number'
        sys.exit()
    main(target, 7)
except (KeyboardInterrupt, SystemExit):
    sys.exit()
