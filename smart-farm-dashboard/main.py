import panel as pn
import pandas as pd
import hvplot.pandas  # noqa
from mqtt_client import start_mqtt, register_message_callback, publish_command
from db import init_db, log_measurement, get_recent_measurements


pn.extension(design="material")  # ← Removed "hvplot" from extension


# ── DATABASE ──────────────────────────────────────────────────────
init_db()


# ── LIVE DISPLAY PANES ────────────────────────────────────────────
temp_pane  = pn.pane.Str("Temperature : -- °C")
hum_pane   = pn.pane.Str("Humidity    : -- %")
soil_pane  = pn.pane.Str("Soil        : -- %")
light_pane = pn.pane.Str("Light       : -- %")
water_pane = pn.pane.Str("Water Level : -- %")
rain_pane  = pn.pane.Str("Rainfall    : -- %")
status     = pn.pane.Str("Status: waiting for data...")
last_cmd   = pn.pane.Str("Last command: none")


# ── MQTT MESSAGE HANDLER ──────────────────────────────────────────
def handle_message(topic, payload):
    if   topic == "ROLETTA/FARM/TEMPERATURE": temp_pane.object  = f"Temperature : {payload} °C"
    elif topic == "ROLETTA/FARM/HUMIDITY":    hum_pane.object   = f"Humidity    : {payload} %"
    elif topic == "ROLETTA/FARM/SOIL":        soil_pane.object  = f"Soil        : {payload} %"
    elif topic == "ROLETTA/FARM/LIGHT":       light_pane.object = f"Light       : {payload} %"
    elif topic == "ROLETTA/FARM/WATERLEVEL":  water_pane.object = f"Water Level : {payload} %"
    elif topic == "ROLETTA/FARM/RAINFALL":    rain_pane.object  = f"Rainfall    : {payload} %"
    status.object = f"Status: last update → {topic} = {payload}"
    log_measurement(topic, payload)


register_message_callback(handle_message)
start_mqtt()


# ── HISTORY PLOTS ─────────────────────────────────────────────────
def make_plot(topic, label, color):
    rows = get_recent_measurements(topic)
    if not rows:
        return pn.pane.Markdown(f"*No {label} history yet. Waiting for data...*")
    df = pd.DataFrame(rows, columns=["timestamp", "value"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.hvplot.line(
        x="timestamp", y="value",
        title=f"{label} History",
        xlabel="Time", ylabel=label,
        line_width=2, color=color,
        responsive=True, height=250,
    )


def temp_plot():  return make_plot("ROLETTA/FARM/TEMPERATURE", "Temperature (°C)",  "orange")
def hum_plot():   return make_plot("ROLETTA/FARM/HUMIDITY",    "Humidity (%)",      "deepskyblue")
def soil_plot():  return make_plot("ROLETTA/FARM/SOIL",        "Soil Moisture (%)", "green")


# ── CONTROLS ──────────────────────────────────────────────────────
def send(char, desc):
    publish_command("ROLETTA/FARM/CMD", char)
    last_cmd.object = f"Last command: {desc} ({char})"


btn_led_on     = pn.widgets.Button(name="LED ON",       button_type="success")
btn_led_off    = pn.widgets.Button(name="LED OFF",      button_type="warning")
btn_pump       = pn.widgets.Button(name="Irrigate",     button_type="primary")
btn_fan_on     = pn.widgets.Button(name="Fan ON",       button_type="primary")
btn_fan_off    = pn.widgets.Button(name="Fan OFF",      button_type="danger")
btn_feed_open  = pn.widgets.Button(name="Open Feeder",  button_type="primary")
btn_feed_close = pn.widgets.Button(name="Close Feeder", button_type="danger")
btn_buzzer     = pn.widgets.Button(name="Buzzer Beep",  button_type="warning")

btn_led_on.on_click(     lambda e: send('a', "LED ON"))
btn_led_off.on_click(    lambda e: send('A', "LED OFF"))
btn_pump.on_click(       lambda e: send('b', "Irrigation pump"))
btn_fan_on.on_click(     lambda e: send('c', "Fan ON"))
btn_fan_off.on_click(    lambda e: send('C', "Fan OFF"))
btn_feed_open.on_click(  lambda e: send('d', "Feeder OPEN"))
btn_feed_close.on_click( lambda e: send('D', "Feeder CLOSE"))
btn_buzzer.on_click(     lambda e: send('e', "Buzzer"))


# ── LAYOUT ────────────────────────────────────────────────────────
live_tab = pn.Column(
    "### Live Sensor Readings",
    pn.Row(temp_pane,  hum_pane),
    pn.Row(soil_pane,  light_pane),
    pn.Row(water_pane, rain_pane),
    pn.Spacer(height=10),
    status,
)

controls_tab = pn.Column(
    "### Actuator Controls",
    pn.Row(btn_led_on,    btn_led_off),
    pn.Row(btn_pump),
    pn.Row(btn_fan_on,    btn_fan_off),
    pn.Row(btn_feed_open, btn_feed_close),
    pn.Row(btn_buzzer),
    pn.Spacer(height=10),
    last_cmd,
)

history_tab = pn.Column(
    "### Sensor History",
    pn.bind(temp_plot),
    pn.bind(hum_plot),
    pn.bind(soil_plot),
)

app = pn.Column(
    "# 🌱 Smart Farm IoT Dashboard",
    pn.Tabs(
        ("🌡 Live",      live_tab),
        ("🎛 Controls",  controls_tab),
        ("📈 History",   history_tab),
    ),
)

app.servable()