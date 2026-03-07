# Overview

In this test, we will be working as a penetration tester in order to prove our security actually works: an eavesdropper test, a certificate test, a speed test, and a stress test. 

# Eavesdrop test
Part A: Without TLS (Insecure)
Open three separate terminal windows and run each command in its own terminal:
Terminal 1 — Start insecure broker:
```
mosquitto -c mosquitto_insecure.conf -v
```
![broker](images/insecure-conf.png)

Terminal 2 — Be the eavesdropper:
```
mosquitto_sub -h localhost -p 1883 -t "grandmarina/#" -v
```
![broker](images/eavesa.png)
Terminal 3 — Publish sensor data:
```
python experiment_runner.py --mode publish --tls off --count 5
```
![broker](images/tls-off.png)

Part B: With TLS (Secure)
we will be using the same three terminal windows. Stop the running commands in each one with Ctrl+C, then run the new commands below.
Terminal 1 — Stop insecure broker (Ctrl+C), start TLS broker:
```
mosquitto -c mosquitto_tls.conf -v
```
![broker](images/secure-conf.png)

Terminal 2 — Try to eavesdrop (without certificates):
```
mosquitto_sub -h localhost -p 8883 -t "grandmarina/#" -v
```
![broker](images/eavesb.png)

Error: A TLS error occurred.
Terminal 3 — Publish with TLS (proper certificates):
```
python experiment_runner.py --mode publish --tls on --count 5
```
![broker](images/tls-on.png)

The result: The eavesdropper can't connect. Messages are sent securely. TLS works!
