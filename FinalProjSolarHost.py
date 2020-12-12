import paho.mqtt.client as paho
import matplotlib.pyplot as plt
import requests
import json


# Pull current solar radiation
url = "https://api.solcast.com.au/world_radiation/forecasts/ghi"

api_key = "-Q9CanYnfix4dxyisoknf0QF3PhQZsuZ"
params = {
  'api_key': api_key,
  'latitude': 40.79204,
  'longitude': -73.539848
}

headers = {
  'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers, params=params)

json_response = response.json()

current_ghi = json_response['forecasts'][0]['ghi']

session = "ishan"
BROKER = 'test.mosquitto.org'
qos = 0

# connect to MQTT broker
print("Connecting to MQTT broker", BROKER, "...", end="")
mqtt = paho.Client()
mqtt.connect(BROKER, port=1883)
print("Connected!")

# initialize data vector
p = []
efficiencyArray = []

area = 0.107 * 0.061 #m^2

def efficiency(area, power, radiation):
    return 100 * power / (area * radiation)

# mqtt callbacks
def data(c, u, message):
    # extract data from MQTT message
    msg = message.payload.decode('ascii')
    # convert to vector of floats
    f = [ float(x) for x in msg.split(',') ][0]
    eff = efficiency(area, f, current_ghi)
    eff = round(eff, 2)
    if (eff < 0.75):
        print("Panel efficiency indicates debris buildup")
    print("efficiency: ", eff, "%")
    # append to data vectors, add more as needed
    p.append(f)
    efficiencyArray.append(eff)

# subscribe to topics
data_topic = "{}/data".format(session, qos)

mqtt.subscribe(data_topic)

mqtt.message_callback_add(data_topic, data)

# wait for MQTT messages
# this function never returns
print("waiting for data ...")
mqtt.loop_forever()