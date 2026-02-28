"""Simple publisher script using WaterSensorMQTT

This script instantiates a sensor located in the `main-building` and
starts sending a reading every two seconds to the
`hydroficient/grandmarina/sensors/main-building/readings` topic.
    python sensor_publisher.py

"""

from publisher import WaterSensorMQTT


def main():
    # create a sensor with a unique identifier and fixed location
    sensor = WaterSensorMQTT(device_id="sensor-001", location="main-building")
    # run continuously with a 2 second cadence
    sensor.run_continuous(interval=2)


if __name__ == "__main__":
    main()
