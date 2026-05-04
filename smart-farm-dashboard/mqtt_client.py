import threading
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion

# ── BROKER SETTINGS ──────────────────────────────────────────────
MQTT_BROKER    = "broker.hivemq.com"
MQTT_PORT      = 1883
MQTT_KEEPALIVE = 60

# ── UNIQUE TOPICS ─────────────────────────────────────────────────
# ROLETTA/FARM/ prefix makes these unique on the public broker
# so no other user's data mixes with yours
SUBSCRIBE_TOPICS = [
    "ROLETTA/FARM/TEMPERATURE",
    "ROLETTA/FARM/HUMIDITY",
    "ROLETTA/FARM/SOIL",
    "ROLETTA/FARM/LIGHT",
    "ROLETTA/FARM/WATERLEVEL",
    "ROLETTA/FARM/RAINFALL",
]

_client = None
_message_callbacks = []


def register_message_callback(callback):
    _message_callbacks.append(callback)


def _on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[MQTT] Connected: {reason_code}")
    for t in SUBSCRIBE_TOPICS:
        client.subscribe(t)
        print(f"[MQTT] Subscribed to {t}")


def _on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    topic   = message.topic
    print(f"[MQTT] {topic} => {payload}")
    for cb in _message_callbacks:
        cb(topic, payload)


def start_mqtt():
    global _client
    if _client is not None:
        return
    _client = mqtt.Client(
        CallbackAPIVersion.VERSION2,
        client_id="SmartFarmDashboard"
    )
    _client.on_connect = _on_connect
    _client.on_message = _on_message
    _client.connect(MQTT_BROKER, port=MQTT_PORT, keepalive=MQTT_KEEPALIVE)
    thread = threading.Thread(target=_client.loop_forever, daemon=True)
    thread.start()
    print("[MQTT] Connected to public broker")


def publish_command(topic, payload):
    if _client is None:
        raise RuntimeError("Call start_mqtt() first.")
    _client.publish(topic, payload)
    print(f"[MQTT] Published '{payload}' to '{topic}'")