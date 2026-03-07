# Overview

You'll run four experiments to prove your security actually works: an eavesdropper test, 
a certificate test, a speed test, and a stress test. 
This module covers the first one — the eavesdropper test. Can someone still read your data in transit? 
You'll try to spy on your own traffic. First without TLS to see what's exposed, then with TLS to prove it's 
blocked. This is exactly how penetration testers start: verify the most obvious attack first.

# Eavesdrop test
Part A: Without TLS (Insecure)
Open three separate terminal windows and run each command in its own terminal:
Terminal 1 — Start insecure broker:
```
mosquitto -c mosquitto_insecure.conf -v
```
Terminal 2 — Be the eavesdropper:
```
mosquitto_sub -h localhost -p 1883 -t "grandmarina/#" -v
```
Terminal 3 — Publish sensor data:
```
python experiment_runner.py --mode publish --tls off --count 5
```

 
# Part B: With TLS (Secure)
Use the same three terminal windows. Stop the running commands in each one with Ctrl+C, then run the new commands below.
Terminal 1 — Stop insecure broker (Ctrl+C), start TLS broker:
```
mosquitto -c mosquitto_tls.conf -v
```
Terminal 2 — Try to eavesdrop (without certificates):
```
mosquitto_sub -h localhost -p 8883 -t "grandmarina/#" -v
```
What you should see:
Error: A TLS error occurred.
Terminal 3 — Publish with TLS (proper certificates):
python experiment_runner.py --mode publish --tls on --count 5
The result: The eavesdropper can't connect. Messages are sent securely. TLS works!
