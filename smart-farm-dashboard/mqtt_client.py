import threading
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import ssl


# ── HIVEMQ CLOUD BROKER SETTINGS ──────────────────────────────────
MQTT_BROKER    = "da704a6633684c3babbb04059852362e.s1.eu.hivemq.cloud"
MQTT_PORT      = 8883  # TLS/SSL secure port
MQTT_KEEPALIVE = 60

# TODO: Get these credentials from HiveMQ Cloud Console > Access Management
MQTT_USERNAME  = "Nthama"  # ← Replace with your username
MQTT_PASSWORD  = "Ntharm!n@ter2023"  # ← Replace with your password


# ── UNIQUE TOPICS ─────────────────────────────────────────────────
# Your ROLETTA/FARM/ prefix is perfect - keeps your data separate
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
    if reason_code == 0:
        print(f"[MQTT] ✓ Connected to HiveMQ Cloud: {MQTT_BROKER}")
        for t in SUBSCRIBE_TOPICS:
            client.subscribe(t, qos=1)
            print(f"[MQTT]   → Subscribed to {t}")
    else:
        # Detailed error messages
        error_messages = {
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorized"
        }
        error = error_messages.get(reason_code, f"Unknown error code {reason_code}")
        print(f"[MQTT] ✗ Connection failed: {error}")
        if reason_code == 4:
            print(f"[MQTT]   → Check MQTT_USERNAME and MQTT_PASSWORD in this file")


def _on_message(client, userdata, message):
    payload = message.payload.d