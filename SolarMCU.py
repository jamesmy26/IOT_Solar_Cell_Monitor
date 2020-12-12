from mqttclient import MQTTClient
from math import sin
import network
import sys
from ina219 import INA219
from machine import I2C, Pin
from board import SDA, SCL
import time

i2c = I2C(id=0, scl=Pin(SCL), sda=Pin(SDA), freq=100000)

print("scanning I2C bus ...")
print("I2C:", i2c.scan())

SHUNT_RESISTOR_OHMS = 0.1
ina = INA219(SHUNT_RESISTOR_OHMS, i2c)
ina.configure()

session = 'ishan'
BROKER = 'test.mosquitto.org'

# check wifi connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
ip = wlan.ifconfig()[0]
if ip == '0.0.0.0':
    print("no wifi connection")
    sys.exit()
else:
    print("connected to WiFi at IP", ip)

# connect to MQTT brokerxxx
print("Connecting to MQTT broker", BROKER, "...", end="")
mqtt = MQTTClient(BROKER, port=1883)
print("Connected!")

while True:
    v = ina.voltage()
    i = ina.current()
    p = v * i / 1000
    print("P = ", p)
    time.sleep(1)
    topic = "{}/data".format(session)
    data = "{}".format(p)
    print("send topic='{}' data='{}'".format(topic, data))
    mqtt.publish(topic, data)

mqtt.disconnect()





