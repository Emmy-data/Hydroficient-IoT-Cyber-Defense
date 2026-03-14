# Overview
On top of our TLS pipeline, we will add mTLS for device authentication. After device verifies broker's identity, broker will verify device identity before accepting readings. This prevents attackers from setting up a fake sensor and sending fake readings and dangerous commands. We will generate client certificates — one per HYDROLOGIC device and configure Mosquitto to require client certificates (require_certificate true).

# Protection added to pipeline:
1. Authentication of devices (sensors and dashboards have to prove they are not an imposter)

# mTLS Handshake Overview
1. Device will send hello to server (mosquitto broker).

2. Broker will send its server certificate.

3. Device will use CA certificate to check if the server certificate is signed by  CA.

4. Now device will send its certificate to server.

3. Now server will use CA certificate to check if the device certificate is signed by CA.

6. Encrypted data will be sent using the other entities' public key, which can only be decrypted by the other entities' private key. This makes sure only the real client/holding their private key can decrypt data.

# Set up instructions
### 1. Generate key and certificates for the broker and Hydrologic devices.
Generate CA and server keys, certificates using the python file:
```
python3 generate_certs.py
```
### 2. Configure Mosquitto Broker to Use Certificates
This file will tell mosquitto broker to require device authenticate and not allow anonymous users.
```
allow_anonymous false
require_certificate true
tls_version tlsv1.2
```

### 3. Upgrade subscriber.py and publisher.py to use mTLS
We provide path to CA certificate, device certificate, device private key. 

publisher.py:
```
mqttc.tls_set('certs/ca.pem','certs/sensor1.pem','certs/sensor1-key.pem')
```

subscriber.py:
```
mqttc.tls_set('certs/ca.pem','certs/dashboard1.pem','certs/dashboard1-key.pem')
```

### 4. Test if mTLS is working
![mTLS Tests](images/broker.png)

Start mosquitto broker with mTLS configuration (provide proper path to conf file):
```
mosquitto -c mosquitto-mtls.conf -v      
```
On another terminal, run subscriber.py:
```
python3 subscriber.py
```
![mTLS Tests](images/sub.png)
On another terminal, run publisher.py:
```
python3 publisher.py
```
![mTLS Tests](images/pub.png)
This will start publishing readings.

We will start seeing readings from publisher. Visually, this looks same, however, now broker and devices verify each other and readings are encrypted.


# Security Tests
### Test 1: Can a device with no certificate connect?
Run the no_certs python file that only points to a CA certificate (no device certificate or key).
```
python3 no_certs.py
```
Error: peer did not return a certificate. Broker rejected the connection, test passed.

![no-device-certificate](images/no_certs.png)

### Test 2: Connection time experiment
We need two Mosquitto instances running at the same time — one with one-way TLS, one with mTLS.

Terminal 1 — Start the one-way TLS broker (port 8883)
```
mosquitto -c mosquitto_tls.conf -v
```
Terminal 2 — Start the mTLS broker (port 8884)
```
mosquitto -c mosquitto_mtls_benchmark.conf -v
```
Terminal 3 - Run the connection benchmark file (20 test for tls and 20 for mtls)
```
python3 mtls_benchmark.py --mode connection --trials 20
```
The python file mTLS_benchmark.py runs 20 connection trials for each mode and
calculate the minimum, maximum and average connection time for each mode.

![test3](images/connect.png)

Result: The overhead is 55.4% as it takes extra 3.7 ms for the devices to connect
under Mutual TLS connection (mTLS).

### Test 3: Message Latency Test
Run the latency benchmark:
```
python mtls_benchmark.py --mode latency --count 50
```

![test4](media/test4.png)


# Cost
Adding mTLS has a connection time overhead. While making the connection, there’s an extra step (server has to verify client). This increase connection time, however, it is a one time cost. Sensors don’t need to connect again for hours or days. Once connection is established, there’s no extra message latency. In our environment, the benefits of mTLS outweigh this cost. 
