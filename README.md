simpleHLTControl
================

A simple temp control designed for controlling a heating element in a hot liquor tun.


This depends on the jeelabs output plug to have the address 0x26. Note that the output plug expects ground wires to be attached, not hot. Power the relays seperately and return their grounds to the output plug. 


Adafruit libraries are being used to interface with the output plug in a readable way. They were taken from https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code, I take no credit for them. Worked great out of the box.


potentially depends on celery for async web stuff. rabbitmq for the message queue, flask for the web
sudo pip install celery 
sudo apt-get install rabbitmq-server
sudo pip install flask

