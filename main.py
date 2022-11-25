from machine import Pin, I2C
import time
import bme280
import math
import network
import socket

ssid='UPC3915714'
password=''

def debug(i2c):
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

def serve(i2c, connection):
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

def start_webpage(i2c):
     #for starting webpage
    try:
        ip = connect()
        connection = open_socket(ip)
        serve(i2c, connection)
    except KeyboardInterrupt:
        machine.reset()

def LED_blinking():
    #simplest LED blinking test
    led = machine.Pin("LED", machine.Pin.OUT)
    while True:
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(1)

#rainfall rf sensors
    
if 1:
    #temperature, humidity, pressure
    sda=Pin(0) 
    scl=Pin(1) 
    i2c=I2C(0,sda=sda, scl=scl, freq=400000) 
    bme = bme280.BME280(i2c=i2c, address=119)          #BME280 object created
    
    #windspeed (ws)
    button_ws = Pin(16, Pin.IN, Pin.PULL_UP)
    button_ws_state=0
    circumference_ws = 2*3.1415*0.09 #meter
    rotations_ws=0
    time_average_ws=1 #seconds
    time_sleep_ws=0.01
    runs_ws=0
    
    #rainfall rf
    button_rf = Pin(6, Pin.IN, Pin.PULL_UP)
    button_rf_state=1
    bucket_size_rf = 0.2794
    count_rf = 0
    time0_rf = time.time()
    average_time_rf = 30 #rainfall in the last 900 seconds

    
    while 1:
        #windspeed ws
        if button_ws_state==0 and button_ws.value():
            button_ws_state=1
            rotations_ws+=0.5
        if button_ws_state and button_ws.value()==0:
            button_ws_state=0
        time.sleep(time_sleep_ws)
        runs_ws+=1
        if runs_ws*time_sleep_ws>=time_average_ws:
            runs_ws=0
            wind_speed=rotations_ws*circumference_ws/time_average_ws #m/s
            print("Wind speed = %1.2f m/s which is %1.2f km/h"%(wind_speed, wind_speed*3.6))
            print("Temperature=%s, Pressue=%s, Humidity=%s"%(bme.values[0], bme.values[1], bme.values[2]))
            rotations_ws=0
            
        #rainfall rf

        if button_rf_state==0 and button_rf.value():
            button_rf_state=1
            count_rf+=1
        if button_rf_state and button_rf.value()==0:
            button_rf_state=0
        if time.time() >= time0_rf + average_time_rf:
            rainfall = count_rf * bucket_size_rf
            count_rf=0
            time0_rf=time.time()
            print("rainfall", average_time_rf)
            
            
        

  


