"""
Publisher that connects three hydrologic sensors to MQTT.
One — an MQTT client in __init__. The sensor now has a connection to the broker.
Two — a topic based on location. The sensor knows where to publish its readings.
Three — a publish_reading() method that sends to MQTT instead of just returning the data.
Four — a run_continuous() helper for easy testing. Start it and it keeps publishing until you stop it.

"""

from venv import logger
from zipfile import Path

import paho.mqtt.client as mqtt
import json
import time
import threading
import ssl
from sensor import WaterSensor
from subscriber import TLS_CONFIG
from pathlib import Path


class WaterSensorMQTT:
    """
    A water sensor that publishes readings to MQTT.
    """

    def __init__(self, device_id, location, broker="localhost", port=8883):
        self.device_id = device_id
        self.location = location
        self.broker = broker
        self.port = port

        # Use WaterSensor for reading generation
        self.sensor = WaterSensor(device_id, location)

        # MQTT setup
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        
        # TLS Configuration
        #check that certificate file exists
        ca_path = Path("certs/ca_cert.pem")
        if ca_path.exists():
            logger.info(f"Configuring TLS with CA: {ca_path}")
        else:
            logger.error(f"CA certificate not found: {ca_path}")
            logger.error("Run generate_certs.py first!")
            raise FileNotFoundError(f"CA certificate not found: {ca_path}")   
            self.client.tls_set(
                ca_certs=str(ca_path),
                certfile=None,
                keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,        # Use modern TLS           
            )
        logger.info("TLS configuration complete.")
        self.client.connect(broker, port)
        self.client.loop_start()
        
        # Publish readings to this topic
        self.topic = f"hydroficient/grandmarina/sensors/{self.location}/readings"

    def get_reading(self):
        """Get a sensor reading."""
        return self.sensor.get_reading()

    def publish_reading(self):
        """Generate a reading and publish it to MQTT."""
        reading = self.get_reading()
        self.client.publish(self.topic, json.dumps(reading))
        return reading

    def run_continuous(self, interval=2):
        """Publish readings continuously at the specified interval."""
        print(f"Starting device: {self.device_id}")
        print(f"Location: {self.location}")
        print(f"Publishing to: {self.topic}")
        print(f"Interval: {interval} seconds")
        print("-" * 40)

        try:
            next_time = time.perf_counter()
            while True:
                # Publish and log
                reading = self.publish_reading()
                print(f"[{reading['counter']}] Pressure: {reading['pressure_upstream']}/{reading['pressure_downstream']} PSI, Flow: {reading['flow_rate']} gal/min")

                # Schedule next send time and sleep only the remaining time
                next_time += interval
                sleep_for = next_time - time.perf_counter()
                if sleep_for > 0:
                    time.sleep(sleep_for)
                else:
                    # If we're behind schedule, don't sleep — continue immediately
                    next_time = time.perf_counter()
        except KeyboardInterrupt:
            print("\nSensor stopped.")
            self.client.loop_stop()
            self.client.disconnect()

def run_sensor(device_id, location, interval):
    sensor = WaterSensorMQTT(device_id=device_id, location=location)
    sensor.run_continuous(interval)

devices = [
    {"device_id": "GM-HYDROLOGIC-01", "location": "main-building"},
    {"device_id": "GM-HYDROLOGIC-02", "location": "pool-wing"},
    {"device_id": "GM-HYDROLOGIC-03", "location": "kitchen"},
]

threads = []
for d in devices:
    t = threading.Thread(target=run_sensor, args=(d["device_id"], d["location"], 2), daemon=True)
    t.start()
    threads.append(t)

print("All sensors running. Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping all sensors...") 