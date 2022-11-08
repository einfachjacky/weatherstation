from machine import Pin, I2C
import time
import bme280
import math
import network
import socket

ssid='UPC3915714'
password=''

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(reading):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <title>Pico W Weather Station </title>
            <meta http-equiv="refresh" content="10">
            </head>
            <body>
            <p>{reading}</p>
            </body>
            </html>
            """
    return str(html)

sda=Pin(0) 
scl=Pin(1) 
i2c=I2C(0,sda=sda, scl=scl, freq=400000)

# Check if RPi pico is found and some properties
print('Scan i2c bus...')
devices = i2c.scan()
if len(devices) == 0:
    print("No i2c device !")
else:
    print("Device found")
devices = i2c.scan()
if devices:
    for i in devices:
        print("The device hex code is ", hex(i), " the address number is ", i)


def serve(connection):
    #Start a web server
    while 1:
        bme=bme280.BME280(i2c=i2c, address=119)
        temp = bme.values[0]
        pressure = bme.values[1]
        humidity = bme.values[2]
        reading = "Temperature: " + temp
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        html = webpage(reading)
        client.send(html)
        client.close()

if 0:
    #for starting webpage
    try:
        ip = connect()
        connection = open_socket(ip)
        serve(connection)
    except KeyboardInterrupt:
        machine.reset()


if 0:
    #simplest LED blinking test
    led = machine.Pin("LED", machine.Pin.OUT)
    while True:
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(1)


#read out temperature, air pressure and humidity
if 1:
    bme = bme280.BME280(i2c=i2c, address=119)          #BME280 object created
    print(bme.values)

if 1:
    button = Pin(16, Pin.IN, Pin.PULL_UP)
    button_state=0
    circumference = 2*3.1415*0.09 #meter
    rotations=0
    time_average=1 #seconds
    time_sleep=0.01
    runs=0
    while 1:
        if button_state==0 and button.value():
            button_state=1
            rotations+=0.5
        if button_state and button.value()==0:
            button_state=0
        
        time.sleep(time_sleep)
        runs+=1
        if runs*time_sleep>=time_average:
            runs=0
            wind_speed=rotations*circumference/time_average #m/s
            print("wind speed = %1.2f m/s which is %1.2f km/h"%(wind_speed, wind_speed*3.6))
            rotations=0

  


