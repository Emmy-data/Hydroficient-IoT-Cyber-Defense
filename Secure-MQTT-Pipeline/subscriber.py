# This is a standard dashboard (Subscriber) that recieves the readings from the Hydrologic
# devices in all the locations.

from asyncio.log import logger
import ssl   # ADD THIS FOR TLS
import sys
import paho.mqtt.client as mqtt
import json
from datetime import datetime

def _as_float(v, default=0.0):
    """Convert value to float, return default if conversion fails."""
    try:
        return float(v)
    except Exception:
        return default

def on_connect(client, userdata, flags, rc, properties=None):
    print("\n" + "=" * 60)
    print("  GRAND MARINA WATER MONITORING DASHBOARD")
    print("  Connected at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    client.subscribe("hydroficient/grandmarina/#")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        display_reading(data)
    except json.JSONDecodeError:
        print(f"\nRaw message: {msg.payload.decode()}")
    except Exception as e:
        print(f"\n[ERR] Failed to handle message on {msg.topic}: {e}")

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

# TLS CONFIGURATION - ADD THIS FOR TLS

TLS_CONFIG = {
    "ca_certs": "certs/ca_cert.pem",      # Path to CA certificate
    "broker_host": "localhost",
    "broker_port": 8883,              # TLS port (not 1883!)
}

# Create and configure client (explicit MQTT v3.1.1 for compatibility)
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

# This call is what actually activates encryption. 
# Add this before your client.connect() line:
logger.info(f"Configuring TLS with CA: {TLS_CONFIG['ca_certs']}")
client.tls_set(                
    ca_certs=TLS_CONFIG["ca_certs"],
    certfile=None,
    keyfile=None,
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS,
)
logger.info("TLS configuration complete.")  
print("Connecting to broker...")
try:
    client.connect("localhost", 8883)
except Exception as e:
    print(f"Failed to connect to broker: {e}")
    sys.exit(1)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nDisconnecting...")
    client.disconnect()
