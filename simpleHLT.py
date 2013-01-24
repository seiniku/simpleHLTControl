#!/usr/bin/python
import sys, time, wiringpi
from decimal import *
from smbus import SMBus
import sqlite3
from Adafruit_MCP230xx import *

'''
Takes the pin on a jeelabs output plug and sets it to 1 or 0 depending on if the heat should be on or not.
'''
def switch(jee,pin,heatIsOn):
    if heatIsOn:
        jee.output(pin,1)
    else:
        jee.output(pin,0)
    return

# returns temperature of the 1wire sensor. Needs to be abstracted more.    
# catches for if owfs is not running would be good. or bitbang.
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

def turnItAllOff():
    gpios = 8
    jee = Adafruit_MCP230XX(address = 0x26, num_gpios = gpios) 
    for pin in range(gpios):
        switch(jee,pin,False)
        print "disabling pin " + str(pin)
'''
Sets pin to output mode, if temp is less than target+band then pin is on otherwise it's off
this runs as fast as the temp sensor will poll.
'''
def main(target, pin):
    database = connectdb()
    print "output mode on pin " + str(pin)
    gpios = 8
    #create output plug object
    jee = Adafruit_MCP230XX(address = 0x26, num_gpios = gpios)
    #set all output plug pins to output and off
    for outpin in range(gpios):
        jee.config(outpin, jee.OUTPUT)
        switch(jee,outpin,False)
    
    #the temp swing that is allowed. ie temp +- band
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
        switch(jee, pin, isHeatOn)


if __name__ == "__main__":        
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
        turnItAllOff()
        sys.exit()
