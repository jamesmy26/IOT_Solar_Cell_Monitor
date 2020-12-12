from ina219 import INA219
from mqttclient import MQTTClient
from machine import I2C, Pin
from board import SDA, SCL
import utime
import time
import network
import sys

# grab local time
localTime = utime.localtime()


# check wifi connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
ip = wlan.ifconfig()[0]
if ip == '0.0.0.0':
    print("no wifi connection")
    sys.exit()
else:
    print("connected to WiFi at IP", ip)

# Set up Adafruit connection
adafruitIoUrl = 'io.adafruit.com'
adafruitUsername = 'jamesmy26'
adafruitAioKey = 'aio_DjNi69lpIFnN2yYILMYOoxTDYV0s'

# Define callback function
def sub_cb(topic, msg):
    print((topic, msg))

# Connect to Adafruit server
print("Connecting to Adafruit")
mqtt = MQTTClient(adafruitIoUrl, port='1883', user=adafruitUsername, password=adafruitAioKey)
time.sleep(0.5)
print("Connected!")

# This will set the function sub_cb to be called when mqtt.check_msg() checks
# that there is a message pending
mqtt.set_callback(sub_cb)

#reset i2c
i2c.deinit()
#initialize ina219.
i2c = I2C(id=0, scl=Pin(SCL), sda=Pin(SDA), freq=100000)
#2.1195
print("scanning I2C bus ...")
print("I2C:", i2c.scan())

SHUNT_RESISTOR_OHMS = 0.1
ina = INA219(SHUNT_RESISTOR_OHMS, i2c)
ina.configure()


v_calibrated = 2.3
threshold = 0.12
lT = True
tMax = 10
count = 0




#if localTime[3] > 22:
if lT is True:  #this is a placeholder for testing purposes.
    for count in range (tMax):
        #measure every .5 second for 5 seconds.
        time.sleep(0.5)
        count += 1
        voltage = ina.current()*SHUNT_RESISTOR_OHMS
        v_diff = voltage-v_calibrated
        print(voltage)
        print('Voltage difference: ' + str(v_diff))
        if v_diff > threshold:

            # Send test message
            feedName = "jamesmy26/feeds/photosensor-test"
            Message = "Threshold passed: "+ str('%.3f'%(v_diff)) + " mV. Panels may be dirty."

            # testMessage = "1"
            mqtt.publish(feedName,Message)
            print("Published {} to {}.".format(Message,feedName))

            mqtt.subscribe(feedName)

            # For one minute look for messages (e.g. from the Adafruit Toggle block) on your test feed:
            for i in range(0, 60):
                mqtt.check_msg()
                time.sleep(1)

            '''
            # add additional values as required by application
            topic = "{}/data".format(session)
            data = "Threshold passed: "+ str(v_diff) + " mV. Panels may be dirty."

            #"Voltage: " + str(v) + "\n Current: " + str(i)+ "\n Power: " + str(p) + "\n Resistance: " + str(r)
            print("send topic='{}' data='{}'".format(topic, data))

            time.sleep(.3)
            mqtt.publish(topic, data)
            '''

            break

mqtt.disconnect()
