print("Sensors and Actuators")

import time
import serial.tools.list_ports
import sys
import requests
import random
from Adafruit_IO import MQTTClient

AIO_USERNAME = "duyp"
AIO_KEY = ""

#global_equation = "x1 + x2 + x3"

try:
    ser = serial.Serial(port="COM3", baudrate=115200)
except:
    print("Can not open the port")

def sendCommand(cmd):
    ser.write(cmd.encode())

mess = ""
def processData(data, client):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    for i in range(3):
      client.publish("sensordata",splitData[i])
    
def readSerial(client):
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1], client)
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]

def requestData(cmd, client):
    sendCommand(cmd)
    time.sleep(1)
    readSerial(client)

def connected(client):
    print("Server connected ...")
    client.subscribe("button1")
    client.subscribe("button2")
    client.subscribe("equation")

def subscribe(client , userdata , mid , granted_qos):
    print("Subscribeb!!!")

def disconnected(client):
    print("Disconnected from the server!!!")
    sys.exit(1)

def message(client , feed_id , payload):
    print("Received: " + payload)
    if feed_id == "button1":
      if payload == "1":
          print("on")
          sendCommand("2")
      elif payload == "0":
          print("off")
          sendCommand("3")
    if feed_id == "button2":
        if payload == "1":
            print("on")
            sendCommand("4")
        elif payload == "0":
            print("off")
            sendCommand("5")
    if feed_id == "equation":
      global global_equation
      global_equation = payload
      print(global_equation)

def init_global_equation():
    global global_equation
    headers = {}
    aio_url = "https://io.adafruit.com/api/v2/duyp/feeds/equation"
    x = requests.get(url=aio_url, headers=headers, verify=False)
    data = x.json()
    global_equation = data["last_value"]
    print("Get lastest value:", global_equation)

def modify_value(x1, x2, x3):
    global  global_equation
    print("Equation: ", global_equation)
    result = eval(global_equation)
    print(result)
    return result

client = MQTTClient(AIO_USERNAME , AIO_KEY)

client.on_connect = connected  #function pointer
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe

client.connect()
client.loop_background()
init_global_equation()

while True:
    requestData("0", client)
    requestData("1", client)
    time.sleep(3)
    s1 = random.randint(4,110)
    s2 = random.randint(2,1000)
    s3 = random.randint(1,800)
    client.publish("sensor1", s1)
    client.publish("sensor2", s2)
    client.publish("sensor3", s3)
    s4 = modify_value(s1, s2, s3)
    client.publish("sensor4", s4)
    print(s4)
    time.sleep(1)

    pass
