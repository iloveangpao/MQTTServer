from paho import mqtt
import paho.mqtt.client as paho
import firebase_admin
from firebase_admin import credentials, db
import json

# Initialize Firebase with your credentials file
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {'databaseURL' : 'https://coen-446-default-rtdb.firebaseio.com/'})

# Callback functions for MQTT client
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")
    client.subscribe("plants")  # Subscribe to the temperature topic

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
    received_data_dict = json.loads(msg.payload.decode())
    update_firebase(msg.topic, received_data_dict)

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def update_firebase(topic, data):
    # Reference to your Firebase database
    ref = db.reference(topic)  # Reference to the 'plants' node

    plant_id = data['id']
    initial_data = data['data']
    datetime_reading = initial_data['moisture']['currentDateAndTime']
    moisture_value = initial_data['moisture']['reading']

    # Check if the plant ID exists as a child under 'plants'
    if not ref.child(plant_id).get():
        # If the plant ID does not exist, add the child with initial data
        toSet = initial_data
        toSet['moisture'] = {datetime_reading:moisture_value}
        ref.child(plant_id).set(toSet)
    else:
        # If the plant ID exists, update the moisture data
        moisture_ref = ref.child(plant_id).child('moisture')
        existing_moisture = moisture_ref.get()
        
        if existing_moisture:
            # Update existing data with new entry
            existing_moisture[datetime_reading] = moisture_value
            moisture_ref.set(existing_moisture)
        else:
            # If 'moisture' node doesn't exist, create a new one
            moisture_ref.set({datetime_reading: moisture_value})

client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set("username", "WErock123")
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("94e50a3aa3a041ddb033aad7d78701cd.s1.eu.hivemq.cloud", 8883)
client.loop_forever()
