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
    sqlite3.register_adapter(Decimal, adapt_decimal)
    sqlite3.register_converter("decimal", convert_decimal)

    conn = sqlite3.connect("db_simple.db", detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('create table if not exists templog (brewid INTEGER, time DATETIME default CURRENT_TIMESTAMP, temp REAL, target DECIMAL, state BOOLEAN, pin INT, FOREIGN KEY(brewid) REFERENCES brewlog(id))')
    cursor.execute('create table if not exists brewday (id INTEGER PRIMARY KEY, brew TEXT, brewdate DATETIME default CURRENT_DATE)')
    cursor.close()
    return conn

#updates the relevant info in the database.
def updatedb(brewid, temp, target, state, pin, sql):
#time is a default column, inserts timestamp in UTC. 
    data =(brewid,temp,target,state,pin)
    cursor = sql.cursor()
    cursor.execute('INSERT INTO templog (brewid, temp, target, state, pin) VALUES (?,?,?,?,?)',data)
    cursor.close()

def adapt_decimal(d):
    return str(d)

def convert_decimal(s):
    return D(s)
        

'''
Configures all pins as output pins and sets them to 'low'. This is to prevent any relay from being left on
unexpectedly. 
'''
def turnItAllOff(jee, gpioCount):
    print "Disabling all output pins"
    for pin in range(gpioCount):
        jee.config(pin, jee.OUTPUT)
        switch(jee,pin,False)
'''
Sets pin to output mode, if temp is less than target+band then pin is on otherwise it's off
this runs as fast as the temp sensor will poll.
'''
def main(target, pin):
    database = connectdb()
    brewinput = str(raw_input("What type of beer are we brewing? "))
    cursor = database.cursor()
    cursor.execute('INSERT INTO brewday (brew) VALUES (?)',[brewinput] )
    brewid = cursor.lastrowid
    print brewid 
    print "output mode on pin " + str(pin)
    gpios = 8
    #create output plug object
    jee = Adafruit_MCP230XX(address = 0x26, num_gpios = gpios)
    #set all output plug pins to output and off
    turnItAllOff(jee,gpios) 
    #the temp swing that is allowed. ie temp +- band
    band = Decimal(0.2)
    isHeatOn = False
    try:
        while (True):
            temp = get_temp()
            if temp < (target - band):
                print "on"
                isHeatOn = True
            elif temp > (target + band):
                print "off"
                isHeatOn = False
            else:
                print "Operating within normal parameters."
            updatedb(brewid, temp, target, isHeatOn, pin, database)
            switch(jee, pin, isHeatOn)
    except (KeyboardInterrupt, SystemExit):
        turnItAllOff(jee,gpios)
        sys.exit()

if __name__ == "__main__":        
    if len(sys.argv) < 2:
        print 'usage: ' + sys.argv[0] + ' targettemp'
        sys.exit()
    if sys.argv[1].isdigit():    
        target = Decimal(sys.argv[1])
    else:
        print 'target must be a number'
        sys.exit()
    main(target, 0)
