import threading
import ssl
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion


# ── CLOUDAMQP LAVINMQ — Whitelisted on PythonAnywhere FREE ───────
MQTT_BROKER    = "chameleon.lmq.cloudamqp.com"
MQTT_PORT      = 8883
MQTT_KEEPALIVE = 60
MQTT_USERNAME  = "ygmtijpl:ygmtijpl"
MQTT_PASSWORD  = "Qvl3fhaA1Z8Mnaeo6i60aUISpRrozMPW"


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
        print(f"[MQTT] ✓ Connected to LavinMQ: {MQTT_BROKER}")
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
        print(f"[MQTT] ⚠ Disconnected (code {rc})")


def start_mqtt():
    global _client
    if _client is not None:
        print("[MQTT] Already connected")
        return

    _client = mqtt.Client(
        CallbackAPIVersion.VERSION2,
        client_id="RolettaSmartFarmDashboard"
    )

    _client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    ssl_context = ssl.create_default_context()
    _client.tls_set_context(ssl_context)

    _client.on_connect    = _on_connect
    _client.on_message    = _on_message
    _client.on_disconnect = _on_disconnect

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