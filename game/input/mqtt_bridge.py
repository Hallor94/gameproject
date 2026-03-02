# file: input/mqtt_bridge.py

import json
import paho.mqtt.client as mqtt
from utils import globals as G
from utils.logger import log_info, log_debug, log_error
from input.board_object_router import watch_board_state_for_objects

# === MQTT CONFIG ===
BROKER_ADDRESS = "localhost"

# === Internal: listener registry ===
_listeners = []

def register_mqtt_listener(func):
    _listeners.append(func)

# === Internal: MQTT callbacks ===
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log_info("MQTT", "Connected successfully — subscribing to all board topics")
        client.subscribe("board/1/objects")
        client.subscribe("board/1/motion")
    else:
        log_error("MQTT", f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        log_info("MQTT", f"Received message on topic '{msg.topic}'")
        data = json.loads(msg.payload.decode())
        log_debug("MQTT", f"Payload:\n{json.dumps(data, indent=2)}")
        for func in _listeners:
            func(data)
    except Exception as e:
        log_error("MQTT", f"Error handling message: {e}")

def unified_message_handler(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == "board/1/motion":
        try:
            data = json.loads(payload)
            G.is_recognizer_busy = bool(data.get("motion", False))
            log_debug("MQTT", f"Motion update received: {G.is_recognizer_busy}")
        except Exception as e:
            log_error("MQTT", f"Error parsing motion payload: {e}")
    elif topic == "board/1/objects":
        on_message(client, userdata, msg)

# === MQTT setup ===
def _start_mqtt():
    client = mqtt.Client(client_id="receiver_program", protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = unified_message_handler
    client.connect(BROKER_ADDRESS)
    client.loop_start()

# === Main dispatch function ===
def handle_mqtt_message(data):
    G.last_board_state = data["objects"] if isinstance(data, dict) else data
    # Notify any listeners (e.g. debug HUD, resolver watcher)
    for func in _listeners:
        func(G.last_board_state)

# === Init ===
def init_mqtt_bridge():
    register_mqtt_listener(handle_mqtt_message)
    register_mqtt_listener(watch_board_state_for_objects)
    _start_mqtt()
    log_info("MQTT", "MQTT bridge initialized.")
