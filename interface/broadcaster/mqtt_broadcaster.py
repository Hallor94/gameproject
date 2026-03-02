# mqtt_broadcaster.py

import json
import paho.mqtt.client as mqtt

BROKER_ADDRESS = "localhost"  # or use your Pi's IP if needed
TOPIC = "board/1/objects"

client = mqtt.Client(client_id="recognizer_board_1", protocol=mqtt.MQTTv311)
client.connect(BROKER_ADDRESS)


def publish_recognition(results):
    """
    Publish recognition results (cards and dice) to MQTT topic.
    `results` should be a list of dicts from recognize_cards().
    """
    payload = []
    for obj in results:
        payload.append({
            "id": obj["object_id"],
            "type": obj["type"],
            "label": obj["best_label"],
            "confidence": obj["vote_count"],
            "is_confident": obj["is_confident"],
        })

    message = json.dumps({
        "source": "board_1",
        "objects": payload
    })

    result = client.publish(TOPIC, message)
    status = result.rc
    if status == 0:
        print(f"[MQTT] Published {len(payload)} objects to {TOPIC}")
    else:
        print(f"[MQTT] Failed to send message to {TOPIC}. Error code: {status}")
