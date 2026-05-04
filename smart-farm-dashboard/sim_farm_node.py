import time
import random
import paho.mqtt.client as mqtt

# ── BROKER SETTINGS ──────────────────────────────────────────────
BROKER = "broker.hivemq.com"
PORT   = 1883

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

# ── COMMAND MAP ───────────────────────────────────────────────────
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


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"[SIM] Connected to broker (rc={rc})")
    client.subscribe(CMD_TOPIC)
    print(f"[SIM] Listening for commands on {CMD_TOPIC}")


def on_message(client, userdata, message):
    cmd    = message.payload.decode("utf-8")
    action = ACTIONS.get(cmd, f"Unknown command: {cmd}")
    print(f"[SIM] Command received: '{cmd}' → {action}")


# ── CLIENT SETUP ──────────────────────────────────────────────────
client = mqtt.Client(client_id="SimFarmNode")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_start()

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

        client.publish(TOPICS["temp"],  str(temp))
        client.publish(TOPICS["hum"],   str(hum))
        client.publish(TOPICS["soil"],  str(soil))
        client.publish(TOPICS["light"], str(light))
        client.publish(TOPICS["water"], str(water))
        client.publish(TOPICS["rain"],  str(rain))

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