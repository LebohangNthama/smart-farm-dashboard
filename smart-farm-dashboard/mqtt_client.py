import threading
import ssl
import socket
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion


# ── HIVEMQ CLOUD BROKER SETTINGS ──────────────────────────────────
MQTT_BROKER    = "da704a6633684c3babbb04059852362e.s1.eu.hivemq.cloud"
MQTT_PORT      = 8883
MQTT_KEEPALIVE = 60

MQTT_USERNAME  = "YOUR_HIVEMQ_USERNAME"  # ← Replace
MQTT_PASSWORD  = "YOUR_HIVEMQ_PASSWORD"  # ← Replace


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
    if reason_code == 0:
        print(f"[MQTT] ✓ Connected to HiveMQ Cloud: {MQTT_BROKER}")
        for t in SUBSCRIBE_TOPICS:
            client.subscribe(t, qos=1)
            print(f"[MQTT]   → Subscribed to {t}")
    else:
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
            print("[MQTT]   → Check MQTT_USERNAME and MQTT_PASSWORD")


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

    # Authentication
    _client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Use the SAME SSL context that passed the SSL OK test
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    _client.tls_set_context(ssl_context)

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
        print(f"[MQTT]   → Check broker URL and credentials")


def publish_command(topic, payload):
    if _client is None:
        raise RuntimeError("Call start_mqtt() first.")
    result = _client.publish(topic, payload, qos=1)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"[MQTT] ✓ Published '{payload}' to '{topic}'")
    else:
        print(f"[MQTT] ✗ Failed to publish to '{topic}'")
    return result