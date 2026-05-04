import time
import random
import ssl
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion


# ── CLOUDAMQP LAVINMQ ─────────────────────────────────────────────
BROKER   = "chameleon.lmq.cloudamqp.com"
PORT     = 8883
USERNAME = "ygmtijpl:ygmtijpl"
PASSWORD = "Qvl3fhaA1Z8Mnaeo6i60aUISpRrozMPW"


# ── UNIQUE TOPICS ─────────────────────────────────────────────────
TOPICS = {
    "temp":  "ROLETTA/FARM/TEMPERATURE",
    "hum":   "ROLETTA/FARM/HUMIDITY",
    "soil":  "ROLETTA/FARM/SOIL",
    "light": "ROLETTA/FARM/LIGHT",
    "water": "ROLETTA/FARM/WATERLEVEL",
    "rain":  "ROLETTA/FARM/RAINFALL",
}

CMD_TOPIC = "ROLETTA/FARM/CMD"

ACTIONS = {
    'a': "LED ON",
    'A': "LED OFF",
    'b': "Irrigation pump PULSE",
    'c': "Fan ON",
    'C': "Fan OFF",
    'd': "Feeder OPEN  (servo 80°)",
    'D': "Feeder CLOSE (servo 160°)",
    'e': "Buzzer BEEP",
}


def on_connect(client, userdata, flags, reason_code, properties=None):
    rc_str = str(reason_code)
    if rc_str == "Success":
        print(f"[SIM] ✓ Connected to LavinMQ: {BROKER}")
        client.subscribe(CMD_TOPIC, qos=1)
        print(f"[SIM] Listening for commands on {CMD_TOPIC}\n")
    else:
        print(f"[SIM] ✗ Connection failed: {rc_str}")


def on_message(client, userdata, message):
    cmd    = message.payload.decode("utf-8")
    action = ACTIONS.get(cmd, f"Unknown command: {cmd}")
    print(f"[SIM] Command received: '{cmd}' → {action}")


# ── CLIENT SETUP ──────────────────────────────────────────────────
client = mqtt.Client(
    CallbackAPIVersion.VERSION2,
    client_id="RolettaSimFarmNode"
)

client.username_pw_set(USERNAME, PASSWORD)

ssl_context = ssl.create_default_context()
client.tls_set_context(ssl_context)

client.on_connect = on_connect
client.on_message = on_message

print(f"[SIM] Connecting to {BROKER}:{PORT}...")
client.connect(BROKER, PORT, 60)
client.loop_start()

time.sleep(2)
print("[SIM] Simulator running. Press Ctrl+C to stop.\n")


# ── PUBLISH LOOP ──────────────────────────────────────────────────
try:
    while True:
        temp  = round(random.uniform(18, 35), 1)
        hum   = round(random.uniform(40, 85), 1)
        soil  = round(random.uniform(20, 90), 1)
        light = random.randint(10, 100)
        water = random.randint(10, 100)
        rain  = random.randint(0,  100)

        client.publish(TOPICS["temp"],  str(temp),  qos=1)
        client.publish(TOPICS["hum"],   str(hum),   qos=1)
        client.publish(TOPICS["soil"],  str(soil),  qos=1)
        client.publish(TOPICS["light"], str(light), qos=1)
        client.publish(TOPICS["water"], str(water), qos=1)
        client.publish(TOPICS["rain"],  str(rain),  qos=1)

        print(
            f"[SIM] Published → "
            f"Temp={temp}°C  Hum={hum}%  "
            f"Soil={soil}%  Light={light}%  "
            f"Water={water}%  Rain={rain}%"
        )
        time.sleep(2)

except KeyboardInterrupt:
    print("\n[SIM] Stopping simulator...")
finally:
    client.loop_stop()
    client.disconnect()
    print("[SIM] Disconnected. Goodbye.")