# Hydroficient-IoT-Cyber-Defense
This is a repository committed to what i learnt and did i building a secure IoT device for Hydroficient water usuage and monitoring activities. This project secures the Grand Marina hotel’s HYDROLOGIC water monitoring system by implementing a secure IoT pipeline.

It includes:

* TLS and Mutual TLS (mTLS) for encrypted and authenticated communication between sensors, server, and dashboard.

* Replay attack protection using timestamp validation, counters, and HMAC message signing.

* Real-time monitoring dashboard for water flow, pressure, and remote shutoff controls.

# Set up
### 1. Clone or download repo
```
https://github.com/Emmy-data/Hydroficient-IoT-Cyber-Defense.git
```

### 2. Install mosquitto: 
[https://mosquitto.org/download/](https://mosquitto.org/download/)


### 3. Create & activate virtual environment

```
python3 -m venv venv
source venv/bin/activate
```
### 4. Install dependencies
```
pip install paho-mqtt
```

