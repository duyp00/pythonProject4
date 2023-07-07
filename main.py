print("Sensors and Actuators")

import time
import serial.tools.list_ports
import sys
from Adafruit_IO import MQTTClient

AIO_USERNAME = "duyp"
AIO_KEY = ""

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
    client.publish("sensordata",splitData[2])

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
    client.subscribe("sensordata")

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


client = MQTTClient(AIO_USERNAME , AIO_KEY)

client.on_connect = connected  #function pointer
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe

client.connect()
client.loop_background()

while True:
    requestData("0", client)
    time.sleep(1)
    requestData("1", client)
    time.sleep(1)

    pass