"""Dashboard subscriber for Grand Marina topics.

Connects to the local MQTT broker and subscribes to
`hydroficient/grandmarina/#`. Incoming payloads are assumed to be JSON; the
subscriber parses them and prints a formatted view of any sensor readings.
Non-JSON messages are shown verbatim with the topic.

Usage:
    python dashboard_subscriber.py

"""

import sys
import paho.mqtt.client as mqtt
import json
from datetime import datetime


def on_connect(client, userdata, flags, rc, properties=None):
    print("\n" + "=" * 60)
    print("  GRAND MARINA WATER MONITORING DASHBOARD")
    print("  Connected at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    client.subscribe("hydroficient/grandmarina/#")


def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8', errors='replace')
    try:
        data = json.loads(payload)
        display_reading(data)
    except json.JSONDecodeError:
        print(f"\n[RAW] {msg.topic}")
        print(f"      {payload}")
    except Exception as e:
        print(f"\n[ERR] failed to handle message on {msg.topic}: {e}")
        print(f"      {payload}")


def _as_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def display_reading(data):
    print(f"\n{'─' * 40}")
    print(f"  Location:  {data.get('location', 'Unknown')}")
    print(f"  Device ID: {data.get('device_id', 'Unknown')}")
    print(f"  Time:      {data.get('timestamp', 'N/A')}")
    print(f"  Count:     #{data.get('counter', 0)}")
    print(f"{'─' * 40}")

    up = _as_float(data.get('pressure_upstream', 0))
    down = _as_float(data.get('pressure_downstream', 0))
    print(f"  Pressure (upstream):   {up:6.1f} PSI")
    print(f"  Pressure (downstream): {down:6.1f} PSI")

    diff = up - down
    print(f"  Pressure differential: {diff:6.1f} PSI")

    flow = _as_float(data.get('flow_rate', 0))
    print(f"  Flow rate:             {flow:6.1f} gal/min")


if __name__ == "__main__":
    # setup client
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting to broker...")
    try:
        client.connect("localhost", 1883)
    except Exception as e:
        print(f"Failed to connect to broker: {e}")
        sys.exit(1)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        client.disconnect()
