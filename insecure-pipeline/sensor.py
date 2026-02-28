import random
from datetime import datetime, timezone

class WaterSensor:
    def __init__(self, device_id):
        self.device_id = device_id
        self.counter = 0
        # Base values for realistic variation
        self.base_pressure_up = 82.0
        self.base_pressure_down = 76.0
        self.base_flow = 40.0

    def get_reading(self):
        """Generate a normal sensor reading"""
        self.counter += 1

        return {
            "device_id": self.device_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "counter": self.counter,
            "pressure_upstream": round(self.base_pressure_up + random.uniform(-2, 2), 1),
            "pressure_downstream": round(self.base_pressure_down + random.uniform(-2, 2), 1),
            "flow_rate": round(self.base_flow + random.uniform(-3, 3), 1)
        }
    # leak means high flow rate
    def get_leak_reading(self):
        """Generate a reading simulating a water leak"""
        reading = self.get_reading()
        reading["flow_rate"] = round(random.uniform(80, 120), 1)
        return reading
    #Water blockage means high upstream and low downstream
    def get_blockage_reading(self):
        """Generate a reading simulating a pipe blockage"""
        reading = self.get_reading()
        reading["pressure_upstream"] = round(random.uniform(85, 95), 1)
        reading["pressure_downstream"] = round(random.uniform(30, 50), 1)
        return reading
    # Stuck sensor means you keep getting the same readings.
    def get_stuck_reading(self):
        """Generate a reading simulating a stuck sensor"""
        reading = self.get_reading()
        stuck_value = 82.0
        reading["pressure_upstream"] = stuck_value
        reading["pressure_downstream"] = stuck_value
        reading["flow_rate"] = stuck_value
        return reading
