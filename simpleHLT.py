#!/usr/bin/python
import sys, time
from decimal import *
from smbus import SMBus
import sqlite3,datetime
from Adafruit_MCP230xx import *

'''
Takes the pin on a jeelabs output plug and sets it to 1 or 0 depending on if the heat should be on or not.
'''
def switch(jee,pin,duty_cycle):
    cycle_time = 2
    if duty_cycle > 0:
        duty = duty_cycle/100.0
        #on for xtime
        jee.output(pin,1)
	print "on"
        time.sleep(cycle_time*(duty))
        #off for ytime
        jee.output(pin,0)
	print "off"
        time.sleep(cycle_time*(1.0-duty))
    else:
        jee.output(pin,0)
        time.sleep(cycle_time)

    return

# returns temperature of the 1wire sensor. Needs to be abstracted more.
# catches for if owfs is not running would be good. or bitbang.
def get_temp():
    with open('/mnt/1wire/28.49B94A040000/temperature','r') as f:
    #with open('/mnt/1wire/10.67C6697351FF/temperature','r') as f:
        temp = Decimal(f.readline().strip())
        return temp + 8

#makes database connection, and creates the table if it doesn't exist yet.
def connectdb():
    sqlite3.register_adapter(Decimal, adapt_decimal)
    sqlite3.register_converter("decimal", convert_decimal)

    conn = sqlite3.connect("db_simple.db", detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('create table if not exists templog (brewid INTEGER, time TIMESTAMP, temp REAL, target DECIMAL, state BOOLEAN, element STRING, FOREIGN KEY(brewid) REFERENCES brewlog(id))')
    cursor.execute('create table if not exists brewday (id INTEGER PRIMARY KEY, brew TEXT, brewdate DATETIME default CURRENT_DATE)')
    cursor.execute('create table if not exists tempconfig (brewid INTEGER, target DECIMAL, swing DECIMAL, element STRING, FOREIGN KEY(brewid) REFERENCES brewlog(id))')
    cursor.close()
    return conn

#updates the relevant info in the database.
def updatedb(brewid, temp, target, state, element, sql):
    time = datetime.datetime.now()
    data =(brewid,time,temp,target,state,element)
    cursor = sql.cursor()
    cursor.execute('INSERT INTO templog (brewid,time, temp, target, state, element) VALUES (?,?,?,?,?,?)',data)
    cursor.close()

def adapt_decimal(d):
    return str(d)

def convert_decimal(s):
    return Decimal(s)

#could be moved to a database configuration. this will work for now.
def getpin(element):
    if element.lower() == "hlt":
        pin = 4
    elif element.lower() == "boil":
        pin = 1
    elif element.lower() == "test":
        pin = 7
    else:
        print "unconfigured pin"
        sys.exit()
    return pin

'''
Configures all pins as output pins and sets them to 'low'. This is to prevent any relay from being left on
unexpectedly.
'''
def turnItAllOff(jee, gpioCount):
    print "Disabling all output pins"
    for pin in range(gpioCount):
        jee.config(pin, jee.OUTPUT)
        switch(jee,pin,False)

def getUserInput():
    brewinput = raw_input("What type of beer are we brewing? ")
    if not brewinput:
        brewinput = "testbrau"
    element = raw_input("Which element is this?(HLT,boil)")
    if not element:
        element = "HLT"
    return brewinput, element

def settarget(brewid, element, target, sql):
    data = target, brewid, element
    cursor = sql.cursor()
    cursor.execute('update tempconfig set target=? WHERE brewid = ? AND element = ?',data)
    cursor.close()

def gettarget(brewid, element, sql):
    ids = brewid, element
    cursor = sql.cursor()
    cursor.execute('SELECT target FROM tempconfig where brewid = ? AND element = ?',ids)
    return cursor.fetchone()[0]

'''
Sets pin to output mode, if temp is less than target+band then pin is on otherwise it's off
this runs as fast as the temp sensor will poll.
'''
def tempcontrol():
    target = 0
    database = connectdb()
    brewname, element = getUserInput()
    pin = getpin(element)

    cursor = database.cursor()
    cursor.execute('INSERT INTO brewday (brew) VALUES (?)',[brewname] )
    brewid = cursor.lastrowid
    cursor.execute('INSERT INTO tempconfig (brewid, target, element) VALUES (?,?,?)',[brewid,target,element])
    settarget(brewid, element, target, database)
    print brewname + " has an id of " + str(brewid)
    print "output mode on " + element  + " pin " + str(pin)

    #there are 8 plugs on the JeeLabs Output Plug.
    gpios = 8
    #create output plug object
    jee = Adafruit_MCP230XX(address = 0x26, num_gpios = gpios, busnum = 1)
    #set all output plug pins to output and off
    turnItAllOff(jee,gpios)
    #the temp swing that is allowed. ie temp +- band
    band = Decimal(0.2)
    isHeatOn = False
    duty = 0
    try:
        while (True):
            temp = get_temp()
            if temp < (target - 10):
                duty = 100
            elif (target - 10) < temp < (target - band):
                duty = 50
            elif (target - 5) < temp < (target - band):
                duty = 25
            elif temp > (target + band):
                duty = 0
            else:
                print "Operating within normal parameters."
                duty = 0
            print "temp: " + str(temp) + " duty: " + str(duty) + " target: " + str(target)
            print "updating database"
	    updatedb(brewid, temp, target, isHeatOn, element, database)
            print "getting target"
	    target = gettarget(brewid, element, database)
	    print "switching"
            switch(jee, pin, duty)
    except (KeyboardInterrupt, SystemExit):
        turnItAllOff(jee,gpios)
        sys.exit()

if __name__ == "__main__":
   tempcontrol()
