import threading
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion


# ── MOSQUITTO PUBLIC BROKER ───────────────────────────────────────
MQTT_BROKER    = "test.mosquitto.org"
MQTT_PORT      = 1883  # Plain — works on PythonAnywhere FREE tier
MQTT_KEEPALIVE = 60

# No username/password needed for Mosquitto public broker
MQTT_USERNAME  = ""
MQTT_PASSWORD  = ""


# ── UNIQUE TOPICS ─────────────────────────────────────────────────
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
    rc_str = str(reason_code)

    if rc_str == "Success":
        print(f"[MQTT] ✓ Connected to Mosquitto: {MQTT_BROKER}")
        for t in SUBSCRIBE_TOPICS:
            client.subscribe(t, qos=1)
            print(f"[MQTT]   → Subscribed to {t}")
    else:
        print(f"[MQTT] ✗ Connection failed: {rc_str}")


def _on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    topic   = message.topic
    print(f"[MQTT] {topic} => {payload}")
    for cb in _message_callbacks:
        cb(topic, payload)


def _on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"[MQTT] ⚠ Unexpected disconnection (code {rc})")


def start_mqtt():
    global _client
    if _client is not None:
        print("[MQTT] Already connected")
        return

    _client = mqtt.Client(
        CallbackAPIVersion.VERSION2,
        client_id="RolettaSmartFarmDashboard"
    )

    # No TLS needed for Mosquitto port 1883
    # No authentication needed

    # Callbacks
    _client.on_connect    = _on_connect
    _client.on_message    = _on_message
    _client.on_disconnect = _on_disconnect

    # Connect
    print(f"[MQTT] Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
    try:
        _client.connect(MQTT_BROKER, port=MQTT_PORT, keepalive=MQTT_KEEPALIVE)
        thread = threading.Thread(target=_client.loop_forever, daemon=True)
        thread.start()
    except Exception as e:
        print(f"[MQTT] ✗ Connection error: {e}")


def publish_command(topic, payload):
    if _client is None:
        raise RuntimeError("Call start_mqtt() first.")
    result = _client.publish(topic, payload, qos=1)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"[MQTT] ✓ Published '{payload}' to '{topic}'")
    else:
        print(f"[MQTT] ✗ Failed to publish to '{topic}'")
    return result