# mqtt_listener.py

import json
import paho.mqtt.client as mqtt

BROKER_ADDRESS = "localhost"  # Replace with IP if running on a different device
TOPIC = "board/1/objects"

def on_connect(client, userdata, flags, rc, properties=None):
    print("[MQTT] Connected with result code", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"\n[MQTT] Message received on {msg.topic}:")
    try:
        data = json.loads(msg.payload.decode())
        for obj in data.get("objects", []):
            print(f"  • {obj['type'].capitalize()} #{obj['id']}: {obj['label']} (votes: {obj['confidence']})")
    except json.JSONDecodeError:
        print("[ERROR] Could not decode JSON payload.")

client = mqtt.Client(client_id="listener_test", protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_ADDRESS)
client.loop_forever()
